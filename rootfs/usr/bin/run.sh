#!/usr/bin/with-contenv bashio

# Get configuration from Home Assistant
export AZURE_OPENAI_ENDPOINT=$(bashio::config 'azure_openai_endpoint')
export AZURE_OPENAI_API_KEY=$(bashio::config 'azure_openai_api_key')
export AZURE_OPENAI_API_VERSION=$(bashio::config 'azure_openai_api_version')
export MODEL=$(bashio::config 'model')
export WYOMING_URI=$(bashio::config 'wyoming_uri')
export DEBUG=$(bashio::config 'debug')

# Log startup information
bashio::log.info "Starting CasaBot Wyoming Protocol Server..."
bashio::log.info "Azure OpenAI Endpoint: ${AZURE_OPENAI_ENDPOINT}"
bashio::log.info "Model: ${MODEL}"
bashio::log.info "Wyoming URI: ${WYOMING_URI}"

# Validate required configuration
if bashio::var.is_empty "${AZURE_OPENAI_ENDPOINT}"; then
    bashio::log.fatal "Azure OpenAI endpoint is required!"
    exit 1
fi

if bashio::var.is_empty "${AZURE_OPENAI_API_KEY}"; then
    bashio::log.fatal "Azure OpenAI API key is required!"
    exit 1
fi

# Start the Wyoming protocol server
cd /usr/share/
python3 -m casabot