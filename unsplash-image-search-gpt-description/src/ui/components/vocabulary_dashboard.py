"""
Vocabulary dashboard component with progress visualization, statistics, and interactive charts.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional, Any, Tuple
import math
from datetime import datetime, timedelta
import json
from pathlib import Path

from ..styles import StyleManager, Easing


class ProgressRing(tk.Canvas):
    """Custom progress ring widget for circular progress indication."""
    
    def __init__(self, parent: tk.Widget, size: int = 100, thickness: int = 8,
                 style_manager: StyleManager = None):
        super().__init__(parent, width=size, height=size, highlightthickness=0)
        
        self.size = size
        self.thickness = thickness
        self.style_manager = style_manager
        self.progress = 0.0
        self.max_value = 100
        self.current_value = 0
        
        self._setup_colors()
        self._draw_ring()
    
    def _setup_colors(self):
        """Setup colors based on theme."""
        if self.style_manager:
            self.bg_color = self.style_manager.theme.colors.surface_variant
            self.fg_color = self.style_manager.theme.colors.primary
            self.text_color = self.style_manager.theme.colors.on_surface
            self.configure(bg=self.style_manager.theme.colors.background)
        else:
            self.bg_color = "#e0e0e0"
            self.fg_color = "#2196f3"
            self.text_color = "#000000"
    
    def _draw_ring(self):
        """Draw the progress ring."""
        self.delete("all")
        
        center = self.size // 2
        radius = (self.size - self.thickness) // 2
        
        # Background ring
        self.create_arc(
            center - radius, center - radius,
            center + radius, center + radius,
            start=0, extent=360,
            outline=self.bg_color, width=self.thickness,
            style="arc"
        )
        
        # Progress arc
        if self.progress > 0:
            extent = 360 * self.progress
            self.create_arc(
                center - radius, center - radius,
                center + radius, center + radius,
                start=90, extent=-extent,  # Start from top, go clockwise
                outline=self.fg_color, width=self.thickness,
                style="arc"
            )
        
        # Center text
        percentage = int(self.progress * 100)
        self.create_text(
            center, center,
            text=f"{percentage}%",
            font=('Segoe UI', 12, 'bold'),
            fill=self.text_color
        )
    
    def set_progress(self, current: int, maximum: int):
        """Set progress value."""
        self.current_value = current
        self.max_value = maximum
        self.progress = min(1.0, current / maximum if maximum > 0 else 0)
        self._draw_ring()
    
    def animate_to_progress(self, target_current: int, target_max: int, duration: float = 1.0):
        """Animate progress change."""
        start_progress = self.progress
        target_progress = min(1.0, target_current / target_max if target_max > 0 else 0)
        
        if start_progress == target_progress:
            return
        
        start_time = datetime.now()
        
        def update_progress():
            elapsed = (datetime.now() - start_time).total_seconds()
            t = min(1.0, elapsed / duration)
            
            # Ease out animation
            eased_t = 1 - (1 - t) * (1 - t)
            
            current_progress = start_progress + (target_progress - start_progress) * eased_t
            current_val = int(self.max_value * current_progress)
            
            self.set_progress(current_val, target_max)
            
            if t < 1.0:
                self.after(16, update_progress)  # ~60fps
            else:
                self.set_progress(target_current, target_max)
        
        update_progress()


class StatCard(tk.Frame):
    """Individual statistic card widget."""
    
    def __init__(self, parent: tk.Widget, title: str, value: str,
                 subtitle: str = "", icon: str = "", 
                 style_manager: StyleManager = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        
        self._create_widgets()
        
        if self.style_manager:
            self.style_manager.register_widget(self, classes=['frame', 'stat-card'])
    
    def _create_widgets(self):
        """Create card widgets."""
        # Apply card styling
        if self.style_manager:
            self.configure(
                bg=self.style_manager.theme.colors.surface,
                relief='solid',
                borderwidth=1,
                padx=20,
                pady=15
            )
        
        # Icon and title row
        header_frame = tk.Frame(self, bg=self.configure()['bg'][-1])
        header_frame.pack(fill='x', anchor='w')
        
        if self.icon:
            icon_label = tk.Label(
                header_frame,
                text=self.icon,
                font=('Segoe UI', 16),
                bg=self.configure()['bg'][-1],
                fg=self.style_manager.theme.colors.primary if self.style_manager else "#2196f3"
            )
            icon_label.pack(side='left')
        
        title_label = tk.Label(
            header_frame,
            text=self.title,
            font=('Segoe UI', 10),
            bg=self.configure()['bg'][-1],
            fg=self.style_manager.theme.colors.on_surface if self.style_manager else "#000000",
            anchor='w'
        )
        title_label.pack(side='left', padx=(5 if self.icon else 0, 0))
        
        # Value
        self.value_label = tk.Label(
            self,
            text=self.value,
            font=('Segoe UI', 24, 'bold'),
            bg=self.configure()['bg'][-1],
            fg=self.style_manager.theme.colors.on_surface if self.style_manager else "#000000",
            anchor='w'
        )
        self.value_label.pack(anchor='w', pady=(5, 0))
        
        # Subtitle
        if self.subtitle:
            self.subtitle_label = tk.Label(
                self,
                text=self.subtitle,
                font=('Segoe UI', 9),
                bg=self.configure()['bg'][-1],
                fg=self.style_manager.theme.colors.outline if self.style_manager else "#666666",
                anchor='w'
            )
            self.subtitle_label.pack(anchor='w', pady=(2, 0))
    
    def update_value(self, new_value: str, new_subtitle: str = None):
        """Update card value and subtitle."""
        self.value = new_value
        self.value_label.configure(text=new_value)
        
        if new_subtitle is not None:
            self.subtitle = new_subtitle
            if hasattr(self, 'subtitle_label'):
                self.subtitle_label.configure(text=new_subtitle)


class ProgressChart(tk.Canvas):
    """Simple progress chart for vocabulary learning over time."""
    
    def __init__(self, parent: tk.Widget, width: int = 400, height: int = 200,
                 style_manager: StyleManager = None):
        super().__init__(parent, width=width, height=height, highlightthickness=0)
        
        self.chart_width = width
        self.chart_height = height
        self.style_manager = style_manager
        self.data_points: List[Tuple[datetime, int]] = []
        
        self._setup_colors()
        self._draw_chart()
    
    def _setup_colors(self):
        """Setup chart colors."""
        if self.style_manager:
            self.bg_color = self.style_manager.theme.colors.surface
            self.line_color = self.style_manager.theme.colors.primary
            self.grid_color = self.style_manager.theme.colors.outline_variant
            self.text_color = self.style_manager.theme.colors.on_surface
            self.configure(bg=self.bg_color)
        else:
            self.bg_color = "#ffffff"
            self.line_color = "#2196f3"
            self.grid_color = "#e0e0e0"
            self.text_color = "#000000"
    
    def set_data(self, data_points: List[Tuple[datetime, int]]):
        """Set chart data points."""
        self.data_points = data_points
        self._draw_chart()
    
    def _draw_chart(self):
        """Draw the progress chart."""
        self.delete("all")
        
        if not self.data_points:
            # Show placeholder
            self.create_text(
                self.chart_width // 2, self.chart_height // 2,
                text="No data available",
                font=('Segoe UI', 12),
                fill=self.text_color
            )
            return
        
        # Calculate chart area (with margins)
        margin = 40
        chart_left = margin
        chart_right = self.chart_width - margin
        chart_top = margin
        chart_bottom = self.chart_height - margin
        
        chart_w = chart_right - chart_left
        chart_h = chart_bottom - chart_top
        
        # Find data ranges
        dates = [point[0] for point in self.data_points]
        values = [point[1] for point in self.data_points]
        
        min_date = min(dates)
        max_date = max(dates)
        min_value = 0  # Always start from 0
        max_value = max(values) if values else 100
        
        # Draw grid lines
        grid_lines = 5
        for i in range(grid_lines + 1):
            y = chart_bottom - (i / grid_lines) * chart_h
            self.create_line(
                chart_left, y, chart_right, y,
                fill=self.grid_color, width=1
            )
            
            # Y-axis labels
            value = min_value + (max_value - min_value) * (i / grid_lines)
            self.create_text(
                chart_left - 10, y,
                text=str(int(value)),
                font=('Segoe UI', 9),
                fill=self.text_color,
                anchor='e'
            )
        
        # Draw data line
        if len(self.data_points) > 1:
            points = []
            for date, value in self.data_points:
                # Calculate position
                date_ratio = (date - min_date).total_seconds() / (max_date - min_date).total_seconds() if max_date != min_date else 0
                value_ratio = (value - min_value) / (max_value - min_value) if max_value != min_value else 0
                
                x = chart_left + date_ratio * chart_w
                y = chart_bottom - value_ratio * chart_h
                
                points.extend([x, y])
            
            # Draw line
            if len(points) >= 4:
                self.create_line(
                    *points,
                    fill=self.line_color,
                    width=3,
                    smooth=True
                )
                
                # Draw data points
                for i in range(0, len(points), 2):
                    x, y = points[i], points[i + 1]
                    self.create_oval(
                        x - 4, y - 4, x + 4, y + 4,
                        fill=self.line_color,
                        outline=self.bg_color,
                        width=2
                    )
        
        # X-axis labels (dates)
        if len(dates) > 1:
            date_labels = min(5, len(dates))  # Max 5 date labels
            for i in range(date_labels):
                idx = int(i * (len(dates) - 1) / (date_labels - 1))
                date = dates[idx]
                
                date_ratio = (date - min_date).total_seconds() / (max_date - min_date).total_seconds() if max_date != min_date else 0
                x = chart_left + date_ratio * chart_w
                
                self.create_text(
                    x, chart_bottom + 15,
                    text=date.strftime('%m/%d'),
                    font=('Segoe UI', 9),
                    fill=self.text_color,
                    anchor='n'
                )


class CategoryBreakdown(tk.Frame):
    """Category breakdown with horizontal bars."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.categories: Dict[str, int] = {}
        
        self._create_widgets()
        
        if self.style_manager:
            self.style_manager.register_widget(self, classes=['frame', 'category-breakdown'])
    
    def _create_widgets(self):
        """Create breakdown widgets."""
        # Title
        if self.style_manager:
            title_label = self.style_manager.create_label(
                self, "Categories", heading=3
            )
        else:
            title_label = tk.Label(self, text="Categories", font=('Segoe UI', 12, 'bold'))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Container for category bars
        self.bars_container = tk.Frame(self)
        self.bars_container.pack(fill='both', expand=True)
    
    def set_categories(self, categories: Dict[str, int]):
        """Set category data."""
        self.categories = categories
        self._draw_bars()
    
    def _draw_bars(self):
        """Draw category bars."""
        # Clear existing bars
        for widget in self.bars_container.winfo_children():
            widget.destroy()
        
        if not self.categories:
            no_data_label = tk.Label(
                self.bars_container,
                text="No category data",
                font=('Segoe UI', 10),
                fg=self.style_manager.theme.colors.outline if self.style_manager else "#666666"
            )
            no_data_label.pack()
            return
        
        # Sort categories by count
        sorted_categories = sorted(self.categories.items(), key=lambda x: x[1], reverse=True)
        max_count = max(self.categories.values()) if self.categories else 1
        
        # Color palette for categories
        colors = [
            "#2196f3", "#4caf50", "#ff9800", "#9c27b0",
            "#f44336", "#00bcd4", "#795548", "#607d8b"
        ]
        
        for i, (category, count) in enumerate(sorted_categories[:8]):  # Max 8 categories
            bar_frame = tk.Frame(self.bars_container)
            bar_frame.pack(fill='x', pady=2)
            
            # Category label
            label = tk.Label(
                bar_frame,
                text=category,
                font=('Segoe UI', 10),
                width=12,
                anchor='w'
            )
            label.pack(side='left')
            
            # Progress bar
            bar_container = tk.Frame(bar_frame, height=20)
            bar_container.pack(side='left', fill='x', expand=True, padx=(10, 5))
            bar_container.pack_propagate(False)
            
            bar_width = int((count / max_count) * 200) if max_count > 0 else 0
            
            bar = tk.Frame(
                bar_container,
                bg=colors[i % len(colors)],
                height=20,
                width=bar_width
            )
            bar.pack(side='left')
            
            # Count label
            count_label = tk.Label(
                bar_frame,
                text=str(count),
                font=('Segoe UI', 10),
                width=4,
                anchor='e'
            )
            count_label.pack(side='right')


class VocabularyDashboard(tk.Frame):
    """Main vocabulary dashboard with statistics and visualizations."""
    
    def __init__(self, parent: tk.Widget, style_manager: StyleManager,
                 data_dir: Path, on_export: Callable = None):
        super().__init__(parent)
        
        self.style_manager = style_manager
        self.data_dir = data_dir
        self.on_export = on_export
        
        # Data
        self.vocabulary_data = []
        self.session_data = []
        self.statistics = {}
        
        self._create_widgets()
        self._load_data()
        
        # Register with style manager
        self.style_manager.register_widget(self, classes=['frame', 'vocabulary-dashboard'])
    
    def _create_widgets(self):
        """Create dashboard widgets."""
        # Header
        header = tk.Frame(self)
        header.pack(fill='x', padx=20, pady=10)
        
        title_label = self.style_manager.create_label(
            header, "Vocabulary Dashboard", heading=1
        )
        title_label.pack(side='left')
        
        # Refresh button
        refresh_btn = self.style_manager.create_button(
            header, "🔄 Refresh", variant='text'
        )
        refresh_btn.configure(command=self.refresh_data)
        refresh_btn.pack(side='right')
        
        # Export button
        if self.on_export:
            export_btn = self.style_manager.create_button(
                header, "📤 Export", variant='secondary'
            )
            export_btn.configure(command=self.on_export)
            export_btn.pack(side='right', padx=(0, 10))
        
        # Create scrollable content
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Statistics cards row
        stats_frame = tk.Frame(self.scrollable_frame)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # Create stat cards
        self.total_words_card = StatCard(
            stats_frame, "Total Words", "0", "vocabulary learned", "📚", self.style_manager
        )
        self.total_words_card.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.this_week_card = StatCard(
            stats_frame, "This Week", "0", "new words", "📈", self.style_manager
        )
        self.this_week_card.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.avg_daily_card = StatCard(
            stats_frame, "Daily Average", "0", "words per day", "📊", self.style_manager
        )
        self.avg_daily_card.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.streak_card = StatCard(
            stats_frame, "Learning Streak", "0", "consecutive days", "🔥", self.style_manager
        )
        self.streak_card.pack(side='left', fill='x', expand=True)
        
        # Progress section
        progress_frame = self.style_manager.create_frame(self.scrollable_frame, variant='card')
        progress_frame.pack(fill='x', padx=20, pady=10)
        
        progress_title = self.style_manager.create_label(
            progress_frame, "Learning Progress", heading=2
        )
        progress_title.pack(anchor='w', padx=20, pady=(15, 10))
        
        progress_content = tk.Frame(progress_frame)
        progress_content.pack(fill='x', padx=20, pady=(0, 15))
        
        # Daily goal progress
        daily_goal_frame = tk.Frame(progress_content)
        daily_goal_frame.pack(side='left', padx=(0, 30))
        
        daily_goal_label = self.style_manager.create_label(
            daily_goal_frame, "Daily Goal", font=('Segoe UI', 11, 'bold')
        )
        daily_goal_label.pack()
        
        self.daily_progress_ring = ProgressRing(
            daily_goal_frame, size=120, thickness=10, style_manager=self.style_manager
        )
        self.daily_progress_ring.pack(pady=10)
        
        # Weekly goal progress
        weekly_goal_frame = tk.Frame(progress_content)
        weekly_goal_frame.pack(side='left')
        
        weekly_goal_label = self.style_manager.create_label(
            weekly_goal_frame, "Weekly Goal", font=('Segoe UI', 11, 'bold')
        )
        weekly_goal_label.pack()
        
        self.weekly_progress_ring = ProgressRing(
            weekly_goal_frame, size=120, thickness=10, style_manager=self.style_manager
        )
        self.weekly_progress_ring.pack(pady=10)
        
        # Charts section
        charts_frame = tk.Frame(self.scrollable_frame)
        charts_frame.pack(fill='x', padx=20, pady=10)
        
        # Progress chart
        chart_card = self.style_manager.create_frame(charts_frame, variant='card')
        chart_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        chart_title = self.style_manager.create_label(
            chart_card, "Learning Trend", heading=3
        )
        chart_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        self.progress_chart = ProgressChart(
            chart_card, width=400, height=200, style_manager=self.style_manager
        )
        self.progress_chart.pack(padx=15, pady=(0, 15))
        
        # Category breakdown
        category_card = self.style_manager.create_frame(charts_frame, variant='card')
        category_card.pack(side='right', fill='y', padx=(10, 0))
        
        self.category_breakdown = CategoryBreakdown(category_card, self.style_manager)
        self.category_breakdown.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Recent activity section
        activity_frame = self.style_manager.create_frame(self.scrollable_frame, variant='card')
        activity_frame.pack(fill='x', padx=20, pady=10)
        
        activity_title = self.style_manager.create_label(
            activity_frame, "Recent Activity", heading=2
        )
        activity_title.pack(anchor='w', padx=20, pady=(15, 10))
        
        self.activity_list = tk.Frame(activity_frame)
        self.activity_list.pack(fill='x', padx=20, pady=(0, 15))
    
    def _load_data(self):
        """Load vocabulary and session data."""
        try:
            # Load vocabulary data
            vocab_file = self.data_dir / "vocabulary_target_words.csv"
            if vocab_file.exists():
                import csv
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.vocabulary_data = list(reader)
            
            # Load session data
            session_file = self.data_dir / "session_log.json"
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    self.session_data = session_data.get('sessions', [])
            
            self._calculate_statistics()
            self._update_dashboard()
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def _calculate_statistics(self):
        """Calculate dashboard statistics."""
        now = datetime.now()
        
        # Total words
        total_words = len(self.vocabulary_data)
        
        # Words this week
        week_start = now - timedelta(days=now.weekday())
        week_words = 0
        
        # Daily words count for trend
        daily_counts = {}
        
        for word in self.vocabulary_data:
            try:
                word_date = datetime.strptime(word['Date'], '%Y-%m-%d %H:%M')
                date_key = word_date.date()
                
                if word_date >= week_start:
                    week_words += 1
                
                if date_key in daily_counts:
                    daily_counts[date_key] += 1
                else:
                    daily_counts[date_key] = 1
                    
            except (ValueError, KeyError):
                continue
        
        # Average daily words (last 30 days)
        days_30_ago = now - timedelta(days=30)
        recent_words = [
            word for word in self.vocabulary_data
            if self._parse_date(word.get('Date', '')) >= days_30_ago
        ]
        avg_daily = len(recent_words) / 30 if recent_words else 0
        
        # Learning streak
        streak = self._calculate_streak(daily_counts)
        
        # Category breakdown
        categories = {}
        for word in self.vocabulary_data:
            search_query = word.get('Search Query', 'Other')
            if search_query in categories:
                categories[search_query] += 1
            else:
                categories[search_query] = 1
        
        self.statistics = {
            'total_words': total_words,
            'week_words': week_words,
            'avg_daily': avg_daily,
            'streak': streak,
            'categories': categories,
            'daily_counts': daily_counts
        }
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string safely."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        except ValueError:
            return datetime.min
    
    def _calculate_streak(self, daily_counts: Dict) -> int:
        """Calculate learning streak."""
        if not daily_counts:
            return 0
        
        today = datetime.now().date()
        streak = 0
        
        # Check consecutive days backwards from today
        check_date = today
        while check_date in daily_counts and daily_counts[check_date] > 0:
            streak += 1
            check_date -= timedelta(days=1)
        
        return streak
    
    def _update_dashboard(self):
        """Update all dashboard components."""
        stats = self.statistics
        
        # Update stat cards
        self.total_words_card.update_value(
            str(stats['total_words']),
            "words learned"
        )
        
        self.this_week_card.update_value(
            str(stats['week_words']),
            "new this week"
        )
        
        self.avg_daily_card.update_value(
            f"{stats['avg_daily']:.1f}",
            "avg per day"
        )
        
        self.streak_card.update_value(
            str(stats['streak']),
            "day streak" if stats['streak'] == 1 else "days streak"
        )
        
        # Update progress rings
        # Daily goal: assume 5 words per day
        daily_goal = 5
        today_words = stats['daily_counts'].get(datetime.now().date(), 0)
        self.daily_progress_ring.animate_to_progress(today_words, daily_goal, 1.0)
        
        # Weekly goal: assume 25 words per week
        weekly_goal = 25
        self.weekly_progress_ring.animate_to_progress(stats['week_words'], weekly_goal, 1.2)
        
        # Update progress chart
        chart_data = []
        for date, count in sorted(stats['daily_counts'].items()):
            chart_data.append((datetime.combine(date, datetime.min.time()), count))
        
        self.progress_chart.set_data(chart_data)
        
        # Update category breakdown
        self.category_breakdown.set_categories(stats['categories'])
        
        # Update recent activity
        self._update_recent_activity()
    
    def _update_recent_activity(self):
        """Update recent activity list."""
        # Clear existing activity
        for widget in self.activity_list.winfo_children():
            widget.destroy()
        
        # Show last 5 vocabulary entries
        recent_words = sorted(
            self.vocabulary_data,
            key=lambda x: self._parse_date(x.get('Date', '')),
            reverse=True
        )[:5]
        
        if not recent_words:
            no_activity = self.style_manager.create_label(
                self.activity_list,
                "No recent activity",
                font=('Segoe UI', 10)
            )
            no_activity.configure(fg=self.style_manager.theme.colors.outline)
            no_activity.pack()
            return
        
        for word_data in recent_words:
            activity_item = tk.Frame(self.activity_list)
            activity_item.pack(fill='x', pady=2)
            
            # Word
            word_label = self.style_manager.create_label(
                activity_item,
                word_data.get('Spanish', 'Unknown'),
                font=('Segoe UI', 11, 'bold')
            )
            word_label.pack(side='left')
            
            # Translation
            translation = word_data.get('English', '')
            if translation:
                trans_label = self.style_manager.create_label(
                    activity_item,
                    f"→ {translation}",
                    font=('Segoe UI', 10)
                )
                trans_label.configure(fg=self.style_manager.theme.colors.outline)
                trans_label.pack(side='left', padx=(10, 0))
            
            # Date
            date_str = word_data.get('Date', '')
            if date_str:
                try:
                    word_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                    time_ago = self._format_time_ago(word_date)
                    
                    date_label = self.style_manager.create_label(
                        activity_item,
                        time_ago,
                        font=('Segoe UI', 9)
                    )
                    date_label.configure(fg=self.style_manager.theme.colors.outline)
                    date_label.pack(side='right')
                except ValueError:
                    pass
    
    def _format_time_ago(self, past_date: datetime) -> str:
        """Format time ago string."""
        now = datetime.now()
        diff = now - past_date
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"
    
    def refresh_data(self):
        """Refresh dashboard data."""
        # Show loading animation
        for card in [self.total_words_card, self.this_week_card, 
                    self.avg_daily_card, self.streak_card]:
            self.style_manager.animate_widget(card, 'pulse', duration=0.3)
        
        # Reload data
        self._load_data()
    
    def export_data(self):
        """Export dashboard data."""
        if self.on_export:
            self.on_export()
    
    def set_goals(self, daily_goal: int, weekly_goal: int):
        """Set learning goals."""
        # Update progress rings with new goals
        today_words = self.statistics.get('daily_counts', {}).get(datetime.now().date(), 0)
        week_words = self.statistics.get('week_words', 0)
        
        self.daily_progress_ring.animate_to_progress(today_words, daily_goal)
        self.weekly_progress_ring.animate_to_progress(week_words, weekly_goal)