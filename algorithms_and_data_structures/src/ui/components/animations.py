#!/usr/bin/env python3
"""
Terminal Animations - Beautiful loading animations and effects

This module provides:
- Loading spinners with multiple styles
- Progress animations
- Text typing effects
- Smooth transitions
- Cross-platform compatibility
"""

import asyncio
import sys
import time
import threading
from typing import Optional, List, Callable, Union
from enum import Enum
import random
import os


class SpinnerStyle(Enum):
    """Different spinner animation styles"""
    DOTS = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    DOTS2 = "⣾⣽⣻⢿⡿⣟⣯⣷"
    CIRCLES = "◐◓◑◒"
    ARROWS = "←↖↑↗→↘↓↙"
    BARS = "▁▃▄▅▆▇█▇▆▅▄▃"
    BLOCKS = "▖▘▝▗"
    BOUNCE = "⠁⠂⠄⠂"
    CLOCK = "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛"
    MOON = "🌑🌒🌓🌔🌕🌖🌗🌘"
    EARTH = "🌍🌎🌏"
    
    # ASCII-only options for compatibility
    ASCII_DOTS = ".oO@*"
    ASCII_BARS = "|/-\\"
    ASCII_ARROWS = "<^>v"
    ASCII_BLOCKS = "[]{}()"


class AnimationSpeed(Enum):
    """Animation speed presets"""
    SLOW = 0.2
    NORMAL = 0.1
    FAST = 0.05
    VERY_FAST = 0.02


class ProgressStyle(Enum):
    """Progress bar animation styles"""
    BLOCKS = "█▉▊▋▌▍▎▏"
    DOTS = "●◉○◯"
    ARROWS = "►▶▷▸"
    WAVES = "~≈∼≋"
    ASCII_BLOCKS = "#="
    ASCII_DOTS = "*o."


class LoadingAnimation:
    """Manages loading animations and spinners"""
    
    def __init__(self, style: SpinnerStyle = SpinnerStyle.DOTS, 
                 speed: AnimationSpeed = AnimationSpeed.NORMAL,
                 color_enabled: bool = True):
        """Initialize loading animation
        
        Args:
            style: Spinner style to use
            speed: Animation speed
            color_enabled: Whether colors are supported
        """
        self.style = style
        self.speed = speed.value
        self.color_enabled = color_enabled
        self.active = False
        self.thread: Optional[threading.Thread] = None
        self.message = ""
        
        # Auto-detect if we should use ASCII fallbacks
        if not self._supports_unicode():
            self._fallback_to_ascii()
    
    def _supports_unicode(self) -> bool:
        """Check if terminal supports Unicode characters"""
        try:
            # Try to encode some Unicode characters
            test_chars = "⠋◐▁🌑"
            for char in test_chars:
                char.encode(sys.stdout.encoding or 'utf-8')
            return True
        except (UnicodeEncodeError, LookupError):
            return False
    
    def _fallback_to_ascii(self):
        """Fallback to ASCII-compatible spinners"""
        ascii_map = {
            SpinnerStyle.DOTS: SpinnerStyle.ASCII_DOTS,
            SpinnerStyle.DOTS2: SpinnerStyle.ASCII_DOTS,
            SpinnerStyle.CIRCLES: SpinnerStyle.ASCII_BLOCKS,
            SpinnerStyle.ARROWS: SpinnerStyle.ASCII_ARROWS,
            SpinnerStyle.BARS: SpinnerStyle.ASCII_BARS,
            SpinnerStyle.BLOCKS: SpinnerStyle.ASCII_BLOCKS,
            SpinnerStyle.BOUNCE: SpinnerStyle.ASCII_DOTS,
            SpinnerStyle.CLOCK: SpinnerStyle.ASCII_BARS,
            SpinnerStyle.MOON: SpinnerStyle.ASCII_BLOCKS,
            SpinnerStyle.EARTH: SpinnerStyle.ASCII_BLOCKS,
        }
        
        if self.style in ascii_map:
            self.style = ascii_map[self.style]
    
    def spinner(self, message: str = "Loading...") -> 'SpinnerContext':
        """Create a spinner context manager
        
        Args:
            message: Message to display with spinner
            
        Returns:
            Spinner context manager
        """
        return SpinnerContext(self, message)
    
    def progress_bar(self, total: int, description: str = "",
                    style: ProgressStyle = ProgressStyle.BLOCKS) -> 'AnimatedProgressBar':
        """Create an animated progress bar
        
        Args:
            total: Total number of items
            description: Progress description
            style: Progress bar style
            
        Returns:
            Animated progress bar instance
        """
        return AnimatedProgressBar(self, total, description, style)
    
    async def typewriter(self, text: str, speed: float = 0.05,
                        cursor: str = "▌", color_code: str = "") -> None:
        """Display text with typewriter effect
        
        Args:
            text: Text to display
            speed: Typing speed in seconds per character
            cursor: Cursor character
            color_code: ANSI color code to apply
        """
        if not self.color_enabled:
            print(text)
            return
        
        # Hide cursor
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
        
        try:
            displayed = ""
            
            for char in text:
                displayed += char
                
                # Display current text with cursor
                if color_code:
                    line = f"\r{color_code}{displayed}{cursor}\033[0m"
                else:
                    line = f"\r{displayed}{cursor}"
                
                sys.stdout.write(line)
                sys.stdout.flush()
                
                # Variable speed based on character type
                if char in '.!?':
                    await asyncio.sleep(speed * 3)
                elif char in ',;:':
                    await asyncio.sleep(speed * 2)
                elif char == ' ':
                    await asyncio.sleep(speed * 0.5)
                else:
                    await asyncio.sleep(speed)
            
            # Final display without cursor
            if color_code:
                sys.stdout.write(f"\r{color_code}{displayed}\033[0m\n")
            else:
                sys.stdout.write(f"\r{displayed}\n")
            sys.stdout.flush()
            
        finally:
            # Show cursor
            sys.stdout.write('\033[?25h')
            sys.stdout.flush()
    
    async def matrix_rain(self, duration: float = 3.0, width: int = 80) -> None:
        """Display Matrix-style digital rain effect
        
        Args:
            duration: How long to run the effect
            width: Terminal width
        """
        if not self.color_enabled:
            return
        
        # Characters for the rain
        chars = "01" if not self._supports_unicode() else "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
        
        # Initialize streams
        streams = []
        for _ in range(width // 3):
            streams.append({
                'x': random.randint(0, width - 1),
                'y': random.randint(-20, 0),
                'speed': random.uniform(0.5, 2.0),
                'length': random.randint(5, 15),
                'chars': [random.choice(chars) for _ in range(15)]
            })
        
        start_time = time.time()
        
        # Hide cursor
        sys.stdout.write('\033[?25l')
        
        try:
            while time.time() - start_time < duration:
                # Clear screen
                sys.stdout.write('\033[2J\033[H')
                
                # Update and draw streams
                screen = [[' ' for _ in range(width)] for _ in range(25)]
                
                for stream in streams:
                    stream['y'] += stream['speed']
                    
                    # Reset stream if it's gone off screen
                    if stream['y'] > 25 + stream['length']:
                        stream['y'] = random.randint(-20, -5)
                        stream['x'] = random.randint(0, width - 1)
                    
                    # Draw stream
                    for i in range(stream['length']):
                        y = int(stream['y'] - i)
                        if 0 <= y < 25 and 0 <= stream['x'] < width:
                            char = stream['chars'][i % len(stream['chars'])]
                            
                            # Color intensity based on position in stream
                            if i == 0:  # Head - bright white
                                screen[y][stream['x']] = f"\033[97m{char}\033[0m"
                            elif i < 3:  # Near head - bright green
                                screen[y][stream['x']] = f"\033[92m{char}\033[0m"
                            else:  # Tail - dim green
                                screen[y][stream['x']] = f"\033[32m{char}\033[0m"
                
                # Print screen
                for row in screen:
                    sys.stdout.write(''.join(row) + '\n')
                
                sys.stdout.flush()
                await asyncio.sleep(0.1)
                
        finally:
            # Show cursor and clear
            sys.stdout.write('\033[?25h\033[2J\033[H')
            sys.stdout.flush()
    
    async def wave_text(self, text: str, duration: float = 2.0) -> None:
        """Display text with wave animation effect
        
        Args:
            text: Text to animate
            duration: Animation duration
        """
        if not self.color_enabled:
            print(text)
            return
        
        # Hide cursor
        sys.stdout.write('\033[?25l')
        
        try:
            start_time = time.time()
            
            while time.time() - start_time < duration:
                line = ""
                current_time = time.time() - start_time
                
                for i, char in enumerate(text):
                    if char == ' ':
                        line += char
                        continue
                    
                    # Calculate wave offset
                    wave_offset = int(3 * abs(
                        __import__('math').sin(current_time * 3 + i * 0.5)
                    ))
                    
                    # Add vertical spacing
                    if wave_offset == 0:
                        line += f"\033[92m{char}\033[0m"  # Green
                    elif wave_offset == 1:
                        line += f"\033[93m{char}\033[0m"  # Yellow
                    else:
                        line += f"\033[91m{char}\033[0m"  # Red
                
                sys.stdout.write(f"\r{line}")
                sys.stdout.flush()
                await asyncio.sleep(0.1)
            
            # Final display
            sys.stdout.write(f"\r\033[96m{text}\033[0m\n")
            sys.stdout.flush()
            
        finally:
            # Show cursor
            sys.stdout.write('\033[?25h')
            sys.stdout.flush()
    
    async def slide_in_text(self, text: str, direction: str = "left",
                           duration: float = 1.0) -> None:
        """Slide text in from specified direction
        
        Args:
            text: Text to slide in
            direction: Direction to slide from ("left", "right", "top", "bottom")
            duration: Animation duration
        """
        if not self.color_enabled:
            print(text)
            return
        
        steps = 20
        delay = duration / steps
        
        # Hide cursor
        sys.stdout.write('\033[?25l')
        
        try:
            if direction == "left":
                for i in range(steps + 1):
                    offset = len(text) - int((len(text) * i) / steps)
                    visible_text = text[offset:] if offset < len(text) else ""
                    padding = " " * offset
                    
                    sys.stdout.write(f"\r{padding}{visible_text}")
                    sys.stdout.flush()
                    await asyncio.sleep(delay)
            
            elif direction == "right":
                for i in range(steps + 1):
                    visible_length = int((len(text) * i) / steps)
                    visible_text = text[:visible_length]
                    
                    sys.stdout.write(f"\r{visible_text}")
                    sys.stdout.flush()
                    await asyncio.sleep(delay)
            
            # Add newline at the end
            sys.stdout.write("\n")
            sys.stdout.flush()
            
        finally:
            # Show cursor
            sys.stdout.write('\033[?25h')
            sys.stdout.flush()


class SpinnerContext:
    """Context manager for spinner animations"""
    
    def __init__(self, animation: LoadingAnimation, message: str):
        self.animation = animation
        self.message = message
        self.active = False
        self.thread: Optional[threading.Thread] = None
    
    def __enter__(self):
        if not self.animation.color_enabled:
            print(f"{self.message}")
            return self
        
        self.active = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active = False
        if self.thread:
            self.thread.join(timeout=0.2)
        
        # Clear the line
        if self.animation.color_enabled:
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
            sys.stdout.flush()
    
    def update_message(self, message: str):
        """Update the spinner message"""
        self.message = message
    
    def _animate(self):
        """Run the spinner animation"""
        chars = self.animation.style.value
        i = 0
        
        while self.active:
            char = chars[i % len(chars)]
            
            if self.animation.color_enabled:
                # Color the spinner
                colored_char = f"\033[96m{char}\033[0m"  # Cyan
                colored_message = f"\033[97m{self.message}\033[0m"  # White
                line = f"\r{colored_char} {colored_message}"
            else:
                line = f"\r{char} {self.message}"
            
            sys.stdout.write(line)
            sys.stdout.flush()
            
            time.sleep(self.animation.speed)
            i += 1


class AnimatedProgressBar:
    """Animated progress bar with various visual effects"""
    
    def __init__(self, animation: LoadingAnimation, total: int,
                 description: str, style: ProgressStyle):
        self.animation = animation
        self.total = total
        self.description = description
        self.style = style
        self.current = 0
        self.bar_length = 40
        self.start_time = time.time()
    
    def update(self, amount: int = 1) -> None:
        """Update progress bar
        
        Args:
            amount: Amount to increment
        """
        self.current = min(self.current + amount, self.total)
        self._render()
    
    def set_progress(self, current: int) -> None:
        """Set absolute progress
        
        Args:
            current: Current progress value
        """
        self.current = min(max(current, 0), self.total)
        self._render()
    
    def _render(self) -> None:
        """Render the progress bar"""
        if not self.animation.color_enabled:
            percent = (self.current / self.total) * 100 if self.total > 0 else 0
            sys.stdout.write(f"\r{self.description}: {self.current}/{self.total} ({percent:.1f}%)")
            sys.stdout.flush()
            return
        
        # Calculate progress
        percent = self.current / self.total if self.total > 0 else 0
        filled_length = int(self.bar_length * percent)
        
        # Calculate ETA
        elapsed = time.time() - self.start_time
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            eta_seconds = (self.total - self.current) / rate if rate > 0 else 0
            eta_str = f"ETA: {eta_seconds:.0f}s" if eta_seconds > 0 else "ETA: --"
        else:
            eta_str = "ETA: --"
        
        # Create progress bar based on style
        if self.style == ProgressStyle.BLOCKS:
            chars = self.style.value
            filled_char = chars[0]  # Full block
            partial_chars = chars[1:]  # Partial blocks
            empty_char = " "
            
            # Calculate partial progress for smoother animation
            exact_filled = self.bar_length * percent
            full_blocks = int(exact_filled)
            partial_progress = exact_filled - full_blocks
            
            if full_blocks < self.bar_length and partial_progress > 0:
                partial_index = int(partial_progress * len(partial_chars))
                partial_char = partial_chars[min(partial_index, len(partial_chars) - 1)]
                bar = (filled_char * full_blocks + 
                      partial_char + 
                      empty_char * (self.bar_length - full_blocks - 1))
            else:
                bar = (filled_char * filled_length + 
                      empty_char * (self.bar_length - filled_length))
        
        elif self.style == ProgressStyle.ASCII_BLOCKS:
            filled_char = "#"
            empty_char = "-"
            bar = filled_char * filled_length + empty_char * (self.bar_length - filled_length)
        
        else:
            # Other styles - use first character as filled, space as empty
            chars = self.style.value
            filled_char = chars[0]
            empty_char = " "
            bar = filled_char * filled_length + empty_char * (self.bar_length - filled_length)
        
        # Color the progress bar
        if percent >= 1.0:
            bar_color = "\033[92m"  # Green when complete
        elif percent >= 0.7:
            bar_color = "\033[93m"  # Yellow
        else:
            bar_color = "\033[96m"  # Cyan
        
        # Format percentage with color
        percent_val = percent * 100
        if percent_val >= 100:
            percent_color = "\033[92m"  # Green
        elif percent_val >= 70:
            percent_color = "\033[93m"  # Yellow
        else:
            percent_color = "\033[91m"  # Red
        
        # Build the complete line
        desc_colored = f"\033[97m{self.description}\033[0m"
        bar_colored = f"{bar_color}{bar}\033[0m"
        percent_colored = f"{percent_color}{percent_val:6.1f}%\033[0m"
        progress_text = f"\033[90m({self.current}/{self.total})\033[0m"
        eta_colored = f"\033[94m{eta_str}\033[0m"
        
        line = f"\r{desc_colored} [{bar_colored}] {percent_colored} {progress_text} {eta_colored}"
        
        sys.stdout.write(line)
        sys.stdout.flush()
        
        # Print newline when complete
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()
    
    def finish(self):
        """Mark progress as complete"""
        self.current = self.total
        self._render()


# Convenience functions
async def spinner_task(coro, message: str = "Loading...", 
                      style: SpinnerStyle = SpinnerStyle.DOTS) -> any:
    """Run a coroutine with a spinner
    
    Args:
        coro: Coroutine to run
        message: Spinner message
        style: Spinner style
        
    Returns:
        Result of the coroutine
    """
    animation = LoadingAnimation(style)
    
    with animation.spinner(message):
        return await coro


def create_spinner(style: SpinnerStyle = SpinnerStyle.DOTS,
                  speed: AnimationSpeed = AnimationSpeed.NORMAL) -> LoadingAnimation:
    """Create a new loading animation instance
    
    Args:
        style: Spinner style
        speed: Animation speed
        
    Returns:
        LoadingAnimation instance
    """
    return LoadingAnimation(style, speed)