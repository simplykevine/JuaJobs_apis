#!/bin/bash

# JuaJobs API Test Runner Script

echo "🧪 Running JuaJobs API Tests..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install coverage

# Run Django tests with coverage
echo "🔍 Running tests with coverage..."
coverage run --source='.' manage.py test api.tests

# Generate coverage report
echo "📊 Generating coverage report..."
coverage report

# Generate HTML coverage report
echo "🌐 Generating HTML coverage report..."
coverage html

echo "✅ Tests completed!"
echo "📋 Coverage report available in htmlcov/index.html"

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "🎉 All tests passed!"
else
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi
