# BDA

## Getting Started

```bash
# Install uv for macOS
brew install uv
# Install uv for Windows
choco install uv

# Set up uv
uv venv # Create a virtual environment
source .venv/bin/activate # Activate the virtual environment
uv pip compile pyproject.toml -o requirements.txt # Compile dependencies to requirements.txt
uv pip sync requirements.txt # Sync the virtual environment with requirements.txt

# Run the application
uv run analysis.py
```