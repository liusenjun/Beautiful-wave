"""
Main Streamlit application for Dynamic Wave tide visualization
Beautiful and interactive dashboard for Hong Kong tide data
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_scraper import HKOTideDataScraper
from data_processor import TideDataProcessor
from visualizations import TideVisualizer

# Page config
st.set_page_config(
    page_title="🌊 Dynamic Wave - HK Tides",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ocean theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0d1421 0%, #1e3a5f 50%, #2e5a8a 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e2329 0%, #2a2e39 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #4a90e2;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(74, 144, 226, 0.3);
    }
    
    .status-card-high {
        border-left: 4px solid #e74c3c;
        background: linear-gradient(135deg, #1e2329 0%, #2a2e39 100%);
    }
    
    .status-card-low {
        border-left: 4px solid #3498db;
        background: linear-gradient(135deg, #1e2329 0%, #2a2e39 100%);
    }
    
    .status-card-rising {
        border-left: 4px solid #2ecc71;
        background: linear-gradient(135deg, #1e2329 0%, #2a2e39 100%);
    }
    
    .status-card-falling {
        border-left: 4px solid #f39c12;
        background: linear-gradient(135deg, #1e2329 0%, #2a2e39 100%);
    }
    
    .wave-animation {
        background: linear-gradient(45deg, #4a90e2, #67b7dc, #85c9f0, #4a90e2);
        background-size: 400% 400%;
        animation: wave 3s ease-in-out infinite;
        height: 6px;
        border-radius: 5px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(74, 144, 226, 0.3);
    }
    
    @keyframes wave {
        0% { background-position: 0% 50%; }
        25% { background-position: 100% 0%; }
        50% { background-position: 100% 100%; }
        75% { background-position: 0% 100%; }
        100% { background-position: 0% 50%; }
    }
    
    .floating-animation {
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(74, 144, 226, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(74, 144, 226, 0); }
        100% { box-shadow: 0 0 0 0 rgba(74, 144, 226, 0); }
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0d1421 0%, #1e2329 100%);
    }
    
    .stSelectbox > div > div {
        background: #1e2329;
        color: white;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #2e5a8a 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4a90e2;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class DynamicWaveApp:
    def __init__(self):
        self.processor = TideDataProcessor()
        self.visualizer = TideVisualizer()
        self.data = None
        self.processed_data = None
    
    def get_tide_interpretation(self, current_height, avg_height, height_change):
        """Get meaningful interpretation of current tide conditions"""
        interpretations = {
            'status': '',
            'recommendation': '',
            'activity_level': ''
        }
        
        height_diff = current_height - avg_height
        
        if height_diff > 0.8:
            interpretations['status'] = "Exceptionally High Tide"
            interpretations['recommendation'] = "Perfect for deep water activities"
            interpretations['activity_level'] = "Peak"
        elif height_diff > 0.3:
            interpretations['status'] = "High Tide"
            interpretations['recommendation'] = "Good for boating and swimming"
            interpretations['activity_level'] = "High"
        elif height_diff > -0.3:
            interpretations['status'] = "Mid Tide"
            interpretations['recommendation'] = "Moderate conditions"
            interpretations['activity_level'] = "Moderate"
        elif height_diff > -0.8:
            interpretations['status'] = "Low Tide"
            interpretations['recommendation'] = "Great for beach exploration"
            interpretations['activity_level'] = "Low"
        else:
            interpretations['status'] = "Exceptionally Low Tide"
            interpretations['recommendation'] = "Best for tide pool exploration"
            interpretations['activity_level'] = "Minimal"
        
        return interpretations
        
    @st.cache_data
    def load_and_process_data(_self):
        """Load and process tide data with caching"""
        # Load data
        _self.data = _self.processor.load_data()
        
        # Process data
        _self.processed_data = _self.processor.detect_high_low_tides()
        _self.processed_data = _self.processor.add_tidal_features()
        
        return _self.processed_data
    
    def render_header(self):
        """Render main header"""
        st.markdown("""
        <div class="main-header floating-animation">
            <h1>🌊 Dynamic Wave</h1>
            <h3>Hong Kong Tide Visualization Dashboard</h3>
            <p>Explore the rhythmic beauty of Chek Lap Kok tidal patterns</p>
        </div>
        <div class="wave-animation pulse-animation"></div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.markdown("## 🎛️ Controls")
        
        # Date range selector
        if self.processed_data is not None:
            min_date = self.processed_data['datetime'].dt.date.min()
            max_date = self.processed_data['datetime'].dt.date.max()
            
            date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="date_range"
            )
            
            # Dashboard layout options
            layout_mode = st.sidebar.selectbox(
                "Dashboard Layout",
                ["📊 Multi-View Dashboard", "🌊 Enhanced Wave Animation", "🕐 Tide Clock", 
                 "📅 Seasonal Heatmap", "🏔️ 3D Surface", "📊 Monthly Comparison",
                 "📏 Range Analysis", "⚡ Real-time Gauge"],
                key="layout_mode"
            )
            
            # Multi-view options
            if layout_mode == "📊 Multi-View Dashboard":
                st.sidebar.markdown("### 🎛️ Multi-View Options")
                show_wave = st.sidebar.checkbox("🌊 Wave Animation", True)
                show_gauge = st.sidebar.checkbox("⚡ Real-time Gauge", True)
                show_clock = st.sidebar.checkbox("🕐 Tide Clock", True)
                show_monthly = st.sidebar.checkbox("📊 Monthly Stats", True)
                show_heatmap = st.sidebar.checkbox("📅 Mini Heatmap", False)
                
                multi_view_options = {
                    'wave': show_wave,
                    'gauge': show_gauge,
                    'clock': show_clock,
                    'monthly': show_monthly,
                    'heatmap': show_heatmap
                }
            else:
                multi_view_options = None
            
            # Time period filter
            time_filter = st.sidebar.selectbox(
                "Time Period",
                ["All", "Last 7 Days", "Last 30 Days", "This Month", "Custom"],
                key="time_filter"
            )
            
            # Tide height filter
            height_range = st.sidebar.slider(
                "Height Range (m)",
                min_value=float(self.processed_data['height'].min()),
                max_value=float(self.processed_data['height'].max()),
                value=(float(self.processed_data['height'].min()), 
                      float(self.processed_data['height'].max())),
                step=0.1,
                key="height_range"
            )
            
            return {
                'date_range': date_range,
                'layout_mode': layout_mode,
                'multi_view_options': multi_view_options,
                'time_filter': time_filter,
                'height_range': height_range
            }
        
        return None
    
    def filter_data(self, controls):
        """Filter data based on controls"""
        if controls is None or self.processed_data is None:
            return self.processed_data
        
        filtered_data = self.processed_data.copy()
        
        # Date filter
        if len(controls['date_range']) == 2:
            start_date, end_date = controls['date_range']
            filtered_data = filtered_data[
                (filtered_data['datetime'].dt.date >= start_date) &
                (filtered_data['datetime'].dt.date <= end_date)
            ]
        
        # Height filter
        min_height, max_height = controls['height_range']
        filtered_data = filtered_data[
            (filtered_data['height'] >= min_height) &
            (filtered_data['height'] <= max_height)
        ]
        
        return filtered_data
    
    def render_metrics(self, data):
        """Render meaningful and dynamic key metrics"""
        if data is None or data.empty:
            return
        
        # Calculate meaningful metrics
        current_height = data['height'].iloc[-1]
        previous_height = data['height'].iloc[-2] if len(data) > 1 else current_height
        height_change = current_height - previous_height
        
        # Determine tide status
        high_tides = data[data['tide_type'] == 'high']['height'] if 'tide_type' in data.columns else []
        low_tides = data[data['tide_type'] == 'low']['height'] if 'tide_type' in data.columns else []
        
        # Get current tide phase
        current_time = data['datetime'].iloc[-1]
        avg_height = data['height'].mean()
        
        if current_height > avg_height + 0.5:
            tide_status = "High Tide"
            tide_emoji = "🌊"
        elif current_height < avg_height - 0.5:
            tide_status = "Low Tide" 
            tide_emoji = "🏖️"
        elif height_change > 0:
            tide_status = "Rising"
            tide_emoji = "📈"
        else:
            tide_status = "Falling"
            tide_emoji = "📉"
        
        # Calculate next tide prediction
        if len(high_tides) > 0 and len(low_tides) > 0:
            next_high = high_tides.max()
            next_low = low_tides.min()
            if current_height < avg_height:
                time_to_high = "~2-4 hours"
                next_event = f"High: {next_high:.2f}m"
            else:
                time_to_low = "~3-5 hours"
                next_event = f"Low: {next_low:.2f}m"
        else:
            next_event = "Calculating..."
        
        # Calculate tidal energy (rate of change)
        if len(data) >= 6:
            recent_changes = data['height'].diff().tail(6)
            tidal_energy = abs(recent_changes.mean()) * 100
            energy_status = "High" if tidal_energy > 0.1 else "Moderate" if tidal_energy > 0.05 else "Low"
        else:
            tidal_energy = 0
            energy_status = "Low"
        
        # Moon phase influence (simplified)
        day_of_month = current_time.day
        moon_phase = ""
        if 1 <= day_of_month <= 3 or 28 <= day_of_month <= 31:
            moon_phase = "🌑 New Moon (Spring Tide)"
        elif 13 <= day_of_month <= 16:
            moon_phase = "🌕 Full Moon (Spring Tide)"
        elif 6 <= day_of_month <= 9:
            moon_phase = "🌓 First Quarter"
        elif 21 <= day_of_month <= 24:
            moon_phase = "🌗 Last Quarter"
        else:
            moon_phase = "🌒 Waxing/Waning"
        
        # Today's tidal range
        today_data = data[data['datetime'].dt.date == current_time.date()]
        if not today_data.empty:
            today_range = today_data['height'].max() - today_data['height'].min()
            yesterday_data = data[data['datetime'].dt.date == (current_time.date() - pd.Timedelta(days=1))]
            if not yesterday_data.empty:
                yesterday_range = yesterday_data['height'].max() - yesterday_data['height'].min()
                range_change = today_range - yesterday_range
            else:
                range_change = 0
        else:
            today_range = data['height'].max() - data['height'].min()
            range_change = 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label=f"{tide_emoji} Current Status", 
                value=f"{current_height:.2f}m",
                delta=f"{tide_status} ({height_change:+.2f}m)",
                delta_color="normal"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="� Next Tide Event", 
                value=next_event,
                delta=time_to_high if 'time_to_high' in locals() else time_to_low if 'time_to_low' in locals() else "Calculating...",
                delta_color="off"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="⚡ Tidal Energy", 
                value=f"{energy_status}",
                delta=f"{tidal_energy:.2f}% change rate",
                delta_color="normal" if energy_status == "High" else "off"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="🌙 Lunar Influence", 
                value=moon_phase.split()[1] if len(moon_phase.split()) > 1 else "Phase",
                delta=moon_phase.split("(")[1].replace(")", "") if "(" in moon_phase else "Normal Tide",
                delta_color="normal" if "Spring" in moon_phase else "off"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col5:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="📏 Today's Range", 
                value=f"{today_range:.2f}m",
                delta=f"{range_change:+.2f}m vs yesterday" if range_change != 0 else "First day data",
                delta_color="normal" if range_change > 0 else "inverse" if range_change < 0 else "off"
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_visualization(self, layout_mode, multi_view_options, data):
        """Render selected visualization or multi-view dashboard"""
        if data is None or data.empty:
            st.warning("No data available for visualization")
            return
        
        if layout_mode == "📊 Multi-View Dashboard":
            self.render_multi_view_dashboard(multi_view_options, data)
            
        elif layout_mode == "🌊 Enhanced Wave Animation":
            fig = self.visualizer.create_wave_animation(data, enhanced=True)
            st.plotly_chart(fig, width='stretch')
            
        elif layout_mode == "🕐 Tide Clock":
            selected_date = st.date_input(
                "Select Date for Tide Clock",
                value=data['datetime'].dt.date.iloc[0],
                min_value=data['datetime'].dt.date.min(),
                max_value=data['datetime'].dt.date.max()
            )
            fig = self.visualizer.create_circular_tide_clock(data, selected_date)
            st.plotly_chart(fig, width='stretch')
            
        elif layout_mode == "📅 Seasonal Heatmap":
            fig = self.visualizer.create_seasonal_heatmap(data)
            st.plotly_chart(fig, width='stretch')
            
        elif layout_mode == "🏔️ 3D Surface":
            fig = self.visualizer.create_3d_tide_surface(data)
            st.plotly_chart(fig, width='stretch')
            
        elif layout_mode == "📊 Monthly Comparison":
            fig = self.visualizer.create_monthly_comparison(data)
            st.plotly_chart(fig, width='stretch')
            
        elif layout_mode == "📏 Range Analysis":
            fig = self.visualizer.create_tide_range_analysis(data)
            st.plotly_chart(fig, width='stretch')
            
        elif layout_mode == "⚡ Real-time Gauge":
            current_height = data['height'].iloc[-1]
            max_height = data['height'].max()
            fig = self.visualizer.create_real_time_gauge(current_height, max_height)
            st.plotly_chart(fig, width='stretch')
    
    def render_multi_view_dashboard(self, options, data):
        """Render multi-view dashboard with multiple charts"""
        if not options:
            st.info("Select visualization options from the sidebar")
            return
        
        # Count active views
        active_views = sum(options.values())
        if active_views == 0:
            st.info("Please select at least one visualization from the sidebar")
            return
        
        # Main wave animation (always full width if selected)
        if options.get('wave', False):
            st.markdown("### 🌊 Enhanced Wave Animation")
            fig = self.visualizer.create_wave_animation(data, enhanced=True, height=500)
            st.plotly_chart(fig, width='stretch')
            st.markdown("---")
        
        # Arrange other components in columns
        remaining_views = [k for k, v in options.items() if v and k != 'wave']
        
        if len(remaining_views) == 1:
            # Single remaining view - full width
            view = remaining_views[0]
            if view == 'gauge':
                st.markdown("### ⚡ Real-time Tide Gauge")
                current_height = data['height'].iloc[-1]
                max_height = data['height'].max()
                fig = self.visualizer.create_real_time_gauge(current_height, max_height)
                st.plotly_chart(fig, width='stretch')
            elif view == 'clock':
                st.markdown("### 🕐 Daily Tide Clock")
                selected_date = data['datetime'].dt.date.iloc[0]
                fig = self.visualizer.create_circular_tide_clock(data, selected_date)
                st.plotly_chart(fig, width='stretch')
            elif view == 'monthly':
                st.markdown("### 📊 Monthly Comparison")
                fig = self.visualizer.create_monthly_comparison(data)
                st.plotly_chart(fig, width='stretch')
            elif view == 'heatmap':
                st.markdown("### 📅 Seasonal Heatmap")
                fig = self.visualizer.create_seasonal_heatmap(data)
                st.plotly_chart(fig, width='stretch')
        
        elif len(remaining_views) == 2:
            # Two views side by side
            col1, col2 = st.columns(2)
            with col1:
                self.render_single_view(remaining_views[0], data)
            with col2:
                self.render_single_view(remaining_views[1], data)
        
        elif len(remaining_views) == 3:
            # Three views: one full width, two below
            self.render_single_view(remaining_views[0], data)
            col1, col2 = st.columns(2)
            with col1:
                self.render_single_view(remaining_views[1], data)
            with col2:
                self.render_single_view(remaining_views[2], data)
        
        elif len(remaining_views) >= 4:
            # Four views in 2x2 grid
            col1, col2 = st.columns(2)
            with col1:
                self.render_single_view(remaining_views[0], data)
                if len(remaining_views) > 2:
                    self.render_single_view(remaining_views[2], data)
            with col2:
                self.render_single_view(remaining_views[1], data)
                if len(remaining_views) > 3:
                    self.render_single_view(remaining_views[3], data)
    
    def render_single_view(self, view_type, data):
        """Render a single view component"""
        if view_type == 'gauge':
            st.markdown("#### ⚡ Real-time Gauge")
            current_height = data['height'].iloc[-1]
            max_height = data['height'].max()
            fig = self.visualizer.create_real_time_gauge(current_height, max_height)
            fig.update_layout(height=300)
            st.plotly_chart(fig, width='stretch')
            
        elif view_type == 'clock':
            st.markdown("#### 🕐 Tide Clock")
            selected_date = data['datetime'].dt.date.iloc[0]
            fig = self.visualizer.create_circular_tide_clock(data, selected_date)
            fig.update_layout(height=350)
            st.plotly_chart(fig, width='stretch')
            
        elif view_type == 'monthly':
            st.markdown("#### 📊 Monthly Stats")
            fig = self.visualizer.create_monthly_comparison(data)
            fig.update_layout(height=350)
            st.plotly_chart(fig, width='stretch')
            
        elif view_type == 'heatmap':
            st.markdown("#### 📅 Mini Heatmap")
            fig = self.visualizer.create_seasonal_heatmap(data)
            fig.update_layout(height=300)
            st.plotly_chart(fig, width='stretch')
    
    def render_insights(self, data):
        """Render data insights"""
        if data is None or data.empty:
            return
        
        st.markdown("## 🔍 Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="insight-box">
                <h4>📊 Smart Metrics Explained</h4>
                <p><strong>Current Status:</strong> Shows real-time tide height with rising/falling trend<br>
                <strong>Next Tide Event:</strong> Predicts upcoming high/low tide timing<br>
                <strong>Tidal Energy:</strong> Measures how fast the tide is changing</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Current tide analysis
            current_height = data['height'].iloc[-1]
            avg_height = data['height'].mean()
            current_status = "above average" if current_height > avg_height else "below average"
            
            st.markdown(f"""
            **Current Analysis:**
            - Tide is currently **{current_status}** ({current_height:.2f}m vs {avg_height:.2f}m avg)
            - Tidal activity level based on recent change patterns
            """)
            
            # High/low tide statistics
            high_tides = data[data['tide_type'] == 'high'] if 'tide_type' in data.columns else pd.DataFrame()
            low_tides = data[data['tide_type'] == 'low'] if 'tide_type' in data.columns else pd.DataFrame()
            
            if not high_tides.empty and not low_tides.empty:
                st.write(f"**High Tides:** {len(high_tides)} occurrences, avg: {high_tides['height'].mean():.2f}m")
                st.write(f"**Low Tides:** {len(low_tides)} occurrences, avg: {low_tides['height'].mean():.2f}m")
        
        with col2:
            st.markdown("""
            <div class="insight-box">
                <h4>🌙 Lunar & Tidal Insights</h4>
                <p><strong>Lunar Influence:</strong> Moon phases affect tide strength<br>
                <strong>Spring Tides:</strong> New/Full moon = higher ranges<br>
                <strong>Neap Tides:</strong> Quarter moons = smaller ranges</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tidal range analysis
            current_time = data['datetime'].iloc[-1] if not data.empty else datetime.now()
            day_of_month = current_time.day
            
            if 1 <= day_of_month <= 3 or 28 <= day_of_month <= 31 or 13 <= day_of_month <= 16:
                tide_type = "Spring Tide Period"
                tide_desc = "Expect larger tidal ranges"
            else:
                tide_type = "Neap Tide Period" 
                tide_desc = "Expect smaller tidal ranges"
            
            st.markdown(f"""
            **Current Lunar Phase Impact:**
            - **{tide_type}**: {tide_desc}
            - Moon phase influences tidal strength by up to 40%
            - Best fishing/surfing conditions during spring tides
            """)
            
            # Monthly statistics
            if 'month' in data.columns:
                monthly_stats = data.groupby('month')['height'].agg(['mean', 'std']).round(2)
                highest_month = monthly_stats['mean'].idxmax()
                month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                st.write(f"**Highest avg month:** {month_names[highest_month]} ({monthly_stats.loc[highest_month, 'mean']:.2f}m)")
    
    def render_data_table(self, data):
        """Render data table"""
        if data is None or data.empty:
            return
        
        st.markdown("## 📋 Data Table")
        
        # Display options
        col1, col2, col3 = st.columns(3)
        with col1:
            show_columns = st.multiselect(
                "Select Columns",
                options=data.columns.tolist(),
                default=['datetime', 'height', 'tide_type', 'month', 'day'],
                key="table_columns"
            )
        
        with col2:
            rows_to_show = st.selectbox(
                "Rows to Display",
                [10, 25, 50, 100, 'All'],
                index=1,
                key="table_rows"
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort By",
                options=data.columns.tolist(),
                index=0,
                key="sort_by"
            )
        
        # Filter and display data
        display_data = data[show_columns].sort_values(sort_by)
        
        if rows_to_show != 'All':
            display_data = display_data.head(rows_to_show)
        
        st.dataframe(display_data, use_container_width=True)
        
        # Download button
        csv = display_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"hk_tide_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def run(self):
        """Main application entry point"""
        # Render header
        self.render_header()
        
        # Load data
        with st.spinner("🌊 Loading tide data..."):
            self.processed_data = self.load_and_process_data()
        
        if self.processed_data is None or self.processed_data.empty:
            st.error("Failed to load tide data. Please check your connection.")
            return
        
        # Render sidebar controls
        controls = self.render_sidebar()
        
        # Filter data
        filtered_data = self.filter_data(controls)
        
        # Render metrics
        self.render_metrics(filtered_data)
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Visualizations", "🔍 Analytics", "📋 Data", "ℹ️ About"])
        
        with tab1:
            if controls:
                self.render_visualization(
                    controls['layout_mode'], 
                    controls['multi_view_options'], 
                    filtered_data
                )
            else:
                st.info("Please wait while data loads...")
        
        with tab2:
            self.render_insights(filtered_data)
            
            # Additional analytics
            if st.button("🔬 Run Advanced Analysis"):
                with st.spinner("Performing advanced analysis..."):
                    stats = self.processor.calculate_statistics()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Basic Statistics:**")
                        st.write(stats['basic_stats'])
                    
                    with col2:
                        st.write("**Monthly Statistics:**")
                        st.write(stats['monthly_stats'])
        
        with tab3:
            self.render_data_table(filtered_data)
        
        with tab4:
            st.markdown("""
            ## 🌊 About Dynamic Wave
            
            **Dynamic Wave** is an interactive visualization dashboard for Hong Kong Observatory tide data at Chek Lap Kok.
            
            ### Features:
            - 🌊 **Real-time Visualizations**: Interactive plots with smooth animations
            - 📊 **Multiple Chart Types**: From 2D waves to 3D surfaces and polar plots
            - 🎵 **Harmonic Analysis**: Frequency domain analysis of tidal patterns
            - 📈 **Statistical Insights**: Comprehensive data analysis and trends
            - 🎨 **Beautiful UI**: Ocean-themed design with gradient effects
            
            ### Data Source:
            Hong Kong Observatory - Tidal Information at Chek Lap Kok (E) 2023
            
            ### Technology Stack:
            - **Frontend**: Streamlit with custom CSS
            - **Data Processing**: Pandas, NumPy, SciPy
            - **Visualization**: Plotly, Matplotlib, Seaborn
            - **Analysis**: Harmonic analysis, FFT, statistical modeling
            
            ### Created with ❤️ for ocean data enthusiasts
            """)

def main():
    """Main function"""
    app = DynamicWaveApp()
    app.run()

if __name__ == "__main__":
    main()