"""
Data processing and analysis module for tide data
Handles cleaning, transformation, and feature engineering
"""

import pandas as pd
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
import warnings
warnings.filterwarnings('ignore')

class TideDataProcessor:
    def __init__(self):
        self.df = None
        self.processed_df = None
        
    def load_data(self, filepath=None):
        """Load tide data from CSV or create sample data"""
        if filepath:
            self.df = pd.read_csv(filepath)
            self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        else:
            # Create sample data if no file provided
            from data_scraper import HKOTideDataScraper
            scraper = HKOTideDataScraper()
            tide_records = scraper.create_comprehensive_dataset()
            self.df = scraper.convert_to_dataframe(tide_records)
        
        return self.df
    
    def detect_high_low_tides(self):
        """Detect high and low tides using signal processing"""
        # Sort data by datetime
        df_sorted = self.df.sort_values('datetime').copy()
        
        # Find peaks (high tides) and troughs (low tides)
        heights = df_sorted['height'].values
        
        # Use scipy to find peaks and troughs
        high_tide_indices, _ = signal.find_peaks(heights, distance=2, prominence=0.3)
        low_tide_indices, _ = signal.find_peaks(-heights, distance=2, prominence=0.3)
        
        # Mark tide types
        df_sorted['tide_type'] = 'normal'
        df_sorted.loc[df_sorted.index[high_tide_indices], 'tide_type'] = 'high'
        df_sorted.loc[df_sorted.index[low_tide_indices], 'tide_type'] = 'low'
        
        self.processed_df = df_sorted
        return df_sorted
    
    def add_tidal_features(self):
        """Add advanced tidal features"""
        if self.processed_df is None:
            self.detect_high_low_tides()
        
        df = self.processed_df.copy()
        
        # Tidal range (difference between consecutive high and low tides)
        high_tides = df[df['tide_type'] == 'high']['height']
        low_tides = df[df['tide_type'] == 'low']['height']
        
        if len(high_tides) > 1 and len(low_tides) > 1:
            avg_high = high_tides.mean()
            avg_low = low_tides.mean()
            df['tidal_range'] = avg_high - avg_low
        else:
            df['tidal_range'] = df['height'].max() - df['height'].min()
        
        # Rate of change
        df['height_change'] = df['height'].diff()
        df['height_change_rate'] = df['height_change'] / df['datetime'].diff().dt.total_seconds() * 3600  # per hour
        
        # Moving averages
        df['height_ma_6h'] = df['height'].rolling(window=6, center=True).mean()
        df['height_ma_24h'] = df['height'].rolling(window=24, center=True).mean()
        
        # Seasonal decomposition components
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
        df['hour_sin'] = np.sin(2 * np.pi * df['time_decimal'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['time_decimal'] / 24)
        
        # Tidal harmonics (simplified)
        df['M2_component'] = np.sin(2 * np.pi * df['time_decimal'] / 12.42)  # Principal lunar semi-diurnal
        df['S2_component'] = np.sin(2 * np.pi * df['time_decimal'] / 12.00)  # Principal solar semi-diurnal
        df['K1_component'] = np.sin(2 * np.pi * df['time_decimal'] / 23.93)  # Lunar diurnal
        df['O1_component'] = np.sin(2 * np.pi * df['time_decimal'] / 25.82)  # Lunar diurnal
        
        # Anomalies detection
        height_std = df['height'].std()
        height_mean = df['height'].mean()
        df['is_anomaly'] = np.abs(df['height'] - height_mean) > 2 * height_std
        
        # Tidal categories
        df['tide_category'] = pd.cut(
            df['height'], 
            bins=5, 
            labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
        )
        
        self.processed_df = df
        return df
    
    def perform_harmonic_analysis(self):
        """Perform tidal harmonic analysis"""
        if self.processed_df is None:
            self.add_tidal_features()
        
        df = self.processed_df.copy()
        
        # FFT analysis
        heights = df['height'].values
        n = len(heights)
        
        # Remove trend
        detrended = signal.detrend(heights)
        
        # Apply FFT
        yf = fft(detrended)
        xf = fftfreq(n, d=1)  # Assuming 1-hour sampling
        
        # Find dominant frequencies
        power = np.abs(yf)
        dominant_freqs = xf[np.argsort(power)[-10:]]  # Top 10 frequencies
        
        harmonic_analysis = {
            'frequencies': dominant_freqs,
            'power_spectrum': power,
            'fft_freqs': xf,
            'fft_values': yf
        }
        
        return harmonic_analysis
    
    def calculate_statistics(self):
        """Calculate comprehensive statistics"""
        if self.processed_df is None:
            self.add_tidal_features()
        
        df = self.processed_df
        
        stats = {
            'basic_stats': df['height'].describe(),
            'monthly_stats': df.groupby('month')['height'].agg(['mean', 'std', 'min', 'max']),
            'tide_type_stats': df.groupby('tide_type')['height'].agg(['count', 'mean', 'std']),
            'seasonal_stats': {
                'spring': df[df['month'].isin([3, 4, 5])]['height'].describe(),
                'summer': df[df['month'].isin([6, 7, 8])]['height'].describe(),
                'autumn': df[df['month'].isin([9, 10, 11])]['height'].describe(),
                'winter': df[df['month'].isin([12, 1, 2])]['height'].describe(),
            },
            'weekend_stats': {
                'weekday': df[~df['is_weekend']]['height'].describe(),
                'weekend': df[df['is_weekend']]['height'].describe(),
            }
        }
        
        return stats
    
    def create_interpolated_series(self, resolution_hours=0.25):
        """Create high-resolution interpolated time series"""
        if self.processed_df is None:
            self.add_tidal_features()
        
        df = self.processed_df.sort_values('datetime')
        
        # Create new time index with higher resolution
        start_date = df['datetime'].min()
        end_date = df['datetime'].max()
        new_index = pd.date_range(
            start=start_date, 
            end=end_date, 
            freq=f'{int(resolution_hours * 60)}min'
        )
        
        # Interpolate height values
        df_indexed = df.set_index('datetime')
        interpolated = df_indexed['height'].reindex(new_index).interpolate(method='cubic')
        
        # Create new dataframe
        interpolated_df = pd.DataFrame({
            'datetime': new_index,
            'height': interpolated.values
        })
        
        # Add time features
        interpolated_df['hour'] = interpolated_df['datetime'].dt.hour
        interpolated_df['minute'] = interpolated_df['datetime'].dt.minute
        interpolated_df['day_of_year'] = interpolated_df['datetime'].dt.dayofyear
        interpolated_df['time_decimal'] = (
            interpolated_df['hour'] + interpolated_df['minute'] / 60.0
        )
        
        return interpolated_df
    
    def save_processed_data(self, filename='processed_tide_data.csv'):
        """Save processed data to CSV"""
        if self.processed_df is not None:
            filepath = f"data/{filename}"
            self.processed_df.to_csv(filepath, index=False)
            print(f"Processed data saved to {filepath}")
            return filepath
        else:
            print("No processed data to save. Run processing methods first.")
            return None

def main():
    """Main processing function"""
    processor = TideDataProcessor()
    
    print("Loading and processing tide data...")
    
    # Load data
    df = processor.load_data()
    print(f"Loaded {len(df)} records")
    
    # Detect tides
    processed_df = processor.detect_high_low_tides()
    print(f"Detected high/low tides in {len(processed_df)} records")
    
    # Add features
    enhanced_df = processor.add_tidal_features()
    print(f"Added tidal features: {list(enhanced_df.columns)}")
    
    # Perform harmonic analysis
    harmonic_results = processor.perform_harmonic_analysis()
    print(f"Completed harmonic analysis with {len(harmonic_results['frequencies'])} dominant frequencies")
    
    # Calculate statistics
    stats = processor.calculate_statistics()
    print("Calculated comprehensive statistics")
    
    # Create interpolated series
    interpolated = processor.create_interpolated_series()
    print(f"Created interpolated series with {len(interpolated)} points")
    
    # Save processed data
    processor.save_processed_data()
    
    return processor, stats, harmonic_results, interpolated

if __name__ == "__main__":
    processor, stats, harmonic_results, interpolated = main()