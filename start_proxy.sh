#!/bin/bash
# Start GitCode Proxy Server for CANN Recipes Blog

echo "Starting GitCode Proxy Server..."
echo ""

cd proxy

# Check if Node.js is available
if command -v node &> /dev/null; then
    echo "Using Node.js proxy..."
    node proxy.js
else
    echo "Node.js not found. Using Python proxy..."
    python3 proxy_server.py
fi