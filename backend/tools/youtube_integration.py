"""
YouTube Tool Integration for LLM Function Calling
"""
from typing import Dict, Any, Optional, List
import json

from backend.tools.youtube_tool import youtube_summarizer, YouTubeExtractor


def summarize_youtube_video(
    url: str,
    include_metadata: bool = True,
    include_key_moments: bool = True,
    include_transcript: bool = True
) -> str:
    """
    Analyze and summarize a YouTube video
    
    Args:
        url: YouTube video URL or video ID
        include_metadata: Include video metadata (title, views, duration, etc.)
        include_key_moments: Extract key moments with timestamps
        include_transcript: Include full transcript for detailed analysis
    
    Returns:
        JSON string with video information and transcript
    """
    try:
        result = youtube_summarizer.process_video(
            url=url,
            include_transcript=include_transcript,
            include_metadata=include_metadata,
            include_key_moments=include_key_moments,
            max_transcript_chars=15000
        )
        
        if not result['success']:
            return json.dumps({
                'success': False,
                'url': url,
                'error': result.get('error', 'Failed to process video')
            })
        
        # Format response for LLM
        response = {
            'success': True,
            'video_id': result['video_id'],
            'url': result['url']
        }
        
        # Add metadata
        if include_metadata and result.get('metadata'):
            meta = result['metadata']
            response['title'] = meta.get('title')
            response['author'] = meta.get('author')
            response['duration'] = meta.get('duration')
            response['views'] = meta.get('views')
            response['publish_date'] = meta.get('publish_date')
            response['description'] = meta.get('description')
        
        # Add transcript
        if include_transcript and result.get('transcript'):
            response['transcript'] = result['transcript']
            response['transcript_language'] = result.get('transcript_language')
            response['is_auto_generated'] = result.get('is_auto_generated')
        
        # Add key moments
        if include_key_moments and result.get('key_moments'):
            response['key_moments'] = result['key_moments']
        
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({
            'success': False,
            'url': url,
            'error': f'YouTube processing failed: {str(e)}'
        })


def get_playlist_summary(
    playlist_url: str,
    max_videos: int = 5
) -> str:
    """
    Get summary of videos in a YouTube playlist
    
    Args:
        playlist_url: YouTube playlist URL
        max_videos: Maximum number of videos to analyze (default: 5)
    
    Returns:
        JSON string with playlist information
    """
    try:
        extractor = YouTubeExtractor()
        
        # Extract playlist ID
        playlist_id = extractor.extract_playlist_id(playlist_url)
        if not playlist_id:
            return json.dumps({
                'success': False,
                'error': 'Invalid playlist URL'
            })
        
        # Get playlist videos
        playlist_result = extractor.get_playlist_videos(playlist_id, max_videos)
        
        if not playlist_result.get('success'):
            return json.dumps({
                'success': False,
                'error': playlist_result.get('error')
            })
        
        # Get metadata for each video
        videos_info = []
        for video in playlist_result['videos'][:max_videos]:
            metadata = extractor.get_video_metadata(video['video_id'])
            if metadata.get('success'):
                videos_info.append({
                    'video_id': video['video_id'],
                    'url': video['url'],
                    'title': metadata.get('title'),
                    'duration': metadata.get('duration'),
                    'views': metadata.get('views')
                })
        
        return json.dumps({
            'success': True,
            'playlist_id': playlist_id,
            'playlist_title': playlist_result.get('title'),
            'total_videos': playlist_result.get('total_videos'),
            'videos': videos_info
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f'Playlist processing failed: {str(e)}'
        })


# Tool definitions for LLM function calling
YOUTUBE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "summarize_youtube_video",
            "description": "Analyze and summarize a YouTube video by extracting its transcript, metadata, and key moments. Use this when user asks about YouTube videos, wants summaries, or needs to understand video content without watching.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "YouTube video URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID)"
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include video metadata (title, views, duration, author, etc.)",
                        "default": True
                    },
                    "include_key_moments": {
                        "type": "boolean",
                        "description": "Extract key moments with timestamps from the video",
                        "default": True
                    },
                    "include_transcript": {
                        "type": "boolean",
                        "description": "Include full transcript for detailed analysis",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_playlist_summary",
            "description": "Get information about videos in a YouTube playlist. Use this when user asks about playlist contents or wants to know what's in a playlist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "playlist_url": {
                        "type": "string",
                        "description": "YouTube playlist URL"
                    },
                    "max_videos": {
                        "type": "integer",
                        "description": "Maximum number of videos to analyze (default: 5, max: 10)",
                        "default": 5
                    }
                },
                "required": ["playlist_url"]
            }
        }
    }
]


def get_youtube_tools(enabled: bool = True) -> Optional[List[Dict]]:
    """Get YouTube tools if enabled"""
    return YOUTUBE_TOOLS if enabled else None


def execute_youtube_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Execute a YouTube tool by name"""
    if tool_name == "summarize_youtube_video":
        return summarize_youtube_video(**tool_input)
    elif tool_name == "get_playlist_summary":
        return get_playlist_summary(**tool_input)
    else:
        return json.dumps({
            'success': False,
            'error': f'Unknown tool: {tool_name}'
        })

