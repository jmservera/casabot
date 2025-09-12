"""Configuration validation utilities for CasaBot Wyoming Protocol."""

import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

_LOGGER = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Configuration validation error."""
    pass


def validate_azure_endpoint(endpoint: str) -> bool:
    """Validate Azure OpenAI endpoint URL format."""
    if not endpoint:
        return False
    
    try:
        parsed = urlparse(endpoint)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check for Azure OpenAI endpoint pattern
        if ".openai.azure.com" not in parsed.netloc:
            _LOGGER.warning(f"Endpoint doesn't appear to be an Azure OpenAI endpoint: {endpoint}")
        
        return True
    except Exception:
        return False


def validate_api_key(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key:
        return False
    
    # Basic validation - API key should be non-empty string
    if len(api_key.strip()) < 10:
        return False
    
    return True


def validate_language_code(language: str) -> bool:
    """Validate language code format."""
    if not language:
        return False
    
    if language == "auto":
        return True
    
    # Basic ISO 639-1 language code validation (2-3 letter codes)
    pattern = r"^[a-z]{2,3}(-[A-Z]{2})?$"
    return bool(re.match(pattern, language))


def validate_wyoming_uri(uri: str) -> bool:
    """Validate Wyoming protocol URI."""
    if not uri:
        return False
    
    try:
        parsed = urlparse(uri)
        if parsed.scheme not in ["tcp", "unix"]:
            return False
        
        if parsed.scheme == "tcp":
            if not parsed.hostname or not parsed.port:
                return False
        
        return True
    except Exception:
        return False


def validate_configuration(config: Dict) -> List[str]:
    """Validate complete configuration and return list of errors."""
    errors = []
    
    # Required fields
    if not validate_azure_endpoint(config.get("azure_openai_endpoint", "")):
        errors.append("Invalid or missing Azure OpenAI endpoint")
    
    if not validate_api_key(config.get("azure_openai_api_key", "")):
        errors.append("Invalid or missing Azure OpenAI API key")
    
    # Optional but validated fields
    language = config.get("language", "auto")
    if not validate_language_code(language):
        errors.append(f"Invalid language code: {language}")
    
    wyoming_uri = config.get("wyoming_uri", "tcp://0.0.0.0:11350")
    if not validate_wyoming_uri(wyoming_uri):
        errors.append(f"Invalid Wyoming URI: {wyoming_uri}")
    
    # Model validation (basic)
    model = config.get("model", "whisper-1")
    if not model or len(model.strip()) == 0:
        errors.append("Model name cannot be empty")
    
    # API version validation (basic)
    api_version = config.get("azure_openai_api_version", "2024-02-01")
    if not api_version or not re.match(r"\d{4}-\d{2}-\d{2}", api_version):
        errors.append(f"Invalid API version format: {api_version}")
    
    return errors