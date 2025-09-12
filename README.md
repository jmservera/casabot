# CasaBot - Wyoming Protocol for Azure OpenAI

A Home Assistant add-on that provides speech-to-text capabilities using Azure OpenAI's Whisper model through the Wyoming protocol.

## Features

- Speech-to-text using Azure OpenAI Whisper models
- Wyoming protocol compatibility for Home Assistant
- Configurable language support
- Debug logging support
- Container-based deployment

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "CasaBot - Wyoming Protocol for Azure OpenAI" add-on
3. Configure the add-on with your Azure OpenAI credentials

## Configuration

### Required Settings

- **azure_openai_endpoint**: Your Azure OpenAI endpoint URL
- **azure_openai_api_key**: Your Azure OpenAI API key

### Optional Settings

- **azure_openai_api_version**: API version (default: "2024-02-01")
- **model**: Whisper model to use (default: "whisper-1")
- **language**: Language for transcription (default: "auto" for automatic detection)
- **wyoming_uri**: Wyoming protocol URI (default: "tcp://0.0.0.0:10300")
- **debug**: Enable debug logging (default: false)

### Example Configuration

```yaml
azure_openai_endpoint: "https://your-resource.openai.azure.com/"
azure_openai_api_key: "your-api-key-here"
azure_openai_api_version: "2024-02-01"
model: "whisper-1"
language: "en"
wyoming_uri: "tcp://0.0.0.0:10300"
debug: false
```

## Usage

Once configured and started, the add-on will:

1. Listen for audio streams via the Wyoming protocol on port 10300
2. Process audio using Azure OpenAI's speech-to-text API
3. Return transcribed text through the Wyoming protocol

## Wyoming Protocol Integration

This add-on implements the Wyoming protocol for speech-to-text, making it compatible with:

- Home Assistant's voice assistants
- Other Wyoming protocol clients
- Rhasspy voice assistant framework

## Troubleshooting

### Common Issues

1. **Authentication Error**: Verify your Azure OpenAI endpoint and API key
2. **Model Not Found**: Ensure the specified model is deployed in your Azure OpenAI resource
3. **Connection Issues**: Check network connectivity and firewall settings

### Debug Mode

Enable debug logging in the configuration to see detailed information about:
- Audio processing
- API calls to Azure OpenAI
- Wyoming protocol events

## Support

- [Wyoming Protocol Documentation](https://github.com/rhasspy/rhasspy3/blob/master/docs/wyoming.md)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/audio-completions-quickstart)
