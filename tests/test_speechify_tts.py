"""
Test suite for Speechify TTS implementation.

This module contains comprehensive tests for the Speechify TTS engine to ensure
the migration was successful and all functionality works correctly.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import pytest

# Add the src directory to the path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from open_llm_vtuber.tts.speechify_tts import TTSEngine


class TestSpeechifyTTS(unittest.TestCase):
    """Test cases for Speechify TTS implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_api_key = "test_api_key_12345"
        self.test_voice_id = "scott"
        self.test_model = "simba-english"
        self.test_language = "en-US"
        self.test_audio_format = "mp3"
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_init_success(self, mock_speechify):
        """Test successful initialization of Speechify TTS engine."""
        # Mock the Speechify client
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        # Test initialization with all parameters
        tts_engine = TTSEngine(
            api_key=self.test_api_key,
            voice_id=self.test_voice_id,
            model=self.test_model,
            language=self.test_language,
            audio_format=self.test_audio_format,
            loudness_normalization=True,
            text_normalization=True
        )
        
        # Verify initialization
        self.assertEqual(tts_engine.api_key, self.test_api_key)
        self.assertEqual(tts_engine.voice_id, self.test_voice_id)
        self.assertEqual(tts_engine.model, self.test_model)
        self.assertEqual(tts_engine.language, self.test_language)
        self.assertEqual(tts_engine.audio_format, self.test_audio_format)
        self.assertTrue(tts_engine.loudness_normalization)
        self.assertTrue(tts_engine.text_normalization)
        self.assertEqual(tts_engine.file_extension, self.test_audio_format)
        self.assertIsNotNone(tts_engine.client)

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_init_with_invalid_audio_format(self, mock_speechify):
        """Test initialization with invalid audio format."""
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        # Test with invalid audio format
        tts_engine = TTSEngine(
            api_key=self.test_api_key,
            audio_format="invalid_format"
        )
        
        # Should default to mp3
        self.assertEqual(tts_engine.audio_format, "mp3")
        self.assertEqual(tts_engine.file_extension, "mp3")

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_init_with_invalid_model(self, mock_speechify):
        """Test initialization with invalid model."""
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        # Test with invalid model
        tts_engine = TTSEngine(
            api_key=self.test_api_key,
            model="invalid_model"
        )
        
        # Should default to simba-english
        self.assertEqual(tts_engine.model, "simba-english")

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_init_failure(self, mock_speechify):
        """Test initialization failure."""
        # Mock Speechify to raise an exception
        mock_speechify.side_effect = Exception("API key invalid")
        
        tts_engine = TTSEngine(api_key=self.test_api_key)
        
        # Client should be None on failure
        self.assertIsNone(tts_engine.client)

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_generate_audio_success(self, mock_speechify):
        """Test successful audio generation."""
        # Mock the Speechify client and response
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        # Mock the TTS response
        mock_response = Mock()
        mock_response.audio_data = "dGVzdCBhdWRpbyBkYXRh"  # base64 encoded "test audio data"
        mock_response.billable_characters_count = 10
        
        mock_client.tts.audio.speech.return_value = mock_response
        
        # Create TTS engine
        tts_engine = TTSEngine(api_key=self.test_api_key)
        
        # Test audio generation
        test_text = "Hello, this is a test."
        result = tts_engine.generate_audio(test_text, "test_file")
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith(".mp3"))
        self.assertTrue(os.path.exists(result))
        
        # Verify the API was called correctly
        mock_client.tts.audio.speech.assert_called_once()
        call_args = mock_client.tts.audio.speech.call_args
        self.assertEqual(call_args[1]['input'], test_text)
        self.assertEqual(call_args[1]['voice_id'], "scott")
        self.assertEqual(call_args[1]['model'], "simba-english")

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_generate_audio_with_custom_parameters(self, mock_speechify):
        """Test audio generation with custom parameters."""
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        mock_response = Mock()
        mock_response.audio_data = "dGVzdCBhdWRpbyBkYXRh"
        mock_client.tts.audio.speech.return_value = mock_response
        
        # Create TTS engine with custom parameters
        tts_engine = TTSEngine(
            api_key=self.test_api_key,
            voice_id="custom_voice",
            model="simba-multilingual",
            language="fr-FR",
            audio_format="wav"
        )
        
        # Test audio generation
        test_text = "Bonjour, ceci est un test."
        result = tts_engine.generate_audio(test_text, "test_file")
        
        # Verify the API was called with custom parameters
        call_args = mock_client.tts.audio.speech.call_args
        self.assertEqual(call_args[1]['voice_id'], "custom_voice")
        self.assertEqual(call_args[1]['model'], "simba-multilingual")
        self.assertEqual(call_args[1]['language'], "fr-FR")
        self.assertEqual(call_args[1]['audio_format'], "wav")

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_generate_audio_without_client(self, mock_speechify):
        """Test audio generation when client is not initialized."""
        # Mock Speechify to raise an exception during init
        mock_speechify.side_effect = Exception("API key invalid")
        
        tts_engine = TTSEngine(api_key=self.test_api_key)
        
        # Try to generate audio without a client
        result = tts_engine.generate_audio("Hello world")
        
        # Should return None
        self.assertIsNone(result)

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_generate_audio_with_empty_text(self, mock_speechify):
        """Test audio generation with empty text."""
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        tts_engine = TTSEngine(api_key=self.test_api_key)
        
        # Test with empty text
        result = tts_engine.generate_audio("")
        self.assertIsNone(result)
        
        # Test with whitespace-only text
        result = tts_engine.generate_audio("   ")
        self.assertIsNone(result)

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_generate_audio_with_non_string_text(self, mock_speechify):
        """Test audio generation with non-string text."""
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        tts_engine = TTSEngine(api_key=self.test_api_key)
        
        # Test with non-string text
        result = tts_engine.generate_audio(123)
        self.assertIsNone(result)
        
        result = tts_engine.generate_audio(None)
        self.assertIsNone(result)

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_generate_audio_api_error(self, mock_speechify):
        """Test audio generation when API call fails."""
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        # Mock API call to raise an exception
        mock_client.tts.audio.speech.side_effect = Exception("API error")
        
        tts_engine = TTSEngine(api_key=self.test_api_key)
        
        # Try to generate audio
        result = tts_engine.generate_audio("Hello world")
        
        # Should return None on error
        self.assertIsNone(result)

    def test_filter_voice_models(self):
        """Test the filter_voice_models method."""
        # Create mock voice objects
        mock_voice1 = Mock()
        mock_voice1.gender = "male"
        mock_voice1.tags = ["timbre:deep", "accent:american"]
        mock_model1 = Mock()
        mock_model1.name = "model1"
        mock_lang1 = Mock()
        mock_lang1.locale = "en-US"
        mock_model1.languages = [mock_lang1]
        mock_voice1.models = [mock_model1]
        
        mock_voice2 = Mock()
        mock_voice2.gender = "female"
        mock_voice2.tags = ["timbre:bright"]
        mock_model2 = Mock()
        mock_model2.name = "model2"
        mock_lang2 = Mock()
        mock_lang2.locale = "fr-FR"
        mock_model2.languages = [mock_lang2]
        mock_voice2.models = [mock_model2]
        
        voices = [mock_voice1, mock_voice2]
        
        # Test filtering by gender
        tts_engine = TTSEngine(api_key=self.test_api_key)
        male_voices = tts_engine.filter_voice_models(voices, gender="male")
        self.assertEqual(male_voices, ["model1"])
        
        # Test filtering by locale
        en_voices = tts_engine.filter_voice_models(voices, locale="en-US")
        self.assertEqual(en_voices, ["model1"])
        
        # Test filtering by tags
        deep_voices = tts_engine.filter_voice_models(voices, tags=["timbre:deep"])
        self.assertEqual(deep_voices, ["model1"])
        
        # Test filtering by multiple criteria
        filtered_voices = tts_engine.filter_voice_models(
            voices, gender="male", locale="en-US", tags=["timbre:deep"]
        )
        self.assertEqual(filtered_voices, ["model1"])

    def test_generate_cache_file_name(self):
        """Test the generate_cache_file_name method."""
        tts_engine = TTSEngine(api_key=self.test_api_key)
        
        # Test with custom filename
        result = tts_engine.generate_cache_file_name("test_file", "wav")
        self.assertTrue(result.endswith("test_file.wav"))
        
        # Test with None filename (should use default)
        result = tts_engine.generate_cache_file_name(None, "mp3")
        self.assertTrue(result.endswith("temp.mp3"))

    def test_remove_file(self):
        """Test the remove_file method."""
        tts_engine = TTSEngine(api_key=self.test_api_key)
        
        # Create a temporary file
        temp_file = os.path.join(self.temp_dir, "test_remove.txt")
        with open(temp_file, 'w') as f:
            f.write("test content")
        
        # Test removing existing file
        self.assertTrue(os.path.exists(temp_file))
        tts_engine.remove_file(temp_file)
        self.assertFalse(os.path.exists(temp_file))
        
        # Test removing non-existent file (should not raise exception)
        tts_engine.remove_file("non_existent_file.txt")

    @patch('open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_async_generate_audio(self, mock_speechify):
        """Test the async_generate_audio method."""
        import asyncio
        
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        mock_response = Mock()
        mock_response.audio_data = "dGVzdCBhdWRpbyBkYXRh"
        mock_client.tts.audio.speech.return_value = mock_response
        
        tts_engine = TTSEngine(api_key=self.test_api_key)
        
        async def test_async():
            result = await tts_engine.async_generate_audio("Hello world", "test_async")
            return result
        
        # Run the async test
        result = asyncio.run(test_async())
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith(".mp3"))


class TestSpeechifyTTSIntegration(unittest.TestCase):
    """Integration tests for Speechify TTS (requires real API key)."""
    
    @pytest.mark.integration
    def test_real_api_integration(self):
        """Test integration with real Speechify API (requires API key)."""
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key:
            self.skipTest("SPEECHIFY_API_KEY environment variable not set")
        
        # Test with real API
        tts_engine = TTSEngine(
            api_key=api_key,
            voice_id="scott",
            model="simba-english",
            language="en-US"
        )
        
        # Test basic audio generation
        result = tts_engine.generate_audio("Hello, this is a test of Speechify TTS.")
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".mp3"))
        
        # Clean up
        if os.path.exists(result):
            os.remove(result)


if __name__ == "__main__":
    # Run tests
    unittest.main() 