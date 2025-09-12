#!/usr/bin/env python3
"""Wyoming protocol server for Azure OpenAI speech-to-text."""

import asyncio
import io
import logging
import os
import sys
from typing import Dict, List, Optional
from urllib.parse import urlparse

import openai
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.error import Error
from wyoming.event import Event
from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncEventHandler, AsyncServer

_LOGGER = logging.getLogger(__name__)


class AzureOpenAISttEventHandler(AsyncEventHandler):
    """Event handler for Wyoming protocol with Azure OpenAI STT."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: Dict,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        
        self.wyoming_info = wyoming_info
        self.cli_args = cli_args
        self.client = None
        
        # Audio buffer
        self.audio_buffer = io.BytesIO()
        self.audio_bytes_left = 0
        
        # Initialize OpenAI client
        self._init_openai_client()

    def _init_openai_client(self):
        """Initialize the OpenAI client for Azure."""
        try:
            self.client = openai.AzureOpenAI(
                azure_endpoint=self.cli_args["azure_openai_endpoint"],
                api_key=self.cli_args["azure_openai_api_key"],
                api_version=self.cli_args["azure_openai_api_version"]
            )
            _LOGGER.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            _LOGGER.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise

    async def handle_event(self, event: Event) -> bool:
        """Handle Wyoming protocol events."""
        
        if AudioStart.is_type(event.type):
            # Start of audio stream
            audio_start = AudioStart.from_event(event)
            _LOGGER.debug(f"Audio start: {audio_start}")
            
            self.audio_buffer = io.BytesIO()
            self.audio_bytes_left = 0
            
            return True
            
        if AudioChunk.is_type(event.type):
            # Audio chunk received
            audio_chunk = AudioChunk.from_event(event)
            self.audio_buffer.write(audio_chunk.audio)
            self.audio_bytes_left += len(audio_chunk.audio)
            
            return True
            
        if AudioStop.is_type(event.type):
            # End of audio stream - process transcription
            _LOGGER.debug("Audio stop - processing transcription")
            
            try:
                # Get audio data
                audio_data = self.audio_buffer.getvalue()
                if not audio_data:
                    _LOGGER.warning("No audio data received")
                    await self.write_event(
                        Error(text="No audio data received", context="transcription").event()
                    )
                    return True
                
                # Transcribe with Azure OpenAI
                text = await self._transcribe_audio(audio_data)
                
                if text:
                    # Send transcription result
                    await self.write_event(
                        Transcript(text=text).event()
                    )
                    _LOGGER.info(f"Transcription: {text}")
                else:
                    await self.write_event(
                        Error(text="No transcription result", context="transcription").event()
                    )
                    
            except Exception as e:
                _LOGGER.error(f"Transcription error: {e}")
                await self.write_event(
                    Error(text=f"Transcription failed: {str(e)}", context="transcription").event()
                )
            
            return True
            
        if Transcribe.is_type(event.type):
            # Direct transcription request (if supported)
            _LOGGER.debug("Transcribe event received")
            return True

        return True

    async def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using Azure OpenAI."""
        try:
            # Create a file-like object for the audio
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"  # OpenAI needs a filename
            
            # Call Azure OpenAI transcription
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.audio.transcriptions.create(
                    model=self.cli_args["model"],
                    file=audio_file,
                    language=self.cli_args["language"] if self.cli_args["language"] != "auto" else None
                )
            )
            
            return response.text.strip() if response.text else None
            
        except Exception as e:
            _LOGGER.error(f"Azure OpenAI transcription error: {e}")
            raise


async def main() -> None:
    """Main entry point."""
    
    # Configure logging
    log_level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get configuration from environment
    cli_args = {
        "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        "model": os.getenv("MODEL", "whisper-1"),
        "language": os.getenv("LANGUAGE", "auto"),
        "wyoming_uri": os.getenv("WYOMING_URI", "tcp://0.0.0.0:10300")
    }
    
    # Validate required configuration
    if not cli_args["azure_openai_endpoint"]:
        _LOGGER.error("AZURE_OPENAI_ENDPOINT environment variable is required")
        sys.exit(1)
        
    if not cli_args["azure_openai_api_key"]:
        _LOGGER.error("AZURE_OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    
    # Create Wyoming info
    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="casabot-azure-openai",
                description="Azure OpenAI speech-to-text via Wyoming Protocol",
                attribution=Attribution(
                    name="Azure OpenAI",
                    url="https://azure.microsoft.com/en-us/products/ai-services/openai-service"
                ),
                installed=True,
                models=[
                    AsrModel(
                        name=cli_args["model"],
                        description=f"Azure OpenAI {cli_args['model']} model",
                        attribution=Attribution(
                            name="OpenAI",
                            url="https://openai.com/"
                        ),
                        installed=True,
                        languages=["auto"] if cli_args["language"] == "auto" else [cli_args["language"]]
                    )
                ]
            )
        ]
    )
    
    _LOGGER.info("Starting CasaBot Wyoming Protocol Server")
    _LOGGER.info(f"Wyoming URI: {cli_args['wyoming_uri']}")
    _LOGGER.info(f"Azure OpenAI Endpoint: {cli_args['azure_openai_endpoint']}")
    _LOGGER.info(f"Model: {cli_args['model']}")
    _LOGGER.info(f"Language: {cli_args['language']}")
    
    # Parse Wyoming URI
    parsed_uri = urlparse(cli_args["wyoming_uri"])
    host = parsed_uri.hostname or "0.0.0.0"
    port = parsed_uri.port or 10300
    
    # Create and run server
    server = AsyncServer.from_uri(cli_args["wyoming_uri"])
    
    try:
        await server.run(
            lambda: AzureOpenAISttEventHandler(wyoming_info, cli_args)
        )
    except KeyboardInterrupt:
        _LOGGER.info("Server stopped by user")
    except Exception as e:
        _LOGGER.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())