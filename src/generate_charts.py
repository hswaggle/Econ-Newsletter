import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred
import os
from datetime import datetime, timedelta
import base64
from io import BytesIO
from cache import DataCache  # Add this import

def create_chart(series_data, title, color='#3498db'):
    """Create a clean line chart and return as base64 string"""
    
    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    
    # Plot the data
    ax.plot(series_data.index, series_data.values, color=color, linewidth=2)
    
    # Style the chart
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
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

def generate_all_charts(fred_api_key, use_cache=True):
    """Generate charts for all economic indicators"""
    
    cache = DataCache(cache_duration_hours=24) if use_cache else None
    
    # Check cache first
    if cache:
        cached_charts = cache.get('all_charts')
        if cached_charts:
            return cached_charts
    
    fred = Fred(api_key=fred_api_key)
    
    indicators = {
        'UNRATE': {'name': 'Unemployment Rate', 'color': '#e74c3c'},
        'CPIAUCSL': {'name': 'CPI (Inflation)', 'color': '#e67e22'},
        'DFF': {'name': 'Fed Funds Rate', 'color': '#3498db'},
        'DGS10': {'name': '10-Year Treasury Yield', 'color': '#2ecc71'},
        'UMCSENT': {'name': 'Consumer Sentiment', 'color': '#9b59b6'},
        'HOUST': {'name': 'Housing Starts', 'color':  "#401bc5"},
        'ICSA': {'name': 'Initial Jobless Claims', 'color':  "#d11884"},
        'MORTGAGE30US': {'name': '30-Year Mortgage Rate', 'color':  "#0b5d8d"},
        'EXHOSLUSM495S': {'name': 'Existing Home Sales',  'color':  "#0b8d6d"},
        'PCE': {'name': 'Personal Consumption Expenditure', 'color':  "#dabc14"},
        'PSAVERT': {'name': 'Personal Savings Rate', 'color':  "#721a0a"},
        'M2SL': {'name': 'M2 Money Supply', 'color':  "#0c0a72"}
    }
    
    charts = {}
    
    # Get data from last 2 years for context
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    for series_id, info in indicators.items():
        try:
            print(f"Generating chart for {info['name']}...")
            data = fred.get_series(series_id, observation_start=start_date)
            
            if not data.empty:
                chart_base64 = create_chart(data, info['name'], info['color'])
                charts[info['name']] = chart_base64
                print(f"✓ Chart generated for {info['name']}")
        except Exception as e:
            print(f"✗ Error generating chart for {info['name']}: {str(e)[:100]}")
    
    # Cache the charts
    if cache and charts:
        cache.set('all_charts', charts)
    
    return charts

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    charts = generate_all_charts(os.getenv('FRED_API_KEY'), use_cache=True)
    print(f"\n✓ Generated {len(charts)} charts")
