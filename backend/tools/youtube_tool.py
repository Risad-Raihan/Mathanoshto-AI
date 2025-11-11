"""
YouTube Summarizer Tool - Extract transcripts and metadata from YouTube videos
"""
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json


class YouTubeExtractor:
    """Extract information from YouTube videos"""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats
        
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If it's already just the ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        return None
    
    @staticmethod
    def extract_playlist_id(url: str) -> Optional[str]:
        """Extract YouTube playlist ID from URL"""
        pattern = r'[&?]list=([a-zA-Z0-9_-]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    @staticmethod
    def get_transcript(video_id: str, languages: List[str] = ['en']) -> Dict[str, Any]:
        """
        Get transcript for a YouTube video
        
        Args:
            video_id: YouTube video ID
            languages: List of language codes to try (default: ['en'])
        
        Returns:
            Dictionary with transcript data
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api._errors import (
                TranscriptsDisabled,
                NoTranscriptFound,
                VideoUnavailable
            )
            
            try:
                # Fetch transcript directly
                api = YouTubeTranscriptApi()
                result = api.fetch(video_id, languages=languages)
                
                # Convert snippets to dict format
                transcript_data = [
                    {
                        'text': snippet.text,
                        'start': snippet.start,
                        'duration': snippet.duration
                    }
                    for snippet in result.snippets
                ]
                
                # Format transcript
                full_text = " ".join([entry['text'] for entry in transcript_data])
                
                return {
                    'success': True,
                    'transcript': transcript_data,
                    'full_text': full_text,
                    'language': result.language,
                    'is_generated': result.is_generated,
                    'video_id': video_id
                }
            
            except TranscriptsDisabled:
                return {
                    'success': False,
                    'error': 'Transcripts are disabled for this video'
                }
            except NoTranscriptFound:
                return {
                    'success': False,
                    'error': f'No transcript found in languages: {languages}'
                }
            except VideoUnavailable:
                return {
                    'success': False,
                    'error': 'Video is unavailable'
                }
        
        except ImportError:
            return {
                'success': False,
                'error': 'youtube-transcript-api not installed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get transcript: {str(e)}'
            }
    
    @staticmethod
    def get_video_metadata(video_id: str) -> Dict[str, Any]:
        """
        Get video metadata using pytube
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Dictionary with video metadata
        """
        try:
            from pytube import YouTube
            import isodate
            
            url = f"https://www.youtube.com/watch?v={video_id}"
            yt = YouTube(url)
            
            # Parse duration
            duration_seconds = yt.length
            duration_formatted = f"{duration_seconds // 3600:02d}:{(duration_seconds % 3600) // 60:02d}:{duration_seconds % 60:02d}"
            
            metadata = {
                'success': True,
                'video_id': video_id,
                'title': yt.title,
                'author': yt.author,
                'channel_id': yt.channel_id,
                'length': duration_seconds,
                'duration': duration_formatted,
                'views': yt.views,
                'rating': yt.rating,
                'description': yt.description[:500] if yt.description else '',  # First 500 chars
                'keywords': yt.keywords[:10] if yt.keywords else [],  # First 10 keywords
                'publish_date': str(yt.publish_date) if yt.publish_date else None,
                'thumbnail_url': yt.thumbnail_url,
                'watch_url': yt.watch_url
            }
            
            return metadata
        
        except ImportError:
            return {
                'success': False,
                'error': 'pytube not installed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get metadata: {str(e)}'
            }
    
    @staticmethod
    def extract_key_moments(transcript_data: List[Dict], num_moments: int = 5) -> List[Dict[str, Any]]:
        """
        Extract key moments from transcript based on breaks and sections
        
        Args:
            transcript_data: List of transcript entries with text and start times
            num_moments: Number of key moments to extract
        
        Returns:
            List of key moments with timestamps
        """
        if not transcript_data:
            return []
        
        # Group transcript into segments based on longer pauses
        segments = []
        current_segment = []
        
        for i, entry in enumerate(transcript_data):
            current_segment.append(entry)
            
            # Check if there's a long pause (>3 seconds) or significant break
            if i < len(transcript_data) - 1:
                time_gap = transcript_data[i + 1]['start'] - (entry['start'] + entry.get('duration', 2))
                if time_gap > 3 or len(current_segment) > 20:  # New segment after pause or 20 entries
                    segments.append(current_segment)
                    current_segment = []
        
        if current_segment:
            segments.append(current_segment)
        
        # Extract key moments (evenly distributed)
        key_moments = []
        step = max(1, len(segments) // num_moments)
        
        for i in range(0, len(segments), step):
            if i < len(segments) and len(key_moments) < num_moments:
                segment = segments[i]
                start_time = segment[0]['start']
                text = " ".join([entry['text'] for entry in segment[:5]])  # First 5 entries
                
                # Format timestamp
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                timestamp = f"{minutes}:{seconds:02d}"
                
                key_moments.append({
                    'timestamp': timestamp,
                    'start_seconds': start_time,
                    'text': text[:150]  # First 150 chars
                })
        
        return key_moments
    
    @staticmethod
    def format_transcript_for_llm(
        transcript_data: List[Dict],
        max_chars: int = 15000,
        include_timestamps: bool = True
    ) -> str:
        """
        Format transcript for LLM consumption
        
        Args:
            transcript_data: List of transcript entries
            max_chars: Maximum characters to include
            include_timestamps: Whether to include timestamps
        
        Returns:
            Formatted transcript string
        """
        if not transcript_data:
            return ""
        
        lines = []
        current_length = 0
        
        for entry in transcript_data:
            if include_timestamps:
                minutes = int(entry['start'] // 60)
                seconds = int(entry['start'] % 60)
                line = f"[{minutes}:{seconds:02d}] {entry['text']}"
            else:
                line = entry['text']
            
            if current_length + len(line) > max_chars:
                lines.append("...[Transcript truncated]")
                break
            
            lines.append(line)
            current_length += len(line)
        
        return "\n".join(lines)
    
    @staticmethod
    def get_playlist_videos(playlist_id: str, max_videos: int = 10) -> Dict[str, Any]:
        """
        Get videos from a YouTube playlist
        
        Args:
            playlist_id: YouTube playlist ID
            max_videos: Maximum number of videos to retrieve
        
        Returns:
            Dictionary with playlist videos
        """
        try:
            from pytube import Playlist
            
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            playlist = Playlist(playlist_url)
            
            videos = []
            for video_url in list(playlist.video_urls)[:max_videos]:
                video_id = YouTubeExtractor.extract_video_id(video_url)
                if video_id:
                    videos.append({
                        'video_id': video_id,
                        'url': video_url
                    })
            
            return {
                'success': True,
                'playlist_id': playlist_id,
                'title': playlist.title,
                'videos': videos,
                'total_videos': len(videos)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get playlist: {str(e)}'
            }


class YouTubeSummarizer:
    """Summarize YouTube videos using transcripts and LLM"""
    
    def __init__(self):
        self.extractor = YouTubeExtractor()
    
    def process_video(
        self,
        url: str,
        include_transcript: bool = True,
        include_metadata: bool = True,
        include_key_moments: bool = True,
        max_transcript_chars: int = 15000
    ) -> Dict[str, Any]:
        """
        Process a YouTube video and extract all relevant information
        
        Args:
            url: YouTube video URL or ID
            include_transcript: Include full transcript
            include_metadata: Include video metadata
            include_key_moments: Extract key moments
            max_transcript_chars: Maximum transcript characters
        
        Returns:
            Dictionary with all video information
        """
        result = {
            'success': False,
            'video_id': None,
            'url': None,
            'metadata': {},
            'transcript': None,
            'key_moments': [],
            'error': None
        }
        
        # Extract video ID
        video_id = self.extractor.extract_video_id(url)
        if not video_id:
            result['error'] = 'Invalid YouTube URL or video ID'
            return result
        
        result['video_id'] = video_id
        result['url'] = f"https://www.youtube.com/watch?v={video_id}"
        
        # Get metadata
        if include_metadata:
            metadata = self.extractor.get_video_metadata(video_id)
            if metadata.get('success'):
                result['metadata'] = metadata
            else:
                result['error'] = metadata.get('error')
        
        # Get transcript
        transcript_result = self.extractor.get_transcript(video_id)
        
        if not transcript_result.get('success'):
            result['error'] = transcript_result.get('error')
            result['success'] = False
            return result
        
        transcript_data = transcript_result['transcript']
        
        # Format transcript for LLM
        if include_transcript:
            result['transcript'] = self.extractor.format_transcript_for_llm(
                transcript_data,
                max_chars=max_transcript_chars,
                include_timestamps=True
            )
            result['transcript_language'] = transcript_result.get('language')
            result['is_auto_generated'] = transcript_result.get('is_generated')
        
        # Extract key moments
        if include_key_moments:
            result['key_moments'] = self.extractor.extract_key_moments(transcript_data)
        
        result['success'] = True
        return result


# Global instance
youtube_summarizer = YouTubeSummarizer()

