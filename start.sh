#!/bin/bash

echo "🚀 Starting NONGBUXX Backend..."
echo "Environment Variables:"
echo "PORT: $PORT"
echo "DEBUG: $DEBUG"
echo "FLASK_ENV: $FLASK_ENV"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+설정됨}"
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+설정됨}"

echo "📁 Current directory: $(pwd)"
echo "📄 Files in directory:"
ls -la

echo "🐍 Python version:"
python --version

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔥 Starting Flask app..."
python app.py 