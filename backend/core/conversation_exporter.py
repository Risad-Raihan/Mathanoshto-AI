"""
AI-Powered Conversation Export System
Exports conversations in multiple formats with executive summaries
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from backend.database.models import Message, Conversation
from backend.database.conversation_insights_models import ConversationExport, ConversationSummary
from backend.database.operations import get_db
from sqlalchemy.orm import Session


@dataclass
class ExportOptions:
    """Export configuration options"""
    format: str  # markdown, json, html, pdf
    template: str  # standard, business, technical, meeting_notes
    include_timestamps: bool = True
    include_metadata: bool = True
    include_citations: bool = True
    include_summary: bool = True
    privacy_mode: bool = False


class ConversationExporter:
    """
    Exports conversations in multiple formats with AI-generated summaries
    """
    
    def __init__(self):
        """Initialize exporter"""
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
    
    def export_conversation(
        self,
        conversation: Conversation,
        messages: List[Message],
        options: ExportOptions,
        summary: Optional[ConversationSummary] = None
    ) -> str:
        """
        Export conversation in specified format
        
        Args:
            conversation: Conversation object
            messages: List of messages
            options: Export options
            summary: Optional conversation summary
        
        Returns:
            Path to exported file
        """
        if options.format == 'markdown':
            content = self._export_markdown(conversation, messages, options, summary)
            extension = '.md'
        elif options.format == 'json':
            content = self._export_json(conversation, messages, options, summary)
            extension = '.json'
        elif options.format == 'html':
            content = self._export_html(conversation, messages, options, summary)
            extension = '.html'
        elif options.format == 'pdf':
            # PDF would require additional libraries (reportlab, weasyprint)
            # For now, export as HTML that can be printed to PDF
            content = self._export_html(conversation, messages, options, summary)
            extension = '.html'
        else:
            raise ValueError(f"Unsupported format: {options.format}")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in conversation.title if c.isalnum() or c in (' ', '-', '_'))[:50]
        filename = f"{safe_title}_{timestamp}{extension}"
        filepath = self.export_dir / filename
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def _export_markdown(
        self,
        conversation: Conversation,
        messages: List[Message],
        options: ExportOptions,
        summary: Optional[ConversationSummary]
    ) -> str:
        """Export as Markdown"""
        lines = []
        
        # Title
        lines.append(f"# {conversation.title}\n")
        
        # Metadata
        if options.include_metadata:
            lines.append("## Metadata\n")
            lines.append(f"- **Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"- **Updated:** {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"- **Messages:** {len(messages)}")
            lines.append("")
        
        # Executive Summary
        if options.include_summary and summary:
            lines.append("## Executive Summary\n")
            lines.append(summary.short_summary)
            lines.append("")
            
            if summary.key_points:
                lines.append("### Key Points\n")
                for point in summary.key_points:
                    lines.append(f"- {point}")
                lines.append("")
            
            if summary.decisions_made:
                lines.append("### Decisions Made\n")
                for decision in summary.decisions_made:
                    lines.append(f"- {decision}")
                lines.append("")
            
            if summary.action_items:
                lines.append("### Action Items\n")
                for action in summary.action_items:
                    lines.append(f"- [ ] {action}")
                lines.append("")
        
        # Conversation
        lines.append("## Conversation\n")
        
        for i, msg in enumerate(messages, 1):
            if msg.role in ['user', 'assistant']:
                role = "**User**" if msg.role == "user" else "**Assistant**"
                
                if options.include_timestamps:
                    timestamp = msg.created_at.strftime('%H:%M:%S')
                    lines.append(f"### {role} ({timestamp})\n")
                else:
                    lines.append(f"### {role}\n")
                
                # Content (with privacy redaction if needed)
                content = msg.content
                if options.privacy_mode:
                    content = self._redact_sensitive_info(content)
                
                lines.append(content)
                lines.append("")
                
                # Citations
                if options.include_citations and i < len(messages):
                    lines.append(f"*[Message {i}]*\n")
        
        return "\n".join(lines)
    
    def _export_json(
        self,
        conversation: Conversation,
        messages: List[Message],
        options: ExportOptions,
        summary: Optional[ConversationSummary]
    ) -> str:
        """Export as JSON"""
        data = {
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
            },
            'summary': None,
            'messages': []
        }
        
        # Add summary
        if options.include_summary and summary:
            data['summary'] = {
                'short': summary.short_summary,
                'medium': summary.medium_summary,
                'detailed': summary.detailed_summary,
                'key_points': summary.key_points,
                'decisions': summary.decisions_made,
                'action_items': summary.action_items,
            }
        
        # Add messages
        for msg in messages:
            if msg.role in ['user', 'assistant']:
                msg_data = {
                    'id': msg.id,
                    'role': msg.role,
                    'content': self._redact_sensitive_info(msg.content) if options.privacy_mode else msg.content,
                }
                
                if options.include_timestamps:
                    msg_data['timestamp'] = msg.created_at.isoformat()
                
                if options.include_metadata:
                    msg_data['metadata'] = {
                        'model': msg.model,
                        'provider': msg.provider,
                        'tokens': msg.total_tokens,
                    }
                
                data['messages'].append(msg_data)
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _export_html(
        self,
        conversation: Conversation,
        messages: List[Message],
        options: ExportOptions,
        summary: Optional[ConversationSummary]
    ) -> str:
        """Export as HTML"""
        html_parts = []
        
        # HTML header
        html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{conversation.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .metadata {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .summary {{
            background: #e8f5e9;
            padding: 20px;
            border-radius: 4px;
            border-left: 4px solid #4CAF50;
            margin: 20px 0;
        }}
        .message {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 4px;
        }}
        .message.user {{
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
        }}
        .message.assistant {{
            background: #f3e5f5;
            border-left: 4px solid #9C27B0;
        }}
        .message-header {{
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
        .action-items, .key-points, .decisions {{
            margin: 15px 0;
        }}
        .action-items li, .key-points li, .decisions li {{
            margin: 8px 0;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>{conversation.title}</h1>
""")
        
        # Metadata
        if options.include_metadata:
            html_parts.append(f"""
    <div class="metadata">
        <strong>Created:</strong> {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}<br>
        <strong>Messages:</strong> {len(messages)}<br>
    </div>
""")
        
        # Summary
        if options.include_summary and summary:
            html_parts.append("""
    <div class="summary">
        <h2>📋 Executive Summary</h2>
        <p>{}</p>
""".format(summary.short_summary))
            
            if summary.key_points:
                html_parts.append("""
        <h3>Key Points</h3>
        <ul class="key-points">
            {}
        </ul>
""".format('\n            '.join(f"<li>{point}</li>" for point in summary.key_points)))
            
            if summary.action_items:
                html_parts.append("""
        <h3>Action Items</h3>
        <ul class="action-items">
            {}
        </ul>
""".format('\n            '.join(f"<li>☐ {item}</li>" for item in summary.action_items)))
            
            html_parts.append("    </div>")
        
        # Messages
        html_parts.append("""
    <h2>💬 Conversation</h2>
""")
        
        for msg in messages:
            if msg.role in ['user', 'assistant']:
                role_name = "User" if msg.role == "user" else "Assistant"
                role_class = msg.role
                
                content = msg.content
                if options.privacy_mode:
                    content = self._redact_sensitive_info(content)
                
                # Simple markdown-to-HTML conversion for code blocks
                content = content.replace('```', '<pre><code>').replace('```', '</code></pre>')
                content = content.replace('\n', '<br>')
                
                timestamp_html = ""
                if options.include_timestamps:
                    timestamp_html = f'<span class="timestamp">{msg.created_at.strftime("%H:%M:%S")}</span>'
                
                html_parts.append(f"""
    <div class="message {role_class}">
        <div class="message-header">
            <span>{role_name}</span>
            {timestamp_html}
        </div>
        <div class="message-content">{content}</div>
    </div>
""")
        
        # HTML footer
        html_parts.append("""
</div>
</body>
</html>
""")
        
        return "".join(html_parts)
    
    def _redact_sensitive_info(self, text: str) -> str:
        """Redact potentially sensitive information"""
        import re
        
        # Redact email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REDACTED]', text)
        
        # Redact phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE REDACTED]', text)
        
        # Redact API keys/tokens (simple pattern)
        text = re.sub(r'\b[A-Za-z0-9]{32,}\b', '[TOKEN REDACTED]', text)
        
        return text
    
    def save_export_record(
        self,
        conversation_id: int,
        user_id: int,
        options: ExportOptions,
        filepath: str,
        executive_summary: Optional[str] = None,
        db: Optional[Session] = None
    ) -> ConversationExport:
        """
        Save export record to database
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            options: Export options
            filepath: Path to exported file
            executive_summary: Optional executive summary
            db: Database session
        
        Returns:
            ConversationExport model
        """
        should_close = False
        if db is None:
            db = get_db()
            should_close = True
        
        try:
            # Get file size
            file_size = Path(filepath).stat().st_size
            
            export_record = ConversationExport(
                conversation_id=conversation_id,
                user_id=user_id,
                export_format=options.format,
                template_type=options.template,
                executive_summary=executive_summary,
                file_path=filepath,
                file_size_bytes=file_size,
                include_timestamps=options.include_timestamps,
                include_metadata=options.include_metadata,
                include_citations=options.include_citations,
                privacy_mode=options.privacy_mode
            )
            
            db.add(export_record)
            db.commit()
            db.refresh(export_record)
            return export_record
            
        finally:
            if should_close:
                db.close()


# Convenience function
def export_conversation(
    conversation_id: int,
    user_id: int,
    export_format: str = 'markdown',
    template: str = 'standard',
    include_summary: bool = True,
    privacy_mode: bool = False
) -> str:
    """
    Export a conversation
    
    Args:
        conversation_id: Conversation ID
        user_id: User ID
        export_format: Export format (markdown, json, html, pdf)
        template: Template type
        include_summary: Include executive summary
        privacy_mode: Redact sensitive information
    
    Returns:
        Path to exported file
    """
    from backend.database.operations import ConversationDB, MessageDB
    from backend.core.conversation_summarizer import get_conversation_summary
    
    # Get conversation and messages
    conversation = ConversationDB.get_conversation(conversation_id)
    messages = MessageDB.get_messages(conversation_id)
    
    if not conversation or not messages:
        raise ValueError("Conversation not found or empty")
    
    # Get summary if requested
    summary = None
    if include_summary:
        summary = get_conversation_summary(conversation_id)
    
    # Create export options
    options = ExportOptions(
        format=export_format,
        template=template,
        include_summary=include_summary,
        privacy_mode=privacy_mode
    )
    
    # Export
    exporter = ConversationExporter()
    filepath = exporter.export_conversation(conversation, messages, options, summary)
    
    # Save record
    exporter.save_export_record(
        conversation_id,
        user_id,
        options,
        filepath,
        executive_summary=summary.short_summary if summary else None
    )
    
    return filepath

