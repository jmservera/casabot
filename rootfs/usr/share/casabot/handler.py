import asyncio
import io
import logging
from typing import Dict,  Optional
from urllib.parse import urlparse

import openai
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.error import Error
from wyoming.event import Event
from wyoming.info import  Info
from wyoming.server import AsyncEventHandler

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
        
        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
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
            if not audio_data:
                _LOGGER.warning("Empty audio data provided for transcription")
                return None
                
            if len(audio_data) < 1024:  # Less than 1KB might not be valid audio
                _LOGGER.warning(f"Audio data too small: {len(audio_data)} bytes")
                return None
            
            _LOGGER.debug(f"Processing audio data: {len(audio_data)} bytes")
            
            # Create a file-like object for the audio
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"  # OpenAI needs a filename
            
            # Prepare transcription parameters
            transcribe_params = {
                "model": self.cli_args["model"],
                "file": audio_file
            }
            
            # Add language parameter if not auto-detection
            if self.cli_args["language"] and self.cli_args["language"] != "auto":
                transcribe_params["language"] = self.cli_args["language"]
            
            _LOGGER.debug(f"Calling Azure OpenAI with params: {list(transcribe_params.keys())}")
            
            # Call Azure OpenAI transcription
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.audio.transcriptions.create(**transcribe_params)
            )
            
            if response and hasattr(response, 'text') and response.text:
                result_text = response.text.strip()
                _LOGGER.debug(f"Transcription successful: {len(result_text)} characters")
                return result_text
            else:
                _LOGGER.warning("Empty response from Azure OpenAI")
                return None
            
        except Exception as e:
            _LOGGER.error(f"Azure OpenAI transcription error: {e}")
            raise
