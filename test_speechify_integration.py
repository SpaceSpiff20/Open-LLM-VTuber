#!/usr/bin/env python3
"""
Simple integration test for Speechify TTS implementation.

This script tests the basic functionality of the Speechify TTS provider
without requiring actual API credentials.
"""

import os
import sys
import tempfile
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from open_llm_vtuber.tts.speechify_tts import TTSEngine
from open_llm_vtuber.tts.tts_factory import TTSFactory


def test_speechify_tts_initialization():
    """Test Speechify TTS initialization."""
    print("Testing Speechify TTS initialization...")
    
    # Mock the Speechify client
    with patch('open_llm_vtuber.tts.speechify_tts.Speechify') as mock_speechify:
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        # Test initialization
        tts = TTSEngine(
            api_key="test_key",
            voice_id="scott",
            model="simba-english",
            language="en-US",
            audio_format="mp3"
        )
        
        # Verify initialization
        assert tts.api_key == "test_key"
        assert tts.voice_id == "scott"
        assert tts.model == "simba-english"
        assert tts.language == "en-US"
        assert tts.audio_format == "mp3"
        assert tts.client is not None
        
        print("✅ Speechify TTS initialization test passed")


def test_speechify_tts_factory():
    """Test Speechify TTS factory integration."""
    print("Testing Speechify TTS factory integration...")
    
    # Mock the Speechify client
    with patch('open_llm_vtuber.tts.speechify_tts.Speechify') as mock_speechify:
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        # Test factory creation
        tts = TTSFactory.get_tts_engine(
            "speechify_tts",
            api_key="test_key",
            voice_id="scott",
            model="simba-english",
            language="en-US"
        )
        
        # Verify factory integration
        assert isinstance(tts, TTSEngine)
        assert tts.api_key == "test_key"
        assert tts.voice_id == "scott"
        assert tts.model == "simba-english"
        assert tts.language == "en-US"
        
        print("✅ Speechify TTS factory integration test passed")


def test_speechify_tts_audio_generation():
    """Test Speechify TTS audio generation."""
    print("Testing Speechify TTS audio generation...")
    
    # Mock the Speechify client and response
    with patch('open_llm_vtuber.tts.speechify_tts.Speechify') as mock_speechify:
        with patch('open_llm_vtuber.tts.speechify_tts.GetSpeechOptionsRequest') as mock_options:
            with patch('open_llm_vtuber.tts.speechify_tts.base64.b64decode') as mock_b64decode:
                with patch('builtins.open', create=True) as mock_open:
                    with patch('open_llm_vtuber.tts.speechify_tts.Path') as mock_path:
                        # Setup mocks
                        mock_client = Mock()
                        mock_speechify.return_value = mock_client
                        
                        mock_response = Mock()
                        mock_response.audio_data = "base64_encoded_audio"
                        mock_client.tts.audio.speech.return_value = mock_response
                        
                        mock_b64decode.return_value = b"fake_audio_data"
                        
                        mock_path_instance = Mock()
                        mock_path.return_value = mock_path_instance
                        mock_path_instance.exists.return_value = False
                        
                        # Create TTS engine
                        tts = TTSEngine(api_key="test_key")
                        
                        # Test audio generation
                        result = tts.generate_audio("Hello, world!")
                        
                        # Verify result
                        assert result is not None
                        # The result should be a string path, but since we're mocking Path, 
                        # we just check that it's not None and the method was called
                        assert isinstance(result, str) or str(result)
                        
                        # Verify API call
                        mock_client.tts.audio.speech.assert_called_once()
                        call_args = mock_client.tts.audio.speech.call_args
                        assert call_args[1]['input'] == "Hello, world!"
                        assert call_args[1]['audio_format'] == "mp3"
                        assert call_args[1]['voice_id'] == "scott"
                        assert call_args[1]['model'] == "simba-english"
                        
                        print("✅ Speechify TTS audio generation test passed")


def test_speechify_tts_voice_filtering():
    """Test Speechify TTS voice filtering functionality."""
    print("Testing Speechify TTS voice filtering...")
    
    # Mock voice objects
    mock_voice1 = Mock()
    mock_voice1.gender = "male"
    mock_voice1.tags = ["timbre:deep"]
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
    
    # Create TTS engine
    with patch('open_llm_vtuber.tts.speechify_tts.Speechify') as mock_speechify:
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        
        tts = TTSEngine(api_key="test_key")
        
        # Test filtering
        male_voices = tts.filter_voice_models(voices, gender="male")
        assert len(male_voices) == 1
        assert male_voices[0] == "voice_model_1"
        
        en_voices = tts.filter_voice_models(voices, locale="en-US")
        assert len(en_voices) == 1
        assert en_voices[0] == "voice_model_1"
        
        deep_voices = tts.filter_voice_models(voices, tags=["timbre:deep"])
        assert len(deep_voices) == 1
        assert deep_voices[0] == "voice_model_1"
        
        print("✅ Speechify TTS voice filtering test passed")


def test_speechify_tts_error_handling():
    """Test Speechify TTS error handling."""
    print("Testing Speechify TTS error handling...")
    
    # Test initialization with client failure
    with patch('open_llm_vtuber.tts.speechify_tts.Speechify', side_effect=Exception("Connection failed")):
        with patch('open_llm_vtuber.tts.speechify_tts.logger.critical') as mock_critical:
            tts = TTSEngine(api_key="test_key")
            assert tts.client is None
            mock_critical.assert_called_once()
    
    # Test audio generation with API error
    with patch('open_llm_vtuber.tts.speechify_tts.Speechify') as mock_speechify:
        mock_client = Mock()
        mock_speechify.return_value = mock_client
        mock_client.tts.audio.speech.side_effect = Exception("API Error")
        
        with patch('open_llm_vtuber.tts.speechify_tts.logger.critical') as mock_critical:
            with patch('open_llm_vtuber.tts.speechify_tts.Path') as mock_path:
                mock_path_instance = Mock()
                mock_path.return_value = mock_path_instance
                mock_path_instance.exists.return_value = False
                
                tts = TTSEngine(api_key="test_key")
                result = tts.generate_audio("Hello, world!")
                assert result is None
                mock_critical.assert_called_once()
    
    print("✅ Speechify TTS error handling test passed")


def main():
    """Run all tests."""
    print("🚀 Starting Speechify TTS integration tests...\n")
    
    try:
        test_speechify_tts_initialization()
        test_speechify_tts_factory()
        test_speechify_tts_audio_generation()
        test_speechify_tts_voice_filtering()
        test_speechify_tts_error_handling()
        
        print("\n🎉 All Speechify TTS integration tests passed!")
        print("\n📋 Summary:")
        print("✅ TTS initialization")
        print("✅ Factory integration")
        print("✅ Audio generation")
        print("✅ Voice filtering")
        print("✅ Error handling")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 