#!/bin/bash

# Frontend startup script
echo "Starting Research Paper RAG Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start Next.js dev server
echo "Starting Next.js development server..."
npm run dev




