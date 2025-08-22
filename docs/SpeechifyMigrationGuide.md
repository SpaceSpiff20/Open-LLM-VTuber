# Speechify TTS Migration Guide

This document provides a comprehensive guide for migrating to and using the Speechify TTS provider in Open-LLM-VTuber.

## Overview

Speechify is a cloud-based text-to-speech service that provides high-quality, natural-sounding speech synthesis. This migration adds Speechify as a new TTS provider option in Open-LLM-VTuber, supporting multiple languages and voice options.

## Features

### ✅ Supported Features
- **Multiple Languages**: Support for 6 fully supported languages and 17 beta languages
- **Voice Selection**: Access to various voice options with filtering capabilities
- **Audio Formats**: Support for AAC, MP3, OGG, and WAV formats
- **Language Auto-Detection**: Automatic language detection when not specified
- **Text Normalization**: Built-in text and loudness normalization
- **Async Support**: Full async/await support for non-blocking operation
- **Error Handling**: Comprehensive error handling and logging
- **Backwards Compatibility**: Fully compatible with existing TTS interface

### 🌍 Supported Languages

#### Fully Supported Languages
| Language              | Code  |
|-----------------------|-------|
| English               | en    |
| French                | fr-FR |
| German                | de-DE |
| Spanish               | es-ES |
| Portuguese (Brazil)   | pt-BR |
| Portuguese (Portugal) | pt-PT |

#### Beta Languages
| Language   | Code  |
|------------|-------|
| Arabic     | ar-AE |
| Danish     | da-DK |
| Dutch      | nl-NL |
| Estonian   | et-EE |
| Finnish    | fi-FI |
| Greek      | el-GR |
| Hebrew     | he-IL |
| Hindi      | hi-IN |
| Italian    | it-IT |
| Japanese   | ja-JP |
| Norwegian  | nb-NO |
| Polish     | pl-PL |
| Russian    | ru-RU |
| Swedish    | sv-SE |
| Turkish    | tr-TR |
| Ukrainian  | uk-UA |
| Vietnamese | vi-VN |

## Installation

### 1. Install Dependencies

The Speechify API dependency has been added to the project. Install it using:

```bash
uv add speechify-api
```

Or if you're using pip:

```bash
pip install speechify-api
```

### 2. Get API Key

1. Sign up for a Speechify account at [https://console.sws.speechify.com/signup](https://console.sws.speechify.com/signup)
2. Generate an API key from your dashboard
3. Copy the API key for configuration

## Configuration

### Basic Configuration

Add the following configuration to your `conf.yaml` file:

```yaml
character_config:
  tts_config:
    tts_model: 'speechify_tts'
    
    speechify_tts:
      api_key: 'YOUR_SPEECHIFY_API_KEY'
      voice_id: 'scott'
      model: 'simba-english'
      language: 'en-US'
      audio_format: 'mp3'
      loudness_normalization: true
      text_normalization: true
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | string | required | Your Speechify API key |
| `voice_id` | string | 'scott' | Voice ID for synthesis |
| `model` | string | 'simba-english' | TTS model ('simba-english' or 'simba-multilingual') |
| `language` | string | null | Language code (e.g., 'en-US', 'fr-FR'). Leave empty for auto-detection |
| `audio_format` | string | 'mp3' | Audio format ('aac', 'mp3', 'ogg', 'wav') |
| `loudness_normalization` | boolean | true | Apply loudness normalization |
| `text_normalization` | boolean | true | Apply text normalization |

### Language Configuration

#### When to Specify Language
- **Known single language**: If you know the input text is entirely in one language, providing the `language` parameter will result in better audio quality.
- **Unknown or mixed language**: If you're unsure of the input language or the text contains multiple languages, omit the `language` parameter. Speechify models will automatically detect and handle the language(s) in the input.

## Usage Examples

### Basic Usage

```python
from open_llm_vtuber.tts.tts_factory import TTSFactory

# Create Speechify TTS engine
tts_engine = TTSFactory.get_tts_engine(
    "speechify_tts",
    api_key="your_api_key",
    voice_id="scott",
    model="simba-english",
    language="en-US"
)

# Generate audio
audio_path = tts_engine.generate_audio("Hello, this is a test!")
```

### Advanced Usage with Custom Parameters

```python
# Create engine with custom parameters
tts_engine = TTSFactory.get_tts_engine(
    "speechify_tts",
    api_key="your_api_key",
    voice_id="custom_voice",
    model="simba-multilingual",
    language="fr-FR",
    audio_format="wav",
    loudness_normalization=False,
    text_normalization=True
)

# Generate audio in French
audio_path = tts_engine.generate_audio("Bonjour, comment allez-vous?")
```

### Async Usage

```python
import asyncio

async def generate_audio_async():
    tts_engine = TTSFactory.get_tts_engine(
        "speechify_tts",
        api_key="your_api_key"
    )
    
    # Generate audio asynchronously
    audio_path = await tts_engine.async_generate_audio("Hello world!")
    return audio_path

# Run async function
audio_path = asyncio.run(generate_audio_async())
```

### Voice Filtering

```python
# Get available voices and filter them
voices = tts_engine.client.tts.voices.list()

# Filter by gender
male_voices = tts_engine.filter_voice_models(voices, gender="male")

# Filter by locale
en_voices = tts_engine.filter_voice_models(voices, locale="en-US")

# Filter by tags
deep_voices = tts_engine.filter_voice_models(voices, tags=["timbre:deep"])

# Filter by multiple criteria
filtered_voices = tts_engine.filter_voice_models(
    voices, 
    gender="male", 
    locale="en-US", 
    tags=["timbre:deep"]
)
```

## API Reference

### TTSEngine Class

#### Constructor

```python
TTSEngine(
    api_key: str,
    voice_id: str = "scott",
    model: str = "simba-english",
    language: Optional[str] = None,
    audio_format: str = "mp3",
    loudness_normalization: bool = True,
    text_normalization: bool = True,
    **kwargs
)
```

#### Methods

##### `generate_audio(text: str, file_name_no_ext: Optional[str] = None) -> Optional[str]`

Generate speech audio from text.

**Parameters:**
- `text` (str): The text to synthesize
- `file_name_no_ext` (str, optional): Name of the file without extension

**Returns:**
- `str`: Path to the generated audio file, or `None` if generation failed

##### `async_generate_audio(text: str, file_name_no_ext: Optional[str] = None) -> str`

Generate speech audio asynchronously.

**Parameters:**
- `text` (str): The text to synthesize
- `file_name_no_ext` (str, optional): Name of the file without extension

**Returns:**
- `str`: Path to the generated audio file

##### `filter_voice_models(voices, *, gender=None, locale=None, tags=None) -> list[str]`

Filter available voices by criteria.

**Parameters:**
- `voices` (list): List of GetVoice objects
- `gender` (str, optional): Gender filter ('male', 'female')
- `locale` (str, optional): Locale filter (e.g., 'en-US')
- `tags` (list, optional): Tags filter (e.g., ['timbre:deep'])

**Returns:**
- `list[str]`: IDs of matching voice models

## Testing

### Running Tests

The migration includes a comprehensive test suite. Run the tests using:

```bash
cd tests
python run_speechify_tests.py
```

### Test Categories

1. **Unit Tests**: Test individual components and methods
2. **Integration Tests**: Test with real API (requires API key)
3. **Configuration Tests**: Validate configuration structure
4. **Factory Tests**: Test TTS factory integration
5. **Code Quality Tests**: Check formatting and linting

### Setting Up Integration Tests

To run integration tests with the real API:

```bash
export SPEECHIFY_API_KEY="your_api_key"
python run_speechify_tests.py
```

## Migration from Other TTS Providers

### From OpenAI TTS

```yaml
# Before (OpenAI TTS)
openai_tts:
  model: 'tts-1'
  voice: 'alloy'
  api_key: 'your_openai_key'
  base_url: 'https://api.openai.com/v1'

# After (Speechify TTS)
speechify_tts:
  api_key: 'your_speechify_key'
  voice_id: 'scott'
  model: 'simba-english'
  language: 'en-US'
```

### From Azure TTS

```yaml
# Before (Azure TTS)
azure_tts:
  api_key: 'your_azure_key'
  region: 'eastus'
  voice: 'en-US-AshleyNeural'

# After (Speechify TTS)
speechify_tts:
  api_key: 'your_speechify_key'
  voice_id: 'scott'
  model: 'simba-english'
  language: 'en-US'
```

## Troubleshooting

### Common Issues

#### 1. API Key Invalid
```
Error: Failed to initialize Speechify client: API key invalid
```
**Solution**: Verify your API key is correct and has the necessary permissions.

#### 2. Unsupported Audio Format
```
Warning: Unsupported audio format 'flac' for Speechify TTS. Defaulting to 'mp3'.
```
**Solution**: Use one of the supported formats: 'aac', 'mp3', 'ogg', 'wav'.

#### 3. Unsupported Model
```
Warning: Unsupported model 'invalid-model' for Speechify TTS. Defaulting to 'simba-english'.
```
**Solution**: Use either 'simba-english' or 'simba-multilingual'.

#### 4. Empty Text
```
Warning: Speechify TTS: There is no text to speak.
```
**Solution**: Ensure the input text is not empty or whitespace-only.

### Error Handling

The implementation includes comprehensive error handling:

- **Invalid API key**: Graceful fallback with clear error messages
- **Network errors**: Proper exception handling and cleanup
- **Invalid parameters**: Validation with sensible defaults
- **File operations**: Safe file handling with cleanup on errors

## Performance Considerations

### Latency
- **API Calls**: Network latency depends on your location and Speechify's servers
- **Audio Processing**: Base64 decoding and file I/O are minimal overhead
- **Caching**: Generated audio files are cached in the `cache/` directory

### Optimization Tips
1. **Language Specification**: Specify the language when known for better quality
2. **Voice Selection**: Choose appropriate voices for your use case
3. **Audio Format**: Use MP3 for good balance of quality and file size
4. **Text Length**: Consider breaking very long texts into smaller chunks

## Limitations and Considerations

### Current Limitations
1. **Internet Dependency**: Requires internet connection for API calls
2. **API Rate Limits**: Subject to Speechify's API rate limits
3. **Voice Availability**: Voice selection depends on your Speechify plan
4. **Language Support**: Some languages are in beta

### Missing Features from Other TTS Providers
Compared to some other TTS providers, Speechify may not support:
- **Real-time streaming**: Audio is generated in full before playback
- **Custom voice training**: Limited to available voices
- **Advanced SSML**: Basic text-to-speech without advanced markup
- **Offline operation**: Always requires internet connection

## Future Enhancements

Potential improvements for future versions:
1. **Streaming Support**: Real-time audio streaming
2. **Voice Cloning**: Custom voice training capabilities
3. **Advanced SSML**: Support for Speech Synthesis Markup Language
4. **Batch Processing**: Efficient handling of multiple text inputs
5. **Caching Strategy**: Intelligent caching of frequently used audio

## Support and Resources

### Documentation
- [Speechify API Documentation](https://console.sws.speechify.com/signup)
- [Open-LLM-VTuber Documentation](https://github.com/1996scarlet/Open-LLM-VTuber)

### Community
- [Open-LLM-VTuber Issues](https://github.com/1996scarlet/Open-LLM-VTuber/issues)
- [Speechify Support](https://console.sws.speechify.com/signup)

### Migration Support
If you encounter issues during migration, please:
1. Check the troubleshooting section above
2. Run the test suite to identify specific issues
3. Review the error logs for detailed information
4. Open an issue with detailed error information

## Conclusion

The Speechify TTS migration provides a robust, feature-rich text-to-speech solution with excellent language support and voice quality. The implementation maintains full backwards compatibility while adding new capabilities for multilingual support and voice customization.

The comprehensive test suite ensures reliability, and the detailed documentation provides clear guidance for configuration and usage. With proper setup and configuration, Speechify TTS can provide high-quality speech synthesis for a wide range of applications and languages. 