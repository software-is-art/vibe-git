#!/bin/bash
# Run the same tests that CI runs

echo "🧪 Running CI test suite locally..."
echo

# Configure git for testing
git config --global user.name "Test User" 2>/dev/null || true
git config --global user.email "test@example.com" 2>/dev/null || true

# Run unit tests
echo "📋 Running unit tests..."
uv run pytest test_status_only.py -v --tb=short
UNIT_EXIT=$?

# Run integration tests
echo
echo "🔗 Running integration tests..."
uv run pytest test_status_only.py -v --tb=short
INTEGRATION_EXIT=$?

# Run linting
echo
echo "🎨 Running ruff format check..."
uv run ruff format --check .
FORMAT_EXIT=$?

echo
echo "🔍 Running ruff lint..."
uv run ruff check .
LINT_EXIT=$?

# Run mutation testing with mutmut
echo
echo "🧬 Running mutation testing with mutmut..."
# Always start fresh to avoid cache corruption issues
rm -rf .mutmut-cache

# Run mutmut mutation testing with parallel execution
uv run mutmut run

# Display results
echo
echo "📊 Mutation Testing Results:"
uv run mutmut results

# Check mutation score
MUTMUT_EXIT=$?

# Summary
echo
echo "📊 Test Summary:"
echo "- unit tests: $([ $UNIT_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- integration tests: $([ $INTEGRATION_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- ruff format: $([ $FORMAT_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- ruff lint: $([ $LINT_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- mutation testing: $([ $MUTMUT_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"

# Exit with error if any test failed
if [ $UNIT_EXIT -ne 0 ] || [ $INTEGRATION_EXIT -ne 0 ] || [ $FORMAT_EXIT -ne 0 ] || [ $LINT_EXIT -ne 0 ] || [ $MUTMUT_EXIT -ne 0 ]; then
    exit 1
fi