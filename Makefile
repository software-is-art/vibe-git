.PHONY: test test-unit test-mutation lint format install-dev clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  install-dev    Install development dependencies"
	@echo "  test          Run all tests (unit + mutation)"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-mutation Run mutation tests"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black"
	@echo "  clean         Clean up test artifacts"

# Install development dependencies
install-dev:
	uv sync --extra test --extra dev

# Run all tests
test: test-unit test-mutation

# Run unit tests
test-unit:
	uv run pytest -v

# Run mutation testing with parallel execution
test-mutation:
	uv run mutmut run --max-children=auto

# Show mutation testing results
mutation-results:
	uv run mutmut results

# Generate mutation testing HTML report
mutation-report:
	uv run mutmut show --format=html > mutation_report.html
	@echo "Mutation report generated: mutation_report.html"

# Run linting
lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run python -m py_compile main.py test_vibe_git.py

# Format code
format:
	uv run ruff format .
	uv run ruff check --fix .

# Clean up
clean:
	rm -rf .mutmut-cache
	rm -f mutation_report.html
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete

# Quick development workflow
dev-check: format lint test-unit
	@echo "✅ All development checks passed!"

# CI simulation (what GitHub Actions runs)
ci: lint test-unit test-mutation
	@echo "✅ CI checks complete!"