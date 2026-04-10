#!/bin/bash
# OpenHands session bootstrap script
# Installs dependencies and prepares the environment.

# Install uv if not already available
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install project dependencies
uv sync
