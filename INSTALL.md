# Installation Guide

## Prerequisites

1. **Home Assistant**: A running Home Assistant instance
2. **Azure OpenAI**: An Azure OpenAI resource with Whisper model deployed
3. **Add-on Store**: Access to install custom add-ons in Home Assistant

## Steps

### 1. Prepare Azure OpenAI

1. Create an Azure OpenAI resource in Azure Portal
2. Deploy a Whisper model (e.g., `whisper-1`)
3. Note down your:
   - Endpoint URL (e.g., `https://your-resource.openai.azure.com/`)
   - API Key
   - API Version (default: `2024-02-01`)

### 2. Install the Add-on

#### Option A: From Repository (Recommended)

1. In Home Assistant, go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the three dots menu → **Repositories**
3. Add this repository URL: `https://github.com/jmservera/casabot`
4. Find "CasaBot - Wyoming Protocol for Azure OpenAI" in the store
5. Click **Install**

#### Option B: Manual Installation

1. Clone this repository to your Home Assistant add-ons folder:
   ```bash
   git clone https://github.com/jmservera/casabot /usr/share/hassio/addons/local/casabot
   ```
2. Restart Home Assistant
3. The add-on will appear in the local add-ons section

### 3. Configure the Add-on

1. Click on the installed add-on
2. Go to the **Configuration** tab
3. Fill in the required settings:

```yaml
azure_openai_endpoint: "https://your-resource.openai.azure.com/"
azure_openai_api_key: "your-api-key-here"
model: "whisper-1"
language: "auto"
```

### 4. Start the Add-on

1. Go to the **Info** tab
2. Click **Start**
3. Enable **Start on boot** if desired
4. Monitor the logs for any startup issues

### 5. Configure Home Assistant Voice Assistant

1. Go to **Settings** → **Voice assistants**
2. Create or edit a voice assistant
3. Set **Speech-to-text** to use Wyoming Protocol
4. Configure the Wyoming URI: `tcp://localhost:11350`

## Verification

1. Check the add-on logs for successful startup
2. Test voice commands through Home Assistant
3. Monitor the logs for transcription activity

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check your API key and endpoint
2. **Model not found**: Ensure the model is deployed in Azure OpenAI
3. **Connection refused**: Verify the Wyoming URI configuration
4. **Empty transcriptions**: Check audio input levels and language settings

### Debug Mode

Enable debug logging in the add-on configuration:

```yaml
debug: true
```

This will provide detailed logs about:
- Audio processing
- API calls to Azure OpenAI  
- Wyoming protocol events

### Log Analysis

View add-on logs through:
1. Home Assistant UI: Add-ons → CasaBot → Logs tab
2. Docker logs: `docker logs addon_local_casabot`
3. Home Assistant logs: Check for Wyoming-related entries

## Support

- [Wyoming Protocol Documentation](https://github.com/rhasspy/rhasspy3/blob/master/docs/wyoming.md)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/audio-completions-quickstart)
- [Home Assistant Voice Assistant Guide](https://www.home-assistant.io/voice_control/)

For issues specific to this add-on, please create an issue in the GitHub repository.