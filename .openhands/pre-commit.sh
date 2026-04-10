#!/bin/bash
# OpenHands pre-commit script
# Mirrors CI checks so the agent gets fast feedback before pushing.

set -o pipefail

echo "Running tests..."
uv run pytest tests/
test_exit=$?

echo "Running type checking..."
cd kepler && uv run mypy --python-version 3.12 --ignore-missing-imports .
mypy_exit=$?
cd ..

if [ $test_exit -ne 0 ] || [ $mypy_exit -ne 0 ]; then
    echo "Pre-commit checks failed."
    exit 1
fi

echo "All checks passed."
