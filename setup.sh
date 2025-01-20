#!/bin/bash

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate a private key
openssl genrsa -out ssl/server.key 2048

# Generate a self-signed certificate
openssl req -new -x509 -key ssl/server.key -out ssl/server.crt -days 365 -subj "/C=US/ST=Development/L=LocalDev/O=DevApp/CN=localhost"

# Set proper permissions
chmod 600 ssl/server.key
chmod 644 ssl/server.crt

echo "Self-signed SSL certificate generated in ssl/ directory"