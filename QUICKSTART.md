# 🚀 Quick Start Guide

## Getting Started with Dynamic Wave

### 1. **Launch the Application**
- Open your terminal/command prompt
- Navigate to the project folder
- Run: `streamlit run src/app.py`
- Open `http://localhost:8501` in your browser

### 2. **Dashboard Overview**
- **Header**: Beautiful ocean-themed title with wave animation
- **Sidebar**: Interactive controls for filtering and visualization selection
- **Metrics**: Real-time tide statistics (current height, max/min, range)
- **Main Tabs**: Four main sections for exploration

### 3. **Dashboard Layout Modes**
📊 **Multi-View Dashboard**: Display multiple charts simultaneously on one screen
🌊 **Enhanced Wave Animation**: Dynamic wave visualization with layered effects and animations
🕐 **Tide Clock**: Circular 24-hour tide pattern display
📅 **Seasonal Heatmap**: Day vs. hour tide height patterns
🏔️ **3D Surface**: Three-dimensional tide surface visualization
📊 **Monthly Comparison**: Violin plots comparing monthly distributions
📏 **Range Analysis**: Daily tidal range and average height trends
⚡ **Real-time Gauge**: Live tide height gauge with thresholds

### 4. **Interactive Controls**
- **Dashboard Layout**: Choose between single view or multi-view dashboard
- **Multi-View Options**: When in multi-view mode, select which charts to display
- **Date Range**: Filter data by specific date periods
- **Time Period**: Quick filters (Last 7 days, 30 days, etc.)
- **Height Range**: Slider to filter by tide height range

### 5. **Analytics Tab**
- **Data Insights**: Automated analysis of tidal patterns
- **Seasonal Variations**: Monthly and seasonal statistics
- **Advanced Analysis**: Button to run comprehensive statistical analysis
- **Tidal Patterns**: High/low tide occurrence statistics

### 6. **Data Tab**
- **Interactive Table**: Sortable and filterable data display
- **Column Selection**: Choose which columns to display
- **Export**: Download filtered data as CSV
- **Row Limits**: Control how many rows to show

### 7. **Key Features to Explore**
- 📊 **Multi-View Dashboard**: See multiple visualizations simultaneously
- � **Enhanced Wave Animation**: Layered wave effects with smooth animations
- �🌙 **Moon Phase Integration**: Correlate tides with lunar cycles
- 📈 **Predictive Modeling**: ML-based tide predictions
- 🔍 **Anomaly Detection**: Identify unusual tidal patterns  
- 🎨 **Enhanced Animations**: Floating headers, pulsing effects, and smooth transitions

### 8. **Pro Tips**
- **Start with Multi-View Dashboard**: Enable Wave Animation + Gauge + Clock for a comprehensive view
- **Enhanced Wave Mode**: Use for presentations - it has beautiful layered animations
- Use the sidebar filters to focus on specific time periods
- Try different combinations in multi-view mode to compare patterns
- Check the Analytics tab for deeper insights
- Export data for external analysis
- The 3D surface view shows annual patterns beautifully
- Multi-view is perfect for comprehensive analysis

### 9. **Data Source**
The application uses Hong Kong Observatory tide data from Chek Lap Kok (E) for 2023, with intelligent data generation to create comprehensive patterns for visualization.

### 10. **Troubleshooting**
- If charts don't load: Refresh the page or adjust date filters
- For performance: Reduce date range for complex visualizations
- If Streamlit crashes: Restart with `streamlit run src/app.py`

Enjoy exploring the rhythmic beauty of Hong Kong's tidal patterns! 🌊