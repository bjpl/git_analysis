#!/usr/bin/env python3
"""
Progress Visualizations and Charts - Terminal-based data visualization

This module provides:
- Progress bars with various styles
- Bar charts and histograms
- Line charts with trend indicators
- Pie charts using ASCII art
- Sparklines for compact data display
- Real-time updating charts
"""

import sys
import time
import math
from typing import List, Dict, Any, Optional, Union, Tuple
from enum import Enum
from dataclasses import dataclass
import statistics


class ChartStyle(Enum):
    """Chart rendering styles"""
    BLOCKS = "blocks"
    BARS = "bars"
    DOTS = "dots"
    ASCII = "ascii"
    MINIMAL = "minimal"


class ProgressStyle(Enum):
    """Progress bar styles"""
    BLOCKS = "█▉▊▋▌▍▎▏"
    ARROWS = "►▶▷▸"
    CIRCLES = "●◉○◯"
    DOTS = "⚫⚪"
    ASCII_BLOCKS = "#="
    ASCII_BARS = "|/-\\"


@dataclass
class DataPoint:
    """Represents a single data point in a chart"""
    label: str
    value: float
    color: Optional[str] = None


class ProgressBar:
    """Advanced progress bar with animations and ETA"""
    
    def __init__(self, total: int, description: str = "",
                 style: ProgressStyle = ProgressStyle.BLOCKS,
                 width: int = 40, color_enabled: bool = True):
        """Initialize progress bar
        
        Args:
            total: Total number of items
            description: Progress description
            style: Progress bar style
            width: Bar width in characters
            color_enabled: Whether colors are supported
        """
        self.total = total
        self.description = description
        self.style = style
        self.width = width
        self.color_enabled = color_enabled
        self.current = 0
        self.start_time = time.time()
        
        # Get style characters
        if isinstance(style, ProgressStyle):
            self.chars = style.value
        else:
            self.chars = "#="
    
    def update(self, current: int) -> None:
        """Update progress bar
        
        Args:
            current: Current progress value
        """
        self.current = min(current, self.total)
        self._render()
    
    def increment(self, amount: int = 1) -> None:
        """Increment progress by amount
        
        Args:
            amount: Amount to increment
        """
        self.update(self.current + amount)
    
    def _render(self) -> None:
        """Render the progress bar"""
        # Calculate progress
        progress = self.current / self.total if self.total > 0 else 0
        filled_length = int(self.width * progress)
        
        # Calculate timing info
        elapsed = time.time() - self.start_time
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            eta = (self.total - self.current) / rate if rate > 0 else 0
            eta_str = f"ETA: {self._format_time(eta)}"
        else:
            eta_str = "ETA: --:--"
        
        # Create progress bar
        if self.style == ProgressStyle.BLOCKS:
            chars = self.chars
            filled_char = chars[0]  # Full block
            empty_char = " "
            
            # Smooth progress with partial blocks
            if len(chars) > 1:
                exact_filled = self.width * progress
                full_blocks = int(exact_filled)
                partial_progress = exact_filled - full_blocks
                
                if full_blocks < self.width and partial_progress > 0:
                    partial_chars = chars[1:]
                    partial_index = int(partial_progress * len(partial_chars))
                    partial_char = partial_chars[min(partial_index, len(partial_chars) - 1)]
                    bar = (filled_char * full_blocks + 
                          partial_char + 
                          empty_char * (self.width - full_blocks - 1))
                else:
                    bar = filled_char * filled_length + empty_char * (self.width - filled_length)
            else:
                bar = filled_char * filled_length + empty_char * (self.width - filled_length)
        
        elif self.style == ProgressStyle.ASCII_BLOCKS:
            filled_char = "#"
            empty_char = "-"
            bar = filled_char * filled_length + empty_char * (self.width - filled_length)
        
        else:
            # Other styles
            filled_char = self.chars[0] if self.chars else "#"
            empty_char = " "
            bar = filled_char * filled_length + empty_char * (self.width - filled_length)
        
        # Apply colors
        if self.color_enabled:
            if progress >= 1.0:
                bar_color = "\033[92m"  # Green
            elif progress >= 0.7:
                bar_color = "\033[93m"  # Yellow
            else:
                bar_color = "\033[96m"  # Cyan
            
            percent_color = "\033[97m"  # White
            desc_color = "\033[94m"  # Blue
            eta_color = "\033[90m"  # Gray
            
            colored_bar = f"{bar_color}{bar}\033[0m"
            colored_desc = f"{desc_color}{self.description}\033[0m" if self.description else ""
            colored_percent = f"{percent_color}{progress * 100:6.1f}%\033[0m"
            colored_eta = f"{eta_color}{eta_str}\033[0m"
            
        else:
            colored_bar = bar
            colored_desc = self.description
            colored_percent = f"{progress * 100:6.1f}%"
            colored_eta = eta_str
        
        # Format complete line
        progress_text = f"({self.current}/{self.total})"
        
        if colored_desc:
            line = f"\r{colored_desc} [{colored_bar}] {colored_percent} {progress_text} {colored_eta}"
        else:
            line = f"\r[{colored_bar}] {colored_percent} {progress_text} {colored_eta}"
        
        sys.stdout.write(line)
        sys.stdout.flush()
        
        # Print newline when complete
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS"""
        if seconds < 0 or seconds > 3600:  # More than 1 hour
            return "--:--"
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def finish(self):
        """Mark progress as complete"""
        self.update(self.total)


class BarChart:
    """Horizontal bar chart renderer"""
    
    def __init__(self, data: List[Union[DataPoint, Tuple[str, float]]],
                 title: str = "", width: int = 60,
                 style: ChartStyle = ChartStyle.BLOCKS,
                 color_enabled: bool = True):
        """Initialize bar chart
        
        Args:
            data: Chart data as DataPoint objects or (label, value) tuples
            title: Chart title
            width: Chart width in characters
            style: Chart rendering style
            color_enabled: Whether colors are supported
        """
        self.title = title
        self.width = width
        self.style = style
        self.color_enabled = color_enabled
        
        # Convert data to DataPoint objects
        self.data: List[DataPoint] = []
        for item in data:
            if isinstance(item, DataPoint):
                self.data.append(item)
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                self.data.append(DataPoint(str(item[0]), float(item[1])))
            else:
                continue
        
        # Find max value for scaling
        self.max_value = max((point.value for point in self.data), default=1)
        self.min_value = min((point.value for point in self.data), default=0)
    
    def render(self, show_values: bool = True, 
              show_grid: bool = False) -> str:
        """Render the bar chart
        
        Args:
            show_values: Whether to show numeric values
            show_grid: Whether to show grid lines
            
        Returns:
            Rendered chart as string
        """
        lines = []
        
        # Title
        if self.title:
            if self.color_enabled:
                title_line = f"\033[1;96m{self.title}\033[0m"
            else:
                title_line = self.title
            lines.append(title_line.center(self.width + 20))
            lines.append("")
        
        # Find max label length for alignment
        max_label_length = max(len(point.label) for point in self.data) if self.data else 0
        
        # Render bars
        for i, point in enumerate(self.data):
            # Calculate bar length
            if self.max_value > 0:
                bar_length = int((point.value / self.max_value) * self.width)
            else:
                bar_length = 0
            
            # Choose bar character based on style
            if self.style == ChartStyle.BLOCKS:
                bar_char = "█"
            elif self.style == ChartStyle.BARS:
                bar_char = "|"
            elif self.style == ChartStyle.DOTS:
                bar_char = "●"
            else:  # ASCII
                bar_char = "#"
            
            # Create bar
            bar = bar_char * bar_length
            
            # Apply colors
            if self.color_enabled:
                if point.color:
                    colored_bar = f"{point.color}{bar}\033[0m"
                else:
                    # Auto-color based on value
                    if point.value >= self.max_value * 0.8:
                        colored_bar = f"\033[92m{bar}\033[0m"  # Green
                    elif point.value >= self.max_value * 0.5:
                        colored_bar = f"\033[93m{bar}\033[0m"  # Yellow
                    else:
                        colored_bar = f"\033[91m{bar}\033[0m"  # Red
            else:
                colored_bar = bar
            
            # Format label
            padded_label = point.label.ljust(max_label_length)
            
            # Build line
            if show_values:
                value_str = f" {point.value:,.1f}"
            else:
                value_str = ""
            
            line = f"{padded_label} |{colored_bar}{value_str}"
            lines.append(line)
        
        # Add scale if showing grid
        if show_grid and self.data:
            lines.append("")
            scale_line = " " * max_label_length + " |"
            
            # Add scale markers
            for i in range(0, self.width + 1, self.width // 5):
                if i == 0:
                    scale_line += "0"
                else:
                    value = (i / self.width) * self.max_value
                    scale_line += f"{value:,.0f}".rjust(self.width // 5)
            
            lines.append(scale_line)
        
        return "\n".join(lines)
    
    def print(self, **kwargs):
        """Print the chart to stdout"""
        print(self.render(**kwargs))


class LineChart:
    """ASCII line chart with trend indicators"""
    
    def __init__(self, data: List[Union[float, Tuple[str, float]]],
                 title: str = "", width: int = 60, height: int = 15,
                 color_enabled: bool = True):
        """Initialize line chart
        
        Args:
            data: Chart data as values or (label, value) tuples
            title: Chart title
            width: Chart width in characters
            height: Chart height in characters
            color_enabled: Whether colors are supported
        """
        self.title = title
        self.width = width
        self.height = height
        self.color_enabled = color_enabled
        
        # Process data
        self.values: List[float] = []
        self.labels: List[str] = []
        
        for i, item in enumerate(data):
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                self.labels.append(str(item[0]))
                self.values.append(float(item[1]))
            else:
                self.labels.append(str(i))
                self.values.append(float(item))
        
        if not self.values:
            self.values = [0]
            self.labels = ["0"]
        
        self.max_value = max(self.values)
        self.min_value = min(self.values)
        self.value_range = self.max_value - self.min_value if self.max_value != self.min_value else 1
    
    def render(self, show_trend: bool = True, 
              show_points: bool = True) -> str:
        """Render the line chart
        
        Args:
            show_trend: Whether to show trend arrow
            show_points: Whether to show data points
            
        Returns:
            Rendered chart as string
        """
        lines = []
        
        # Title
        if self.title:
            if self.color_enabled:
                title_line = f"\033[1;96m{self.title}\033[0m"
            else:
                title_line = self.title
            lines.append(title_line.center(self.width))
            lines.append("")
        
        # Create chart grid
        chart_lines = [list(" " * self.width) for _ in range(self.height)]
        
        # Plot points and lines
        for i in range(len(self.values)):
            # Calculate position
            x = int((i / (len(self.values) - 1)) * (self.width - 1)) if len(self.values) > 1 else 0
            y = int(((self.values[i] - self.min_value) / self.value_range) * (self.height - 1))
            y = self.height - 1 - y  # Flip Y axis
            
            # Plot point
            if show_points:
                if self.color_enabled:
                    chart_lines[y][x] = "●"
                else:
                    chart_lines[y][x] = "*"
            
            # Draw line to next point
            if i < len(self.values) - 1:
                next_x = int(((i + 1) / (len(self.values) - 1)) * (self.width - 1))
                next_y = int(((self.values[i + 1] - self.min_value) / self.value_range) * (self.height - 1))
                next_y = self.height - 1 - next_y
                
                # Simple line drawing
                self._draw_line(chart_lines, x, y, next_x, next_y)
        
        # Convert chart to strings with colors
        for i, line in enumerate(chart_lines):
            line_str = "".join(line)
            
            if self.color_enabled:
                # Color the line based on position (gradient)
                colored_line = ""
                for char in line_str:
                    if char in "●*|-/\\":
                        height_ratio = (self.height - i) / self.height
                        if height_ratio > 0.7:
                            colored_line += f"\033[92m{char}\033[0m"  # Green
                        elif height_ratio > 0.3:
                            colored_line += f"\033[93m{char}\033[0m"  # Yellow
                        else:
                            colored_line += f"\033[91m{char}\033[0m"  # Red
                    else:
                        colored_line += char
                lines.append(colored_line)
            else:
                lines.append(line_str)
        
        # Add Y-axis labels
        if len(lines) >= self.height:
            lines[0] += f" {self.max_value:>8.1f}"
            lines[self.height // 2] += f" {(self.max_value + self.min_value) / 2:>8.1f}"
            lines[self.height - 1] += f" {self.min_value:>8.1f}"
        
        # Add trend indicator
        if show_trend and len(self.values) >= 2:
            trend = "↗" if self.values[-1] > self.values[0] else "↘" if self.values[-1] < self.values[0] else "→"
            trend_text = f"Trend: {trend}"
            
            if self.color_enabled:
                if trend == "↗":
                    trend_colored = f"\033[92m{trend_text}\033[0m"
                elif trend == "↘":
                    trend_colored = f"\033[91m{trend_text}\033[0m"
                else:
                    trend_colored = f"\033[93m{trend_text}\033[0m"
            else:
                trend_colored = trend_text
            
            lines.append("")
            lines.append(trend_colored)
        
        return "\n".join(lines)
    
    def _draw_line(self, chart: List[List[str]], x1: int, y1: int, x2: int, y2: int):
        """Draw a line between two points using simple ASCII characters"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        if dx > dy:
            # Horizontal line
            char = "-"
            start_x, end_x = (x1, x2) if x1 < x2 else (x2, x1)
            y = y1
            for x in range(start_x + 1, end_x):
                if 0 <= x < len(chart[0]) and 0 <= y < len(chart):
                    chart[y][x] = char
        else:
            # Vertical or diagonal line
            if y1 == y2:
                char = "-"
            elif x1 == x2:
                char = "|"
            else:
                char = "/" if (x2 > x1) == (y2 < y1) else "\\"
            
            steps = max(dx, dy)
            if steps > 0:
                for i in range(1, steps):
                    x = x1 + (x2 - x1) * i // steps
                    y = y1 + (y2 - y1) * i // steps
                    if 0 <= x < len(chart[0]) and 0 <= y < len(chart):
                        chart[y][x] = char
    
    def print(self, **kwargs):
        """Print the chart to stdout"""
        print(self.render(**kwargs))


class PieChart:
    """ASCII pie chart representation"""
    
    def __init__(self, data: List[Union[DataPoint, Tuple[str, float]]],
                 title: str = "", color_enabled: bool = True):
        """Initialize pie chart
        
        Args:
            data: Chart data as DataPoint objects or (label, value) tuples
            title: Chart title
            color_enabled: Whether colors are supported
        """
        self.title = title
        self.color_enabled = color_enabled
        
        # Convert data to DataPoint objects
        self.data: List[DataPoint] = []
        for item in data:
            if isinstance(item, DataPoint):
                self.data.append(item)
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                self.data.append(DataPoint(str(item[0]), float(item[1])))
        
        # Calculate total and percentages
        self.total = sum(point.value for point in self.data) if self.data else 1
        
        # Pie chart characters for different segments
        self.pie_chars = ["█", "▉", "▊", "▋", "▌", "▍", "▎", "▏"]
    
    def render(self) -> str:
        """Render the pie chart as a horizontal bar representation
        
        Returns:
            Rendered chart as string
        """
        lines = []
        
        # Title
        if self.title:
            if self.color_enabled:
                title_line = f"\033[1;96m{self.title}\033[0m"
            else:
                title_line = self.title
            lines.append(title_line)
            lines.append("")
        
        # Calculate percentages and create segments
        total_width = 50
        segments = []
        
        for i, point in enumerate(self.data):
            percentage = (point.value / self.total) * 100
            width = int((point.value / self.total) * total_width)
            
            # Choose color
            if self.color_enabled:
                colors = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"]
                color = colors[i % len(colors)]
                segment = f"{color}{'█' * width}\033[0m"
            else:
                chars = ["#", "=", "-", ".", "+", "*"]
                char = chars[i % len(chars)]
                segment = char * width
            
            segments.append(segment)
            
            # Add legend entry
            legend_line = f"  {segment[:1] if not self.color_enabled else '█'} {point.label}: {point.value:,.1f} ({percentage:.1f}%)"
            if self.color_enabled and i < len(colors):
                legend_line = f"  {colors[i % len(colors)]}█\033[0m {point.label}: {point.value:,.1f} ({percentage:.1f}%)"
            lines.append(legend_line)
        
        # Add the pie visualization
        lines.insert(-len(self.data), "")
        lines.insert(-len(self.data), "".join(segments))
        lines.insert(-len(self.data), "")
        
        return "\n".join(lines)
    
    def print(self):
        """Print the chart to stdout"""
        print(self.render())


class Sparkline:
    """Compact sparkline chart for inline data visualization"""
    
    def __init__(self, data: List[float], color_enabled: bool = True):
        """Initialize sparkline
        
        Args:
            data: Data values
            color_enabled: Whether colors are supported
        """
        self.data = data or [0]
        self.color_enabled = color_enabled
        
        # Sparkline characters (Unicode block elements)
        self.spark_chars = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        
        # Calculate min/max for scaling
        self.min_val = min(self.data)
        self.max_val = max(self.data)
        self.range_val = self.max_val - self.min_val if self.max_val != self.min_val else 1
    
    def render(self, show_stats: bool = False) -> str:
        """Render the sparkline
        
        Args:
            show_stats: Whether to include statistics
            
        Returns:
            Rendered sparkline
        """
        # Generate sparkline
        spark = ""
        for value in self.data:
            # Normalize to 0-8 range for character selection
            normalized = ((value - self.min_val) / self.range_val) * (len(self.spark_chars) - 1)
            char_index = min(int(normalized), len(self.spark_chars) - 1)
            char = self.spark_chars[char_index]
            
            # Apply color based on value
            if self.color_enabled:
                if normalized >= len(self.spark_chars) * 0.75:
                    spark += f"\033[92m{char}\033[0m"  # Green
                elif normalized >= len(self.spark_chars) * 0.5:
                    spark += f"\033[93m{char}\033[0m"  # Yellow
                elif normalized >= len(self.spark_chars) * 0.25:
                    spark += f"\033[91m{char}\033[0m"  # Red
                else:
                    spark += f"\033[94m{char}\033[0m"  # Blue
            else:
                spark += char
        
        if show_stats:
            avg = statistics.mean(self.data)
            stats = f" min:{self.min_val:.1f} max:{self.max_val:.1f} avg:{avg:.1f}"
            return spark + stats
        
        return spark
    
    def print(self, **kwargs):
        """Print the sparkline to stdout"""
        print(self.render(**kwargs))


# Convenience functions
def progress_bar(total: int, description: str = "",
                style: ProgressStyle = ProgressStyle.BLOCKS) -> ProgressBar:
    """Create a progress bar
    
    Args:
        total: Total items
        description: Description text
        style: Progress bar style
        
    Returns:
        ProgressBar instance
    """
    return ProgressBar(total, description, style)


def bar_chart(data: List[Union[DataPoint, Tuple[str, float]]],
             title: str = "", **kwargs) -> BarChart:
    """Create a bar chart
    
    Args:
        data: Chart data
        title: Chart title
        **kwargs: Additional arguments
        
    Returns:
        BarChart instance
    """
    return BarChart(data, title, **kwargs)


def line_chart(data: List[Union[float, Tuple[str, float]]],
              title: str = "", **kwargs) -> LineChart:
    """Create a line chart
    
    Args:
        data: Chart data
        title: Chart title
        **kwargs: Additional arguments
        
    Returns:
        LineChart instance
    """
    return LineChart(data, title, **kwargs)


def pie_chart(data: List[Union[DataPoint, Tuple[str, float]]],
             title: str = "") -> PieChart:
    """Create a pie chart
    
    Args:
        data: Chart data
        title: Chart title
        
    Returns:
        PieChart instance
    """
    return PieChart(data, title)


def sparkline(data: List[float]) -> Sparkline:
    """Create a sparkline
    
    Args:
        data: Data values
        
    Returns:
        Sparkline instance
    """
    return Sparkline(data)