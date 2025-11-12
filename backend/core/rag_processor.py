"""
RAG Processor - Main Integration Point
Processes files and handles RAG pipeline for chat integration
"""

from typing import List, Dict, Optional, Tuple
import time
from pathlib import Path
from sqlalchemy.orm import Session

from backend.core.rag_chunker import chunk_text
from backend.core.rag_embedder import RAGEmbedder, embed_chunks
from backend.core.rag_retriever import HybridRetriever
from backend.core.rag_reranker import rerank_results
from backend.core.rag_citations import format_response_with_citations, CitationFormat
from backend.core.rag_optimizer import optimize_retrieval_context, QueryExpander
from backend.database.rag_models import DocumentChunk, RAGConfiguration, RAGMetrics
from backend.database.file_operations import FileDB
from backend.utils.file_storage import file_storage
from backend.utils.file_parser import file_parser
import numpy as np
import pickle


class RAGProcessor:
    """
    Main RAG processor for chat integration
    Handles full pipeline: chunk → embed → retrieve → rerank → cite
    """
    
    def __init__(self, db: Session, user_id: int):
        """
        Initialize RAG processor
        
        Args:
            db: Database session
            user_id: User ID
        """
        self.db = db
        self.user_id = user_id
        self.embedder = RAGEmbedder()
        
        # Load user configuration
        self.config = self._load_config()
    
    def _load_config(self) -> RAGConfiguration:
        """Load user RAG configuration"""
        config = self.db.query(RAGConfiguration).filter(
            RAGConfiguration.user_id == self.user_id
        ).first()
        
        if not config:
            # Create default config
            config = RAGConfiguration(
                user_id=self.user_id,
                is_enabled=True,
                chunk_size=1000,
                chunk_overlap=200,
                chunking_strategy="recursive",
                top_k=5,
                min_similarity=0.5,
                retrieval_mode="hybrid",
                semantic_weight=0.7,
                keyword_weight=0.3,
                use_reranking=True,
                show_citations=True,
                citation_format="inline",
                use_compression=False,
                use_query_expansion=False,
                use_mmr=True,
                mmr_lambda=0.5
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        
        return config
    
    def process_file(self, file_id: int) -> Dict:
        """
        Process a file for RAG
        Chunks and embeds the file
        
        Args:
            file_id: File ID to process
        
        Returns:
            Processing result dictionary
        """
        start_time = time.time()
        
        # Get file
        file_record = FileDB.get_file(file_id)
        if not file_record or file_record.user_id != self.user_id:
            return {"success": False, "error": "File not found"}
        
        # Get file content
        full_path = file_storage.get_file_path(file_record.file_path)
        parse_result = file_parser.parse_file(full_path, file_record.file_type)
        
        if not parse_result['success']:
            return {"success": False, "error": "Failed to parse file"}
        
        text = parse_result.get('text', '')
        if not text:
            return {"success": False, "error": "No text content"}
        
        # Check if already processed
        existing_chunks = self.db.query(DocumentChunk).filter(
            DocumentChunk.file_id == file_id,
            DocumentChunk.user_id == self.user_id
        ).count()
        
        if existing_chunks > 0:
            return {
                "success": True,
                "already_processed": True,
                "chunks_count": existing_chunks,
                "message": "File already processed"
            }
        
        # Chunk document
        chunks = chunk_text(
            text=text,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            strategy=self.config.chunking_strategy,
            metadata={
                "file_id": file_id,
                "filename": file_record.original_filename,
                "file_type": file_record.file_type
            }
        )
        
        if not chunks:
            return {"success": False, "error": "No chunks generated"}
        
        # Generate embeddings
        chunks_with_embeddings = embed_chunks(chunks, use_cache=True)
        
        # Save to database
        saved_count = 0
        for chunk in chunks_with_embeddings:
            embedding = chunk.metadata.get('embedding')
            if embedding is None:
                continue
            
            # Serialize embedding
            embedding_bytes = pickle.dumps(embedding)
            
            db_chunk = DocumentChunk(
                file_id=file_id,
                user_id=self.user_id,
                content=chunk.content,
                chunk_index=chunk.chunk_id,
                total_chunks=len(chunks),
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                chunk_size=len(chunk.content),
                token_count=chunk.token_count(),
                strategy=self.config.chunking_strategy,
                header=chunk.metadata.get('header'),
                page_number=chunk.metadata.get('page_number'),
                chunk_type=chunk.metadata.get('type'),
                language=chunk.metadata.get('language'),
                embedding=embedding_bytes,
                embedding_model=chunk.metadata.get('embedding_model'),
                embedding_dim=chunk.metadata.get('embedding_dim'),
                meta_data=chunk.metadata
            )
            
            self.db.add(db_chunk)
            saved_count += 1
        
        self.db.commit()
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "chunks_count": saved_count,
            "processing_time": round(elapsed, 2),
            "file_name": file_record.original_filename
        }
    
    def retrieve_context(
        self,
        query: str,
        file_ids: Optional[List[int]] = None,
        top_k: Optional[int] = None
    ) -> Tuple[List[DocumentChunk], Dict]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: User query
            file_ids: Specific file IDs to search (None = all files)
            top_k: Number of results (None = use config)
        
        Returns:
            (chunks, metrics)
        """
        start_time = time.time()
        
        top_k = top_k or self.config.top_k
        
        # Get chunks from database
        query_obj = self.db.query(DocumentChunk).filter(
            DocumentChunk.user_id == self.user_id
        )
        
        if file_ids:
            query_obj = query_obj.filter(DocumentChunk.file_id.in_(file_ids))
        
        db_chunks = query_obj.all()
        
        if not db_chunks:
            return [], {"error": "No chunks found"}
        
        # Deserialize embeddings
        chunks = []
        embeddings = []
        
        for db_chunk in db_chunks:
            if db_chunk.embedding:
                try:
                    embedding = pickle.loads(db_chunk.embedding)
                    chunks.append(db_chunk)
                    embeddings.append(embedding)
                except Exception as e:
                    print(f"Error loading embedding: {e}")
                    continue
        
        if not chunks:
            return [], {"error": "No valid embeddings found"}
        
        # Expand query if enabled
        queries = [query]
        if self.config.use_query_expansion:
            expander = QueryExpander()
            queries = expander.expand_query(query, num_variations=2)
        
        # Search with all query variations
        all_results = []
        seen_chunk_ids = set()
        
        for q in queries:
            # Generate query embedding
            query_embedding = self.embedder.embed_text(q)
            if query_embedding is None:
                continue
            
            # Index and retrieve
            retriever = HybridRetriever(
                semantic_weight=self.config.semantic_weight,
                keyword_weight=self.config.keyword_weight
            )
            
            # Create simple chunk objects for retriever
            class SimpleChunk:
                def __init__(self, content, chunk_id, metadata):
                    self.content = content
                    self.chunk_id = chunk_id
                    self.metadata = metadata
            
            simple_chunks = [
                SimpleChunk(c.content, c.id, c.meta_data)
                for c in chunks
            ]
            
            retriever.index_chunks(simple_chunks, embeddings)
            
            results = retriever.retrieve(
                query=q,
                query_embedding=query_embedding,
                top_k=top_k * 2,  # Get more for re-ranking
                min_score=self.config.min_similarity,
                method=self.config.retrieval_mode
            )
            
            # Deduplicate
            for result in results:
                if result.chunk_id not in seen_chunk_ids:
                    all_results.append(result)
                    seen_chunk_ids.add(result.chunk_id)
        
        # Re-rank if enabled
        if self.config.use_reranking and all_results:
            query_embedding = self.embedder.embed_text(query)
            result_embeddings = [embeddings[chunks.index(c)] for r in all_results for c in chunks if c.id == r.chunk_id]
            
            reranked = rerank_results(
                query=query,
                query_embedding=query_embedding,
                results=all_results[:top_k * 2],
                embeddings=result_embeddings[:top_k * 2],
                top_k=top_k,
                method="mmr" if self.config.use_mmr else "cross_encoder"
            )
            
            # Get actual chunks
            final_chunks = [
                next((c for c in chunks if c.id == r.chunk_id), None)
                for r in reranked
            ]
            final_chunks = [c for c in final_chunks if c is not None]
        else:
            # Just take top K
            final_chunks = [
                next((c for c in chunks if c.id == r.chunk_id), None)
                for r in all_results[:top_k]
            ]
            final_chunks = [c for c in final_chunks if c is not None]
        
        # Calculate metrics
        elapsed = time.time() - start_time
        unique_files = len(set(c.file_id for c in final_chunks))
        
        metrics = {
            "chunks_retrieved": len(final_chunks),
            "retrieval_time_ms": int(elapsed * 1000),
            "files_covered": unique_files,
            "query_length": len(query),
            "retrieval_method": self.config.retrieval_mode
        }
        
        return final_chunks, metrics
    
    def generate_rag_context(
        self,
        query: str,
        file_ids: Optional[List[int]] = None
    ) -> Dict:
        """
        Generate complete RAG context for chat
        
        Args:
            query: User query
            file_ids: Specific files to search
        
        Returns:
            Dictionary with context, chunks, citations, metrics
        """
        # Retrieve relevant chunks
        chunks, metrics = self.retrieve_context(query, file_ids)
        
        if not chunks:
            return {
                "has_context": False,
                "context": "",
                "chunks": [],
                "citations": [],
                "metrics": metrics
            }
        
        # Build context text
        chunk_texts = [c.content for c in chunks]
        
        # Optimize context if needed
        if self.config.use_compression:
            from backend.core.rag_optimizer import ContextCompressor
            compressor = ContextCompressor(compression_ratio=0.7)
            result = compressor.compress(chunk_texts, query)
            context_text = result.compressed_text
        else:
            context_text = "\n\n".join(chunk_texts)
        
        # Build citations if enabled
        citations = []
        if self.config.show_citations:
            for i, chunk in enumerate(chunks):
                citations.append({
                    "index": i + 1,
                    "file_id": chunk.file_id,
                    "chunk_id": chunk.id,
                    "filename": chunk.meta_data.get('filename', 'Unknown'),
                    "page": chunk.page_number,
                    "section": chunk.header,
                    "snippet": chunk.content[:150]
                })
        
        return {
            "has_context": True,
            "context": context_text,
            "chunks": chunks,
            "citations": citations,
            "metrics": metrics,
            "num_chunks": len(chunks),
            "files_used": list(set(c.file_id for c in chunks))
        }
    
    def format_rag_prompt(
        self,
        query: str,
        rag_context: Dict,
        include_citations: bool = True
    ) -> str:
        """
        Format RAG context into prompt for LLM
        
        Args:
            query: User query
            rag_context: RAG context from generate_rag_context
            include_citations: Include citation references
        
        Returns:
            Formatted prompt
        """
        if not rag_context.get("has_context"):
            return query
        
        prompt_parts = ["# CONTEXT FROM YOUR DOCUMENTS\n"]
        
        if include_citations and rag_context.get("citations"):
            prompt_parts.append("You have access to the following documents:\n")
            for cite in rag_context["citations"]:
                prompt_parts.append(f"[{cite['index']}] {cite['filename']}")
                if cite.get('page'):
                    prompt_parts[-1] += f" (page {cite['page']})"
                if cite.get('section'):
                    prompt_parts[-1] += f" - {cite['section']}"
                prompt_parts[-1] += "\n"
            prompt_parts.append("\n")
        
        prompt_parts.append("## RELEVANT CONTENT:\n")
        prompt_parts.append(rag_context["context"])
        prompt_parts.append("\n\n---\n\n")
        
        if include_citations:
            prompt_parts.append("**IMPORTANT:** When answering, cite your sources using [1], [2], etc.\n\n")
        
        prompt_parts.append(f"**USER QUESTION:** {query}\n\n")
        prompt_parts.append("Please answer based on the context provided above.")
        
        return "".join(prompt_parts)


def get_rag_processor(db: Session, user_id: int) -> RAGProcessor:
    """Get RAG processor instance"""
    return RAGProcessor(db, user_id)

