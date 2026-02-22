#!/bin/bash
set -e # Exit on error

# Copy configs (Directories created by initializeCommand)
cp .devcontainer/starship.toml ~/.config/starship.toml
cp .devcontainer/config.fish ~/.config/fish/config.fish

echo "Workspace configuration complete."
