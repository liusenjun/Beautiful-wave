"""
Advanced visualization module for tide data
Creates stunning interactive plots and animations
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TideVisualizer:
    def __init__(self):
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'water': '#4a90e2',
            'wave': '#67b7dc',
            'high': '#e74c3c',
            'low': '#3498db',
            'gradient': ['#0d1421', '#1e3a5f', '#2e5a8a', '#4a90e2', '#67b7dc', '#85c9f0']
        }
        
        self.theme = {
            'bg_color': '#0d1421',
            'paper_bgcolor': '#1e2329',
            'font_color': '#ffffff',
            'grid_color': '#2a2e39'
        }
    
    def create_wave_animation(self, df, height=600, enhanced=False):
        """Create animated wave visualization with enhanced effects"""
        # Create interpolated data for smooth animation
        df_sorted = df.sort_values('datetime')
        
        fig = go.Figure()
        
        if enhanced:
            # Enhanced wave with multiple layers and animations
            # Create wave layers with different opacities
            wave_layers = [
                {'opacity': 0.8, 'width': 4, 'offset': 0},
                {'opacity': 0.6, 'width': 3, 'offset': 0.05},
                {'opacity': 0.4, 'width': 2, 'offset': 0.1},
                {'opacity': 0.2, 'width': 1, 'offset': 0.15}
            ]
            
            for i, layer in enumerate(wave_layers):
                # Add wave motion effect
                wave_heights = df_sorted['height'] + layer['offset'] * np.sin(
                    2 * np.pi * np.arange(len(df_sorted)) / 50 + i * np.pi/4
                )
                
                fig.add_trace(go.Scatter(
                    x=df_sorted['datetime'],
                    y=wave_heights,
                    mode='lines',
                    line=dict(
                        color=f'rgba(103, 183, 220, {layer["opacity"]})',
                        width=layer['width'],
                        shape='spline'
                    ),
                    fill='tonexty' if i == 0 else None,
                    fillcolor=f'rgba(74, 144, 226, {layer["opacity"] * 0.3})',
                    name=f'Wave Layer {i+1}' if i == 0 else None,
                    showlegend=i == 0,
                    hovertemplate='<b>%{x}</b><br>Height: %{y:.2f}m<extra></extra>' if i == 0 else None,
                    hoverinfo='skip' if i > 0 else 'all'
                ))
            
            # Add animated water surface effect
            surface_y = [df_sorted['height'].min() - 0.2] * len(df_sorted)
            fig.add_trace(go.Scatter(
                x=df_sorted['datetime'],
                y=surface_y,
                mode='lines',
                line=dict(color='rgba(0, 100, 200, 0.3)', width=1),
                fill='tozeroy',
                fillcolor='rgba(0, 50, 100, 0.1)',
                name='Water Surface',
                showlegend=False,
                hoverinfo='skip'
            ))
            
        else:
            # Standard wave visualization
            fig.add_trace(go.Scatter(
                x=df_sorted['datetime'],
                y=df_sorted['height'],
                mode='lines',
                line=dict(
                    color='rgba(103, 183, 220, 0.8)',
                    width=3,
                    shape='spline'
                ),
                fill='tonexty',
                fillcolor='rgba(74, 144, 226, 0.3)',
                name='Tide Height',
                hovertemplate='<b>%{x}</b><br>Height: %{y:.2f}m<extra></extra>'
            ))
        
        # Add tide markers
        high_tides = df_sorted[df_sorted['tide_type'] == 'high']
        low_tides = df_sorted[df_sorted['tide_type'] == 'low']
        
        if not high_tides.empty:
            fig.add_trace(go.Scatter(
                x=high_tides['datetime'],
                y=high_tides['height'],
                mode='markers',
                marker=dict(
                    size=12,
                    color=self.colors['high'],
                    symbol='triangle-up',
                    line=dict(width=2, color='white')
                ),
                name='High Tide',
                hovertemplate='<b>High Tide</b><br>%{x}<br>Height: %{y:.2f}m<extra></extra>'
            ))
        
        if not low_tides.empty:
            fig.add_trace(go.Scatter(
                x=low_tides['datetime'],
                y=low_tides['height'],
                mode='markers',
                marker=dict(
                    size=12,
                    color=self.colors['low'],
                    symbol='triangle-down',
                    line=dict(width=2, color='white')
                ),
                name='Low Tide',
                hovertemplate='<b>Low Tide</b><br>%{x}<br>Height: %{y:.2f}m<extra></extra>'
            ))
        
        # Apply ocean theme with enhanced styling
        title_text = '🌊 Enhanced Dynamic Tide Visualization' if enhanced else '🌊 Dynamic Tide Visualization - Hong Kong (Chek Lap Kok)'
        
        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=24, color=self.theme['font_color']),
                x=0.5
            ),
            xaxis=dict(
                title='Date & Time',
                gridcolor=self.theme['grid_color'],
                color=self.theme['font_color'],
                showgrid=True,
                gridwidth=1,
                showspikes=True,
                spikesnap='cursor',
                spikecolor='rgba(74, 144, 226, 0.8)',
                spikethickness=2
            ),
            yaxis=dict(
                title='Tide Height (m)',
                gridcolor=self.theme['grid_color'],
                color=self.theme['font_color'],
                showgrid=True,
                gridwidth=1,
                showspikes=True,
                spikesnap='cursor',
                spikecolor='rgba(74, 144, 226, 0.8)',
                spikethickness=2
            ),
            plot_bgcolor=self.theme['bg_color'],
            paper_bgcolor=self.theme['paper_bgcolor'],
            font=dict(color=self.theme['font_color']),
            height=height,
            legend=dict(
                bgcolor='rgba(30, 35, 41, 0.9)',
                bordercolor='rgba(74, 144, 226, 0.5)',
                borderwidth=2
            ),
            hovermode='x unified',
            # Enhanced animations and transitions
            transition=dict(duration=1000, easing='cubic-in-out'),
            # Add some margin for better visual effect
            margin=dict(t=80, b=60, l=60, r=60)
        )
        
        # Add animation configuration for enhanced mode
        if enhanced:
            fig.update_layout(
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'buttons': [{
                        'label': '▶️ Animate',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 100, 'redraw': True},
                            'transition': {'duration': 50}
                        }]
                    }],
                    'x': 0.1,
                    'y': 1.02,
                    'bgcolor': 'rgba(74, 144, 226, 0.8)',
                    'bordercolor': 'rgba(255, 255, 255, 0.2)',
                    'font': {'color': 'white'}
                }]
            )
        
        return fig
    
    def create_circular_tide_clock(self, df, selected_date=None):
        """Create circular tide clock showing daily patterns"""
        if selected_date is None:
            selected_date = df['datetime'].dt.date.iloc[0]
        
        daily_data = df[df['datetime'].dt.date == selected_date].copy()
        
        if daily_data.empty:
            return go.Figure()
        
        # Convert time to polar coordinates
        daily_data['hour_angle'] = (daily_data['time_decimal'] / 24) * 360
        daily_data['radius'] = daily_data['height']
        
        fig = go.Figure()
        
        # Add radial tide pattern
        fig.add_trace(go.Scatterpolar(
            r=daily_data['radius'],
            theta=daily_data['hour_angle'],
            mode='lines+markers',
            line=dict(color='rgba(103, 183, 220, 0.8)', width=3),
            marker=dict(size=8, color=daily_data['height'], 
                       colorscale='Viridis', showscale=True),
            fill='toself',
            fillcolor='rgba(74, 144, 226, 0.3)',
            name='Tide Pattern',
            hovertemplate='<b>Time:</b> %{theta:.0f}°<br><b>Height:</b> %{r:.2f}m<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'🕐 Daily Tide Clock - {selected_date}',
            polar=dict(
                bgcolor=self.theme['bg_color'],
                radialaxis=dict(
                    visible=True,
                    color=self.theme['font_color'],
                    gridcolor=self.theme['grid_color']
                ),
                angularaxis=dict(
                    color=self.theme['font_color'],
                    gridcolor=self.theme['grid_color'],
                    tickmode='array',
                    tickvals=[0, 90, 180, 270],
                    ticktext=['12AM', '6AM', '12PM', '6PM']
                )
            ),
            paper_bgcolor=self.theme['paper_bgcolor'],
            font=dict(color=self.theme['font_color'])
        )
        
        return fig
    
    def create_seasonal_heatmap(self, df):
        """Create seasonal tide height heatmap"""
        # Aggregate data by day of year and hour
        df['day_of_year'] = df['datetime'].dt.dayofyear
        df['hour'] = df['datetime'].dt.hour
        
        pivot_data = df.groupby(['day_of_year', 'hour'])['height'].mean().unstack(fill_value=0)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=list(range(24)),
            y=pivot_data.index,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='<b>Day:</b> %{y}<br><b>Hour:</b> %{x}<br><b>Avg Height:</b> %{z:.2f}m<extra></extra>'
        ))
        
        fig.update_layout(
            title='📅 Seasonal Tide Patterns (Day vs Hour)',
            xaxis=dict(
                title='Hour of Day',
                tickmode='array',
                tickvals=list(range(0, 24, 3)),
                ticktext=[f'{h}:00' for h in range(0, 24, 3)],
                color=self.theme['font_color']
            ),
            yaxis=dict(
                title='Day of Year',
                color=self.theme['font_color']
            ),
            plot_bgcolor=self.theme['bg_color'],
            paper_bgcolor=self.theme['paper_bgcolor'],
            font=dict(color=self.theme['font_color'])
        )
        
        return fig
    
    def create_3d_tide_surface(self, df):
        """Create 3D surface plot of tide patterns"""
        # Prepare data for 3D visualization
        df_copy = df.copy()
        df_copy['day_of_year'] = df_copy['datetime'].dt.dayofyear
        df_copy['hour'] = df_copy['datetime'].dt.hour
        
        # Create pivot table
        surface_data = df_copy.groupby(['day_of_year', 'hour'])['height'].mean().unstack(fill_value=0)
        
        fig = go.Figure(data=[go.Surface(
            z=surface_data.values,
            x=list(range(24)),
            y=surface_data.index,
            colorscale='Viridis',
            hovertemplate='<b>Day:</b> %{y}<br><b>Hour:</b> %{x}<br><b>Height:</b> %{z:.2f}m<extra></extra>'
        )])
        
        fig.update_layout(
            title='🏔️ 3D Tide Surface - Annual Patterns',
            scene=dict(
                xaxis_title='Hour of Day',
                yaxis_title='Day of Year',
                zaxis_title='Tide Height (m)',
                bgcolor=self.theme['bg_color'],
                xaxis=dict(color=self.theme['font_color']),
                yaxis=dict(color=self.theme['font_color']),
                zaxis=dict(color=self.theme['font_color'])
            ),
            paper_bgcolor=self.theme['paper_bgcolor'],
            font=dict(color=self.theme['font_color'])
        )
        
        return fig
    
    def create_harmonic_analysis_plot(self, harmonic_data):
        """Create harmonic analysis visualization"""
        freqs = harmonic_data['fft_freqs']
        power = harmonic_data['power_spectrum']
        
        # Only plot positive frequencies
        positive_freq_mask = freqs > 0
        freqs_pos = freqs[positive_freq_mask]
        power_pos = power[positive_freq_mask]
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Power Spectrum', 'Dominant Harmonics'),
            vertical_spacing=0.1
        )
        
        # Power spectrum
        fig.add_trace(
            go.Scatter(
                x=freqs_pos,
                y=power_pos,
                mode='lines',
                line=dict(color=self.colors['wave'], width=2),
                name='Power Spectrum'
            ),
            row=1, col=1
        )
        
        # Dominant frequencies
        dominant_freqs = harmonic_data['frequencies'][harmonic_data['frequencies'] > 0]
        dominant_power = [power_pos[np.argmin(np.abs(freqs_pos - f))] for f in dominant_freqs]
        
        fig.add_trace(
            go.Bar(
                x=dominant_freqs,
                y=dominant_power,
                marker_color=self.colors['high'],
                name='Dominant Harmonics'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title='🎵 Tidal Harmonic Analysis',
            paper_bgcolor=self.theme['paper_bgcolor'],
            plot_bgcolor=self.theme['bg_color'],
            font=dict(color=self.theme['font_color']),
            showlegend=False
        )
        
        return fig
    
    def create_monthly_comparison(self, df):
        """Create monthly tide comparison violin plot"""
        fig = go.Figure()
        
        months = df['month'].unique()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for month in sorted(months):
            month_data = df[df['month'] == month]['height']
            
            fig.add_trace(go.Violin(
                y=month_data,
                x=[month_names[month-1]] * len(month_data),
                name=month_names[month-1],
                box_visible=True,
                meanline_visible=True,
                fillcolor=f'rgba({74 + month * 10}, {144 + month * 5}, {226 - month * 5}, 0.6)',
                line_color=self.theme['font_color']
            ))
        
        fig.update_layout(
            title='📊 Monthly Tide Height Distribution',
            xaxis_title='Month',
            yaxis_title='Tide Height (m)',
            paper_bgcolor=self.theme['paper_bgcolor'],
            plot_bgcolor=self.theme['bg_color'],
            font=dict(color=self.theme['font_color']),
            showlegend=False
        )
        
        return fig
    
    def create_tide_range_analysis(self, df):
        """Create tidal range analysis"""
        # Calculate daily tidal ranges
        daily_stats = df.groupby(df['datetime'].dt.date).agg({
            'height': ['min', 'max', 'mean', 'std']
        }).round(2)
        
        daily_stats.columns = ['min_height', 'max_height', 'avg_height', 'std_height']
        daily_stats['tidal_range'] = daily_stats['max_height'] - daily_stats['min_height']
        daily_stats.reset_index(inplace=True)
        daily_stats.columns = ['date'] + list(daily_stats.columns[1:])
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily Tidal Range', 'Average Daily Heights'),
            vertical_spacing=0.15
        )
        
        # Tidal range plot
        fig.add_trace(
            go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['tidal_range'],
                mode='lines+markers',
                line=dict(color=self.colors['wave'], width=2),
                marker=dict(size=4),
                name='Tidal Range',
                fill='tonexty',
                fillcolor='rgba(74, 144, 226, 0.3)'
            ),
            row=1, col=1
        )
        
        # Average heights with error bars
        fig.add_trace(
            go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['avg_height'],
                error_y=dict(
                    type='data',
                    array=daily_stats['std_height'],
                    visible=True
                ),
                mode='lines+markers',
                line=dict(color=self.colors['high'], width=2),
                marker=dict(size=4),
                name='Average Height'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title='📏 Tidal Range Analysis',
            paper_bgcolor=self.theme['paper_bgcolor'],
            plot_bgcolor=self.theme['bg_color'],
            font=dict(color=self.theme['font_color']),
            showlegend=False
        )
        
        return fig
    
    def create_real_time_gauge(self, current_height, max_height=3.0):
        """Create real-time tide gauge"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_height,
            delta={'reference': max_height/2},
            gauge={
                'axis': {'range': [None, max_height]},
                'bar': {'color': self.colors['wave']},
                'steps': [
                    {'range': [0, max_height*0.3], 'color': self.colors['low']},
                    {'range': [max_height*0.3, max_height*0.7], 'color': 'lightgray'},
                    {'range': [max_height*0.7, max_height], 'color': self.colors['high']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_height * 0.9
                }
            },
            title={'text': "Current Tide Height (m)"}
        ))
        
        fig.update_layout(
            paper_bgcolor=self.theme['paper_bgcolor'],
            font=dict(color=self.theme['font_color']),
            height=400
        )
        
        return fig

def main():
    """Test visualization functions"""
    # This would typically be called from the main app
    pass

if __name__ == "__main__":
    main()