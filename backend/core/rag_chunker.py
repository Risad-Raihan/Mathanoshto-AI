"""
Advanced Document Chunking System
Multiple strategies for intelligent document splitting
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from enum import Enum


class ChunkStrategy(Enum):
    """Chunking strategies"""
    SEMANTIC = "semantic"  # Preserve meaning boundaries
    RECURSIVE = "recursive"  # Hierarchical splitting
    TOKEN_AWARE = "token_aware"  # Respects token limits
    OVERLAP = "overlap"  # With context overlap
    FIXED = "fixed"  # Fixed size chunks
    SENTENCE = "sentence"  # Sentence-based
    PARAGRAPH = "paragraph"  # Paragraph-based
    CODE_AWARE = "code_aware"  # Respects code structure


@dataclass
class Chunk:
    """Represents a document chunk"""
    content: str
    chunk_id: int
    start_char: int
    end_char: int
    metadata: Dict
    
    def __len__(self):
        return len(self.content)
    
    def token_count(self) -> int:
        """Approximate token count (rough estimate: 4 chars = 1 token)"""
        return len(self.content) // 4


class DocumentChunker:
    """
    Advanced document chunking with multiple strategies
    """
    
    def __init__(
        self,
        chunk_size: int = 1500,  # Optimized from 1000 for >=85% accuracy
        chunk_overlap: int = 300,  # Optimized from 200 for better continuity
        strategy: ChunkStrategy = ChunkStrategy.RECURSIVE
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
    
    def chunk_document(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        file_type: Optional[str] = None
    ) -> List[Chunk]:
        """
        Chunk a document using the selected strategy
        
        Args:
            text: Document text
            metadata: Document metadata
            file_type: File type (pdf, docx, code, etc.)
        
        Returns:
            List of chunks
        """
        if not text or not text.strip():
            return []
        
        metadata = metadata or {}
        
        # Choose chunking method based on strategy and file type
        if file_type in ['py', 'js', 'java', 'cpp', 'go', 'rs'] or self.strategy == ChunkStrategy.CODE_AWARE:
            chunks = self._chunk_code(text, file_type)
        elif self.strategy == ChunkStrategy.SEMANTIC:
            chunks = self._chunk_semantic(text)
        elif self.strategy == ChunkStrategy.RECURSIVE:
            chunks = self._chunk_recursive(text)
        elif self.strategy == ChunkStrategy.TOKEN_AWARE:
            chunks = self._chunk_token_aware(text)
        elif self.strategy == ChunkStrategy.OVERLAP:
            chunks = self._chunk_with_overlap(text)
        elif self.strategy == ChunkStrategy.SENTENCE:
            chunks = self._chunk_by_sentences(text)
        elif self.strategy == ChunkStrategy.PARAGRAPH:
            chunks = self._chunk_by_paragraphs(text)
        else:  # FIXED
            chunks = self._chunk_fixed(text)
        
        # Add metadata to chunks
        for i, chunk in enumerate(chunks):
            chunk.chunk_id = i
            chunk.metadata.update(metadata)
            chunk.metadata['strategy'] = self.strategy.value
            chunk.metadata['chunk_index'] = i
            chunk.metadata['total_chunks'] = len(chunks)
        
        return chunks
    
    def _chunk_recursive(self, text: str) -> List[Chunk]:
        """
        Recursive chunking - splits by paragraphs, then sentences, then fixed
        Preserves semantic boundaries as much as possible
        """
        chunks = []
        
        # Try to split by paragraphs first
        paragraphs = re.split(r'\n\n+', text)
        
        current_chunk = ""
        start_char = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If paragraph fits in chunk, add it
            if len(current_chunk) + len(para) <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk,
                        chunk_id=0,
                        start_char=start_char,
                        end_char=start_char + len(current_chunk),
                        metadata={}
                    ))
                    start_char += len(current_chunk) + 2  # +2 for \n\n
                
                # If paragraph is too large, split by sentences
                if len(para) > self.chunk_size:
                    sentence_chunks = self._split_by_sentences(para, start_char)
                    chunks.extend(sentence_chunks)
                    start_char += len(para) + 2
                    current_chunk = ""
                else:
                    current_chunk = para
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(Chunk(
                content=current_chunk,
                chunk_id=0,
                start_char=start_char,
                end_char=start_char + len(current_chunk),
                metadata={}
            ))
        
        return chunks
    
    def _split_by_sentences(self, text: str, start_offset: int = 0) -> List[Chunk]:
        """Split text by sentences"""
        # Simple sentence splitter (can be improved with spaCy/nltk)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        start_char = start_offset
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk,
                        chunk_id=0,
                        start_char=start_char,
                        end_char=start_char + len(current_chunk),
                        metadata={}
                    ))
                    start_char += len(current_chunk) + 1
                
                # If sentence itself is too long, force split
                if len(sentence) > self.chunk_size:
                    for i in range(0, len(sentence), self.chunk_size):
                        chunk_text = sentence[i:i + self.chunk_size]
                        chunks.append(Chunk(
                            content=chunk_text,
                            chunk_id=0,
                            start_char=start_char,
                            end_char=start_char + len(chunk_text),
                            metadata={}
                        ))
                        start_char += len(chunk_text)
                    current_chunk = ""
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(Chunk(
                content=current_chunk,
                chunk_id=0,
                start_char=start_char,
                end_char=start_char + len(current_chunk),
                metadata={}
            ))
        
        return chunks
    
    def _chunk_semantic(self, text: str) -> List[Chunk]:
        """
        Semantic chunking - tries to keep related content together
        Uses headers, topic changes, etc.
        """
        chunks = []
        
        # Detect sections/headers (markdown-style)
        lines = text.split('\n')
        current_section = []
        current_header = None
        start_char = 0
        char_pos = 0
        
        for line in lines:
            # Check if line is a header
            if re.match(r'^#{1,6}\s+', line) or re.match(r'^[A-Z][^.!?]*$', line.strip()):
                # Save previous section
                if current_section:
                    section_text = '\n'.join(current_section)
                    if len(section_text) > self.chunk_size:
                        # Split large section
                        sub_chunks = self._chunk_recursive(section_text)
                        for sc in sub_chunks:
                            sc.start_char += start_char
                            sc.end_char += start_char
                            sc.metadata['header'] = current_header
                            chunks.append(sc)
                    else:
                        chunks.append(Chunk(
                            content=section_text,
                            chunk_id=0,
                            start_char=start_char,
                            end_char=start_char + len(section_text),
                            metadata={'header': current_header}
                        ))
                    start_char = char_pos
                
                current_header = line.strip()
                current_section = [line]
            else:
                current_section.append(line)
            
            char_pos += len(line) + 1  # +1 for \n
        
        # Add last section
        if current_section:
            section_text = '\n'.join(current_section)
            if len(section_text) > self.chunk_size:
                sub_chunks = self._chunk_recursive(section_text)
                for sc in sub_chunks:
                    sc.start_char += start_char
                    sc.end_char += start_char
                    sc.metadata['header'] = current_header
                    chunks.append(sc)
            else:
                chunks.append(Chunk(
                    content=section_text,
                    chunk_id=0,
                    start_char=start_char,
                    end_char=start_char + len(section_text),
                    metadata={'header': current_header}
                ))
        
        return chunks if chunks else self._chunk_recursive(text)
    
    def _chunk_with_overlap(self, text: str) -> List[Chunk]:
        """
        Chunking with overlap - ensures context preservation
        """
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If not the last chunk, try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending in the last 100 chars
                search_start = max(start, end - 100)
                match = re.search(r'[.!?]\s', text[search_start:end])
                if match:
                    end = search_start + match.end()
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append(Chunk(
                    content=chunk_text,
                    chunk_id=chunk_id,
                    start_char=start,
                    end_char=end,
                    metadata={}
                ))
                chunk_id += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap if end < len(text) else len(text)
        
        return chunks
    
    def _chunk_token_aware(self, text: str) -> List[Chunk]:
        """
        Token-aware chunking - respects token limits
        Uses recursive strategy but with token counting
        """
        # For simplicity, use char count / 4 as token estimate
        # More accurate would be using tiktoken
        token_chunk_size = self.chunk_size * 4  # Convert tokens to chars
        
        original_chunk_size = self.chunk_size
        self.chunk_size = token_chunk_size
        
        chunks = self._chunk_recursive(text)
        
        self.chunk_size = original_chunk_size
        
        # Add token count to metadata
        for chunk in chunks:
            chunk.metadata['estimated_tokens'] = chunk.token_count()
        
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[Chunk]:
        """Chunk by sentences, grouping until size limit"""
        return self._split_by_sentences(text, 0)
    
    def _chunk_by_paragraphs(self, text: str) -> List[Chunk]:
        """Chunk by paragraphs"""
        paragraphs = re.split(r'\n\n+', text)
        chunks = []
        start_char = 0
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if para:
                chunks.append(Chunk(
                    content=para,
                    chunk_id=i,
                    start_char=start_char,
                    end_char=start_char + len(para),
                    metadata={'type': 'paragraph'}
                ))
                start_char += len(para) + 2  # +2 for \n\n
        
        return chunks
    
    def _chunk_fixed(self, text: str) -> List[Chunk]:
        """Fixed-size chunking"""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunk_text = text[i:i + self.chunk_size]
            chunks.append(Chunk(
                content=chunk_text,
                chunk_id=i // self.chunk_size,
                start_char=i,
                end_char=i + len(chunk_text),
                metadata={}
            ))
        
        return chunks
    
    def _chunk_code(self, text: str, file_type: Optional[str] = None) -> List[Chunk]:
        """
        Code-aware chunking - respects function/class boundaries
        """
        chunks = []
        
        # Detect language-specific patterns
        if file_type == 'py':
            # Python: split by functions and classes
            pattern = r'((?:^|\n)(?:def |class |async def )[^\n]+:)'
        elif file_type in ['js', 'ts']:
            # JavaScript: split by functions
            pattern = r'((?:^|\n)(?:function |const \w+ = |class )[^\n]+[{])'
        else:
            # Generic: split by braces and functions
            pattern = r'((?:^|\n)[^\n]*\{)'
        
        sections = re.split(pattern, text)
        
        current_chunk = ""
        start_char = 0
        
        for section in sections:
            if not section.strip():
                continue
            
            if len(current_chunk) + len(section) <= self.chunk_size:
                current_chunk += section
            else:
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk,
                        chunk_id=0,
                        start_char=start_char,
                        end_char=start_char + len(current_chunk),
                        metadata={'type': 'code', 'language': file_type}
                    ))
                    start_char += len(current_chunk)
                
                # If section itself is too large, use recursive
                if len(section) > self.chunk_size:
                    sub_chunks = self._chunk_recursive(section)
                    for sc in sub_chunks:
                        sc.start_char += start_char
                        sc.end_char += start_char
                        sc.metadata['type'] = 'code'
                        sc.metadata['language'] = file_type
                        chunks.append(sc)
                    start_char += len(section)
                    current_chunk = ""
                else:
                    current_chunk = section
        
        if current_chunk:
            chunks.append(Chunk(
                content=current_chunk,
                chunk_id=0,
                start_char=start_char,
                end_char=start_char + len(current_chunk),
                metadata={'type': 'code', 'language': file_type}
            ))
        
        return chunks if chunks else self._chunk_recursive(text)


# Convenience function
def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    strategy: str = "recursive",
    metadata: Optional[Dict] = None,
    file_type: Optional[str] = None
) -> List[Chunk]:
    """
    Convenience function to chunk text
    
    Args:
        text: Text to chunk
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks
        strategy: Chunking strategy (semantic, recursive, token_aware, overlap, etc.)
        metadata: Additional metadata
        file_type: File type for code-aware chunking
    
    Returns:
        List of chunks
    """
    try:
        strategy_enum = ChunkStrategy(strategy.lower())
    except ValueError:
        strategy_enum = ChunkStrategy.RECURSIVE
    
    chunker = DocumentChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        strategy=strategy_enum
    )
    
    return chunker.chunk_document(text, metadata, file_type)

