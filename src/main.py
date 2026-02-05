"""
Main script to fetch data, generate report, and send email.
This is what GitHub Actions will run weekly.
"""
import os
from dotenv import load_dotenv
from fetch_data import EconomicDataFetcher
from generate_report import generate_html_report
from send_email import send_email_report

def main():
    """Main execution function"""
    
    load_dotenv()
    
    print("="*60)
    print("WEEKLY ECONOMIC REPORT - AUTOMATED RUN")
    print("="*60)
    
    # Step 1: Fetch data
    print("\n[1/3] Fetching economic data...")
    fetcher = EconomicDataFetcher(use_cache=False)  # No cache for scheduled runs
    data = fetcher.fetch_all_data()
    
    if not data.get('economic'):
        print("✗ No economic data retrieved. Aborting.")
        return False
    
    print(f"✓ Successfully fetched {len(data['economic'])} indicators")
    
    # Step 2: Generate report
    print("\n[2/3] Generating HTML report...")
    html, charts = generate_html_report(data, include_charts=True)
    print(f"✓ Report generated with {len(charts)} charts")
    
    # Step 3: Send email
    print("\n[3/3] Sending email report...")
    success = send_email_report(html, charts_dict=charts)
    
    if success:
        print("\n" + "="*60)
        print("✓ WEEKLY REPORT COMPLETED SUCCESSFULLY")
        print("="*60)
        return True
    else:
        print("\n" + "="*60)
        print("✗ FAILED TO SEND EMAIL")
        print("="*60)
        return False

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)