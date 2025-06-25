#!/bin/bash
# Test runner script with multiple options

set -e

# Default values
TEST_TYPE="all"
COVERAGE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -t, --type TYPE    Test type: all, unit, integration, api (default: all)"
            echo "  -c, --coverage     Run with coverage report"
            echo "  -v, --verbose      Verbose output"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Build test command
CMD="python -m pytest"

# Add test path based on type
case $TEST_TYPE in
    unit)
        CMD="$CMD tests/unit/"
        ;;
    integration)
        CMD="$CMD tests/integration/"
        ;;
    api)
        CMD="$CMD tests/api/"
        ;;
    all)
        CMD="$CMD tests/"
        ;;
    *)
        echo "Invalid test type: $TEST_TYPE"
        echo "Valid types: all, unit, integration, api"
        exit 1
        ;;
esac

# Add coverage if requested
if [ "$COVERAGE" = true ]; then
    CMD="coverage run --source='trust_management_app' -m pytest"
    case $TEST_TYPE in
        unit)
            CMD="$CMD tests/unit/"
            ;;
        integration)
            CMD="$CMD tests/integration/"
            ;;
        api)
            CMD="$CMD tests/api/"
            ;;
        all)
            CMD="$CMD tests/"
            ;;
    esac
fi

# Add verbose flag if requested
if [ "$VERBOSE" = true ]; then
    CMD="$CMD -v"
fi

echo "Running tests: $TEST_TYPE"
echo "Command: $CMD"
echo "----------------------------------------"

# Run the tests
eval $CMD

# Generate coverage report if coverage was used
if [ "$COVERAGE" = true ]; then
    echo "----------------------------------------"
    echo "Generating coverage report..."
    coverage report
    coverage html
    echo "HTML coverage report generated in coverage/htmlcov/"
    echo "XML coverage report generated in coverage/coverage.xml"
fi
