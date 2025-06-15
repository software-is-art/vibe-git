#!/bin/bash
# Run the same tests that CI runs

echo "🧪 Running CI test suite locally..."
echo

# Configure git for testing
git config --global user.name "Test User" 2>/dev/null || true
git config --global user.email "test@example.com" 2>/dev/null || true

# Run pytest
echo "📋 Running pytest..."
uv run pytest -v --tb=short
PYTEST_EXIT=$?

# Run linting
echo
echo "🎨 Running ruff format check..."
uv run ruff format --check .
FORMAT_EXIT=$?

echo
echo "🔍 Running ruff lint..."
uv run ruff check .
LINT_EXIT=$?

# Run mutation testing on main.py
echo
echo "🧬 Running mutation testing on main.py..."
rm -rf .mutmut-cache 2>/dev/null || true
uv run mutmut run --paths-to-mutate main.py
uv run mutmut results

# Clean cache
rm -rf .mutmut-cache 2>/dev/null || true

# Run focused mutation testing
echo
echo "🧬 Running mutation testing on vibe_status_only.py..."
uv run mutmut run
uv run mutmut results

# Summary
echo
echo "📊 Test Summary:"
echo "- pytest: $([ $PYTEST_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- ruff format: $([ $FORMAT_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- ruff lint: $([ $LINT_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- mutation testing: See results above"

# Exit with error if any test failed
if [ $PYTEST_EXIT -ne 0 ] || [ $FORMAT_EXIT -ne 0 ] || [ $LINT_EXIT -ne 0 ]; then
    exit 1
fi