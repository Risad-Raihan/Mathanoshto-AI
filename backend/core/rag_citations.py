"""
RAG Citation System
Tracks source documents and formats citations
Ensures transparency and traceability of RAG responses
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class CitationFormat(Enum):
    """Citation format styles"""
    INLINE = "inline"  # [Doc1, p.5]
    FOOTNOTE = "footnote"  # [1]
    NUMBERED = "numbered"  # (1)
    APA = "apa"  # Author (Year)
    SUPERSCRIPT = "superscript"  # ¹
    MARKDOWN = "markdown"  # [^1]


@dataclass
class Citation:
    """Represents a single citation"""
    citation_id: str
    chunk_id: int
    file_id: int
    filename: str
    page_number: Optional[int]
    section: Optional[str]
    relevance_score: float
    content_snippet: str  # Brief excerpt
    
    def to_dict(self) -> Dict:
        return {
            "citation_id": self.citation_id,
            "chunk_id": self.chunk_id,
            "file_id": self.file_id,
            "filename": self.filename,
            "page_number": self.page_number,
            "section": self.section,
            "relevance_score": self.relevance_score,
            "content_snippet": self.content_snippet
        }


class CitationManager:
    """
    Manages citations for RAG responses
    Tracks sources and formats references
    """
    
    def __init__(self, format_style: CitationFormat = CitationFormat.INLINE):
        """
        Initialize citation manager
        
        Args:
            format_style: Citation format to use
        """
        self.format_style = format_style
        self.citations: List[Citation] = []
        self.citation_map: Dict[int, Citation] = {}  # chunk_id -> citation
    
    def add_citation(
        self,
        chunk_id: int,
        file_id: int,
        filename: str,
        relevance_score: float,
        content_snippet: str,
        page_number: Optional[int] = None,
        section: Optional[str] = None
    ) -> Citation:
        """
        Add a citation
        
        Args:
            chunk_id: Chunk identifier
            file_id: File identifier
            filename: File name
            relevance_score: Relevance score
            content_snippet: Brief content excerpt
            page_number: Page number if available
            section: Section/chapter if available
        
        Returns:
            Citation object
        """
        citation_id = f"cite_{len(self.citations) + 1}"
        
        citation = Citation(
            citation_id=citation_id,
            chunk_id=chunk_id,
            file_id=file_id,
            filename=filename,
            page_number=page_number,
            section=section,
            relevance_score=relevance_score,
            content_snippet=content_snippet
        )
        
        self.citations.append(citation)
        self.citation_map[chunk_id] = citation
        
        return citation
    
    def format_inline_citation(self, citation: Citation) -> str:
        """
        Format citation for inline use
        
        Args:
            citation: Citation to format
        
        Returns:
            Formatted citation string
        """
        # Shorten filename (remove extension, limit length)
        short_name = citation.filename.rsplit('.', 1)[0]
        if len(short_name) > 20:
            short_name = short_name[:17] + "..."
        
        # Build citation
        parts = [short_name]
        
        if citation.page_number:
            parts.append(f"p.{citation.page_number}")
        elif citation.section:
            parts.append(citation.section[:30])
        
        if self.format_style == CitationFormat.INLINE:
            return f"[{', '.join(parts)}]"
        elif self.format_style == CitationFormat.NUMBERED:
            idx = self.citations.index(citation) + 1
            return f"({idx})"
        elif self.format_style == CitationFormat.FOOTNOTE:
            idx = self.citations.index(citation) + 1
            return f"[{idx}]"
        elif self.format_style == CitationFormat.SUPERSCRIPT:
            idx = self.citations.index(citation) + 1
            return self._to_superscript(str(idx))
        elif self.format_style == CitationFormat.MARKDOWN:
            idx = self.citations.index(citation) + 1
            return f"[^{idx}]"
        else:
            return f"[{', '.join(parts)}]"
    
    def inject_citations_into_text(
        self,
        text: str,
        chunk_citations: List[Tuple[int, float]]  # (chunk_id, score)
    ) -> str:
        """
        Inject citations into generated text
        
        Args:
            text: Generated text
            chunk_citations: List of (chunk_id, score) tuples
        
        Returns:
            Text with injected citations
        """
        # For now, add citations at end of sentences mentioning key facts
        # In production, would use more sophisticated NLP to place citations
        
        # Simple approach: add citation for each unique source at end
        unique_files = {}
        for chunk_id, score in chunk_citations:
            if chunk_id in self.citation_map:
                citation = self.citation_map[chunk_id]
                if citation.file_id not in unique_files:
                    unique_files[citation.file_id] = citation
        
        if unique_files:
            citations_text = " ".join(
                self.format_inline_citation(cite)
                for cite in unique_files.values()
            )
            
            # Add citations at end of first paragraph or text
            paragraphs = text.split('\n\n')
            if paragraphs:
                paragraphs[0] = paragraphs[0].rstrip() + " " + citations_text
                text = '\n\n'.join(paragraphs)
        
        return text
    
    def generate_references_section(self) -> str:
        """
        Generate a references/bibliography section
        
        Returns:
            Formatted references section
        """
        if not self.citations:
            return ""
        
        lines = ["\n\n## 📚 **Sources**\n"]
        
        # Group by file
        file_citations: Dict[int, List[Citation]] = {}
        for citation in self.citations:
            if citation.file_id not in file_citations:
                file_citations[citation.file_id] = []
            file_citations[citation.file_id].append(citation)
        
        # Format each file's citations
        for file_id, cites in file_citations.items():
            # Use first citation for file info
            first_cite = cites[0]
            
            if self.format_style == CitationFormat.INLINE:
                lines.append(f"\n**{first_cite.filename}**")
            else:
                idx = self.citations.index(first_cite) + 1
                lines.append(f"\n**[{idx}] {first_cite.filename}**")
            
            # Add page/section info if available
            pages = [c.page_number for c in cites if c.page_number]
            if pages:
                pages_str = ", ".join(f"p.{p}" for p in sorted(set(pages)))
                lines.append(f"  - Referenced pages: {pages_str}")
            
            sections = [c.section for c in cites if c.section]
            if sections:
                sections_str = ", ".join(set(sections))
                lines.append(f"  - Sections: {sections_str}")
        
        return "\n".join(lines)
    
    def generate_citation_details(self, detailed: bool = False) -> List[Dict]:
        """
        Generate detailed citation information
        
        Args:
            detailed: Include content snippets
        
        Returns:
            List of citation dictionaries
        """
        details = []
        
        for i, citation in enumerate(self.citations):
            detail = {
                "index": i + 1,
                "filename": citation.filename,
                "relevance": round(citation.relevance_score, 3)
            }
            
            if citation.page_number:
                detail["page"] = citation.page_number
            
            if citation.section:
                detail["section"] = citation.section
            
            if detailed:
                # Truncate snippet
                snippet = citation.content_snippet
                if len(snippet) > 200:
                    snippet = snippet[:197] + "..."
                detail["snippet"] = snippet
            
            details.append(detail)
        
        return details
    
    def _to_superscript(self, text: str) -> str:
        """Convert numbers to superscript"""
        superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
        }
        return ''.join(superscript_map.get(c, c) for c in text)
    
    def clear(self):
        """Clear all citations"""
        self.citations.clear()
        self.citation_map.clear()


class CitationVerifier:
    """
    Verifies that generated text is supported by cited sources
    Helps detect hallucinations
    """
    
    def __init__(self):
        pass
    
    def verify_claim(
        self,
        claim: str,
        cited_chunks: List[str],
        threshold: float = 0.5
    ) -> Tuple[bool, float]:
        """
        Verify if a claim is supported by cited chunks
        
        Args:
            claim: Claim to verify
            cited_chunks: Content from cited chunks
            threshold: Minimum overlap threshold
        
        Returns:
            (is_supported, confidence_score)
        """
        claim_lower = claim.lower()
        claim_tokens = set(self._tokenize(claim_lower))
        
        if not claim_tokens:
            return False, 0.0
        
        max_overlap = 0.0
        
        for chunk in cited_chunks:
            chunk_lower = chunk.lower()
            chunk_tokens = set(self._tokenize(chunk_lower))
            
            if not chunk_tokens:
                continue
            
            # Calculate token overlap
            overlap = len(claim_tokens & chunk_tokens) / len(claim_tokens)
            max_overlap = max(max_overlap, overlap)
            
            # Check for direct quote
            if claim_lower in chunk_lower:
                return True, 1.0
        
        is_supported = max_overlap >= threshold
        return is_supported, max_overlap
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        return re.findall(r'\w+', text)
    
    def extract_claims(self, text: str) -> List[str]:
        """
        Extract factual claims from text
        
        Args:
            text: Generated text
        
        Returns:
            List of claims (sentences)
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Filter out short or question sentences
        claims = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 20 and not sent.endswith('?'):
                claims.append(sent)
        
        return claims


# Convenience functions
def create_citation_from_chunk(chunk, rank: int = 1) -> Citation:
    """
    Create citation from a chunk object
    
    Args:
        chunk: Chunk object with metadata
        rank: Citation rank/number
    
    Returns:
        Citation object
    """
    metadata = chunk.metadata if hasattr(chunk, 'metadata') else {}
    
    # Extract snippet (first 150 chars)
    snippet = chunk.content[:150]
    if len(chunk.content) > 150:
        snippet += "..."
    
    return Citation(
        citation_id=f"cite_{rank}",
        chunk_id=getattr(chunk, 'chunk_id', 0),
        file_id=metadata.get('file_id', 0),
        filename=metadata.get('filename', 'Unknown'),
        page_number=metadata.get('page_number'),
        section=metadata.get('header') or metadata.get('section'),
        relevance_score=getattr(chunk, 'score', 0.0),
        content_snippet=snippet
    )


def format_response_with_citations(
    response_text: str,
    chunks: List,
    format_style: CitationFormat = CitationFormat.INLINE,
    include_references: bool = True
) -> Tuple[str, List[Citation]]:
    """
    Format response with citations
    
    Args:
        response_text: Generated response
        chunks: Chunks used in generation
        format_style: Citation format style
        include_references: Include references section
    
    Returns:
        (formatted_text, citations_list)
    """
    manager = CitationManager(format_style=format_style)
    
    # Add citations for each chunk
    chunk_citations = []
    for i, chunk in enumerate(chunks):
        citation = create_citation_from_chunk(chunk, rank=i + 1)
        manager.citations.append(citation)
        manager.citation_map[citation.chunk_id] = citation
        chunk_citations.append((citation.chunk_id, citation.relevance_score))
    
    # Inject citations into text
    formatted_text = manager.inject_citations_into_text(response_text, chunk_citations)
    
    # Add references section if requested
    if include_references:
        formatted_text += manager.generate_references_section()
    
    return formatted_text, manager.citations

