"""
CLI Auto-completion Support
Provides bash and zsh completion for the adaptive learning CLI.
"""

import click
from typing import List, Dict, Any
from pathlib import Path

# Available commands and their options
COMMANDS = {
    'learn': {
        'options': ['--difficulty', '--time-limit'],
        'choices': {
            '--difficulty': ['beginner', 'intermediate', 'advanced']
        }
    },
    'practice': {
        'options': ['--count', '--difficulty'],
        'choices': {
            '--difficulty': ['beginner', 'intermediate', 'advanced']
        }
    },
    'quiz': {
        'options': ['--questions'],
        'choices': {}
    },
    'search': {
        'options': ['--type'],
        'choices': {
            '--type': ['all', 'topics', 'problems', 'concepts']
        }
    },
    'analytics': {
        'options': ['--detailed'],
        'choices': {}
    }
}

# Available topics (would be loaded dynamically in real implementation)
TOPICS = [
    'arrays',
    'linked-lists', 
    'stacks',
    'queues',
    'trees',
    'binary-trees',
    'graphs',
    'sorting',
    'searching',
    'dynamic-programming',
    'greedy-algorithms',
    'backtracking',
    'divide-and-conquer',
    'hash-tables',
    'heaps',
    'tries'
]


def get_bash_completion_script() -> str:
    """Generate bash completion script."""
    return '''#!/bin/bash

_adaptive_learning_completion() {
    local cur prev words cword
    _init_completion || return

    local commands="learn practice quiz progress recommendations analytics topics search config help"
    local global_opts="--interactive --debug --verbose --config --profile --help --version"
    
    case $prev in
        --difficulty)
            COMPREPLY=($(compgen -W "beginner intermediate advanced" -- "$cur"))
            return
            ;;
        --type)
            COMPREPLY=($(compgen -W "all topics problems concepts" -- "$cur"))
            return
            ;;
        --config)
            _filedir
            return
            ;;
        --profile)
            # Could load actual profiles here
            COMPREPLY=($(compgen -W "default student teacher researcher" -- "$cur"))
            return
            ;;
    esac

    if [[ $cur == -* ]]; then
        case ${words[1]} in
            learn)
                COMPREPLY=($(compgen -W "--difficulty --time-limit --help" -- "$cur"))
                ;;
            practice)
                COMPREPLY=($(compgen -W "--count --difficulty --help" -- "$cur"))
                ;;
            quiz)
                COMPREPLY=($(compgen -W "--questions --help" -- "$cur"))
                ;;
            search)
                COMPREPLY=($(compgen -W "--type --help" -- "$cur"))
                ;;
            analytics)
                COMPREPLY=($(compgen -W "--detailed --help" -- "$cur"))
                ;;
            *)
                COMPREPLY=($(compgen -W "$global_opts" -- "$cur"))
                ;;
        esac
    else
        case ${words[1]} in
            learn|practice|quiz)
                # Topic completion
                local topics="arrays linked-lists stacks queues trees binary-trees graphs sorting searching dynamic-programming greedy-algorithms backtracking divide-and-conquer hash-tables heaps tries"
                COMPREPLY=($(compgen -W "$topics" -- "$cur"))
                ;;
            *)
                if [[ $cword -eq 1 ]]; then
                    COMPREPLY=($(compgen -W "$commands" -- "$cur"))
                fi
                ;;
        esac
    fi
}

complete -F _adaptive_learning_completion adaptive-learning
complete -F _adaptive_learning_completion als
complete -F _adaptive_learning_completion learn
'''


def get_zsh_completion_script() -> str:
    """Generate zsh completion script."""
    return '''#compdef adaptive-learning als learn

_adaptive_learning() {
    local context state state_descr line
    typeset -A opt_args

    local commands=(
        'learn:Start an adaptive learning session'
        'practice:Practice problems for specific topic'
        'quiz:Take a quiz on algorithms and data structures'
        'progress:View learning progress and statistics'
        'recommendations:Get personalized study recommendations'
        'analytics:View detailed performance analytics'
        'topics:List all available topics'
        'search:Search for specific content'
        'config:Manage application configuration'
        'help:Show help information'
    )

    local global_opts=(
        '(--interactive -i)'{--interactive,-i}'[Start in interactive mode]'
        '(--debug -d)'{--debug,-d}'[Enable debug mode]'
        '(--verbose -v)'{--verbose,-v}'[Enable verbose output]'
        '(--config -c)'{--config,-c}'[Path to config file]:config file:_files'
        '(--profile -p)'{--profile,-p}'[User profile name]:profile:(default student teacher researcher)'
        '(--help -h)'{--help,-h}'[Show help message]'
        '(--version)'{--version}'[Show version information]'
    )

    local topics=(
        'arrays' 'linked-lists' 'stacks' 'queues' 'trees' 'binary-trees'
        'graphs' 'sorting' 'searching' 'dynamic-programming'
        'greedy-algorithms' 'backtracking' 'divide-and-conquer'
        'hash-tables' 'heaps' 'tries'
    )

    _arguments -C \\
        $global_opts \\
        '1: :->command' \\
        '*: :->args' && return

    case $state in
        command)
            _describe -t commands 'available commands' commands
            ;;
        args)
            case ${words[1]} in
                learn)
                    _arguments \\
                        '(--difficulty -d)'{--difficulty,-d}'[Set difficulty level]:difficulty:(beginner intermediate advanced)' \\
                        '(--time-limit -t)'{--time-limit,-t}'[Session time limit in minutes]:time limit:' \\
                        '1:topic:($topics)'
                    ;;
                practice)
                    _arguments \\
                        '(--count -n)'{--count,-n}'[Number of practice problems]:count:' \\
                        '(--difficulty -d)'{--difficulty,-d}'[Difficulty level]:difficulty:(beginner intermediate advanced)' \\
                        '1:topic:($topics)'
                    ;;
                quiz)
                    _arguments \\
                        '(--questions -q)'{--questions,-q}'[Number of quiz questions]:questions:' \\
                        '1:topic:($topics)'
                    ;;
                search)
                    _arguments \\
                        '(--type -t)'{--type,-t}'[Search type]:search type:(all topics problems concepts)' \\
                        '1:query:'
                    ;;
                analytics)
                    _arguments \\
                        '(--detailed -d)'{--detailed,-d}'[Show detailed analytics]'
                    ;;
            esac
            ;;
    esac
}

_adaptive_learning "$@"
'''


def get_fish_completion_script() -> str:
    """Generate fish shell completion script."""
    return '''# Fish completion for adaptive-learning

# Commands
complete -c adaptive-learning -f -a "learn practice quiz progress recommendations analytics topics search config help"
complete -c als -f -a "learn practice quiz progress recommendations analytics topics search config help"
complete -c learn -f -a "learn practice quiz progress recommendations analytics topics search config help"

# Global options
complete -c adaptive-learning -l interactive -s i -d "Start in interactive mode"
complete -c adaptive-learning -l debug -s d -d "Enable debug mode"
complete -c adaptive-learning -l verbose -s v -d "Enable verbose output"
complete -c adaptive-learning -l config -s c -d "Path to config file" -F
complete -c adaptive-learning -l profile -s p -d "User profile name" -xa "default student teacher researcher"
complete -c adaptive-learning -l help -s h -d "Show help message"
complete -c adaptive-learning -l version -d "Show version information"

# Topics
set -l topics arrays linked-lists stacks queues trees binary-trees graphs sorting searching dynamic-programming greedy-algorithms backtracking divide-and-conquer hash-tables heaps tries

# Command specific completions
complete -c adaptive-learning -n "__fish_seen_subcommand_from learn" -l difficulty -s d -xa "beginner intermediate advanced" -d "Set difficulty level"
complete -c adaptive-learning -n "__fish_seen_subcommand_from learn" -l time-limit -s t -d "Session time limit in minutes"
complete -c adaptive-learning -n "__fish_seen_subcommand_from learn" -xa "$topics" -d "Topic to learn"

complete -c adaptive-learning -n "__fish_seen_subcommand_from practice" -l count -s n -d "Number of practice problems"
complete -c adaptive-learning -n "__fish_seen_subcommand_from practice" -l difficulty -s d -xa "beginner intermediate advanced" -d "Difficulty level"
complete -c adaptive-learning -n "__fish_seen_subcommand_from practice" -xa "$topics" -d "Topic to practice"

complete -c adaptive-learning -n "__fish_seen_subcommand_from quiz" -l questions -s q -d "Number of quiz questions"
complete -c adaptive-learning -n "__fish_seen_subcommand_from quiz" -xa "$topics" -d "Quiz topic"

complete -c adaptive-learning -n "__fish_seen_subcommand_from search" -l type -s t -xa "all topics problems concepts" -d "Search type"

complete -c adaptive-learning -n "__fish_seen_subcommand_from analytics" -l detailed -s d -d "Show detailed analytics"
'''


def install_completion(shell: str = 'bash') -> str:
    """
    Generate installation instructions for shell completion.
    
    Args:
        shell: Shell type ('bash', 'zsh', 'fish')
        
    Returns:
        Installation instructions
    """
    if shell == 'bash':
        return '''
To enable bash completion, add this to your ~/.bashrc:

    eval "$(_ADAPTIVE_LEARNING_COMPLETE=bash_source adaptive-learning)"

Or save the completion script to a file and source it:

    adaptive-learning --completion bash > ~/.adaptive-learning-complete.bash
    echo "source ~/.adaptive-learning-complete.bash" >> ~/.bashrc
        '''
    
    elif shell == 'zsh':
        return '''
To enable zsh completion, add this to your ~/.zshrc:

    eval "$(_ADAPTIVE_LEARNING_COMPLETE=zsh_source adaptive-learning)"

Or save the completion script and add it to your fpath:

    adaptive-learning --completion zsh > ~/.adaptive-learning-complete.zsh
    echo "source ~/.adaptive-learning-complete.zsh" >> ~/.zshrc
        '''
    
    elif shell == 'fish':
        return '''
To enable fish completion, save the completion script:

    adaptive-learning --completion fish > ~/.config/fish/completions/adaptive-learning.fish

The completion will be automatically loaded by fish.
        '''
    
    else:
        return f"Unsupported shell: {shell}"


# Click completion integration
def complete_topic(ctx, param, incomplete):
    """Complete topic names."""
    return [topic for topic in TOPICS if topic.startswith(incomplete)]


def complete_difficulty(ctx, param, incomplete):
    """Complete difficulty levels."""
    difficulties = ['beginner', 'intermediate', 'advanced']
    return [d for d in difficulties if d.startswith(incomplete)]


def complete_search_type(ctx, param, incomplete):
    """Complete search types."""
    types = ['all', 'topics', 'problems', 'concepts']
    return [t for t in types if t.startswith(incomplete)]


# Add completion support to main CLI
def add_completion_command(cli_group):
    """Add completion command to CLI group."""
    
    @cli_group.command()
    @click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']))
    def completion(shell):
        """Generate shell completion script."""
        if shell == 'bash':
            click.echo(get_bash_completion_script())
        elif shell == 'zsh':
            click.echo(get_zsh_completion_script())
        elif shell == 'fish':
            click.echo(get_fish_completion_script())
    
    @cli_group.command()
    @click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']))
    def install_completion_cmd(shell):
        """Show completion installation instructions."""
        click.echo(install_completion(shell))