# Makefile for PatentPulse test data generation

.PHONY: testdata

testdata:
	python fixtures/generate_toxic_data.py

.PHONY: activate-env
activate-env:
	@echo "To activate Python environment:"
	@echo "PowerShell: .\\ai-service\\venv\\Scripts\\Activate.ps1"
	@echo "Cmd:        .\\ai-service\\venv\\Scripts\\activate.bat"
	@echo "After activation, run: pip install -r ai-service/requirements.txt"

.PHONY: run-ai
run-ai:
	cd ai-service && powershell -ExecutionPolicy Bypass -File run_ai.ps1

# Windows users:
#   Set VIRTUAL_ENV_ACTIVATE to the correct activation command for your shell.
#   Example for PowerShell:
#     set VIRTUAL_ENV_ACTIVATE=.\\venv\\Scripts\\Activate.ps1
#   Example for Cmd:
#     set VIRTUAL_ENV_ACTIVATE=.\\venv\\Scripts\\activate.bat
#   Then run: make run-ai

# Usage:
#   make testdata
# This will generate test files in fixtures/test_data/
#   make install-ai-deps # Installs FastAPI and dependencies into venv
