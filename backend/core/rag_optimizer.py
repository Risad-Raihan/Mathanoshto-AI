"""
RAG Context Optimization
Query expansion, context compression, and other optimization techniques
"""

from typing import List, Dict, Optional, Tuple
import re
from dataclasses import dataclass


@dataclass
class OptimizedContext:
    """Optimized context for generation"""
    compressed_text: str
    original_length: int
    compressed_length: int
    compression_ratio: float
    num_chunks: int
    relevance_score: float


class QueryExpander:
    """
    Expands queries to improve retrieval
    Generates query variations to capture different phrasings
    """
    
    def __init__(self):
        pass
    
    def expand_query(self, query: str, num_variations: int = 3) -> List[str]:
        """
        Generate query variations
        
        Args:
            query: Original query
            num_variations: Number of variations to generate
        
        Returns:
            List of query variations (includes original)
        """
        variations = [query]
        
        # Technique 1: Rephrase with synonyms and paraphrasing
        # In production, would use an LLM or synonym library
        # For now, use rule-based variations
        
        # Add question variations
        if not query.endswith('?'):
            variations.append(f"What is {query}?")
            variations.append(f"Explain {query}")
        
        # Add imperative variation
        if query.lower().startswith(('what', 'how', 'why', 'when', 'where')):
            # Convert question to statement
            statement = re.sub(r'^(what|how|why|when|where)\s+(is|are|does|do)\s+', '', query.lower())
            variations.append(statement)
        
        # Add keyword-focused variation (remove question words)
        keywords = self._extract_keywords(query)
        if keywords:
            variations.append(' '.join(keywords))
        
        return variations[:num_variations + 1]  # +1 for original
    
    def expand_with_hypothetical(self, query: str) -> List[str]:
        """
        HyDE (Hypothetical Document Embeddings)
        Generate hypothetical answers that documents might contain
        
        Args:
            query: Query text
        
        Returns:
            List including query and hypothetical answer
        """
        variations = [query]
        
        # Generate a hypothetical answer template
        # In production, would use an LLM to generate this
        if '?' in query:
            # Transform question into potential answer
            hypothetical = f"The answer is that {query.lower().replace('?', '').strip()}."
            variations.append(hypothetical)
        
        return variations
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common stop words
        stop_words = {'what', 'how', 'why', 'when', 'where', 'is', 'are', 'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for'}
        
        words = re.findall(r'\w+', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        return keywords


class ContextCompressor:
    """
    Compresses retrieved context to reduce token usage
    Removes irrelevant sentences while keeping important information
    """
    
    def __init__(self, compression_ratio: float = 0.6):
        """
        Initialize context compressor
        
        Args:
            compression_ratio: Target ratio (0.5 = compress to 50% of original)
        """
        self.compression_ratio = compression_ratio
    
    def compress(
        self,
        chunks: List[str],
        query: str,
        max_length: Optional[int] = None
    ) -> OptimizedContext:
        """
        Compress context chunks
        
        Args:
            chunks: List of chunk texts
            query: Query for relevance scoring
            max_length: Maximum length in characters
        
        Returns:
            Optimized context
        """
        if not chunks:
            return OptimizedContext(
                compressed_text="",
                original_length=0,
                compressed_length=0,
                compression_ratio=0.0,
                num_chunks=0,
                relevance_score=0.0
            )
        
        # Combine chunks
        original_text = '\n\n'.join(chunks)
        original_length = len(original_text)
        
        # Extract sentences from all chunks
        all_sentences = []
        for chunk in chunks:
            sentences = self._split_sentences(chunk)
            all_sentences.extend(sentences)
        
        if not all_sentences:
            return OptimizedContext(
                compressed_text=original_text,
                original_length=original_length,
                compressed_length=original_length,
                compression_ratio=1.0,
                num_chunks=len(chunks),
                relevance_score=1.0
            )
        
        # Score each sentence for relevance to query
        scored_sentences = []
        for sent in all_sentences:
            score = self._score_sentence(sent, query)
            scored_sentences.append((sent, score))
        
        # Sort by score (descending)
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Select top sentences up to target length
        target_length = int(original_length * self.compression_ratio)
        if max_length:
            target_length = min(target_length, max_length)
        
        selected_sentences = []
        current_length = 0
        avg_relevance = 0.0
        
        for sent, score in scored_sentences:
            sent_length = len(sent)
            if current_length + sent_length <= target_length or not selected_sentences:
                selected_sentences.append(sent)
                current_length += sent_length
                avg_relevance += score
            else:
                break
        
        # Reconstruct compressed text (preserve some order)
        compressed_text = ' '.join(selected_sentences)
        
        avg_relevance = avg_relevance / len(selected_sentences) if selected_sentences else 0.0
        
        return OptimizedContext(
            compressed_text=compressed_text,
            original_length=original_length,
            compressed_length=len(compressed_text),
            compression_ratio=len(compressed_text) / original_length if original_length > 0 else 0.0,
            num_chunks=len(chunks),
            relevance_score=avg_relevance
        )
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _score_sentence(self, sentence: str, query: str) -> float:
        """
        Score sentence relevance to query
        
        Args:
            sentence: Sentence to score
            query: Query text
        
        Returns:
            Relevance score
        """
        sent_lower = sentence.lower()
        query_lower = query.lower()
        
        # Token overlap
        sent_tokens = set(re.findall(r'\w+', sent_lower))
        query_tokens = set(re.findall(r'\w+', query_lower))
        
        if not query_tokens:
            return 0.5
        
        overlap = len(sent_tokens & query_tokens) / len(query_tokens)
        
        # Boost for exact query phrase
        if query_lower in sent_lower:
            overlap += 0.3
        
        # Boost for longer sentences (more informative)
        length_bonus = min(0.2, len(sentence) / 500)
        
        return min(1.0, overlap + length_bonus)


class ContextWindowOptimizer:
    """
    Optimizes context to fit within model context windows
    Smart truncation and prioritization
    """
    
    def __init__(self, max_tokens: int = 4000):
        """
        Initialize optimizer
        
        Args:
            max_tokens: Maximum tokens for context
        """
        self.max_tokens = max_tokens
    
    def optimize_for_window(
        self,
        chunks: List[str],
        query: str,
        reserved_tokens: int = 1000  # For query + response
    ) -> List[str]:
        """
        Optimize chunks to fit context window
        
        Args:
            chunks: List of chunk texts
            query: Query text
            reserved_tokens: Tokens to reserve for query/response
        
        Returns:
            Optimized list of chunks
        """
        available_tokens = self.max_tokens - reserved_tokens
        
        # Estimate tokens (rough: 4 chars = 1 token)
        optimized_chunks = []
        current_tokens = 0
        
        for chunk in chunks:
            chunk_tokens = len(chunk) // 4
            
            if current_tokens + chunk_tokens <= available_tokens:
                optimized_chunks.append(chunk)
                current_tokens += chunk_tokens
            else:
                # Try to fit partial chunk
                remaining_tokens = available_tokens - current_tokens
                remaining_chars = remaining_tokens * 4
                
                if remaining_chars > 100:  # Only if meaningful amount left
                    truncated = chunk[:remaining_chars] + "..."
                    optimized_chunks.append(truncated)
                
                break
        
        return optimized_chunks


class ChunkMerger:
    """
    Merges related chunks to provide better context
    Especially useful when chunks are from same document/section
    """
    
    def __init__(self):
        pass
    
    def merge_related_chunks(
        self,
        chunks: List,
        max_gap: int = 2
    ) -> List[str]:
        """
        Merge chunks that are adjacent or close in original document
        
        Args:
            chunks: List of chunk objects with metadata
            max_gap: Maximum chunk index gap to merge
        
        Returns:
            List of merged chunk texts
        """
        if not chunks:
            return []
        
        # Group by file
        file_groups: Dict[int, List] = {}
        for chunk in chunks:
            file_id = chunk.metadata.get('file_id', 0) if hasattr(chunk, 'metadata') else 0
            if file_id not in file_groups:
                file_groups[file_id] = []
            file_groups[file_id].append(chunk)
        
        merged = []
        
        for file_id, file_chunks in file_groups.items():
            # Sort by chunk index
            file_chunks.sort(key=lambda c: c.metadata.get('chunk_index', 0) if hasattr(c, 'metadata') else 0)
            
            current_group = [file_chunks[0]]
            
            for i in range(1, len(file_chunks)):
                prev_chunk = file_chunks[i - 1]
                curr_chunk = file_chunks[i]
                
                prev_idx = prev_chunk.metadata.get('chunk_index', 0) if hasattr(prev_chunk, 'metadata') else 0
                curr_idx = curr_chunk.metadata.get('chunk_index', 0) if hasattr(curr_chunk, 'metadata') else 0
                
                # If chunks are close, add to current group
                if curr_idx - prev_idx <= max_gap:
                    current_group.append(curr_chunk)
                else:
                    # Save current group and start new one
                    merged_text = self._merge_group(current_group)
                    merged.append(merged_text)
                    current_group = [curr_chunk]
            
            # Add last group
            if current_group:
                merged_text = self._merge_group(current_group)
                merged.append(merged_text)
        
        return merged
    
    def _merge_group(self, chunks: List) -> str:
        """Merge a group of chunks"""
        texts = [chunk.content if hasattr(chunk, 'content') else str(chunk) for chunk in chunks]
        return '\n\n'.join(texts)


# Convenience functions
def optimize_retrieval_context(
    chunks: List[str],
    query: str,
    max_tokens: int = 4000,
    use_compression: bool = True,
    compression_ratio: float = 0.6
) -> str:
    """
    Optimize retrieved context for generation
    
    Args:
        chunks: Retrieved chunks
        query: Query text
        max_tokens: Maximum tokens
        use_compression: Use compression
        compression_ratio: Compression target
    
    Returns:
        Optimized context string
    """
    # First, fit to context window
    window_optimizer = ContextWindowOptimizer(max_tokens=max_tokens)
    optimized_chunks = window_optimizer.optimize_for_window(chunks, query)
    
    # Optionally compress further
    if use_compression:
        compressor = ContextCompressor(compression_ratio=compression_ratio)
        result = compressor.compress(optimized_chunks, query)
        return result.compressed_text
    else:
        return '\n\n'.join(optimized_chunks)


def expand_and_search(
    query: str,
    search_function,
    num_variations: int = 2
) -> List:
    """
    Expand query and search with variations
    
    Args:
        query: Original query
        search_function: Function to call for searching
        num_variations: Number of query variations
    
    Returns:
        Combined search results
    """
    expander = QueryExpander()
    variations = expander.expand_query(query, num_variations)
    
    all_results = []
    seen_ids = set()
    
    for variation in variations:
        results = search_function(variation)
        
        # Deduplicate
        for result in results:
            result_id = getattr(result, 'chunk_id', id(result))
            if result_id not in seen_ids:
                all_results.append(result)
                seen_ids.add(result_id)
    
    return all_results

