#!/bin/bash

# Configuration
# API_URL="https://aifrauddetection.onrender.com/api/voice-detection"
API_URL="http://localhost:8000/api/voice-detection"
API_KEY="sk_test_123456789"
AUDIO_FILE="/home/mritunjay/Downloads/audio_test.mp3"
TEMP_JSON="request_payload.json"

# Check if file exists
if [ ! -f "$AUDIO_FILE" ]; then
    echo "Error: File $AUDIO_FILE not found!"
    exit 1
fi

echo "Encoding audio file..."
# Create the JSON file directly to avoid "Argument list too long"
# We write the first part of the JSON, then append the base64, then the closing brace.
echo -n '{"language": "English", "audioFormat": "mp3", "audioBase64": "' > "$TEMP_JSON"
base64 -w 0 "$AUDIO_FILE" >> "$TEMP_JSON"
echo '"}' >> "$TEMP_JSON"

echo "Sending request to $API_URL..."
# Send POST request using the file (@file syntax)
curl -s -X POST "$API_URL" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d @"$TEMP_JSON"

# Print a newline for formatted output
echo ""

# Cleanup
rm "$TEMP_JSON"
