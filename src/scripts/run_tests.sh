#!/bin/bash
# Helper script to run all tests for the Fraud Analytics Workbench

echo "🚀 Running all tests..."

# Unit Tests
echo "🧪 Running Unit Tests..."
PYTHONPATH=. pytest tests/unit/

# Integration Tests
echo "🔌 Running Integration Tests..."
PYTHONPATH=. pytest tests/integration/

echo "✅ All tests completed!"
