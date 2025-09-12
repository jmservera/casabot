#!/bin/bash

# Build script for CasaBot Wyoming Protocol Add-on

set -e

echo "Building CasaBot Wyoming Protocol Add-on..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker is required but not installed. Exiting."
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t casabot-wyoming-azure:latest .

echo "Build completed successfully!"
echo ""
echo "To test the add-on:"
echo "1. Set environment variables for Azure OpenAI:"
echo "   export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'"
echo "   export AZURE_OPENAI_API_KEY='your-api-key'"
echo ""
echo "2. Run the container:"
echo "   docker run -p 11350:11350 -e AZURE_OPENAI_ENDPOINT -e AZURE_OPENAI_API_KEY casabot-wyoming-azure:latest"