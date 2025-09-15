#!/usr/bin/env python3
"""
Formatted Data Tables - Beautiful table rendering with sorting and formatting

This module provides:
- Rich table formatting with borders
- Column sorting and filtering
- Data type-aware formatting
- Responsive column sizing
- Color-coded cells
- Export capabilities
"""

import sys
import re
from typing import List, Dict, Any, Optional, Union, Callable, Tuple
from enum import Enum
from dataclasses import dataclass
import json
import csv
from io import StringIO


class TableStyle(Enum):
    """Table border styles"""
    SIMPLE = "simple"
    DOUBLE = "double"
    ROUNDED = "rounded"
    HEAVY = "heavy"
    ASCII = "ascii"
    MINIMAL = "minimal"
    GRID = "grid"


class ColumnAlignment(Enum):
    """Column text alignment options"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    AUTO = "auto"  # Auto-detect based on data type


class SortDirection(Enum):
    """Sort direction options"""
    ASC = "asc"
    DESC = "desc"


@dataclass
class ColumnConfig:
    """Configuration for a table column"""
    name: str
    title: Optional[str] = None
    width: Optional[int] = None
    alignment: ColumnAlignment = ColumnAlignment.AUTO
    formatter: Optional[Callable[[Any], str]] = None
    sortable: bool = True
    color_func: Optional[Callable[[Any], str]] = None  # Returns ANSI color code


class DataTable:
    """Rich data table with formatting and sorting capabilities"""
    
    def __init__(self, data: List[Dict[str, Any]], 
                 style: TableStyle = TableStyle.SIMPLE,
                 color_enabled: bool = True,
                 max_width: Optional[int] = None):
        """Initialize data table
        
        Args:
            data: List of data dictionaries
            style: Table border style
            color_enabled: Whether colors are supported
            max_width: Maximum table width (auto-detect if None)
        """
        self.data = data or []
        self.style = style
        self.color_enabled = color_enabled
        self.max_width = max_width or self._get_terminal_width()
        
        # Column configurations
        self.columns: Dict[str, ColumnConfig] = {}
        
        # Sorting state
        self.sort_column: Optional[str] = None
        self.sort_direction: SortDirection = SortDirection.ASC
        
        # Initialize default columns from data
        if self.data:
            for key in self.data[0].keys():
                self.columns[key] = ColumnConfig(name=key)
        
        # Style characters
        self.chars = self._get_style_chars()
    
    def _get_terminal_width(self) -> int:
        """Get terminal width"""
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except (AttributeError, OSError):
            return 80
    
    def _get_style_chars(self) -> Dict[str, str]:
        """Get border characters for the current style"""
        if self.style == TableStyle.DOUBLE:
            return {
                'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
                'h': '═', 'v': '║', 'cross': '╬',
                'tee_down': '╦', 'tee_up': '╩',
                'tee_right': '╠', 'tee_left': '╣'
            }
        elif self.style == TableStyle.ROUNDED:
            return {
                'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯',
                'h': '─', 'v': '│', 'cross': '┼',
                'tee_down': '┬', 'tee_up': '┴',
                'tee_right': '├', 'tee_left': '┤'
            }
        elif self.style == TableStyle.HEAVY:
            return {
                'tl': '┏', 'tr': '┓', 'bl': '┗', 'br': '┛',
                'h': '━', 'v': '┃', 'cross': '╋',
                'tee_down': '┳', 'tee_up': '┻',
                'tee_right': '┣', 'tee_left': '┫'
            }
        elif self.style == TableStyle.ASCII:
            return {
                'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
                'h': '-', 'v': '|', 'cross': '+',
                'tee_down': '+', 'tee_up': '+',
                'tee_right': '+', 'tee_left': '+'
            }
        elif self.style == TableStyle.MINIMAL:
            return {
                'tl': ' ', 'tr': ' ', 'bl': ' ', 'br': ' ',
                'h': ' ', 'v': ' ', 'cross': ' ',
                'tee_down': ' ', 'tee_up': ' ',
                'tee_right': ' ', 'tee_left': ' '
            }
        elif self.style == TableStyle.GRID:
            return {
                'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
                'h': '─', 'v': '│', 'cross': '┼',
                'tee_down': '┬', 'tee_up': '┴',
                'tee_right': '├', 'tee_left': '┤'
            }
        else:  # SIMPLE
            return {
                'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
                'h': '─', 'v': '│', 'cross': '┼',
                'tee_down': '┬', 'tee_up': '┴',
                'tee_right': '├', 'tee_left': '┤'
            }
    
    def configure_column(self, name: str, title: Optional[str] = None,
                        width: Optional[int] = None, 
                        alignment: ColumnAlignment = ColumnAlignment.AUTO,
                        formatter: Optional[Callable[[Any], str]] = None,
                        sortable: bool = True,
                        color_func: Optional[Callable[[Any], str]] = None) -> 'DataTable':
        """Configure a table column
        
        Args:
            name: Column name (key in data)
            title: Display title (uses name if None)
            width: Fixed column width
            alignment: Text alignment
            formatter: Value formatting function
            sortable: Whether column can be sorted
            color_func: Function to determine cell color
            
        Returns:
            Self for method chaining
        """
        if name not in self.columns:
            self.columns[name] = ColumnConfig(name=name)
        
        col = self.columns[name]
        if title is not None:
            col.title = title
        if width is not None:
            col.width = width
        col.alignment = alignment
        if formatter is not None:
            col.formatter = formatter
        col.sortable = sortable
        if color_func is not None:
            col.color_func = color_func
        
        return self
    
    def sort_by(self, column: str, direction: SortDirection = SortDirection.ASC) -> 'DataTable':
        """Sort table by column
        
        Args:
            column: Column name to sort by
            direction: Sort direction
            
        Returns:
            Self for method chaining
        """
        if column not in self.columns or not self.columns[column].sortable:
            return self
        
        self.sort_column = column
        self.sort_direction = direction
        
        # Sort the data
        reverse = direction == SortDirection.DESC
        
        def sort_key(row):
            value = row.get(column)
            if value is None:
                return ""
            
            # Try to convert to number for numeric sorting
            try:
                return float(str(value).replace(',', '').replace('$', ''))
            except (ValueError, TypeError):
                return str(value).lower()
        
        self.data.sort(key=sort_key, reverse=reverse)
        return self
    
    def filter_rows(self, predicate: Callable[[Dict[str, Any]], bool]) -> 'DataTable':
        """Filter table rows based on predicate
        
        Args:
            predicate: Function that returns True for rows to keep
            
        Returns:
            New DataTable with filtered data
        """
        filtered_data = [row for row in self.data if predicate(row)]
        new_table = DataTable(filtered_data, self.style, self.color_enabled, self.max_width)
        new_table.columns = self.columns.copy()
        return new_table
    
    def _calculate_column_widths(self, visible_columns: List[str]) -> Dict[str, int]:
        """Calculate optimal column widths"""
        widths = {}
        
        # Calculate minimum widths needed
        for col_name in visible_columns:
            col = self.columns[col_name]
            title = col.title or col_name
            
            # Start with title width
            min_width = len(title)
            
            # Check data widths
            for row in self.data:
                value = row.get(col_name, "")
                if col.formatter:
                    formatted = col.formatter(value)
                else:
                    formatted = str(value)
                
                # Remove ANSI codes for width calculation
                clean_formatted = re.sub(r'\033\[[0-9;]*m', '', formatted)
                min_width = max(min_width, len(clean_formatted))
            
            widths[col_name] = min_width
        
        # Apply fixed widths
        for col_name in visible_columns:
            col = self.columns[col_name]
            if col.width:
                widths[col_name] = col.width
        
        # Adjust for maximum table width
        total_width = sum(widths.values()) + len(visible_columns) * 3 + 1  # borders and padding
        
        if total_width > self.max_width:
            # Proportionally reduce column widths
            available_width = self.max_width - len(visible_columns) * 3 - 1
            total_content_width = sum(widths.values())
            
            for col_name in visible_columns:
                if not self.columns[col_name].width:  # Don't resize fixed-width columns
                    ratio = widths[col_name] / total_content_width
                    widths[col_name] = max(3, int(available_width * ratio))
        
        return widths
    
    def _format_cell_value(self, value: Any, column: ColumnConfig, width: int) -> str:
        """Format a cell value with alignment and truncation"""
        # Apply custom formatter
        if column.formatter:
            formatted = column.formatter(value)
        else:
            formatted = str(value) if value is not None else ""
        
        # Remove ANSI codes for length calculation
        clean_formatted = re.sub(r'\033\[[0-9;]*m', '', formatted)
        
        # Truncate if too long
        if len(clean_formatted) > width:
            # Keep ANSI codes but truncate visible content
            if '\033[' in formatted:
                # Complex case with ANSI codes
                truncated = self._truncate_with_ansi(formatted, width - 3) + "..."
            else:
                truncated = clean_formatted[:width - 3] + "..."
        else:
            truncated = formatted
        
        # Apply alignment
        clean_truncated = re.sub(r'\033\[[0-9;]*m', '', truncated)
        padding_needed = width - len(clean_truncated)
        
        if column.alignment == ColumnAlignment.CENTER:
            left_pad = padding_needed // 2
            right_pad = padding_needed - left_pad
            result = " " * left_pad + truncated + " " * right_pad
        elif column.alignment == ColumnAlignment.RIGHT or (
            column.alignment == ColumnAlignment.AUTO and self._is_numeric(value)
        ):
            result = " " * padding_needed + truncated
        else:  # LEFT or AUTO (non-numeric)
            result = truncated + " " * padding_needed
        
        return result
    
    def _truncate_with_ansi(self, text: str, max_length: int) -> str:
        """Truncate text while preserving ANSI codes"""
        visible_length = 0
        result = ""
        in_ansi = False
        
        for char in text:
            if char == '\033':
                in_ansi = True
                result += char
            elif in_ansi:
                result += char
                if char == 'm':
                    in_ansi = False
            else:
                if visible_length >= max_length:
                    break
                result += char
                visible_length += 1
        
        return result
    
    def _is_numeric(self, value: Any) -> bool:
        """Check if a value is numeric"""
        if isinstance(value, (int, float)):
            return True
        
        if isinstance(value, str):
            try:
                float(value.replace(',', '').replace('$', ''))
                return True
            except (ValueError, TypeError):
                return False
        
        return False
    
    def _apply_cell_color(self, value: Any, formatted_value: str, column: ColumnConfig) -> str:
        """Apply color to a cell value"""
        if not self.color_enabled or not column.color_func:
            return formatted_value
        
        color_code = column.color_func(value)
        if color_code:
            return f"{color_code}{formatted_value}\033[0m"
        return formatted_value
    
    def render(self, columns: Optional[List[str]] = None, 
              show_header: bool = True,
              show_borders: bool = True) -> str:
        """Render the table as a string
        
        Args:
            columns: Columns to display (all if None)
            show_header: Whether to show column headers
            show_borders: Whether to show table borders
            
        Returns:
            Formatted table string
        """
        if not self.data:
            return "No data to display"
        
        # Determine visible columns
        if columns:
            visible_columns = [col for col in columns if col in self.columns]
        else:
            visible_columns = list(self.columns.keys())
        
        if not visible_columns:
            return "No columns to display"
        
        # Calculate column widths
        widths = self._calculate_column_widths(visible_columns)
        
        lines = []
        
        # Top border
        if show_borders and self.style != TableStyle.MINIMAL:
            top_line = self._build_border_line(widths, visible_columns, "top")
            lines.append(top_line)
        
        # Header row
        if show_header:
            header_line = self._build_header_line(widths, visible_columns)
            lines.append(header_line)
            
            # Header separator
            if show_borders and self.style != TableStyle.MINIMAL:
                sep_line = self._build_border_line(widths, visible_columns, "middle")
                lines.append(sep_line)
        
        # Data rows
        for i, row in enumerate(self.data):
            data_line = self._build_data_line(row, widths, visible_columns)
            lines.append(data_line)
        
        # Bottom border
        if show_borders and self.style != TableStyle.MINIMAL:
            bottom_line = self._build_border_line(widths, visible_columns, "bottom")
            lines.append(bottom_line)
        
        return "\n".join(lines)
    
    def _build_border_line(self, widths: Dict[str, int], 
                          columns: List[str], position: str) -> str:
        """Build a horizontal border line"""
        chars = self.chars
        
        if position == "top":
            start_char = chars['tl']
            end_char = chars['tr']
            join_char = chars['tee_down']
        elif position == "bottom":
            start_char = chars['bl']
            end_char = chars['br']
            join_char = chars['tee_up']
        else:  # middle
            start_char = chars['tee_right']
            end_char = chars['tee_left']
            join_char = chars['cross']
        
        segments = []
        for col_name in columns:
            width = widths[col_name]
            segments.append(chars['h'] * (width + 2))  # +2 for padding
        
        if self.color_enabled:
            border_color = "\033[90m"  # Dark gray
            reset = "\033[0m"
            line = f"{border_color}{start_char}{join_char.join(segments)}{end_char}{reset}"
        else:
            line = f"{start_char}{join_char.join(segments)}{end_char}"
        
        return line
    
    def _build_header_line(self, widths: Dict[str, int], columns: List[str]) -> str:
        """Build the header line"""
        cells = []
        
        for col_name in columns:
            col = self.columns[col_name]
            title = col.title or col_name
            width = widths[col_name]
            
            # Format header cell
            if len(title) > width:
                display_title = title[:width - 3] + "..."
            else:
                display_title = title
            
            # Center align headers
            padding = width - len(display_title)
            left_pad = padding // 2
            right_pad = padding - left_pad
            formatted_title = " " * left_pad + display_title + " " * right_pad
            
            # Add sort indicator
            if self.sort_column == col_name:
                if self.sort_direction == SortDirection.ASC:
                    indicator = "↑"
                else:
                    indicator = "↓"
                
                if len(formatted_title) > 0:
                    formatted_title = formatted_title[:-1] + indicator
            
            # Apply color
            if self.color_enabled:
                colored_title = f"\033[1;96m{formatted_title}\033[0m"  # Bold cyan
            else:
                colored_title = formatted_title
            
            cells.append(colored_title)
        
        # Join cells with borders
        if self.style == TableStyle.MINIMAL:
            return "  ".join(cells)
        else:
            border_char = self.chars['v']
            if self.color_enabled:
                border_colored = f"\033[90m{border_char}\033[0m"
            else:
                border_colored = border_char
            
            return f"{border_colored} {f' {border_colored} '.join(cells)} {border_colored}"
    
    def _build_data_line(self, row: Dict[str, Any], 
                        widths: Dict[str, int], columns: List[str]) -> str:
        """Build a data row line"""
        cells = []
        
        for col_name in columns:
            col = self.columns[col_name]
            value = row.get(col_name)
            width = widths[col_name]
            
            # Format the cell value
            formatted_value = self._format_cell_value(value, col, width)
            
            # Apply cell color
            colored_value = self._apply_cell_color(value, formatted_value, col)
            
            cells.append(colored_value)
        
        # Join cells with borders
        if self.style == TableStyle.MINIMAL:
            return "  ".join(cells)
        else:
            border_char = self.chars['v']
            if self.color_enabled:
                border_colored = f"\033[90m{border_char}\033[0m"
            else:
                border_colored = border_char
            
            return f"{border_colored} {f' {border_colored} '.join(cells)} {border_colored}"
    
    def print(self, **kwargs) -> None:
        """Print the table to stdout"""
        print(self.render(**kwargs))
    
    def to_csv(self, filename: Optional[str] = None) -> str:
        """Export table to CSV format
        
        Args:
            filename: File to write to (returns string if None)
            
        Returns:
            CSV string if filename is None
        """
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=list(self.columns.keys()))
        
        # Write header
        header_row = {}
        for col_name, col in self.columns.items():
            header_row[col_name] = col.title or col_name
        writer.writerow(header_row)
        
        # Write data
        for row in self.data:
            # Format values
            formatted_row = {}
            for col_name, value in row.items():
                col = self.columns.get(col_name)
                if col and col.formatter:
                    # Remove ANSI codes from formatted output
                    formatted = col.formatter(value)
                    formatted_row[col_name] = re.sub(r'\033\[[0-9;]*m', '', formatted)
                else:
                    formatted_row[col_name] = value
            
            writer.writerow(formatted_row)
        
        csv_content = output.getvalue()
        output.close()
        
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_content)
            return f"Table exported to {filename}"
        
        return csv_content
    
    def to_json(self, filename: Optional[str] = None, indent: int = 2) -> str:
        """Export table to JSON format
        
        Args:
            filename: File to write to (returns string if None)
            indent: JSON indentation
            
        Returns:
            JSON string if filename is None
        """
        json_content = json.dumps(self.data, indent=indent, default=str)
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_content)
            return f"Table exported to {filename}"
        
        return json_content


# Convenience functions and formatters
def currency_formatter(value: Any) -> str:
    """Format value as currency"""
    try:
        num_value = float(value)
        return f"${num_value:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def percentage_formatter(value: Any) -> str:
    """Format value as percentage"""
    try:
        num_value = float(value)
        return f"{num_value:.1f}%"
    except (ValueError, TypeError):
        return str(value)


def number_formatter(decimals: int = 2) -> Callable[[Any], str]:
    """Create a number formatter with specified decimal places"""
    def formatter(value: Any) -> str:
        try:
            num_value = float(value)
            return f"{num_value:,.{decimals}f}"
        except (ValueError, TypeError):
            return str(value)
    return formatter


def status_color_func(value: Any) -> str:
    """Color function for status values"""
    str_value = str(value).lower()
    if str_value in ['success', 'completed', 'active', 'online']:
        return "\033[92m"  # Green
    elif str_value in ['error', 'failed', 'inactive', 'offline']:
        return "\033[91m"  # Red
    elif str_value in ['warning', 'pending', 'processing']:
        return "\033[93m"  # Yellow
    return ""


def create_table(data: List[Dict[str, Any]], 
                style: TableStyle = TableStyle.SIMPLE,
                color_enabled: bool = True) -> DataTable:
    """Create a new data table
    
    Args:
        data: Table data
        style: Table style
        color_enabled: Whether colors are enabled
        
    Returns:
        DataTable instance
    """
    return DataTable(data, style, color_enabled)