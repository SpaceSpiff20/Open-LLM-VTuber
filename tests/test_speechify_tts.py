"""
Test suite for Speechify TTS implementation.

This module contains comprehensive tests to ensure the Speechify TTS migration
was successful and maintains backwards compatibility.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import pytest

# Import the TTS engine
from src.open_llm_vtuber.tts.speechify_tts import TTSEngine


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
        self.original_cache_dir = "cache"
        
        # Mock the cache directory
        with patch('src.open_llm_vtuber.tts.speechify_tts.os.path.exists', return_value=True):
            with patch('src.open_llm_vtuber.tts.speechify_tts.os.makedirs'):
                self.tts_engine = TTSEngine(
                    api_key=self.test_api_key,
                    voice_id=self.test_voice_id,
                    model=self.test_model,
                    language=self.test_language,
                    audio_format=self.test_audio_format
                )

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test TTS engine initialization."""
        # Test with valid parameters
        tts = TTSEngine(
            api_key=self.test_api_key,
            voice_id=self.test_voice_id,
            model=self.test_model
        )
        
        self.assertEqual(tts.api_key, self.test_api_key)
        self.assertEqual(tts.voice_id, self.test_voice_id)
        self.assertEqual(tts.model, self.test_model)
        self.assertEqual(tts.audio_format, "mp3")  # Default format
        self.assertTrue(tts.loudness_normalization)
        self.assertTrue(tts.text_normalization)

    def test_initialization_with_invalid_audio_format(self):
        """Test initialization with invalid audio format."""
        with patch('src.open_llm_vtuber.tts.speechify_tts.logger.warning') as mock_warning:
            tts = TTSEngine(
                api_key=self.test_api_key,
                audio_format="invalid_format"
            )
            
            # Should default to mp3
            self.assertEqual(tts.audio_format, "mp3")
            mock_warning.assert_called_once()

    def test_initialization_with_invalid_model(self):
        """Test initialization with invalid model."""
        with patch('src.open_llm_vtuber.tts.speechify_tts.logger.warning') as mock_warning:
            tts = TTSEngine(
                api_key=self.test_api_key,
                model="invalid_model"
            )
            
            # Should default to simba-english
            self.assertEqual(tts.model, "simba-english")
            mock_warning.assert_called_once()

    def test_initialization_with_client_failure(self):
        """Test initialization when Speechify client fails."""
        with patch('src.open_llm_vtuber.tts.speechify_tts.Speechify', side_effect=Exception("Connection failed")):
            with patch('src.open_llm_vtuber.tts.speechify_tts.logger.critical') as mock_critical:
                tts = TTSEngine(api_key=self.test_api_key)
                
                self.assertIsNone(tts.client)
                mock_critical.assert_called_once()

    @patch('src.open_llm_vtuber.tts.speechify_tts.Speechify')
    @patch('src.open_llm_vtuber.tts.speechify_tts.GetSpeechOptionsRequest')
    @patch('src.open_llm_vtuber.tts.speechify_tts.base64.b64decode')
    def test_generate_audio_success(self, mock_b64decode, mock_options, mock_speechify):
        """Test successful audio generation."""
        # Mock the Speechify client
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        # Mock the TTS response
        mock_response = Mock()
        mock_response.audio_data = "base64_encoded_audio_data"
        mock_client.tts.audio.speech.return_value = mock_response
        
        # Mock base64 decode
        mock_b64decode.return_value = b"fake_audio_data"
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            with patch('src.open_llm_vtuber.tts.speechify_tts.Path') as mock_path:
                mock_path_instance = Mock()
                mock_path.return_value = mock_path_instance
                mock_path_instance.exists.return_value = False
                
                # Test audio generation
                result = self.tts_engine.generate_audio("Hello, world!")
                
                # Verify the result
                self.assertIsNotNone(result)
                
                # Verify Speechify client was called correctly
                mock_client.tts.audio.speech.assert_called_once()
                call_args = mock_client.tts.audio.speech.call_args
                
                self.assertEqual(call_args[1]['audio_format'], self.test_audio_format)
                self.assertEqual(call_args[1]['input'], "Hello, world!")
                self.assertEqual(call_args[1]['language'], self.test_language)
                self.assertEqual(call_args[1]['model'], self.test_model)
                self.assertEqual(call_args[1]['voice_id'], self.test_voice_id)

    def test_generate_audio_without_client(self):
        """Test audio generation when client is not initialized."""
        self.tts_engine.client = None
        
        with patch('src.open_llm_vtuber.tts.speechify_tts.logger.error') as mock_error:
            result = self.tts_engine.generate_audio("Hello, world!")
            
            self.assertIsNone(result)
            mock_error.assert_called_once()

    @patch('src.open_llm_vtuber.tts.speechify_tts.Speechify')
    def test_generate_audio_with_api_error(self, mock_speechify):
        """Test audio generation when API call fails."""
        # Mock the Speechify client to raise an exception
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        mock_client.tts.audio.speech.side_effect = Exception("API Error")
        
        with patch('src.open_llm_vtuber.tts.speechify_tts.logger.critical') as mock_critical:
            with patch('src.open_llm_vtuber.tts.speechify_tts.Path') as mock_path:
                mock_path_instance = Mock()
                mock_path.return_value = mock_path_instance
                mock_path_instance.exists.return_value = False
                
                result = self.tts_engine.generate_audio("Hello, world!")
                
                self.assertIsNone(result)
                mock_critical.assert_called_once()

    def test_filter_voice_models(self):
        """Test voice model filtering functionality."""
        # Create mock voice objects
        mock_voice1 = Mock()
        mock_voice1.gender = "male"
        mock_voice1.tags = ["timbre:deep", "accent:american"]
        mock_model1 = Mock()
        mock_model1.name = "voice_model_1"
        mock_lang1 = Mock()
        mock_lang1.locale = "en-US"
        mock_model1.languages = [mock_lang1]
        mock_voice1.models = [mock_model1]
        
        mock_voice2 = Mock()
        mock_voice2.gender = "female"
        mock_voice2.tags = ["timbre:bright"]
        mock_model2 = Mock()
        mock_model2.name = "voice_model_2"
        mock_lang2 = Mock()
        mock_lang2.locale = "fr-FR"
        mock_model2.languages = [mock_lang2]
        mock_voice2.models = [mock_model2]
        
        voices = [mock_voice1, mock_voice2]
        
        # Test filtering by gender
        male_voices = self.tts_engine.filter_voice_models(voices, gender="male")
        self.assertEqual(len(male_voices), 1)
        self.assertEqual(male_voices[0], "voice_model_1")
        
        # Test filtering by locale
        en_voices = self.tts_engine.filter_voice_models(voices, locale="en-US")
        self.assertEqual(len(en_voices), 1)
        self.assertEqual(en_voices[0], "voice_model_1")
        
        # Test filtering by tags
        deep_voices = self.tts_engine.filter_voice_models(voices, tags=["timbre:deep"])
        self.assertEqual(len(deep_voices), 1)
        self.assertEqual(deep_voices[0], "voice_model_1")
        
        # Test filtering by multiple criteria
        male_en_voices = self.tts_engine.filter_voice_models(
            voices, gender="male", locale="en-US"
        )
        self.assertEqual(len(male_en_voices), 1)
        self.assertEqual(male_en_voices[0], "voice_model_1")

    def test_generate_cache_file_name(self):
        """Test cache file name generation."""
        # Test with custom file name
        file_name = self.tts_engine.generate_cache_file_name("test_audio", "mp3")
        self.assertIn("test_audio.mp3", file_name)
        self.assertIn("cache", file_name)
        
        # Test with None file name (should use default)
        file_name = self.tts_engine.generate_cache_file_name(None, "wav")
        self.assertIn("temp.wav", file_name)
        self.assertIn("cache", file_name)

    def test_remove_file(self):
        """Test file removal functionality."""
        # Create a temporary file
        temp_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(temp_file, 'w') as f:
            f.write("test content")
        
        # Test removing existing file
        self.tts_engine.remove_file(temp_file)
        self.assertFalse(os.path.exists(temp_file))
        
        # Test removing non-existent file
        with patch('src.open_llm_vtuber.tts.speechify_tts.logger.warning') as mock_warning:
            self.tts_engine.remove_file("non_existent_file.txt")
            mock_warning.assert_called_once()

    def test_async_generate_audio(self):
        """Test async audio generation."""
        import asyncio
        
        # Mock the synchronous generate_audio method
        with patch.object(self.tts_engine, 'generate_audio', return_value="test_audio.mp3"):
            async def test_async():
                result = await self.tts_engine.async_generate_audio("Hello, world!")
                return result
            
            # Run the async test
            result = asyncio.run(test_async())
            self.assertEqual(result, "test_audio.mp3")


class TestSpeechifyTTSIntegration(unittest.TestCase):
    """Integration tests for Speechify TTS with the factory pattern."""

    def test_factory_integration(self):
        """Test that Speechify TTS can be created through the factory."""
        from src.open_llm_vtuber.tts.tts_factory import TTSFactory
        
        # Test factory creation
        tts_engine = TTSFactory.get_tts_engine(
            "speechify_tts",
            api_key="test_key",
            voice_id="scott",
            model="simba-english",
            language="en-US",
            audio_format="mp3"
        )
        
        self.assertIsInstance(tts_engine, TTSEngine)
        self.assertEqual(tts_engine.api_key, "test_key")
        self.assertEqual(tts_engine.voice_id, "scott")
        self.assertEqual(tts_engine.model, "simba-english")
        self.assertEqual(tts_engine.language, "en-US")
        self.assertEqual(tts_engine.audio_format, "mp3")

    def test_factory_with_defaults(self):
        """Test factory creation with default parameters."""
        from src.open_llm_vtuber.tts.tts_factory import TTSFactory
        
        tts_engine = TTSFactory.get_tts_engine(
            "speechify_tts",
            api_key="test_key"
        )
        
        self.assertIsInstance(tts_engine, TTSEngine)
        self.assertEqual(tts_engine.voice_id, "scott")  # Default
        self.assertEqual(tts_engine.model, "simba-english")  # Default
        self.assertEqual(tts_engine.audio_format, "mp3")  # Default
        self.assertTrue(tts_engine.loudness_normalization)  # Default
        self.assertTrue(tts_engine.text_normalization)  # Default


class TestSpeechifyTTSConfiguration(unittest.TestCase):
    """Test configuration validation for Speechify TTS."""

    def test_valid_configuration(self):
        """Test valid configuration parameters."""
        from src.open_llm_vtuber.config_manager.tts import SpeechifyTTSConfig
        
        config = SpeechifyTTSConfig(
            api_key="test_key",
            voice_id="scott",
            model="simba-english",
            language="en-US",
            audio_format="mp3",
            loudness_normalization=True,
            text_normalization=True
        )
        
        self.assertEqual(config.api_key, "test_key")
        self.assertEqual(config.voice_id, "scott")
        self.assertEqual(config.model, "simba-english")
        self.assertEqual(config.language, "en-US")
        self.assertEqual(config.audio_format, "mp3")
        self.assertTrue(config.loudness_normalization)
        self.assertTrue(config.text_normalization)

    def test_configuration_with_defaults(self):
        """Test configuration with default values."""
        from src.open_llm_vtuber.config_manager.tts import SpeechifyTTSConfig
        
        config = SpeechifyTTSConfig(api_key="test_key")
        
        self.assertEqual(config.voice_id, "scott")  # Default
        self.assertEqual(config.model, "simba-english")  # Default
        self.assertIsNone(config.language)  # Default
        self.assertEqual(config.audio_format, "mp3")  # Default
        self.assertTrue(config.loudness_normalization)  # Default
        self.assertTrue(config.text_normalization)  # Default

    def test_invalid_model_configuration(self):
        """Test configuration with invalid model."""
        from src.open_llm_vtuber.config_manager.tts import SpeechifyTTSConfig
        from pydantic import ValidationError
        
        with self.assertRaises(ValidationError):
            SpeechifyTTSConfig(
                api_key="test_key",
                model="invalid_model"
            )

    def test_invalid_audio_format_configuration(self):
        """Test configuration with invalid audio format."""
        from src.open_llm_vtuber.config_manager.tts import SpeechifyTTSConfig
        from pydantic import ValidationError
        
        with self.assertRaises(ValidationError):
            SpeechifyTTSConfig(
                api_key="test_key",
                audio_format="invalid_format"
            )


if __name__ == '__main__':
    unittest.main() 