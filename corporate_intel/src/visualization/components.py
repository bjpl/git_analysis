"""
Visualization Components for Corporate Intelligence Platform
=============================================================

SPARC SPECIFICATION:
-------------------
Purpose: Create reusable, production-grade visualization components for EdTech analytics
Requirements:
  - Financial waterfall charts for revenue decomposition
  - Cohort retention heatmaps for user behavior analysis
  - Competitive landscape scatter plots with market positioning
  - Interactive segment comparison radars
  - Hierarchical market share sunbursts
  
Performance Targets:
  - Render < 100ms for datasets up to 10K points
  - Support real-time updates via WebSocket
  - Responsive design for 4K → mobile displays

PSEUDOCODE ARCHITECTURE:
-----------------------
For each visualization:
  1. Validate input data schema
  2. Apply business logic transformations
  3. Generate Plotly figure with optimized layout
  4. Add interactivity (hover, click, zoom)
  5. Return figure with caching headers

REFINEMENT NOTES:
----------------
- Use Plotly's graph_objects for fine control over rendering
- Implement data sampling for large datasets (> 10K points)
- Add accessibility features (ARIA labels, keyboard navigation)
- Cache computed layouts for 60 seconds
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats


class VisualizationComponents:
    """
    SPARC-designed visualization component factory.
    
    Architecture Decision: Class-based to enable state management
    and component lifecycle hooks for future enhancements.
    """
    
    # Color palette optimized for colorblind accessibility
    COLORS = {
        'primary': '#1e3a5f',
        'secondary': '#4a90e2',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'info': '#3498db',
        'gradient_start': '#667eea',
        'gradient_end': '#764ba2',
    }
    
    # Category-specific colors for consistency
    CATEGORY_COLORS = {
        'k12': '#FF6B6B',
        'higher_education': '#4ECDC4',
        'corporate_learning': '#45B7D1',
        'direct_to_consumer': '#96CEB4',
        'enabling_technology': '#FFEAA7',
    }


def create_metrics_waterfall(company_data: Dict[str, Any]) -> go.Figure:
    """
    Create waterfall chart showing revenue/metric decomposition.
    
    SPARC Design:
    - Specification: Show metric contribution analysis
    - Pseudocode: Start → Add components → Show delta → End
    - Architecture: Sequential bars with running total
    - Refinement: Color code positive/negative changes
    """
    
    # Extract metrics for waterfall
    ticker = company_data.get('ticker', 'Unknown')
    
    # Build waterfall data
    categories = ['Previous Quarter', 'Organic Growth', 'New Products', 
                  'Price Changes', 'Churn Impact', 'Current Quarter']
    
    # Sample calculation (would come from data)
    prev_revenue = company_data.get('prev_quarter_revenue', 100)
    curr_revenue = company_data.get('latest_revenue', 120)
    
    # Decompose revenue change
    organic = curr_revenue * 0.15
    new_products = curr_revenue * 0.08
    price = curr_revenue * 0.05
    churn = -curr_revenue * 0.08
    
    values = [prev_revenue, organic, new_products, price, churn, None]
    
    # Calculate cumulative for final value
    cumulative = prev_revenue + organic + new_products + price + churn
    values[-1] = cumulative
    
    # Create waterfall
    fig = go.Figure(go.Waterfall(
        name="Revenue",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=categories,
        textposition="outside",
        text=[f"${v/1e6:.1f}M" if v else f"${cumulative/1e6:.1f}M" for v in values],
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": VisualizationComponents.COLORS['success']}},
        decreasing={"marker": {"color": VisualizationComponents.COLORS['danger']}},
        totals={"marker": {"color": VisualizationComponents.COLORS['primary']}},
    ))
    
    fig.update_layout(
        title=f"{ticker} Revenue Bridge Analysis",
        showlegend=False,
        template="plotly_white",
        height=400,
        margin=dict(t=60, b=40, l=40, r=40),
        yaxis=dict(
            title="Revenue ($M)",
            tickformat="$,.0f",
        ),
        xaxis=dict(
            title="",
        ),
    )
    
    return fig


def create_cohort_heatmap(cohort_data: pd.DataFrame) -> go.Figure:
    """
    Create cohort retention heatmap.
    
    SPARC Design:
    - Specification: Visualize retention patterns over time
    - Pseudocode: Matrix[cohort][period] = retention_rate
    - Architecture: 2D heatmap with time on X, cohorts on Y
    - Refinement: Add annotations for key insights
    """
    
    # Sample cohort data structure
    if cohort_data.empty:
        # Generate sample data
        months = ['M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6']
        cohorts = ['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4']
        
        # Simulate retention decay
        retention_matrix = []
        for i, cohort in enumerate(cohorts):
            base_retention = 100 - (i * 5)  # Newer cohorts have better retention
            retention = [base_retention]
            for month in range(1, len(months)):
                # Exponential decay with some randomness
                decay = np.exp(-month * 0.15) * base_retention
                retention.append(decay + np.random.normal(0, 2))
            retention_matrix.append(retention)
        
        z_data = retention_matrix
    else:
        z_data = cohort_data.values
        cohorts = cohort_data.index.tolist()
        months = cohort_data.columns.tolist()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=months,
        y=cohorts,
        colorscale='RdYlGn',
        text=[[f"{val:.0f}%" for val in row] for row in z_data],
        texttemplate="%{text}",
        textfont={"size": 10},
        colorbar=dict(
            title="Retention %",
            titleside="right",
            tickmode="linear",
            tick0=0,
            dtick=20,
        ),
    ))
    
    # Add trend lines for each cohort
    for i, cohort in enumerate(cohorts):
        if i == 0:  # Only show for first cohort to avoid clutter
            fig.add_scatter(
                x=months,
                y=[cohort] * len(months),
                mode='lines',
                line=dict(color='white', width=2, dash='dash'),
                showlegend=False,
                hoverinfo='skip',
            )
    
    fig.update_layout(
        title="Cohort Retention Analysis",
        xaxis_title="Months Since Acquisition",
        yaxis_title="Cohort",
        template="plotly_white",
        height=400,
        margin=dict(t=60, b=40, l=80, r=40),
    )
    
    return fig


def create_competitive_landscape_scatter(
    companies_df: pd.DataFrame,
    highlighted_companies: List[str] = None
) -> go.Figure:
    """
    Create competitive positioning scatter plot.
    
    SPARC Design:
    - Specification: 2D positioning (growth vs retention)
    - Pseudocode: Plot(x=growth, y=retention, size=revenue, color=category)
    - Architecture: Bubble chart with quadrant analysis
    - Refinement: Add annotations for market leaders
    """
    
    if highlighted_companies is None:
        highlighted_companies = []
    
    # Create scatter plot
    fig = go.Figure()
    
    # Add traces for each category
    for category in companies_df['edtech_category'].unique():
        df_category = companies_df[companies_df['edtech_category'] == category]
        
        # Determine which points to highlight
        df_category['highlighted'] = df_category['ticker'].isin(highlighted_companies)
        
        # Add main scatter
        fig.add_trace(go.Scatter(
            x=df_category['revenue_yoy_growth'],
            y=df_category['latest_nrr'],
            mode='markers+text',
            name=category.replace('_', ' ').title(),
            text=df_category['ticker'],
            textposition="top center",
            textfont=dict(
                size=10,
                color='black',
            ),
            marker=dict(
                size=df_category['latest_revenue'] / 1e7,  # Scale by revenue
                color=VisualizationComponents.CATEGORY_COLORS.get(
                    category, 
                    VisualizationComponents.COLORS['info']
                ),
                line=dict(
                    width=df_category['highlighted'].apply(lambda x: 3 if x else 1),
                    color='black',
                ),
                opacity=0.7,
            ),
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "Growth: %{x:.1f}%<br>" +
                "NRR: %{y:.0f}%<br>" +
                "Revenue: $%{marker.size:.0f}M<br>" +
                "<extra></extra>"
            ),
        ))
    
    # Add quadrant lines
    fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    annotations = [
        dict(x=30, y=120, text="Stars", showarrow=False, font=dict(size=12, color="green")),
        dict(x=-20, y=120, text="Cash Cows", showarrow=False, font=dict(size=12, color="blue")),
        dict(x=30, y=80, text="Question Marks", showarrow=False, font=dict(size=12, color="orange")),
        dict(x=-20, y=80, text="Dogs", showarrow=False, font=dict(size=12, color="red")),
    ]
    
    fig.update_layout(
        title="Competitive Landscape: Growth vs Retention",
        xaxis_title="Revenue YoY Growth (%)",
        yaxis_title="Net Revenue Retention (%)",
        template="plotly_white",
        height=500,
        hovermode='closest',
        annotations=annotations,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            range=[-30, 50],
            tickformat=".0f",
            ticksuffix="%",
        ),
        yaxis=dict(
            range=[70, 130],
            tickformat=".0f",
            ticksuffix="%",
        ),
    )
    
    return fig


def create_segment_comparison_radar(segments_df: pd.DataFrame) -> go.Figure:
    """
    Create radar chart comparing segment performance.
    
    SPARC Design:
    - Specification: Multi-dimensional segment comparison
    - Pseudocode: RadialPlot(metrics=[growth, retention, efficiency, scale])
    - Architecture: Polar coordinate system with normalized scales
    - Refinement: Interactive legend for segment toggling
    """
    
    # Define metrics for radar
    metrics = ['Growth', 'Retention', 'Efficiency', 'Market Size', 'Profitability']
    
    fig = go.Figure()
    
    # Add trace for each segment
    for _, segment in segments_df.iterrows():
        # Normalize metrics to 0-100 scale
        values = [
            min(segment.get('avg_revenue_growth', 0) * 2, 100),  # Growth
            segment.get('avg_nrr', 100) - 80,  # Retention (80-120 → 0-40 → 0-100)
            segment.get('avg_ltv_cac_ratio', 1) * 25,  # Efficiency
            min(segment.get('total_segment_revenue', 0) / 1e8, 100),  # Market size
            segment.get('avg_gross_margin', 0),  # Profitability
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics,
            fill='toself',
            name=segment['edtech_category'].replace('_', ' ').title(),
            line=dict(
                color=VisualizationComponents.CATEGORY_COLORS.get(
                    segment['edtech_category'],
                    VisualizationComponents.COLORS['info']
                ),
                width=2,
            ),
            opacity=0.6,
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickformat=".0f",
            ),
        ),
        showlegend=True,
        title="Segment Performance Comparison",
        template="plotly_white",
        height=500,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
        ),
    )
    
    return fig


def create_market_share_sunburst(market_df: pd.DataFrame, selected_category: str = None) -> go.Figure:
    """
    Create hierarchical market share sunburst.
    
    SPARC Design:
    - Specification: Nested hierarchy (Category → Company → Product)
    - Pseudocode: Tree structure with size = revenue
    - Architecture: Sunburst with drill-down capability
    - Refinement: Color intensity based on growth rate
    """
    
    # Prepare hierarchical data
    labels = ["EdTech Market"]
    parents = [""]
    values = [market_df['total_segment_revenue'].sum()]
    colors = [VisualizationComponents.COLORS['primary']]
    
    # Add categories
    for _, row in market_df.iterrows():
        category = row['edtech_category']
        labels.append(category.replace('_', ' ').title())
        parents.append("EdTech Market")
        values.append(row['total_segment_revenue'])
        colors.append(VisualizationComponents.CATEGORY_COLORS.get(
            category,
            VisualizationComponents.COLORS['info']
        ))
    
    # Create sunburst
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(
            colors=colors,
            line=dict(color="white", width=2),
        ),
        textinfo="label+percent parent",
        hovertemplate=(
            "<b>%{label}</b><br>" +
            "Revenue: $%{value:.1f}B<br>" +
            "Share: %{percentParent}<br>" +
            "<extra></extra>"
        ),
    ))
    
    fig.update_layout(
        title="EdTech Market Share Distribution",
        template="plotly_white",
        height=500,
        margin=dict(t=60, b=0, l=0, r=0),
    )
    
    return fig


def create_retention_curves(retention_data: pd.DataFrame) -> go.Figure:
    """
    Create retention curves over time.
    
    SPARC Design:
    - Specification: Time-series retention by cohort
    - Pseudocode: Line plot with confidence intervals
    - Architecture: Multi-line chart with shared X-axis
    - Refinement: Add benchmark lines and annotations
    """
    
    fig = go.Figure()
    
    # Sample retention curves if no data
    if retention_data.empty:
        months = list(range(13))
        
        # Generate different retention patterns
        patterns = {
            'Premium': [100, 92, 85, 80, 76, 73, 71, 70, 69, 68, 68, 67, 67],
            'Standard': [100, 85, 75, 68, 62, 58, 55, 53, 52, 51, 50, 50, 49],
            'Free': [100, 70, 50, 35, 25, 20, 18, 16, 15, 14, 13, 13, 12],
        }
        
        for tier, retention in patterns.items():
            fig.add_trace(go.Scatter(
                x=months,
                y=retention,
                mode='lines+markers',
                name=tier,
                line=dict(width=2),
                marker=dict(size=6),
            ))
    
    # Add benchmark line
    fig.add_hline(
        y=40,
        line_dash="dash",
        line_color="gray",
        annotation_text="Industry Benchmark (40%)",
        annotation_position="right",
    )
    
    fig.update_layout(
        title="User Retention Curves by Tier",
        xaxis_title="Months Since Registration",
        yaxis_title="Retention Rate (%)",
        template="plotly_white",
        height=400,
        hovermode='x unified',
        yaxis=dict(
            range=[0, 105],
            tickformat=".0f",
            ticksuffix="%",
        ),
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    
    return fig