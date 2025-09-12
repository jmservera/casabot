#!/usr/bin/env python3
"""Simple test client for the Wyoming protocol server."""

import asyncio
import io
import logging
import wave
from pathlib import Path

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.client import AsyncClient
from wyoming.info import Info

_LOGGER = logging.getLogger(__name__)


async def test_transcription():
    """Test the Wyoming protocol server with a sample audio file."""
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Connect to the Wyoming server
    client = AsyncClient("localhost", 10300)
    
    try:
        await client.connect()
        _LOGGER.info("Connected to Wyoming server")
        
        # Get server info
        info = await client.read_event()
        if info and hasattr(info, 'event'):
            info_data = Info.from_event(info.event)
            _LOGGER.info(f"Server info: {info_data}")
        
        # Create a simple test audio (sine wave)
        sample_rate = 16000
        duration = 2  # seconds
        frequency = 440  # Hz (A note)
        
        import numpy as np
        
        # Generate sine wave
        t = np.linspace(0, duration, sample_rate * duration, False)
        wave_data = np.sin(frequency * 2 * np.pi * t) * 0.5
        
        # Convert to 16-bit PCM
        audio_bytes = (wave_data * 32767).astype(np.int16).tobytes()
        
        # Send audio start event
        await client.write_event(
            AudioStart(
                rate=sample_rate,
                width=2,  # 16-bit
                channels=1
            ).event()
        )
        
        # Send audio in chunks
        chunk_size = 1024
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            await client.write_event(
                AudioChunk(audio=chunk, rate=sample_rate, width=2, channels=1).event()
            )
        
        # Send audio stop event
        await client.write_event(AudioStop().event())
        
        # Wait for transcription result
        _LOGGER.info("Waiting for transcription result...")
        
        while True:
            event = await client.read_event()
            if not event:
                break
                
            if Transcript.is_type(event.type):
                transcript = Transcript.from_event(event)
                _LOGGER.info(f"Transcription result: {transcript.text}")
                break
            else:
                _LOGGER.debug(f"Received event: {event}")
    
    except Exception as e:
        _LOGGER.error(f"Test failed: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_transcription())