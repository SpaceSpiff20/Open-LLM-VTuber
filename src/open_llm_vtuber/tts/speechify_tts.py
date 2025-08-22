import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger
from speechify import Speechify
from speechify.tts import GetSpeechOptionsRequest
import base64

from .tts_interface import TTSInterface

# Add the current directory to sys.path for relative imports if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


class TTSEngine(TTSInterface):
    """
    Uses Speechify's TTS API to generate speech.
    
    Speechify is a cloud-based text-to-speech service that supports multiple languages
    and voices. This implementation provides access to Speechify's high-quality TTS
    capabilities with support for various audio formats and voice options.
    
    API Reference: https://console.sws.speechify.com/signup
    """

    def __init__(
        self,
        api_key: str,
        voice_id: str = "scott",
        model: str = "simba-english",
        language: Optional[str] = None,
        audio_format: str = "mp3",
        loudness_normalization: bool = True,
        text_normalization: bool = True,
        **kwargs,
    ):
        """
        Initialize the Speechify TTS engine.

        Args:
            api_key (str): The Speechify API key for authentication.
            voice_id (str, optional): The voice ID to use for synthesis. Defaults to "scott".
            model (str, optional): The TTS model to use. Must be "simba-english" or "simba-multilingual". 
                                 Defaults to "simba-english".
            language (str, optional): The language of the input text (e.g., "en-US", "fr-FR"). 
                                    If None, Speechify will auto-detect. Defaults to None.
            audio_format (str, optional): The audio format. Must be one of "aac", "mp3", "ogg", "wav". 
                                        Defaults to "mp3".
            loudness_normalization (bool, optional): Whether to apply loudness normalization. 
                                                   Defaults to True.
            text_normalization (bool, optional): Whether to apply text normalization. 
                                               Defaults to True.
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model
        self.language = language
        self.audio_format = audio_format.lower()
        self.loudness_normalization = loudness_normalization
        self.text_normalization = text_normalization
        
        # Validate audio format
        if self.audio_format not in ["aac", "mp3", "ogg", "wav"]:
            logger.warning(
                f"Unsupported audio format '{self.audio_format}' for Speechify TTS. Defaulting to 'mp3'."
            )
            self.audio_format = "mp3"
        
        # Validate model
        if self.model not in ["simba-english", "simba-multilingual"]:
            logger.warning(
                f"Unsupported model '{self.model}' for Speechify TTS. Defaulting to 'simba-english'."
            )
            self.model = "simba-english"
        
        # Set file extension based on audio format
        self.file_extension = self.audio_format
        self.new_audio_dir = "cache"
        self.temp_audio_file = "temp_speechify"

        if not os.path.exists(self.new_audio_dir):
            os.makedirs(self.new_audio_dir)

        try:
            # Initialize Speechify client
            self.client = Speechify(token=api_key, **kwargs)
            logger.info("Speechify TTS Engine initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize Speechify client: {e}")
            self.client = None

    def generate_audio(self, text: str, file_name_no_ext: Optional[str] = None) -> Optional[str]:
        """
        Generate speech audio file using Speechify TTS.

        Args:
            text (str): The text to synthesize.
            file_name_no_ext (str, optional): Name of the file without extension. 
                                            Defaults to a generated name.

        Returns:
            str: The path to the generated audio file, or None if generation failed.
        """
        if not self.client:
            logger.error("Speechify client not initialized. Cannot generate audio.")
            return None

        # Validate input text
        if not isinstance(text, str):
            logger.warning("Speechify TTS: The text cannot be non-string.")
            logger.warning(f"Received type: {type(text)} and value: {text}")
            return None
        
        text = text.strip()
        if not text:
            logger.warning("Speechify TTS: There is no text to speak.")
            return None

        # Generate file path
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)
        speech_file_path = Path(file_name)

        try:
            logger.debug(
                f"Generating audio via Speechify for text: '{text[:50]}...' "
                f"with voice '{self.voice_id}' model '{self.model}'"
            )
            
            # Create options for the TTS request
            options = GetSpeechOptionsRequest(
                loudness_normalization=self.loudness_normalization,
                text_normalization=self.text_normalization,
            )
            
            # Make the TTS request
            audio_response = self.client.tts.audio.speech(
                audio_format=self.audio_format,
                input=text,
                language=self.language,
                model=self.model,
                options=options,
                voice_id=self.voice_id,
            )
            
            # Decode the base64 audio data and write to file
            audio_bytes = base64.b64decode(audio_response.audio_data)
            
            with open(speech_file_path, "wb") as f:
                f.write(audio_bytes)

            logger.info(
                f"Successfully generated audio file via Speechify: {speech_file_path}"
            )
            
            # Log billing information if available
            if hasattr(audio_response, 'billable_characters_count'):
                logger.debug(
                    f"Billable characters: {audio_response.billable_characters_count}"
                )

        except Exception as e:
            logger.critical(f"Error: Speechify TTS unable to generate audio: {e}")
            # Clean up potentially incomplete file
            if speech_file_path.exists():
                try:
                    os.remove(speech_file_path)
                except OSError as rm_err:
                    logger.error(
                        f"Could not remove incomplete file {speech_file_path}: {rm_err}"
                    )
            return None

        return str(speech_file_path)

    def filter_voice_models(self, voices, *, gender=None, locale=None, tags=None):
        """
        Filter Speechify voices by gender, locale, and/or tags,
        and return the list of model IDs for matching voices.

        Args:
            voices (list): List of GetVoice objects.
            gender (str, optional): e.g. 'male', 'female'.
            locale (str, optional): e.g. 'en-US'.
            tags (list, optional): list of tags, e.g. ['timbre:deep'].

        Returns:
            list[str]: IDs of matching voice models.
        """
        results = []

        for voice in voices:
            # gender filter
            if gender and voice.gender.lower() != gender.lower():
                continue

            # locale filter (check across models and languages)
            if locale:
                if not any(
                    any(lang.locale == locale for lang in model.languages)
                    for model in voice.models
                ):
                    continue

            # tags filter
            if tags:
                if not all(tag in voice.tags for tag in tags):
                    continue

            # If we got here, the voice matches -> collect model ids
            for model in voice.models:
                results.append(model.name)

        return results


# Example usage (optional, for testing)
# if __name__ == '__main__':
#     # Configure TTSEngine with your Speechify API key
#     tts_engine = TTSEngine(
#         api_key="YOUR_SPEECHIFY_API_KEY",
#         voice_id="scott",
#         model="simba-english",
#         language="en-US"
#     )
#     test_text = "Hello world! This is a test using Speechify TTS."
#     audio_path = tts_engine.generate_audio(test_text, "speechify_test")
#     if audio_path:
#         print(f"Generated audio saved to: {audio_path}")
#     else:
#         print("Failed to generate audio.") 