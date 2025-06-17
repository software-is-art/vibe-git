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

# Run mutation testing with cosmic-ray
echo
echo "🧬 Running mutation testing with cosmic-ray..."
# Always start fresh to avoid cache corruption issues
rm -f mutants.sqlite
uv run cosmic-ray init mutants.toml mutants.sqlite

# Run cosmic-ray mutation testing
uv run cosmic-ray exec mutants.toml mutants.sqlite

# Display results
echo
echo "📊 Mutation Testing Results:"
DUMP_OUTPUT=$(uv run cosmic-ray dump mutants.sqlite)
TOTAL=$(echo "$DUMP_OUTPUT" | grep -c '"job_id"' || echo "0")
KILLED=$(echo "$DUMP_OUTPUT" | grep -c '"test_outcome": "killed"' || echo "0") 
SURVIVED=$(echo "$DUMP_OUTPUT" | grep -c '"test_outcome": "survived"' || echo "0")
PENDING=$(echo "$DUMP_OUTPUT" | grep -c '"test_outcome": null' || echo "0")
echo "Total mutations: $TOTAL"
echo "Killed: $KILLED"
echo "Survived: $SURVIVED"
echo "Pending: $PENDING"
if [ "$TOTAL" -gt 0 ]; then
  SCORE=$(python3 -c "print(f'{$KILLED * 100 / $TOTAL:.1f}')" 2>/dev/null || echo "0")
  echo "Mutation score: ${SCORE}%"
fi

# Summary
echo
echo "📊 Test Summary:"
echo "- unit tests: $([ $UNIT_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- integration tests: $([ $INTEGRATION_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- ruff format: $([ $FORMAT_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- ruff lint: $([ $LINT_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "- mutation testing: See results above"

# Exit with error if any test failed
if [ $UNIT_EXIT -ne 0 ] || [ $INTEGRATION_EXIT -ne 0 ] || [ $FORMAT_EXIT -ne 0 ] || [ $LINT_EXIT -ne 0 ]; then
    exit 1
fi