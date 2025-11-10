#!/bin/bash
# Run Personal LLM Assistant

echo "🚀 Starting Personal LLM Assistant..."
echo ""
echo "Activating pyenv environment..."
pyenv activate edubot

echo "Running Streamlit app..."
echo ""
echo "📱 Once started, your app will be available at:"
echo "   🌐 Local URL: http://localhost:8501"
echo "   🌐 Network URL: (will be shown below)"
echo ""
echo "Press Ctrl+C to stop the app"
echo "=" * 60
echo ""

cd /home/risad/projects/tavily_search_wraper
streamlit run frontend/streamlit/app.py

