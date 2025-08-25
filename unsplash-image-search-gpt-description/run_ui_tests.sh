#!/bin/bash

# UI Rendering Test Runner for Unsplash Image Search Application
# This script runs comprehensive UI validation tests

show_header() {
    echo ""
    echo "=========================================="
    echo "    UI Rendering Test Suite"
    echo "=========================================="
    echo ""
}

show_help() {
    echo ""
    echo "Usage: ./run_ui_tests.sh [--full] [--help]"
    echo ""
    echo "Options:"
    echo "   --quick    Run quick health check only (default)"
    echo "   --full     Run comprehensive UI test suite"
    echo "   --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "   ./run_ui_tests.sh           # Quick health check"
    echo "   ./run_ui_tests.sh --quick   # Quick health check"
    echo "   ./run_ui_tests.sh --full    # Full test suite"
    echo ""
    exit 0
}

check_environment() {
    # Check if we're in the right directory
    if [ ! -f "main.py" ]; then
        echo "ERROR: Please run this script from the project root directory"
        echo "Expected to find main.py in current directory"
        exit 1
    fi

    # Check Python availability
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            echo "ERROR: Python is not available in PATH"
            echo "Please install Python or add it to your PATH"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi

    # Check if running in headless environment and set up display
    if [ -z "$DISPLAY" ] && command -v xvfb-run &> /dev/null; then
        echo "No display detected, using Xvfb for headless testing..."
        PYTHON_CMD="xvfb-run -a $PYTHON_CMD"
    fi
}

run_tests() {
    local mode=$1
    
    echo "Running UI tests in $mode mode..."
    echo ""
    
    if [ "$mode" = "full" ]; then
        echo "Running comprehensive UI test suite..."
        $PYTHON_CMD tests/test_ui_validation_runner.py --full
    else
        echo "Running quick health check..."
        $PYTHON_CMD tests/test_ui_validation_runner.py --quick
    fi
    
    return $?
}

show_results() {
    local result=$1
    
    echo ""
    if [ $result -eq 0 ]; then
        echo "=========================================="
        echo "    ✅ UI Tests PASSED"
        echo "=========================================="
        echo "The UI should load correctly without issues."
    else
        echo "=========================================="
        echo "    ❌ UI Tests FAILED"
        echo "=========================================="
        echo "Please check the output above for specific issues."
        echo ""
        echo "Common solutions:"
        echo "  • Ensure all dependencies are installed: pip install -r requirements.txt"
        echo "  • Verify API keys are configured properly"
        echo "  • Check that the display is available for GUI testing"
        echo "  • Try running with xvfb-run for headless environments"
    fi
    echo ""
}

main() {
    # Parse command line arguments
    MODE="quick"
    
    case "$1" in
        --full)
            MODE="full"
            ;;
        --help)
            show_help
            ;;
        --quick|"")
            MODE="quick"
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
    
    show_header
    check_environment
    run_tests "$MODE"
    RESULT=$?
    show_results $RESULT
    
    exit $RESULT
}

# Make script executable if needed
chmod +x "$0" 2>/dev/null || true

# Run main function
main "$@"