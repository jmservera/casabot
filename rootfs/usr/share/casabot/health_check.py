#!/usr/bin/env python3
"""Health check script for the Wyoming protocol server."""

import asyncio
import logging
import socket
import sys
from urllib.parse import urlparse

_LOGGER = logging.getLogger(__name__)


async def check_wyoming_server(host: str, port: int, timeout: float = 5.0) -> bool:
    """Check if the Wyoming server is responding."""
    try:
        # Simple TCP connection test
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        
        writer.close()
        await writer.wait_closed()
        return True
        
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
        _LOGGER.error(f"Health check failed: {e}")
        return False


def main():
    """Main health check function."""
    # Configure logging
    logging.basicConfig(level=logging.WARNING)
    
    # Get Wyoming URI from environment or use default
    import os
    wyoming_uri = os.getenv("WYOMING_URI", "tcp://0.0.0.0:10300")
    
    try:
        parsed = urlparse(wyoming_uri)
        host = parsed.hostname or "localhost"
        port = parsed.port or 10300
        
        # Run health check
        is_healthy = asyncio.run(check_wyoming_server(host, port))
        
        if is_healthy:
            print("✓ Wyoming server is healthy")
            sys.exit(0)
        else:
            print("✗ Wyoming server is not responding")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Health check error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()