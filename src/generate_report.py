from jinja2 import Template
from datetime import datetime
import json
import os
from generate_charts import generate_all_charts

def generate_html_report(data, include_charts=True):
    """Generate HTML email report from data"""
    
    # Read the template
    with open('templates/email_template.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    
    # Format the report date
    report_date = datetime.now().strftime('%B %d, %Y')
    
    # Generate charts if requested
    charts = {}
    if include_charts:
        from dotenv import load_dotenv
        load_dotenv()
        print("Generating charts...")
        charts = generate_all_charts(os.getenv('FRED_API_KEY'))
        
        # Debug: print what charts we got
        print(f"\nCharts generated: {list(charts.keys())}")
        print(f"Economic indicators: {list(data.get('economic', {}).keys())}")
    
    # Render the template
    html = template.render(
        report_date=report_date,
        economic=data.get('economic', {}),
        charts=charts
    )
    
    return html, charts

if __name__ == '__main__':
    # Test with sample data
    from fetch_data import EconomicDataFetcher
    
    fetcher = EconomicDataFetcher()
    data = fetcher.fetch_all_data()
    
    html, charts = generate_html_report(data, include_charts=True)
    
    # Save to file to preview
    with open('test_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("\n✓ Report generated! Open 'test_report.html' in your browser to preview.")