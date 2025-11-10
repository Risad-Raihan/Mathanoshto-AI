"""
RAG (Retrieval Augmented Generation) for file Q&A and summarization
"""
from typing import Optional, Dict, Any, List
from pathlib import Path

from backend.database.file_operations import FileDB
from backend.utils.file_storage import file_storage
from backend.utils.file_parser import file_parser


class FileRAG:
    """
    RAG system for answering questions about files and generating summaries
    """
    
    @staticmethod
    def get_file_context(file_id: int, user_id: int, max_chars: int = 8000) -> Optional[str]:
        """
        Get file content as context for LLM
        
        Args:
            file_id: File ID
            user_id: User ID (for access control)
            max_chars: Maximum characters to return
        
        Returns:
            File content text or None
        """
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return None
        
        # If we have extracted text, use it
        if file_record.extracted_text:
            text = file_record.extracted_text
        else:
            # Try to extract on-the-fly
            full_path = file_storage.get_file_path(file_record.file_path)
            parse_result = file_parser.parse_file(full_path, file_record.file_type)
            
            if not parse_result['success']:
                return None
            
            text = parse_result['text']
        
        # Truncate if too long
        if len(text) > max_chars:
            text = text[:max_chars] + "...\n[Content truncated]"
        
        return text
    
    @staticmethod
    def create_file_summary_prompt(file_info: Dict[str, Any], file_content: str) -> str:
        """
        Create a prompt for summarizing a file
        
        Args:
            file_info: File metadata
            file_content: File text content
        
        Returns:
            Formatted prompt
        """
        prompt = f"""Please provide a comprehensive summary of the following document:

**File Name:** {file_info.get('original_filename', 'Unknown')}
**File Type:** {file_info.get('file_type', 'Unknown')}
**File Size:** {file_info.get('file_size', 0)} bytes

**Content:**
{file_content}

Please provide:
1. A brief overview (2-3 sentences)
2. Key points or main topics
3. Any important details or insights
4. Conclusion or takeaways

Format your response in a clear, structured manner."""

        return prompt
    
    @staticmethod
    def create_file_qa_prompt(
        file_info: Dict[str, Any],
        file_content: str,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Create a prompt for answering questions about a file
        
        Args:
            file_info: File metadata
            file_content: File text content
            question: User's question
            conversation_history: Optional previous Q&A pairs
        
        Returns:
            Formatted prompt
        """
        prompt = f"""You are an AI assistant helping users understand and analyze documents. You have access to the following document:

**File Name:** {file_info.get('original_filename', 'Unknown')}
**File Type:** {file_info.get('file_type', 'Unknown')}

**Document Content:**
{file_content}

"""
        
        # Add conversation history if available
        if conversation_history:
            prompt += "\n**Previous conversation:**\n"
            for entry in conversation_history[-3:]:  # Last 3 exchanges
                prompt += f"Q: {entry.get('question', '')}\n"
                prompt += f"A: {entry.get('answer', '')}\n\n"
        
        prompt += f"""**Current Question:** {question}

Please answer the question based on the document content. If the information is not in the document, please say so. Be specific and cite relevant parts of the document when possible."""

        return prompt
    
    @staticmethod
    def create_multi_file_prompt(
        files_info: List[Dict[str, Any]],
        files_content: List[str],
        question: str
    ) -> str:
        """
        Create a prompt for answering questions about multiple files
        
        Args:
            files_info: List of file metadata dicts
            files_content: List of file text contents
            question: User's question
        
        Returns:
            Formatted prompt
        """
        prompt = """You are an AI assistant helping users analyze multiple documents. You have access to the following documents:

"""
        
        for i, (info, content) in enumerate(zip(files_info, files_content), 1):
            prompt += f"""
**Document {i}:**
- File Name: {info.get('original_filename', 'Unknown')}
- File Type: {info.get('file_type', 'Unknown')}

Content:
{content}

---

"""
        
        prompt += f"""
**Question:** {question}

Please answer the question by analyzing all the provided documents. If relevant information is in multiple documents, synthesize the information. Cite which document(s) you're referencing in your answer."""

        return prompt
    
    @staticmethod
    def extract_key_information(file_content: str, file_type: str) -> Dict[str, Any]:
        """
        Extract key information from file content
        
        Args:
            file_content: File text content
            file_type: Type of file
        
        Returns:
            Dictionary with extracted info
        """
        info = {
            'word_count': len(file_content.split()),
            'char_count': len(file_content),
            'line_count': len(file_content.split('\n'))
        }
        
        # Type-specific extraction
        if file_type == 'csv':
            # Extract column info if visible in content
            lines = file_content.split('\n')
            if 'Columns:' in file_content:
                for line in lines:
                    if line.startswith('Columns:'):
                        info['columns'] = line.replace('Columns:', '').strip()
                    if line.startswith('Total rows:'):
                        try:
                            info['row_count'] = int(line.replace('Total rows:', '').strip())
                        except:
                            pass
        
        elif file_type == 'json':
            if 'keys:' in file_content.lower():
                # Try to find keys in content
                import re
                keys_match = re.search(r'"keys":\s*\[(.*?)\]', file_content)
                if keys_match:
                    info['json_keys'] = keys_match.group(1)
        
        # Extract potential headers/titles (first few lines)
        lines = file_content.split('\n')
        non_empty_lines = [l.strip() for l in lines if l.strip()]
        if non_empty_lines:
            info['first_line'] = non_empty_lines[0][:200]
        
        return info
    
    @staticmethod
    def create_comparison_prompt(
        file1_info: Dict[str, Any],
        file1_content: str,
        file2_info: Dict[str, Any],
        file2_content: str,
        comparison_aspect: Optional[str] = None
    ) -> str:
        """
        Create a prompt for comparing two files
        
        Args:
            file1_info: First file metadata
            file1_content: First file content
            file2_info: Second file metadata
            file2_content: Second file content
            comparison_aspect: Optional specific aspect to compare
        
        Returns:
            Formatted prompt
        """
        prompt = f"""Please compare the following two documents:

**Document 1:**
- File Name: {file1_info.get('original_filename', 'Unknown')}
- File Type: {file1_info.get('file_type', 'Unknown')}

Content:
{file1_content}

---

**Document 2:**
- File Name: {file2_info.get('original_filename', 'Unknown')}
- File Type: {file2_info.get('file_type', 'Unknown')}

Content:
{file2_content}

---

"""
        
        if comparison_aspect:
            prompt += f"Please compare these documents specifically regarding: {comparison_aspect}\n\n"
        else:
            prompt += """Please provide a comprehensive comparison including:
1. Main similarities
2. Key differences
3. Unique aspects of each document
4. Overall assessment

"""
        
        return prompt


class FileSummarizer:
    """Convenience class for file summarization operations"""
    
    @staticmethod
    def get_summary_for_file(file_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a structured summary request for a file
        
        Returns:
            Dictionary with file info and prompt, ready for LLM
        """
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return None
        
        # Get file content
        content = FileRAG.get_file_context(file_id, user_id)
        
        if not content:
            return None
        
        file_info = {
            'id': file_record.id,
            'original_filename': file_record.original_filename,
            'file_type': file_record.file_type,
            'file_size': file_record.file_size
        }
        
        # Create prompt
        prompt = FileRAG.create_file_summary_prompt(file_info, content)
        
        return {
            'file_info': file_info,
            'content': content,
            'prompt': prompt
        }
    
    @staticmethod
    def get_qa_for_file(
        file_id: int,
        user_id: int,
        question: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a Q&A request for a file
        
        Returns:
            Dictionary with file info and prompt, ready for LLM
        """
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return None
        
        # Get file content
        content = FileRAG.get_file_context(file_id, user_id)
        
        if not content:
            return None
        
        file_info = {
            'id': file_record.id,
            'original_filename': file_record.original_filename,
            'file_type': file_record.file_type,
            'file_size': file_record.file_size
        }
        
        # Create prompt
        prompt = FileRAG.create_file_qa_prompt(file_info, content, question, history)
        
        return {
            'file_info': file_info,
            'content': content,
            'question': question,
            'prompt': prompt
        }


# Global instances
file_rag = FileRAG()
file_summarizer = FileSummarizer()

