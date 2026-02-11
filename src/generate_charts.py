import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred
import os
from datetime import datetime, timedelta
import base64
from io import BytesIO
from cache import DataCache
import pandas as pd

# Chart grouping configuration
CHART_GROUPS = {
    # Group name: [(series_id, display_name, color), ...]
    'Personal Consumption Expenditure': [
        ('PCEPI', 'PCE',  '#1aa526'),
        ('PCEPILFE', 'CORE PCE', '#60159e'),
    ],
    'Term Premium': [
        ('DGS10', '10-Year Treasury Yield', '#cca22e' ),
        ('DGS30', '30-Year Treasury Yield', '#2927ae' ),
    ],
}

# Individual charts (not grouped)
INDIVIDUAL_CHARTS = {
# Labor Market
        'UNRATE': {'name': 'Unemployment Rate', 'color': '#e74c3c'},
        'ICSA': {'name': 'Initial Jobless Claims', 'color': '#f39c12'},
        
        # Inflation & Growth
        'CPIAUCSL': {'name': 'CPI (Inflation)', 'color': '#e67e22'},
        # 'PCEPI': {'name': 'Personal Consumption Expenditure', 'color': "#1aa526"},
        # 'DPCCRV1Q225SBEA': {'name': 'CORE PCE', 'color': "#60159e"},

        # Interest Rates
        'DFF': {'name': 'Fed Funds Rate', 'color': '#3498db'},
        # 'DGS10': {'name': '10-Year Treasury Yield', 'color': "#cca22e"},
        # 'DGS30': {'name': '30-Year Treasury Yield', 'color': "#2927ae"},
        'MORTGAGE30US': {'name': '30-Year Mortgage Rate', 'color': '#e91e63'},
        
        # Yield Curve Spreads
        'T10Y2Y': {'name': '10Y-2Y Treasury Spread', 'color': '#8e44ad'},
        'T10Y3M': {'name': '10Y-3M Treasury Spread', 'color': '#9b59b6'},
        # 'T10Y30Y': {'name': '10Y-30Y Treasury Spread', 'color': '#7d3c98'},
        
        # Housing
        'HOUST': {'name': 'Housing Starts', 'color': '#1abc9c'},
        'EXHOSLUSM495S': {'name': 'Existing Home Sales', 'color': '#16a085'},
        
        # Consumer & Savings
        'UMCSENT': {'name': 'Consumer Sentiment', 'color': '#f39c12'},
        'PSAVERT': {'name': 'Personal Savings Rate', 'color': '#d35400'},
        
        # Monetary
        'M2SL': {'name': 'M2 Money Supply', 'color': '#34495e'},
}

def create_chart(series_data, title, color='#3498db'):
    """Create a clean line chart and return as base64 string"""
    
    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    
    # Plot the data
    ax.plot(series_data.index, series_data.values, color=color, linewidth=2)
    
    # Style the chart
    # ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('')
    
    # Remove gridlines
    ax.grid(False)
    
    # Remove background color - set to transparent
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')
    
    # Keep only bottom and left spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Format x-axis dates: MMM 'YY every 4 months
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    
    # Make dates horizontal instead of diagonal
    plt.xticks(rotation=0, ha='center')
    
    # Tight layout
    plt.tight_layout()
    
    # Convert to base64 for email embedding with transparent background
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64

def create_multi_line_chart(series_list, title):
    """
    Create a chart with multiple lines
    series_list: [(series_data, label, color), ...]
    """
    
    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    
    # Plot all series
    for series_data, label, color in series_list:
        ax.plot(series_data.index, series_data.values, color=color, linewidth=2, label=label)
    
    # Style the chart
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('')
    
    # Add legend
    ax.legend(loc='best', frameon=False, fontsize=10)
    
    # Remove gridlines
    ax.grid(False)
    
    # Remove background color - set to transparent
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')
    
    # Keep only bottom and left spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Format x-axis dates: MMM 'YY every 4 months
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    
    # Make dates horizontal instead of diagonal
    plt.xticks(rotation=0, ha='center')
    
    # Tight layout
    plt.tight_layout()
    
    # Convert to base64 for email embedding with transparent background
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64

def generate_all_charts(fred_api_key, use_cache=True):
    """Generate charts for all economic indicators"""
    
    cache = DataCache(cache_duration_hours=24) if use_cache else None
    
    # Check cache first
    if cache:
        cached_charts = cache.get('all_charts')
        if cached_charts:
            return cached_charts
    
    fred = Fred(api_key=fred_api_key)
    charts = {}
    
    # Get data from last 2 years for context
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    # Generate grouped charts
    for group_name, series_configs in CHART_GROUPS.items():
        try:
            print(f"Generating grouped chart: {group_name}...")
            series_list = []
            
            for series_id, display_name, color in series_configs:
                data = fred.get_series(series_id, observation_start=start_date)
                if not data.empty:
                    series_list.append((data, display_name, color))
            
            if series_list:
                chart_base64 = create_multi_line_chart(series_list, group_name)
                charts[group_name] = chart_base64
                print(f"✓ Chart generated for {group_name}")
        except Exception as e:
            print(f"✗ Error generating grouped chart {group_name}: {str(e)[:100]}")
    
    # Generate individual charts
    for series_id, info in INDIVIDUAL_CHARTS.items():
        try:
            print(f"Generating chart for {info['name']}...")
            data = fred.get_series(series_id, observation_start=start_date)
            
            if not data.empty:
                chart_base64 = create_chart(data, info['name'], info['color'])
                charts[info['name']] = chart_base64
                print(f"✓ Chart generated for {info['name']}")
        except Exception as e:
            print(f"✗ Error generating chart for {info['name']}: {str(e)[:100]}")
    
    # Generate special calculated chart: Mortgage Spreads over Treasuries
    try:
        print("Generating Mortgage Spread chart...")
        mortgage_data = fred.get_series('MORTGAGE30US', observation_start=start_date)
        treasury_30y = fred.get_series('DGS30', observation_start=start_date)
        treasury_10y = fred.get_series('DGS10', observation_start=start_date)
        
        if not mortgage_data.empty and not treasury_30y.empty and not treasury_10y.empty:
            # Calculate spreads (mortgage - treasury)
            combined = pd.DataFrame({
                'mortgage': mortgage_data,
                'treasury_30y': treasury_30y,
                'treasury_10y': treasury_10y
            })
            
            # Forward fill to handle missing data points
            combined = combined.fillna(method='ffill')
            
            # Calculate spreads
            spread_30y = combined['mortgage'] - combined['treasury_30y']
            spread_10y = combined['mortgage'] - combined['treasury_10y']
            
            # Remove NaN values
            spread_30y = spread_30y.dropna()
            spread_10y = spread_10y.dropna()
            
            series_list = [
                (spread_30y, 'Premium over 30Y Treasury', '#e91e63'),
                (spread_10y, 'Premium over 10Y Treasury', '#9b59b6')
            ]
            
            spread_chart = create_multi_line_chart(series_list, 'Mortgage Rate Premium over Treasuries')
            charts['Mortgage Rate Premium'] = spread_chart
            print("✓ Chart generated for Mortgage Rate Premium")
    except Exception as e:
        print(f"✗ Error generating spread chart: {str(e)[:100]}")
    
    # Cache the charts
    if cache and charts:
        cache.set('all_charts', charts)
    
    return charts

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    charts = generate_all_charts(os.getenv('FRED_API_KEY'), use_cache=True)
    print(f"\n✓ Generated {len(charts)} charts")