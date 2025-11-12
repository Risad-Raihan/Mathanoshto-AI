"""
AI Image Generation Tools
Integrates DALL-E, Gemini Imagen, and other image generation APIs
"""
import asyncio
import base64
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

from backend.core.image_handler import image_handler
from backend.config.settings import settings


class ImageGenerator:
    """Generate images using AI models"""
    
    def __init__(self):
        """Initialize image generator"""
        self.output_dir = image_handler.GENERATED_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_dalle(
        self,
        prompt: str,
        user_id: int,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid"
    ) -> Dict[str, Any]:
        """
        Generate image using DALL-E
        
        Args:
            prompt: Image description
            user_id: User ID
            model: DALL-E model ("dall-e-2" or "dall-e-3")
            size: Image size ("1024x1024", "1792x1024", "1024x1792" for dall-e-3)
            quality: "standard" or "hd" (dall-e-3 only)
            style: "vivid" or "natural" (dall-e-3 only)
            
        Returns:
            Dictionary with generation info
        """
        try:
            from openai import AsyncOpenAI
            
            if not settings.openai_api_key:
                return {
                    'success': False,
                    'error': 'OpenAI API key not configured'
                }
            
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            # Validate model-specific options
            if model == "dall-e-2":
                size = "1024x1024"  # Only size supported by dall-e-2
                generation_params = {
                    "model": model,
                    "prompt": prompt,
                    "n": 1,
                    "size": size,
                    "response_format": "b64_json"
                }
            else:  # dall-e-3
                generation_params = {
                    "model": model,
                    "prompt": prompt,
                    "n": 1,
                    "size": size,
                    "quality": quality,
                    "style": style,
                    "response_format": "b64_json"
                }
            
            # Generate image
            response = await client.images.generate(**generation_params)
            
            # Get base64 image data
            image_data = response.data[0]
            b64_json = image_data.b64_json
            
            # Decode and save
            image_bytes = base64.b64decode(b64_json)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            filename = f"{user_id}_dalle_{timestamp}_{prompt_hash}.png"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            return {
                'success': True,
                'file_path': str(filepath),
                'relative_path': str(filepath.relative_to(Path.cwd())),
                'filename': filename,
                'prompt': prompt,
                'model': model,
                'size': size,
                'quality': quality if model == "dall-e-3" else None,
                'style': style if model == "dall-e-3" else None,
                'revised_prompt': image_data.revised_prompt if hasattr(image_data, 'revised_prompt') else None,
                'size_bytes': len(image_bytes),
                'size_kb': round(len(image_bytes) / 1024, 2),
                'created_at': datetime.now().isoformat(),
                'provider': 'openai'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'DALL-E generation failed: {str(e)}'
            }
    
    async def generate_gemini(
        self,
        prompt: str,
        user_id: int,
        model: str = "gemini-1.5-pro",
        num_images: int = 1
    ) -> Dict[str, Any]:
        """
        Generate image using Google Gemini (Imagen via Gemini API)
        
        Note: Gemini's image generation is available through Vertex AI.
        This is a placeholder for when the feature becomes available in the standard API.
        
        Args:
            prompt: Image description
            user_id: User ID
            model: Gemini model
            num_images: Number of images to generate
            
        Returns:
            Dictionary with generation info
        """
        return {
            'success': False,
            'error': 'Gemini image generation is not yet available in the standard API. Use DALL-E or Stability AI instead.'
        }
    
    async def generate_stability(
        self,
        prompt: str,
        user_id: int,
        model: str = "stable-diffusion-xl-1024-v1-0",
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        cfg_scale: float = 7.0,
        steps: int = 30
    ) -> Dict[str, Any]:
        """
        Generate image using Stability AI
        
        Args:
            prompt: Image description
            user_id: User ID
            model: Model ID
            negative_prompt: What to avoid in image
            width: Image width
            height: Image height
            cfg_scale: Prompt strength (7.0 recommended)
            steps: Number of diffusion steps
            
        Returns:
            Dictionary with generation info
        """
        try:
            import aiohttp
            
            # Get API key from settings (would need to be added)
            api_key = getattr(settings, 'stability_api_key', None)
            if not api_key:
                return {
                    'success': False,
                    'error': 'Stability AI API key not configured in .env (STABILITY_API_KEY)'
                }
            
            # Prepare request
            url = "https://api.stability.ai/v1/generation/{model}/text-to-image"
            url = url.format(model=model)
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "text_prompts": [
                    {"text": prompt, "weight": 1.0}
                ],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "steps": steps,
                "samples": 1
            }
            
            if negative_prompt:
                payload["text_prompts"].append({
                    "text": negative_prompt,
                    "weight": -1.0
                })
            
            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Stability AI error ({response.status}): {error_text}'
                        }
                    
                    result = await response.json()
            
            # Save generated image
            artifacts = result.get('artifacts', [])
            if not artifacts:
                return {
                    'success': False,
                    'error': 'No image generated'
                }
            
            # Get first artifact
            artifact = artifacts[0]
            b64_image = artifact['base64']
            image_bytes = base64.b64decode(b64_image)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            filename = f"{user_id}_stability_{timestamp}_{prompt_hash}.png"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            return {
                'success': True,
                'file_path': str(filepath),
                'relative_path': str(filepath.relative_to(Path.cwd())),
                'filename': filename,
                'prompt': prompt,
                'negative_prompt': negative_prompt,
                'model': model,
                'width': width,
                'height': height,
                'cfg_scale': cfg_scale,
                'steps': steps,
                'size_bytes': len(image_bytes),
                'size_kb': round(len(image_bytes) / 1024, 2),
                'created_at': datetime.now().isoformat(),
                'provider': 'stability_ai'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Stability AI generation failed: {str(e)}'
            }
    
    def generate(
        self,
        prompt: str,
        user_id: int,
        provider: str = "dalle",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image (sync wrapper)
        
        Args:
            prompt: Image description
            user_id: User ID
            provider: "dalle", "gemini", or "stability"
            **kwargs: Provider-specific arguments
            
        Returns:
            Dictionary with generation info
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if provider == "dalle":
            return loop.run_until_complete(self.generate_dalle(prompt, user_id, **kwargs))
        elif provider == "gemini":
            return loop.run_until_complete(self.generate_gemini(prompt, user_id, **kwargs))
        elif provider == "stability":
            return loop.run_until_complete(self.generate_stability(prompt, user_id, **kwargs))
        else:
            return {
                'success': False,
                'error': f'Unknown provider: {provider}'
            }


# Tool definitions for LLM integration
IMAGE_GENERATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "Generate an image from a text description using AI (DALL-E 3). Use this when the user asks to create, generate, or visualize an image. Be creative and detailed in your prompts for better results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Detailed description of the image to generate. Be specific about style, colors, composition, lighting, and subject matter."
                    },
                    "provider": {
                        "type": "string",
                        "enum": ["dalle", "stability"],
                        "description": "AI provider to use for generation. Default: dalle",
                        "default": "dalle"
                    },
                    "size": {
                        "type": "string",
                        "enum": ["1024x1024", "1792x1024", "1024x1792"],
                        "description": "Image size (DALL-E 3). Use 1024x1024 for square, 1792x1024 for landscape, 1024x1792 for portrait",
                        "default": "1024x1024"
                    },
                    "quality": {
                        "type": "string",
                        "enum": ["standard", "hd"],
                        "description": "Image quality (DALL-E 3 only). 'hd' creates more detailed images",
                        "default": "standard"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["vivid", "natural"],
                        "description": "Image style (DALL-E 3 only). 'vivid' for more dramatic/artistic, 'natural' for more realistic",
                        "default": "vivid"
                    }
                },
                "required": ["prompt"]
            }
        }
    }
]


def execute_image_generation_tool(function_name: str, function_args: Dict) -> str:
    """
    Execute image generation tool
    
    Args:
        function_name: Tool function name
        function_args: Function arguments
        
    Returns:
        Result string for LLM
    """
    generator = ImageGenerator()
    
    if function_name == "generate_image":
        # Get user_id from session (this would need to be passed properly)
        # For now, we'll use a default or need to update the tool integration
        import streamlit as st
        user_id = st.session_state.get('user_id', 1)
        
        prompt = function_args.get('prompt')
        provider = function_args.get('provider', 'dalle')
        
        # Extract provider-specific params
        if provider == 'dalle':
            kwargs = {
                'size': function_args.get('size', '1024x1024'),
                'quality': function_args.get('quality', 'standard'),
                'style': function_args.get('style', 'vivid')
            }
        elif provider == 'stability':
            kwargs = {
                'width': int(function_args.get('size', '1024x1024').split('x')[0]),
                'height': int(function_args.get('size', '1024x1024').split('x')[1]),
                'negative_prompt': function_args.get('negative_prompt')
            }
        else:
            kwargs = {}
        
        result = generator.generate(prompt, user_id, provider, **kwargs)
        
        if result['success']:
            response_parts = [
                f"✅ **Image Generated Successfully!**\n",
                f"**Prompt:** {prompt}\n",
                f"**Provider:** {provider.upper()}\n",
                f"**Size:** {result.get('size_kb')} KB\n"
            ]
            
            if result.get('revised_prompt'):
                response_parts.append(f"**Enhanced Prompt:** {result['revised_prompt']}\n")
            
            # Add image path that will be detected by display system
            response_parts.append(f"\n[View Image](sandbox:/{result['relative_path']})\n")
            response_parts.append(f"\n![Generated Image](sandbox:/{result['relative_path']})")
            
            return "\n".join(response_parts)
        else:
            return f"❌ Image generation failed: {result['error']}"
    
    return f"❌ Unknown image generation function: {function_name}"


# Global instance
image_generator = ImageGenerator()

