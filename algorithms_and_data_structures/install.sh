#!/bin/bash

# CLI Installation Script for Unix/Linux/macOS
# Version: 1.0.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLI_NAME="algorithms-cli"
REPO_URL="https://github.com/brandonjplambert/algorithms_and_data_structures"
INSTALL_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config/${CLI_NAME}"
VENV_DIR="${HOME}/.${CLI_NAME}-venv"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Algorithms & Data Structures CLI     ${NC}"
    echo -e "${BLUE}  Installation Script v1.0.0           ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        DISTRO=$(lsb_release -si 2>/dev/null || echo "unknown")
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macOS"
    elif [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        DISTRO="Cygwin"
    elif [[ "$OSTYPE" == "msys" ]]; then
        OS="windows"
        DISTRO="MSYS"
    else
        OS="unknown"
        DISTRO="unknown"
    fi
    
    print_info "Detected OS: ${DISTRO} (${OS})"
}

# Check Python version
check_python() {
    print_info "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
        print_error "Python 3.8+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
}

# Check Node.js for Claude Flow
check_nodejs() {
    print_info "Checking Node.js for Claude Flow integration..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version 2>&1)
        print_success "Node.js $NODE_VERSION found"
        HAS_NODE=true
    else
        print_warning "Node.js not found. Claude Flow features will be limited."
        HAS_NODE=false
    fi
}

# Install system dependencies
install_dependencies() {
    print_info "Installing system dependencies..."
    
    case $OS in
        "linux")
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y python3-pip python3-venv git curl
            elif command -v yum &> /dev/null; then
                sudo yum install -y python3-pip python3-venv git curl
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y python3-pip python3-venv git curl
            elif command -v pacman &> /dev/null; then
                sudo pacman -S --noconfirm python-pip git curl
            else
                print_warning "Unknown package manager. Please install python3-pip, python3-venv, git, and curl manually."
            fi
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install python3 git curl
            else
                print_warning "Homebrew not found. Please install Python 3, git, and curl manually."
            fi
            ;;
        *)
            print_warning "Unknown OS. Please install Python 3, git, and curl manually."
            ;;
    esac
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment already exists. Removing..."
        rm -rf "$VENV_DIR"
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment created at $VENV_DIR"
}

# Install CLI
install_cli() {
    print_info "Installing CLI and dependencies..."
    
    source "$VENV_DIR/bin/activate"
    
    # Install core dependencies
    pip install numpy scipy matplotlib pandas jupyter pytest pytest-cov black flake8 mypy
    
    # Install Claude Flow if Node.js is available
    if [[ "$HAS_NODE" == true ]]; then
        npm install -g claude-flow@alpha
        print_success "Claude Flow installed"
    fi
    
    # Create CLI wrapper script
    mkdir -p "$INSTALL_DIR"
    
    cat > "$INSTALL_DIR/$CLI_NAME" << EOF
#!/bin/bash
source "$VENV_DIR/bin/activate"
cd "\$(dirname "\$0")/../..$CLI_NAME-repo"
python -m algorithms_cli "\$@"
EOF
    
    chmod +x "$INSTALL_DIR/$CLI_NAME"
    
    print_success "CLI installed to $INSTALL_DIR/$CLI_NAME"
}

# Setup configuration
setup_config() {
    print_info "Setting up configuration..."
    
    mkdir -p "$CONFIG_DIR"
    
    cat > "$CONFIG_DIR/config.json" << EOF
{
    "version": "1.0.0",
    "python_path": "$VENV_DIR/bin/python",
    "venv_path": "$VENV_DIR",
    "install_date": "$(date -Iseconds)",
    "features": {
        "claude_flow": $HAS_NODE,
        "jupyter": true,
        "testing": true
    },
    "paths": {
        "algorithms": "src/algorithms",
        "data_structures": "src/data_structures",
        "tests": "tests",
        "examples": "examples"
    }
}
EOF
    
    print_success "Configuration saved to $CONFIG_DIR/config.json"
}

# Setup shell completion
setup_completion() {
    print_info "Setting up shell completion..."
    
    # Bash completion
    if [[ -n "$BASH_VERSION" ]]; then
        COMPLETION_DIR="$HOME/.bash_completion.d"
        mkdir -p "$COMPLETION_DIR"
        
        cat > "$COMPLETION_DIR/$CLI_NAME" << 'EOF'
_algorithms_cli_complete() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="run test benchmark analyze visualize sparc help version"
    
    case ${prev} in
        run)
            COMPREPLY=($(compgen -W "sort search graph tree dynamic-programming" -- ${cur}))
            return 0
            ;;
        test)
            COMPREPLY=($(compgen -W "unit integration performance" -- ${cur}))
            return 0
            ;;
        sparc)
            COMPREPLY=($(compgen -W "spec pseudocode arch refine complete tdd" -- ${cur}))
            return 0
            ;;
        *)
            ;;
    esac
    
    COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
    return 0
}

complete -F _algorithms_cli_complete algorithms-cli
EOF
        
        # Add to bashrc if not already present
        if ! grep -q "source $COMPLETION_DIR/$CLI_NAME" ~/.bashrc 2>/dev/null; then
            echo "source $COMPLETION_DIR/$CLI_NAME" >> ~/.bashrc
        fi
        
        print_success "Bash completion installed"
    fi
    
    # Zsh completion
    if [[ -n "$ZSH_VERSION" ]]; then
        COMPLETION_DIR="$HOME/.zsh_completions"
        mkdir -p "$COMPLETION_DIR"
        
        cat > "$COMPLETION_DIR/_$CLI_NAME" << 'EOF'
#compdef algorithms-cli

_algorithms_cli() {
    local context state line
    
    _arguments \
        '1:command:(run test benchmark analyze visualize sparc help version)' \
        '*::arg:->args'
    
    case $state in
        args)
            case $line[1] in
                run)
                    _arguments '1:algorithm:(sort search graph tree dynamic-programming)'
                    ;;
                test)
                    _arguments '1:test-type:(unit integration performance)'
                    ;;
                sparc)
                    _arguments '1:phase:(spec pseudocode arch refine complete tdd)'
                    ;;
            esac
            ;;
    esac
}

_algorithms_cli "$@"
EOF
        
        # Add to zshrc if not already present
        if ! grep -q "fpath=($COMPLETION_DIR \$fpath)" ~/.zshrc 2>/dev/null; then
            echo "fpath=($COMPLETION_DIR \$fpath)" >> ~/.zshrc
            echo "autoload -U compinit && compinit" >> ~/.zshrc
        fi
        
        print_success "Zsh completion installed"
    fi
}

# Add to PATH
add_to_path() {
    print_info "Adding CLI to PATH..."
    
    # Check if already in PATH
    if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
        print_info "Already in PATH"
        return
    fi
    
    # Add to shell profile
    for profile in ~/.bashrc ~/.zshrc ~/.profile; do
        if [[ -f "$profile" ]]; then
            if ! grep -q "export PATH=\"$INSTALL_DIR:\$PATH\"" "$profile" 2>/dev/null; then
                echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$profile"
                print_success "Added to PATH in $profile"
            fi
        fi
    done
    
    # Add to current session
    export PATH="$INSTALL_DIR:$PATH"
}

# Development mode setup
dev_setup() {
    if [[ "$1" == "--dev" ]]; then
        print_info "Setting up development environment..."
        
        source "$VENV_DIR/bin/activate"
        
        # Install development dependencies
        pip install pre-commit black isort mypy pytest-xdist coverage[toml]
        
        # Setup pre-commit hooks
        if [[ -f ".pre-commit-config.yaml" ]]; then
            pre-commit install
            print_success "Pre-commit hooks installed"
        fi
        
        # Create development aliases
        cat >> "$CONFIG_DIR/dev_aliases.sh" << EOF
#!/bin/bash
alias alg-test='python -m pytest tests/ -v'
alias alg-cov='python -m pytest tests/ --cov=src --cov-report=html'
alias alg-lint='black src/ tests/ && isort src/ tests/ && mypy src/'
alias alg-sparc='npx claude-flow sparc'
EOF
        
        print_success "Development environment configured"
    fi
}

# Create uninstaller
create_uninstaller() {
    cat > "$INSTALL_DIR/${CLI_NAME}-uninstall" << EOF
#!/bin/bash

echo "Uninstalling $CLI_NAME..."

# Remove virtual environment
if [[ -d "$VENV_DIR" ]]; then
    rm -rf "$VENV_DIR"
    echo "Removed virtual environment"
fi

# Remove configuration
if [[ -d "$CONFIG_DIR" ]]; then
    rm -rf "$CONFIG_DIR"
    echo "Removed configuration"
fi

# Remove CLI scripts
rm -f "$INSTALL_DIR/$CLI_NAME"
rm -f "$INSTALL_DIR/${CLI_NAME}-uninstall"

# Remove completions
rm -f "$HOME/.bash_completion.d/$CLI_NAME"
rm -f "$HOME/.zsh_completions/_$CLI_NAME"

echo "Uninstallation complete!"
echo "Note: You may need to remove PATH entries manually from your shell profile."
EOF
    
    chmod +x "$INSTALL_DIR/${CLI_NAME}-uninstall"
    print_success "Uninstaller created at $INSTALL_DIR/${CLI_NAME}-uninstall"
}

# Main installation function
main() {
    print_header
    
    # Parse arguments
    DEV_MODE=false
    if [[ "$1" == "--dev" ]]; then
        DEV_MODE=true
        print_info "Installing in development mode"
    fi
    
    # Run installation steps
    detect_os
    check_python
    check_nodejs
    install_dependencies
    create_venv
    install_cli
    setup_config
    setup_completion
    add_to_path
    
    if [[ "$DEV_MODE" == true ]]; then
        dev_setup --dev
    fi
    
    create_uninstaller
    
    # Store installation info in memory
    npx claude-flow@alpha hooks post-edit --file "install.sh" --memory-key "swarm/installer/unix-complete" 2>/dev/null || true
    
    print_success "Installation completed successfully!"
    echo
    print_info "Next steps:"
    echo "  1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
    echo "  2. Test the installation: $CLI_NAME version"
    echo "  3. Run the quickstart guide: $CLI_NAME help"
    echo
    if [[ "$HAS_NODE" == true ]]; then
        print_info "Claude Flow integration available:"
        echo "  • Run: $CLI_NAME sparc tdd 'your-algorithm'"
        echo "  • Full pipeline: npx claude-flow sparc pipeline 'task'"
    fi
    
    if [[ "$DEV_MODE" == true ]]; then
        echo
        print_info "Development tools installed:"
        echo "  • Source dev aliases: source $CONFIG_DIR/dev_aliases.sh"
        echo "  • Run tests: alg-test"
        echo "  • Coverage: alg-cov"
        echo "  • Lint: alg-lint"
    fi
}

# Run main function
main "$@"