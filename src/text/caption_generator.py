"""
AI-powered caption generation using LLM (Ollama or OpenAI)
"""
import json
import requests
from typing import List, Dict, Optional
from pathlib import Path

from src.utils.config import Config
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class CaptionGenerator:
    """
    Generates engaging captions using LLM
    """

    def __init__(self, use_ollama: bool = True):
        """
        Args:
            use_ollama: Use local Ollama (True) or OpenAI API (False)
        """
        self.use_ollama = use_ollama
        self.ollama_host = Config.OLLAMA_HOST
        self.ollama_model = Config.OLLAMA_MODEL
        self.openai_api_key = Config.OPENAI_API_KEY

    def generate_captions(self,
                         description: str,
                         num_clips: int,
                         clip_durations: List[float],
                         style: str = "engaging") -> List[Dict]:
        """
        Generate captions for a reel

        Args:
            description: User's description of the content
            num_clips: Number of clips in the reel
            clip_durations: Duration of each clip
            style: Caption style (engaging, professional, fun, minimal)

        Returns:
            List of caption dictionaries with text, timing, and position
        """
        logger.info(f"Generating {num_clips} captions in '{style}' style")

        # Build prompt
        prompt = self._build_prompt(description, num_clips, clip_durations, style)

        # Generate using LLM
        if self.use_ollama:
            response = self._generate_with_ollama(prompt)
        else:
            response = self._generate_with_openai(prompt)

        # Parse response into structured captions
        captions = self._parse_captions(response, num_clips, clip_durations)

        logger.info(f"✓ Generated {len(captions)} captions")
        return captions

    def _build_prompt(self, description: str, num_clips: int,
                     clip_durations: List[float], style: str) -> str:
        """Build the LLM prompt"""

        total_duration = sum(clip_durations)

        prompt = f"""You are an expert Instagram reel caption writer. Create engaging, short captions for a reel.

Description: {description}
Number of clips: {num_clips}
Total duration: {total_duration:.1f} seconds
Style: {style}

Create {num_clips} short captions (3-7 words each) that:
1. Start with a hook to grab attention
2. Tell a story through the reel
3. Match the {style} style
4. Are optimized for Instagram (use emojis if appropriate)
5. Each caption should appear during a specific clip

Respond ONLY with a JSON array of objects, each with:
- "text": the caption text
- "clip_index": which clip (0 to {num_clips-1})
- "position": "top", "center", or "bottom"

Example format:
[
  {{"text": "🌅 Wake up to this view", "clip_index": 0, "position": "top"}},
  {{"text": "Best morning ever ☕", "clip_index": 1, "position": "center"}},
  {{"text": "Living our best life", "clip_index": 2, "position": "bottom"}}
]

Generate the captions now:"""

        return prompt

    def _generate_with_ollama(self, prompt: str) -> str:
        """Generate text using local Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return self._generate_fallback_captions(prompt)

        except requests.exceptions.RequestException as e:
            logger.warning(f"Ollama not available: {e}")
            logger.info("Falling back to simple captions")
            return self._generate_fallback_captions(prompt)

    def _generate_with_openai(self, prompt: str) -> str:
        """Generate text using OpenAI API"""
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found, using fallback")
            return self._generate_fallback_captions(prompt)

        try:
            import openai
            openai.api_key = self.openai_api_key

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert Instagram caption writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return self._generate_fallback_captions(prompt)

    def _generate_fallback_captions(self, prompt: str) -> str:
        """Generate simple fallback captions when LLM is unavailable"""
        logger.info("Using fallback caption generation")

        # Extract description from prompt
        desc_start = prompt.find("Description: ") + len("Description: ")
        desc_end = prompt.find("\n", desc_start)
        description = prompt[desc_start:desc_end].strip()

        # Extract num_clips
        clips_start = prompt.find("Number of clips: ") + len("Number of clips: ")
        clips_end = prompt.find("\n", clips_start)
        num_clips = int(prompt[clips_start:clips_end].strip())

        # Generate simple captions
        words = description.split()
        captions = []

        # First caption (hook)
        captions.append({
            "text": " ".join(words[:min(5, len(words))]),
            "clip_index": 0,
            "position": "top"
        })

        # Middle captions
        for i in range(1, num_clips - 1):
            pos = ["center", "bottom"][i % 2]
            start_idx = (i * len(words)) // num_clips
            end_idx = min(start_idx + 5, len(words))
            text = " ".join(words[start_idx:end_idx]) if start_idx < len(words) else f"Moment {i+1}"
            captions.append({
                "text": text,
                "clip_index": i,
                "position": pos
            })

        # Last caption
        if num_clips > 1:
            captions.append({
                "text": "Amazing experience ✨",
                "clip_index": num_clips - 1,
                "position": "center"
            })

        return json.dumps(captions)

    def _parse_captions(self, response: str, num_clips: int,
                       clip_durations: List[float]) -> List[Dict]:
        """
        Parse LLM response into structured caption data

        Returns:
            List of dicts with: text, start_time, duration, position
        """
        try:
            # Extract JSON from response (LLM might add extra text)
            json_start = response.find('[')
            json_end = response.rfind(']') + 1

            if json_start == -1 or json_end == 0:
                logger.warning("No JSON found in LLM response, using fallback")
                response = self._generate_fallback_captions("")

            json_str = response[json_start:json_end]
            captions_data = json.loads(json_str)

            # Convert to full caption objects with timing
            captions = []
            cumulative_time = 0

            for i, clip_duration in enumerate(clip_durations):
                # Find caption for this clip
                caption_data = next(
                    (c for c in captions_data if c.get('clip_index') == i),
                    None
                )

                if caption_data:
                    captions.append({
                        'text': caption_data['text'],
                        'start_time': cumulative_time + 0.5,  # Start 0.5s into clip
                        'duration': min(Config.TEXT_DURATION, clip_duration - 1),
                        'position': caption_data.get('position', 'center')
                    })

                cumulative_time += clip_duration

            return captions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response was: {response}")

            # Fallback: create simple captions
            captions = []
            cumulative_time = 0

            for i, duration in enumerate(clip_durations):
                captions.append({
                    'text': f"Moment {i+1}",
                    'start_time': cumulative_time + 0.5,
                    'duration': min(Config.TEXT_DURATION, duration - 1),
                    'position': 'center'
                })
                cumulative_time += duration

            return captions

    def generate_title(self, description: str) -> str:
        """
        Generate a catchy title/hook for the reel

        Args:
            description: User's description

        Returns:
            Short title text
        """
        prompt = f"""Create a catchy 3-5 word title for an Instagram reel about: {description}

The title should be attention-grabbing and include relevant emojis.

Title:"""

        if self.use_ollama:
            response = self._generate_with_ollama(prompt)
        else:
            response = self._generate_with_openai(prompt)

        # Clean up response
        title = response.strip().split('\n')[0]
        return title[:50]  # Limit length

    def test_connection(self) -> bool:
        """
        Test connection to LLM service

        Returns:
            True if connection successful
        """
        if self.use_ollama:
            try:
                response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info("✓ Ollama connection successful")
                    return True
                else:
                    logger.warning(f"Ollama returned status {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                logger.warning(f"Cannot connect to Ollama: {e}")
                return False
        else:
            # Check OpenAI key
            has_key = bool(self.openai_api_key)
            if has_key:
                logger.info("✓ OpenAI API key found")
            else:
                logger.warning("OpenAI API key not found")
            return has_key
