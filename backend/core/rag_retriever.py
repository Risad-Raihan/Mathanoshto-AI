"""
RAG Hybrid Retriever
Combines semantic search (embeddings) and keyword search (BM25)
Uses Reciprocal Rank Fusion (RRF) to merge results
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from collections import Counter
import re
import math


@dataclass
class RetrievalResult:
    """Result from retrieval"""
    chunk_id: int
    content: str
    score: float
    method: str  # semantic, keyword, hybrid
    metadata: Dict
    
    def __lt__(self, other):
        return self.score > other.score  # Higher score = better


class BM25:
    """
    BM25 keyword search algorithm
    Industry-standard for keyword-based retrieval
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25
        
        Args:
            k1: Term frequency saturation parameter (1.2-2.0)
            b: Length normalization parameter (0-1)
        """
        self.k1 = k1
        self.b = b
        
        self.corpus = []
        self.corpus_size = 0
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
    
    def fit(self, corpus: List[str]):
        """
        Fit BM25 on a corpus
        
        Args:
            corpus: List of documents (strings)
        """
        self.corpus = corpus
        self.corpus_size = len(corpus)
        
        # Tokenize documents
        tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        
        # Calculate document lengths
        self.doc_len = [len(doc) for doc in tokenized_corpus]
        self.avgdl = sum(self.doc_len) / self.corpus_size if self.corpus_size > 0 else 0
        
        # Calculate document frequencies
        df = Counter()
        for doc in tokenized_corpus:
            df.update(set(doc))
        
        # Calculate IDF for each term
        self.idf = {}
        for term, freq in df.items():
            self.idf[term] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)
        
        self.doc_freqs = tokenized_corpus
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization (lowercase, alphanumeric)"""
        # Convert to lowercase and split on non-alphanumeric
        tokens = re.findall(r'\w+', text.lower())
        return tokens
    
    def get_scores(self, query: str) -> np.ndarray:
        """
        Get BM25 scores for query against all documents
        
        Args:
            query: Search query
        
        Returns:
            Array of scores for each document
        """
        query_tokens = self._tokenize(query)
        scores = np.zeros(self.corpus_size)
        
        for token in query_tokens:
            if token not in self.idf:
                continue
            
            idf = self.idf[token]
            
            for doc_idx, doc_tokens in enumerate(self.doc_freqs):
                # Term frequency in document
                tf = doc_tokens.count(token)
                
                if tf == 0:
                    continue
                
                # Document length normalization
                doc_len = self.doc_len[doc_idx]
                norm = 1 - self.b + self.b * (doc_len / self.avgdl)
                
                # BM25 score
                score = idf * (tf * (self.k1 + 1)) / (tf + self.k1 * norm)
                scores[doc_idx] += score
        
        return scores
    
    def get_top_n(self, query: str, n: int = 5) -> List[Tuple[int, float]]:
        """
        Get top N documents for query
        
        Args:
            query: Search query
            n: Number of results
        
        Returns:
            List of (doc_index, score) tuples
        """
        scores = self.get_scores(query)
        top_indices = np.argsort(scores)[::-1][:n]
        
        return [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]


class HybridRetriever:
    """
    Hybrid retrieval combining semantic and keyword search
    """
    
    def __init__(
        self,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        use_rrf: bool = True,
        rrf_k: int = 60
    ):
        """
        Initialize hybrid retriever
        
        Args:
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            use_rrf: Use Reciprocal Rank Fusion instead of weighted sum
            rrf_k: RRF parameter (typically 60)
        """
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.use_rrf = use_rrf
        self.rrf_k = rrf_k
        
        self.bm25 = None
        self.chunks = []
        self.embeddings = []
    
    def index_chunks(self, chunks: List, embeddings: List[np.ndarray]):
        """
        Index chunks for retrieval
        
        Args:
            chunks: List of chunk objects
            embeddings: List of embeddings for chunks
        """
        self.chunks = chunks
        self.embeddings = embeddings
        
        # Build BM25 index
        corpus = [chunk.content for chunk in chunks]
        self.bm25 = BM25()
        self.bm25.fit(corpus)
        
        print(f"✅ Indexed {len(chunks)} chunks for hybrid retrieval")
    
    def retrieve(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int = 5,
        min_score: float = 0.0,
        method: str = "hybrid"
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks
        
        Args:
            query: Text query
            query_embedding: Query embedding
            top_k: Number of results
            min_score: Minimum relevance score
            method: "semantic", "keyword", or "hybrid"
        
        Returns:
            List of retrieval results
        """
        if not self.chunks or not self.embeddings:
            return []
        
        if method == "semantic":
            return self._semantic_search(query_embedding, top_k, min_score)
        elif method == "keyword":
            return self._keyword_search(query, top_k, min_score)
        else:  # hybrid
            return self._hybrid_search(query, query_embedding, top_k, min_score)
    
    def _semantic_search(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        min_score: float
    ) -> List[RetrievalResult]:
        """Semantic search using embeddings"""
        scores = []
        
        for i, chunk_emb in enumerate(self.embeddings):
            if chunk_emb is None:
                continue
            
            # Cosine similarity
            similarity = self._cosine_similarity(query_embedding, chunk_emb)
            
            if similarity >= min_score:
                scores.append((i, similarity))
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Create results
        results = []
        for idx, score in scores[:top_k]:
            chunk = self.chunks[idx]
            results.append(RetrievalResult(
                chunk_id=getattr(chunk, 'chunk_id', idx),
                content=chunk.content,
                score=score,
                method="semantic",
                metadata=chunk.metadata if hasattr(chunk, 'metadata') else {}
            ))
        
        return results
    
    def _keyword_search(
        self,
        query: str,
        top_k: int,
        min_score: float
    ) -> List[RetrievalResult]:
        """Keyword search using BM25"""
        if self.bm25 is None:
            return []
        
        bm25_results = self.bm25.get_top_n(query, n=top_k * 2)  # Get more for filtering
        
        # Create results
        results = []
        for idx, score in bm25_results:
            if score >= min_score:
                chunk = self.chunks[idx]
                results.append(RetrievalResult(
                    chunk_id=getattr(chunk, 'chunk_id', idx),
                    content=chunk.content,
                    score=score,
                    method="keyword",
                    metadata=chunk.metadata if hasattr(chunk, 'metadata') else {}
                ))
        
        return results[:top_k]
    
    def _hybrid_search(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int,
        min_score: float
    ) -> List[RetrievalResult]:
        """
        Hybrid search combining semantic and keyword
        Uses RRF or weighted fusion
        """
        # Get semantic results
        semantic_results = self._semantic_search(query_embedding, top_k * 2, 0.0)
        
        # Get keyword results
        keyword_results = self._keyword_search(query, top_k * 2, 0.0)
        
        if self.use_rrf:
            # Reciprocal Rank Fusion
            merged = self._reciprocal_rank_fusion(
                semantic_results,
                keyword_results,
                k=self.rrf_k
            )
        else:
            # Weighted fusion
            merged = self._weighted_fusion(
                semantic_results,
                keyword_results,
                semantic_weight=self.semantic_weight,
                keyword_weight=self.keyword_weight
            )
        
        # Filter by minimum score and return top K
        filtered = [r for r in merged if r.score >= min_score]
        return filtered[:top_k]
    
    def _reciprocal_rank_fusion(
        self,
        semantic_results: List[RetrievalResult],
        keyword_results: List[RetrievalResult],
        k: int = 60
    ) -> List[RetrievalResult]:
        """
        Reciprocal Rank Fusion (RRF)
        State-of-the-art method for combining rankings
        
        RRF score = sum(1 / (k + rank))
        """
        # Build chunk_id -> (rank, score) mappings
        semantic_ranks = {r.chunk_id: (rank + 1, r.score) for rank, r in enumerate(semantic_results)}
        keyword_ranks = {r.chunk_id: (rank + 1, r.score) for rank, r in enumerate(keyword_results)}
        
        # Get all unique chunk IDs
        all_chunk_ids = set(semantic_ranks.keys()) | set(keyword_ranks.keys())
        
        # Calculate RRF scores
        rrf_scores = {}
        for chunk_id in all_chunk_ids:
            score = 0.0
            
            if chunk_id in semantic_ranks:
                rank, _ = semantic_ranks[chunk_id]
                score += 1.0 / (k + rank)
            
            if chunk_id in keyword_ranks:
                rank, _ = keyword_ranks[chunk_id]
                score += 1.0 / (k + rank)
            
            rrf_scores[chunk_id] = score
        
        # Create merged results
        merged = []
        chunk_map = {r.chunk_id: r for r in semantic_results + keyword_results}
        
        for chunk_id, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
            if chunk_id in chunk_map:
                result = chunk_map[chunk_id]
                result.score = score
                result.method = "hybrid"
                merged.append(result)
        
        return merged
    
    def _weighted_fusion(
        self,
        semantic_results: List[RetrievalResult],
        keyword_results: List[RetrievalResult],
        semantic_weight: float,
        keyword_weight: float
    ) -> List[RetrievalResult]:
        """
        Weighted fusion of scores
        Simple but effective
        """
        # Normalize scores to 0-1 range
        semantic_scores = {r.chunk_id: r.score for r in semantic_results}
        keyword_scores = {r.chunk_id: r.score for r in keyword_results}
        
        # Normalize
        if semantic_scores:
            max_semantic = max(semantic_scores.values())
            if max_semantic > 0:
                semantic_scores = {k: v / max_semantic for k, v in semantic_scores.items()}
        
        if keyword_scores:
            max_keyword = max(keyword_scores.values())
            if max_keyword > 0:
                keyword_scores = {k: v / max_keyword for k, v in keyword_scores.items()}
        
        # Combine
        all_chunk_ids = set(semantic_scores.keys()) | set(keyword_scores.keys())
        
        combined_scores = {}
        for chunk_id in all_chunk_ids:
            sem_score = semantic_scores.get(chunk_id, 0.0)
            key_score = keyword_scores.get(chunk_id, 0.0)
            
            combined_scores[chunk_id] = (
                semantic_weight * sem_score +
                keyword_weight * key_score
            )
        
        # Create merged results
        merged = []
        chunk_map = {r.chunk_id: r for r in semantic_results + keyword_results}
        
        for chunk_id, score in sorted(combined_scores.items(), key=lambda x: x[1], reverse=True):
            if chunk_id in chunk_map:
                result = chunk_map[chunk_id]
                result.score = score
                result.method = "hybrid"
                merged.append(result)
        
        return merged
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to [0, 1]
        return float(max(0.0, min(1.0, (similarity + 1) / 2)))


# Convenience function
def search_chunks(
    query: str,
    query_embedding: np.ndarray,
    chunks: List,
    chunk_embeddings: List[np.ndarray],
    top_k: int = 5,
    method: str = "hybrid",
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> List[RetrievalResult]:
    """
    Search chunks using hybrid retrieval
    
    Args:
        query: Text query
        query_embedding: Query embedding
        chunks: List of chunks
        chunk_embeddings: List of chunk embeddings
        top_k: Number of results
        method: "semantic", "keyword", or "hybrid"
        semantic_weight: Weight for semantic search
        keyword_weight: Weight for keyword search
    
    Returns:
        List of retrieval results
    """
    retriever = HybridRetriever(
        semantic_weight=semantic_weight,
        keyword_weight=keyword_weight
    )
    
    retriever.index_chunks(chunks, chunk_embeddings)
    
    return retriever.retrieve(
        query=query,
        query_embedding=query_embedding,
        top_k=top_k,
        method=method
    )

