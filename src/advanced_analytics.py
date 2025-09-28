"""
Advanced analytics module with moon phases and predictive modeling
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import ephem
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class AdvancedTideAnalytics:
    def __init__(self):
        self.moon_phases = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous',
                           'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent']
        self.model = None
        
    def calculate_moon_phase(self, date):
        """Calculate moon phase for a given date"""
        observer = ephem.Observer()
        observer.lat = '22.3193'  # Hong Kong latitude
        observer.lon = '114.1694'  # Hong Kong longitude
        observer.date = date
        
        moon = ephem.Moon(observer)
        
        # Calculate moon phase (0 = new moon, 0.5 = full moon)
        phase = moon.moon_phase
        
        # Convert to phase name
        phase_index = int((phase * 8) % 8)
        phase_name = self.moon_phases[phase_index]
        
        return {
            'phase_value': phase,
            'phase_name': phase_name,
            'illumination': phase,
            'phase_angle': moon.phase
        }
    
    def add_lunar_features(self, df):
        """Add lunar-related features to dataframe"""
        df_copy = df.copy()
        
        # Calculate moon phases for each date
        moon_data = []
        for date in df_copy['datetime']:
            moon_info = self.calculate_moon_phase(date)
            moon_data.append(moon_info)
        
        moon_df = pd.DataFrame(moon_data)
        
        # Add lunar features
        df_copy['moon_phase'] = moon_df['phase_value']
        df_copy['moon_phase_name'] = moon_df['phase_name']
        df_copy['moon_illumination'] = moon_df['illumination']
        
        # Add lunar tidal components
        df_copy['lunar_distance_factor'] = np.sin(2 * np.pi * df_copy['day_of_year'] / 27.32)  # Lunar month
        df_copy['solar_distance_factor'] = np.sin(2 * np.pi * df_copy['day_of_year'] / 365.25)  # Solar year
        
        # Spring/Neap tide indicator
        df_copy['is_spring_tide'] = ((df_copy['moon_phase'] < 0.1) | (df_copy['moon_phase'] > 0.9) |
                                    ((df_copy['moon_phase'] > 0.4) & (df_copy['moon_phase'] < 0.6)))
        
        return df_copy
    
    def harmonic_tide_prediction(self, df, prediction_hours=72):
        """Predict future tides using harmonic analysis"""
        # Extract harmonic components
        time_hours = (df['datetime'] - df['datetime'].min()).dt.total_seconds() / 3600
        heights = df['height'].values
        
        # Fit harmonic components (simplified tidal constituents)
        constituents = {
            'M2': {'period': 12.4206, 'amp': 0, 'phase': 0},  # Principal lunar semi-diurnal
            'S2': {'period': 12.0000, 'amp': 0, 'phase': 0},  # Principal solar semi-diurnal
            'N2': {'period': 12.6583, 'amp': 0, 'phase': 0},  # Lunar elliptic semi-diurnal
            'K1': {'period': 23.9345, 'amp': 0, 'phase': 0},  # Lunar diurnal
            'O1': {'period': 25.8193, 'amp': 0, 'phase': 0},  # Lunar diurnal
            'P1': {'period': 24.0659, 'amp': 0, 'phase': 0},  # Solar diurnal
        }
        
        # Fit each constituent using least squares
        for name, const in constituents.items():
            omega = 2 * np.pi / const['period']
            cos_component = np.cos(omega * time_hours)
            sin_component = np.sin(omega * time_hours)
            
            # Fit amplitude and phase
            A = np.column_stack([cos_component, sin_component])
            coeffs = np.linalg.lstsq(A, heights, rcond=None)[0]
            
            const['amp'] = np.sqrt(coeffs[0]**2 + coeffs[1]**2)
            const['phase'] = np.arctan2(coeffs[1], coeffs[0])
        
        # Generate predictions
        future_times = np.arange(time_hours[-1], time_hours[-1] + prediction_hours, 0.25)
        predictions = np.zeros(len(future_times))
        
        mean_height = np.mean(heights)
        predictions += mean_height
        
        for name, const in constituents.items():
            omega = 2 * np.pi / const['period']
            predictions += const['amp'] * np.cos(omega * future_times + const['phase'])
        
        # Create prediction dataframe
        future_datetimes = [df['datetime'].iloc[-1] + timedelta(hours=h) for h in future_times - time_hours[-1]]
        
        prediction_df = pd.DataFrame({
            'datetime': future_datetimes,
            'predicted_height': predictions,
            'prediction_type': 'harmonic'
        })
        
        return prediction_df, constituents
    
    def ml_tide_prediction(self, df, prediction_hours=72):
        """Predict future tides using machine learning"""
        # Prepare features
        df_ml = df.copy()
        
        # Add lag features
        for lag in [1, 2, 3, 6, 12, 24]:
            df_ml[f'height_lag_{lag}'] = df_ml['height'].shift(lag)
        
        # Add rolling statistics
        for window in [6, 12, 24]:
            df_ml[f'height_mean_{window}'] = df_ml['height'].rolling(window=window).mean()
            df_ml[f'height_std_{window}'] = df_ml['height'].rolling(window=window).std()
        
        # Add time features
        df_ml['hour_sin'] = np.sin(2 * np.pi * df_ml['hour'] / 24)
        df_ml['hour_cos'] = np.cos(2 * np.pi * df_ml['hour'] / 24)
        df_ml['day_sin'] = np.sin(2 * np.pi * df_ml['day_of_year'] / 365.25)
        df_ml['day_cos'] = np.cos(2 * np.pi * df_ml['day_of_year'] / 365.25)
        
        # Select features
        feature_columns = [col for col in df_ml.columns if 
                          col.startswith(('height_lag_', 'height_mean_', 'height_std_', 'hour_', 'day_')) or
                          col in ['month', 'hour', 'day_of_year']]
        
        # Prepare training data
        df_clean = df_ml.dropna()
        X = df_clean[feature_columns]
        y = df_clean['height']
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Make future predictions
        last_row = df_clean.iloc[-1:].copy()
        predictions = []
        
        for i in range(int(prediction_hours * 4)):  # 15-minute intervals
            # Create features for next prediction
            future_datetime = last_row['datetime'].iloc[0] + timedelta(minutes=15 * (i + 1))
            
            future_row = last_row.copy()
            future_row['datetime'] = future_datetime
            future_row['hour'] = future_datetime.hour
            future_row['day_of_year'] = future_datetime.timetuple().tm_yday
            
            # Update time features
            future_row['hour_sin'] = np.sin(2 * np.pi * future_row['hour'] / 24)
            future_row['hour_cos'] = np.cos(2 * np.pi * future_row['hour'] / 24)
            future_row['day_sin'] = np.sin(2 * np.pi * future_row['day_of_year'] / 365.25)
            future_row['day_cos'] = np.cos(2 * np.pi * future_row['day_of_year'] / 365.25)
            
            # Predict
            X_future = future_row[feature_columns]
            pred_height = self.model.predict(X_future)[0]
            
            predictions.append({
                'datetime': future_datetime,
                'predicted_height': pred_height,
                'prediction_type': 'ml'
            })
            
            # Update last_row for next iteration
            future_row['height'] = pred_height
            last_row = future_row
        
        prediction_df = pd.DataFrame(predictions)
        
        model_metrics = {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'r2': r2,
            'feature_importance': dict(zip(feature_columns, self.model.feature_importances_))
        }
        
        return prediction_df, model_metrics
    
    def tidal_anomaly_detection(self, df):
        """Detect anomalous tidal patterns"""
        df_copy = df.copy()
        
        # Calculate rolling statistics
        window = 24  # 24-hour window
        df_copy['rolling_mean'] = df_copy['height'].rolling(window=window, center=True).mean()
        df_copy['rolling_std'] = df_copy['height'].rolling(window=window, center=True).std()
        
        # Z-score based anomaly detection
        df_copy['z_score'] = np.abs((df_copy['height'] - df_copy['rolling_mean']) / df_copy['rolling_std'])
        df_copy['is_anomaly'] = df_copy['z_score'] > 2.5
        
        # Isolation Forest for multivariate anomaly detection
        from sklearn.ensemble import IsolationForest
        
        features = ['height', 'hour', 'day_of_year', 'month']
        iso_forest = IsolationForest(contamination=0.05, random_state=42)
        df_copy['anomaly_score'] = iso_forest.fit_predict(df_copy[features])
        df_copy['is_multivariate_anomaly'] = df_copy['anomaly_score'] == -1
        
        # Combine anomaly indicators
        df_copy['combined_anomaly'] = df_copy['is_anomaly'] | df_copy['is_multivariate_anomaly']
        
        anomaly_summary = {
            'total_anomalies': df_copy['combined_anomaly'].sum(),
            'anomaly_percentage': (df_copy['combined_anomaly'].sum() / len(df_copy)) * 100,
            'anomaly_dates': df_copy[df_copy['combined_anomaly']]['datetime'].tolist()
        }
        
        return df_copy, anomaly_summary
    
    def tidal_extreme_analysis(self, df):
        """Analyze extreme tidal events"""
        # Define extreme thresholds
        height_95 = df['height'].quantile(0.95)
        height_05 = df['height'].quantile(0.05)
        
        extreme_high = df[df['height'] >= height_95].copy()
        extreme_low = df[df['height'] <= height_05].copy()
        
        # Analyze seasonal patterns of extremes
        extreme_high['season'] = extreme_high['month'].map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Autumn', 10: 'Autumn', 11: 'Autumn'
        })
        
        extreme_low['season'] = extreme_low['month'].map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Autumn', 10: 'Autumn', 11: 'Autumn'
        })
        
        extreme_analysis = {
            'high_threshold': height_95,
            'low_threshold': height_05,
            'extreme_high_events': len(extreme_high),
            'extreme_low_events': len(extreme_low),
            'high_seasonal_dist': extreme_high['season'].value_counts().to_dict(),
            'low_seasonal_dist': extreme_low['season'].value_counts().to_dict(),
            'highest_event': {
                'height': df['height'].max(),
                'datetime': df.loc[df['height'].idxmax(), 'datetime']
            },
            'lowest_event': {
                'height': df['height'].min(),
                'datetime': df.loc[df['height'].idxmin(), 'datetime']
            }
        }
        
        return extreme_analysis
    
    def calculate_tidal_statistics(self, df):
        """Calculate comprehensive tidal statistics"""
        stats = {}
        
        # Basic statistics
        stats['basic'] = {
            'mean': df['height'].mean(),
            'median': df['height'].median(),
            'std': df['height'].std(),
            'min': df['height'].min(),
            'max': df['height'].max(),
            'range': df['height'].max() - df['height'].min(),
            'skewness': df['height'].skew(),
            'kurtosis': df['height'].kurtosis()
        }
        
        # Tidal cycle statistics
        high_tides = df[df['tide_type'] == 'high']['height']
        low_tides = df[df['tide_type'] == 'low']['height']
        
        if len(high_tides) > 0 and len(low_tides) > 0:
            stats['tidal_cycles'] = {
                'avg_high_tide': high_tides.mean(),
                'avg_low_tide': low_tides.mean(),
                'avg_tidal_range': high_tides.mean() - low_tides.mean(),
                'high_tide_std': high_tides.std(),
                'low_tide_std': low_tides.std(),
                'num_high_tides': len(high_tides),
                'num_low_tides': len(low_tides)
            }
        
        # Temporal patterns
        stats['temporal'] = {
            'hourly_avg': df.groupby('hour')['height'].mean().to_dict(),
            'monthly_avg': df.groupby('month')['height'].mean().to_dict(),
            'weekend_avg': df[df['is_weekend']]['height'].mean() if 'is_weekend' in df.columns else None,
            'weekday_avg': df[~df['is_weekend']]['height'].mean() if 'is_weekend' in df.columns else None
        }
        
        return stats

def main():
    """Test advanced analytics functions"""
    # This would be called from the main app with real data
    print("Advanced analytics module ready")

if __name__ == "__main__":
    main()