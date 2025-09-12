#!/usr/bin/env python3
"""Wyoming protocol server for Azure OpenAI speech-to-text."""

import asyncio
import io
import logging
import os
import sys
from functools import partial
from urllib.parse import urlparse

from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncServer

from .config_validator import validate_configuration

from . import __version__
from .handler import AzureOpenAISttEventHandler

_LOGGER = logging.getLogger(__name__)


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
        "model": os.getenv("MODEL", "gpt-audio"),
        "language": os.getenv("LANGUAGE", "auto"),
        "wyoming_uri": os.getenv("WYOMING_URI", "tcp://0.0.0.0:11350")
    }
    
    # Validate required configuration
    validation_errors = validate_configuration(cli_args)
    if validation_errors:
        for error in validation_errors:
            _LOGGER.error(f"Configuration error: {error}")
        _LOGGER.error("Cannot start server due to configuration errors")
        sys.exit(1)
    
    # Create Wyoming info
    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="casabot-azure-openai",
                description="Azure OpenAI speech-to-text via Wyoming Protocol",
                attribution=Attribution(
                    name="Juanma",
                    url="https://github.com/jmservera/casabot"
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
                        languages=["auto"],
                        version= __version__
                    )
                ],
                version= __version__
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
    port = parsed_uri.port or 11350
    
    # Create and run server
    server = AsyncServer.from_uri(cli_args["wyoming_uri"])
    
    await server.run(
        # wyoming.server will call handler_factory(reader, writer)
        # so the factory must accept (reader, writer) and pass them
        # to the handler constructor. The handler's __init__ accepts
        # *args/**kwargs and forwards them to the base AsyncEventHandler.
        partial(
            AzureOpenAISttEventHandler,
            wyoming_info,
            cli_args
        )
    )

def run() -> None:
    asyncio.run(main())

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass