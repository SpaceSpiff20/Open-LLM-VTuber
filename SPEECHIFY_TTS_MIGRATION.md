# Speechify TTS Migration Documentation

This document describes the migration of the Open-LLM-VTuber project to support Speechify's TTS API as a new text-to-speech provider.

## Overview

The Speechify TTS provider has been successfully integrated into the Open-LLM-VTuber project, providing users with access to high-quality, multilingual text-to-speech capabilities through Speechify's cloud-based API.

## Features

### ✅ Fully Supported Languages
- **English** (`en`)
- **French** (`fr-FR`)
- **German** (`de-DE`)
- **Spanish** (`es-ES`)
- **Portuguese (Brazil)** (`pt-BR`)
- **Portuguese (Portugal)** (`pt-PT`)

### 🧪 Beta Languages
- **Arabic** (`ar-AE`)
- **Danish** (`da-DK`)
- **Dutch** (`nl-NL`)
- **Estonian** (`et-EE`)
- **Finnish** (`fi-FI`)
- **Greek** (`el-GR`)
- **Hebrew** (`he-IL`)
- **Hindi** (`hi-IN`)
- **Italian** (`it-IT`)
- **Japanese** (`ja-JP`)
- **Norwegian** (`nb-NO`)
- **Polish** (`pl-PL`)
- **Russian** (`ru-RU`)
- **Swedish** (`sv-SE`)
- **Turkish** (`tr-TR`)
- **Ukrainian** (`uk-UA`)
- **Vietnamese** (`vi-VN`)

## Installation

### 1. Install the Speechify API Package

```bash
# Using uv (recommended)
uv add speechify-api

# Using pip
pip install speechify-api
```

### 2. Get Your API Key

1. Visit [Speechify Console](https://console.sws.speechify.com/signup)
2. Sign up for an account
3. Generate an API key from your dashboard

## Configuration

### Basic Configuration

Add the following to your `conf.yaml` file:

```yaml
tts_config:
  tts_model: 'speechify_tts'
  
  speechify_tts:
    api_key: 'your_speechify_api_key_here'
    voice_id: 'scott'  # Default voice ID
    model: 'simba-english'  # or 'simba-multilingual'
    language: 'en-US'  # Optional: auto-detection if not specified
    audio_format: 'mp3'  # Options: 'aac', 'mp3', 'ogg', 'wav'
    loudness_normalization: true
    text_normalization: true
```

### Advanced Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | string | **Required** | Your Speechify API key |
| `voice_id` | string | `"scott"` | Voice ID for synthesis |
| `model` | string | `"simba-english"` | TTS model (`"simba-english"` or `"simba-multilingual"`) |
| `language` | string | `null` | Language code (e.g., `"en-US"`). If `null`, auto-detection is used |
| `audio_format` | string | `"mp3"` | Audio format (`"aac"`, `"mp3"`, `"ogg"`, `"wav"`) |
| `loudness_normalization` | boolean | `true` | Enable loudness normalization |
| `text_normalization` | boolean | `true` | Enable text normalization |

### Language Configuration

#### When to Specify Language
- **Known single language**: If you know the input text is entirely in one language, providing the `language` parameter will result in better audio quality.
- **Unknown or mixed language**: If you're unsure of the input language or the text contains multiple languages, omit the `language` parameter. Speechify models will automatically detect and handle the language(s) in the input.

#### Example Language Configurations

```yaml
# English
speechify_tts:
  language: 'en-US'

# Japanese
speechify_tts:
  language: 'ja-JP'

# French
speechify_tts:
  language: 'fr-FR'

# Auto-detection (recommended for multilingual content)
speechify_tts:
  language: null
```

## Usage Examples

### Basic Usage

```python
from open_llm_vtuber.tts.tts_factory import TTSFactory

# Create TTS engine
tts = TTSFactory.get_tts_engine(
    "speechify_tts",
    api_key="your_api_key",
    voice_id="scott",
    model="simba-english",
    language="en-US"
)

# Generate audio
audio_path = tts.generate_audio("Hello, world!")
print(f"Audio generated: {audio_path}")
```

### Voice Filtering

The Speechify TTS implementation includes a utility function for filtering available voices:

```python
from open_llm_vtuber.tts.speechify_tts import TTSEngine

tts = TTSEngine(api_key="your_api_key")

# Get all available voices
voices = tts.client.tts.voices.list()

# Filter by gender
male_voices = tts.filter_voice_models(voices, gender="male")

# Filter by locale
en_voices = tts.filter_voice_models(voices, locale="en-US")

# Filter by tags
deep_voices = tts.filter_voice_models(voices, tags=["timbre:deep"])

# Filter by multiple criteria
male_en_deep = tts.filter_voice_models(
    voices, 
    gender="male", 
    locale="en-US", 
    tags=["timbre:deep"]
)
```

## Migration Notes

### Backwards Compatibility

✅ **Fully Backwards Compatible**: The Speechify TTS implementation maintains full backwards compatibility with the existing TTS interface. All existing TTS providers continue to work without any changes.

### New Features

1. **Multilingual Support**: Speechify provides excellent support for multiple languages with automatic language detection.
2. **Voice Filtering**: Built-in utility for filtering and discovering available voices.
3. **Advanced Audio Options**: Support for multiple audio formats and normalization options.
4. **Cloud-Based**: No local model downloads required, reducing setup complexity.

### Performance Considerations

- **Latency**: Cloud-based API calls may introduce network latency compared to local TTS engines.
- **Rate Limits**: Be aware of Speechify's API rate limits for your subscription tier.
- **Offline Usage**: Speechify TTS requires an internet connection, unlike some local TTS providers.

### Error Handling

The implementation includes comprehensive error handling:

- **API Connection Failures**: Graceful handling of network issues
- **Invalid Parameters**: Validation and fallback to defaults
- **Audio Generation Failures**: Proper cleanup of incomplete files
- **Configuration Errors**: Clear error messages for missing or invalid settings

## Testing

### Running the Test Suite

```bash
# Run the integration test
python test_speechify_integration.py

# Run the comprehensive test suite (if pytest is available)
pytest tests/test_speechify_tts.py -v
```

### Test Coverage

The test suite covers:
- ✅ TTS engine initialization
- ✅ Factory integration
- ✅ Audio generation
- ✅ Voice filtering
- ✅ Error handling
- ✅ Configuration validation

## Troubleshooting

### Common Issues

1. **API Key Issues**
   ```
   Error: Failed to initialize Speechify client
   ```
   **Solution**: Verify your API key is correct and has sufficient credits.

2. **Network Connectivity**
   ```
   Error: Speechify TTS unable to generate audio
   ```
   **Solution**: Check your internet connection and firewall settings.

3. **Invalid Configuration**
   ```
   Error: Unsupported audio format/model
   ```
   **Solution**: Use only supported formats (`aac`, `mp3`, `ogg`, `wav`) and models (`simba-english`, `simba-multilingual`).

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.getLogger('open_llm_vtuber.tts.speechify_tts').setLevel(logging.DEBUG)
```

## API Reference

### SpeechifyTTSConfig

```python
class SpeechifyTTSConfig:
    api_key: str                    # Required: API key for Speechify service
    voice_id: str = "scott"         # Voice ID for synthesis
    model: Literal["simba-english", "simba-multilingual"] = "simba-english"
    language: Optional[str] = None  # Language code (auto-detection if None)
    audio_format: Literal["aac", "mp3", "ogg", "wav"] = "mp3"
    loudness_normalization: bool = True
    text_normalization: bool = True
```

### TTSEngine Methods

```python
class TTSEngine:
    def __init__(self, api_key: str, voice_id: str = "scott", ...)
    def generate_audio(self, text: str, file_name_no_ext: Optional[str] = None) -> str
    def filter_voice_models(self, voices, *, gender=None, locale=None, tags=None) -> list[str]
    async def async_generate_audio(self, text: str, file_name_no_ext=None) -> str
```

## Comparison with Other TTS Providers

| Feature | Speechify | Edge TTS | Azure TTS | Local TTS |
|---------|-----------|----------|-----------|-----------|
| **Multilingual** | ✅ Excellent | ✅ Good | ✅ Good | ❌ Limited |
| **Voice Quality** | ✅ High | ✅ Good | ✅ High | ✅ Variable |
| **Setup Complexity** | ✅ Low | ✅ Low | ⚠️ Medium | ❌ High |
| **Offline Support** | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Cost** | ⚠️ Per API call | ✅ Free | ⚠️ Per API call | ✅ Free |
| **Latency** | ⚠️ Network | ✅ Low | ⚠️ Network | ✅ Very Low |

## Future Enhancements

Potential improvements for future versions:

1. **Caching**: Implement audio caching to reduce API calls
2. **Streaming**: Add support for real-time audio streaming
3. **Voice Cloning**: Integration with Speechify's voice cloning features
4. **Batch Processing**: Support for processing multiple text segments efficiently

## Support

For issues related to:
- **Open-LLM-VTuber Integration**: Check the project's GitHub issues
- **Speechify API**: Contact Speechify support or check their documentation
- **Configuration**: Refer to this documentation and the configuration templates

## License

The Speechify TTS integration follows the same license as the Open-LLM-VTuber project. Please ensure compliance with Speechify's terms of service when using their API. 