"""
RAG Re-ranking System
Improves retrieval quality by re-ranking initial results
Includes Cross-Encoder re-ranking and MMR for diversity
"""

from typing import List, Optional, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class RankedResult:
    """Re-ranked result"""
    chunk_id: int
    content: str
    original_score: float
    reranked_score: float
    rank: int
    metadata: dict


class MMRReranker:
    """
    Maximum Marginal Relevance (MMR) Re-ranker
    Balances relevance and diversity to avoid redundant results
    """
    
    def __init__(self, lambda_param: float = 0.5):
        """
        Initialize MMR re-ranker
        
        Args:
            lambda_param: Trade-off between relevance (1.0) and diversity (0.0)
                         0.5 = balanced
        """
        self.lambda_param = lambda_param
    
    def rerank(
        self,
        results: List,
        embeddings: List[np.ndarray],
        query_embedding: np.ndarray,
        top_k: Optional[int] = None
    ) -> List[RankedResult]:
        """
        Re-rank using MMR
        
        Args:
            results: Initial retrieval results
            embeddings: Embeddings for each result
            query_embedding: Query embedding
            top_k: Number of results to return (None = all)
        
        Returns:
            Re-ranked results
        """
        if not results:
            return []
        
        top_k = top_k or len(results)
        
        # Start with empty selected set
        selected = []
        selected_embeddings = []
        remaining_indices = list(range(len(results)))
        
        while len(selected) < top_k and remaining_indices:
            mmr_scores = []
            
            for idx in remaining_indices:
                # Relevance to query
                relevance = self._cosine_similarity(
                    embeddings[idx],
                    query_embedding
                )
                
                # Maximum similarity to already selected items (redundancy)
                if selected_embeddings:
                    max_similarity = max(
                        self._cosine_similarity(embeddings[idx], selected_emb)
                        for selected_emb in selected_embeddings
                    )
                else:
                    max_similarity = 0.0
                
                # MMR score
                mmr_score = (
                    self.lambda_param * relevance -
                    (1 - self.lambda_param) * max_similarity
                )
                
                mmr_scores.append((idx, mmr_score))
            
            # Select best MMR score
            best_idx, best_score = max(mmr_scores, key=lambda x: x[1])
            
            selected.append(RankedResult(
                chunk_id=getattr(results[best_idx], 'chunk_id', best_idx),
                content=results[best_idx].content,
                original_score=results[best_idx].score,
                reranked_score=best_score,
                rank=len(selected),
                metadata=getattr(results[best_idx], 'metadata', {})
            ))
            selected_embeddings.append(embeddings[best_idx])
            remaining_indices.remove(best_idx)
        
        return selected
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        if vec1 is None or vec2 is None:
            return 0.0
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


class CrossEncoderReranker:
    """
    Cross-Encoder Re-ranker (simulated)
    In production, would use a cross-encoder model like ms-marco-MiniLM
    For now, uses enhanced similarity scoring
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize cross-encoder re-ranker
        
        Args:
            model_name: Model to use (future implementation)
        """
        self.model_name = model_name
        self.model = None
        
        # For now, we'll use enhanced scoring
        # In production, load actual cross-encoder model:
        # from sentence_transformers import CrossEncoder
        # self.model = CrossEncoder(model_name)
    
    def rerank(
        self,
        query: str,
        results: List,
        top_k: Optional[int] = None
    ) -> List[RankedResult]:
        """
        Re-rank using cross-encoder
        
        Args:
            query: Query text
            results: Initial retrieval results
            top_k: Number of results to return
        
        Returns:
            Re-ranked results
        """
        if not results:
            return []
        
        top_k = top_k or len(results)
        
        # Score each query-document pair
        scores = []
        for result in results:
            # In production, would use:
            # score = self.model.predict([(query, result.content)])[0]
            
            # For now, use enhanced similarity
            score = self._enhanced_similarity(query, result.content)
            scores.append(score)
        
        # Sort by score
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        
        # Create ranked results
        ranked = []
        for rank, idx in enumerate(ranked_indices[:top_k]):
            ranked.append(RankedResult(
                chunk_id=getattr(results[idx], 'chunk_id', idx),
                content=results[idx].content,
                original_score=results[idx].score,
                reranked_score=scores[idx],
                rank=rank + 1,
                metadata=getattr(results[idx], 'metadata', {})
            ))
        
        return ranked
    
    def _enhanced_similarity(self, query: str, content: str) -> float:
        """
        Enhanced similarity scoring
        Combines multiple signals
        """
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Token overlap
        query_tokens = set(query_lower.split())
        content_tokens = set(content_lower.split())
        
        if not query_tokens:
            return 0.0
        
        overlap = len(query_tokens & content_tokens) / len(query_tokens)
        
        # Exact phrase bonus
        phrase_bonus = 0.2 if query_lower in content_lower else 0.0
        
        # Length penalty (very long or very short chunks)
        length_ratio = len(content) / (len(query) + 100)
        length_score = min(1.0, length_ratio) if length_ratio < 2.0 else 0.5
        
        # Combined score
        score = 0.6 * overlap + 0.3 * length_score + phrase_bonus
        
        return min(1.0, score)


class ContextualReranker:
    """
    Contextual re-ranker that considers chunk context
    Boosts scores for chunks from same document/section
    """
    
    def __init__(self, context_bonus: float = 0.15):
        """
        Initialize contextual re-ranker
        
        Args:
            context_bonus: Score bonus for related chunks
        """
        self.context_bonus = context_bonus
    
    def rerank(
        self,
        results: List,
        top_k: Optional[int] = None
    ) -> List[RankedResult]:
        """
        Re-rank considering context
        
        Args:
            results: Initial retrieval results
            top_k: Number of results
        
        Returns:
            Re-ranked results
        """
        if not results:
            return []
        
        top_k = top_k or len(results)
        
        # Group by file
        file_groups = {}
        for i, result in enumerate(results):
            file_id = result.metadata.get('file_id', 0)
            if file_id not in file_groups:
                file_groups[file_id] = []
            file_groups[file_id].append((i, result))
        
        # Boost scores for chunks from same high-scoring files
        adjusted_scores = []
        for i, result in enumerate(results):
            file_id = result.metadata.get('file_id', 0)
            
            # Get average score for this file
            file_results = file_groups[file_id]
            avg_file_score = sum(r.score for _, r in file_results) / len(file_results)
            
            # Boost if file has multiple high-scoring chunks
            bonus = self.context_bonus if len(file_results) > 1 and avg_file_score > 0.6 else 0.0
            
            adjusted_score = result.score + bonus
            adjusted_scores.append((i, adjusted_score))
        
        # Sort by adjusted score
        adjusted_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Create ranked results
        ranked = []
        for rank, (idx, score) in enumerate(adjusted_scores[:top_k]):
            result = results[idx]
            ranked.append(RankedResult(
                chunk_id=getattr(result, 'chunk_id', idx),
                content=result.content,
                original_score=result.score,
                reranked_score=score,
                rank=rank + 1,
                metadata=getattr(result, 'metadata', {})
            ))
        
        return ranked


class EnsembleReranker:
    """
    Ensemble re-ranker combining multiple strategies
    """
    
    def __init__(
        self,
        use_mmr: bool = True,
        use_cross_encoder: bool = False,
        use_contextual: bool = True,
        mmr_weight: float = 0.4,
        cross_encoder_weight: float = 0.3,
        contextual_weight: float = 0.3
    ):
        """
        Initialize ensemble re-ranker
        
        Args:
            use_mmr: Use MMR re-ranking
            use_cross_encoder: Use cross-encoder re-ranking
            use_contextual: Use contextual re-ranking
            mmr_weight: Weight for MMR scores
            cross_encoder_weight: Weight for cross-encoder scores
            contextual_weight: Weight for contextual scores
        """
        self.use_mmr = use_mmr
        self.use_cross_encoder = use_cross_encoder
        self.use_contextual = use_contextual
        
        self.mmr_weight = mmr_weight
        self.cross_encoder_weight = cross_encoder_weight
        self.contextual_weight = contextual_weight
        
        # Normalize weights
        total = mmr_weight + cross_encoder_weight + contextual_weight
        if total > 0:
            self.mmr_weight /= total
            self.cross_encoder_weight /= total
            self.contextual_weight /= total
        
        # Initialize re-rankers
        self.mmr_reranker = MMRReranker() if use_mmr else None
        self.cross_encoder_reranker = CrossEncoderReranker() if use_cross_encoder else None
        self.contextual_reranker = ContextualReranker() if use_contextual else None
    
    def rerank(
        self,
        query: str,
        query_embedding: np.ndarray,
        results: List,
        embeddings: List[np.ndarray],
        top_k: Optional[int] = None
    ) -> List[RankedResult]:
        """
        Re-rank using ensemble
        
        Args:
            query: Query text
            query_embedding: Query embedding
            results: Initial retrieval results
            embeddings: Result embeddings
            top_k: Number of results
        
        Returns:
            Re-ranked results
        """
        if not results:
            return []
        
        top_k = top_k or len(results)
        
        # Get scores from each re-ranker
        all_scores = {}
        
        if self.mmr_reranker:
            mmr_results = self.mmr_reranker.rerank(results, embeddings, query_embedding, top_k * 2)
            for result in mmr_results:
                if result.chunk_id not in all_scores:
                    all_scores[result.chunk_id] = {}
                all_scores[result.chunk_id]['mmr'] = result.reranked_score
        
        if self.cross_encoder_reranker:
            ce_results = self.cross_encoder_reranker.rerank(query, results, top_k * 2)
            for result in ce_results:
                if result.chunk_id not in all_scores:
                    all_scores[result.chunk_id] = {}
                all_scores[result.chunk_id]['cross_encoder'] = result.reranked_score
        
        if self.contextual_reranker:
            ctx_results = self.contextual_reranker.rerank(results, top_k * 2)
            for result in ctx_results:
                if result.chunk_id not in all_scores:
                    all_scores[result.chunk_id] = {}
                all_scores[result.chunk_id]['contextual'] = result.reranked_score
        
        # Combine scores
        final_scores = []
        result_map = {getattr(r, 'chunk_id', i): r for i, r in enumerate(results)}
        
        for chunk_id, scores in all_scores.items():
            combined_score = 0.0
            
            if 'mmr' in scores:
                combined_score += self.mmr_weight * scores['mmr']
            if 'cross_encoder' in scores:
                combined_score += self.cross_encoder_weight * scores['cross_encoder']
            if 'contextual' in scores:
                combined_score += self.contextual_weight * scores['contextual']
            
            final_scores.append((chunk_id, combined_score))
        
        # Sort by combined score
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Create final ranked results
        ranked = []
        for rank, (chunk_id, score) in enumerate(final_scores[:top_k]):
            if chunk_id in result_map:
                result = result_map[chunk_id]
                ranked.append(RankedResult(
                    chunk_id=chunk_id,
                    content=result.content,
                    original_score=result.score,
                    reranked_score=score,
                    rank=rank + 1,
                    metadata=getattr(result, 'metadata', {})
                ))
        
        return ranked


# Convenience function
def rerank_results(
    query: str,
    query_embedding: np.ndarray,
    results: List,
    embeddings: List[np.ndarray],
    top_k: int = 5,
    method: str = "mmr",
    **kwargs
) -> List[RankedResult]:
    """
    Re-rank retrieval results
    
    Args:
        query: Query text
        query_embedding: Query embedding
        results: Initial results
        embeddings: Result embeddings
        top_k: Number of results
        method: "mmr", "cross_encoder", "contextual", or "ensemble"
        **kwargs: Additional parameters
    
    Returns:
        Re-ranked results
    """
    if method == "mmr":
        reranker = MMRReranker(**kwargs)
        return reranker.rerank(results, embeddings, query_embedding, top_k)
    
    elif method == "cross_encoder":
        reranker = CrossEncoderReranker(**kwargs)
        return reranker.rerank(query, results, top_k)
    
    elif method == "contextual":
        reranker = ContextualReranker(**kwargs)
        return reranker.rerank(results, top_k)
    
    else:  # ensemble
        reranker = EnsembleReranker(**kwargs)
        return reranker.rerank(query, query_embedding, results, embeddings, top_k)

