import yfinance as yf
from fredapi import Fred
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time
from cache import DataCache  # Add this import

load_dotenv()

class EconomicDataFetcher:
    def __init__(self, use_cache=True, cache_duration_hours=24):
        fred_key = os.getenv('FRED_API_KEY')
        print(f"FRED API Key loaded: {fred_key[:8] if fred_key else 'None'}... (length: {len(fred_key) if fred_key else 0})")
        self.fred = Fred(api_key=fred_key)
        self.cache = DataCache(cache_duration_hours=cache_duration_hours) if use_cache else None
        
    # def fetch_market_data(self):
    #     """Fetch major market indices and commodities"""
        
    #     # Check cache first
    #     if self.cache:
    #         cached_data = self.cache.get('market_data')
    #         if cached_data:
    #             return cached_data
        
    #     tickers = {
    #         '^GSPC': 'S&P 500',
    #         '^DJI': 'Dow Jones',
    #         '^IXIC': 'Nasdaq',
    #         '^VIX': 'VIX',
    #         'GC=F': 'Gold',
    #         'CL=F': 'Crude Oil'
    #     }
        
        # market_data = {}
        
        # # Download all at once to reduce requests
        # ticker_string = ' '.join(tickers.keys())
        
        # try:
        #     # Wait a bit to avoid rate limiting
        #     time.sleep(2)
            
        #     # Simpler download call
        #     data = yf.download(ticker_string, period='5d', progress=False)
            
        #     if not data.empty:
        #         # Handle both single and multi-ticker data structures
        #         for ticker, name in tickers.items():
        #             try:
        #                 # For multiple tickers, Close is a DataFrame
        #                 if isinstance(data['Close'], pd.DataFrame):
        #                     if ticker in data['Close'].columns:
        #                         closes = data['Close'][ticker].dropna()
        #                     else:
        #                         continue
        #                 # For single ticker, Close is a Series
        #                 else:
        #                     closes = data['Close'].dropna()
                        
        #                 if len(closes) >= 2:
        #                     current = closes.iloc[-1]
        #                     previous = closes.iloc[-2]
        #                     change_pct = ((current - previous) / previous) * 100
                            
        #                     market_data[name] = {
        #                         'current': round(float(current), 2),
        #                         'change_pct': round(float(change_pct), 2),
        #                         'date': closes.index[-1].strftime('%Y-%m-%d')
        #                     }
        #                     print(f"✓ Successfully fetched {name}")
        #             except Exception as e:
        #                 print(f"⚠ Could not process {name}: {str(e)[:50]}")
        # except Exception as e:
        #     print(f"✗ Error downloading market data: {str(e)[:100]}")
        
        # # Cache the result
        # if self.cache and market_data:
        #     self.cache.set('market_data', market_data)
            
        # return market_data
    
    def fetch_economic_indicators(self):
        """Fetch key economic indicators from FRED"""
        
        # Check cache first
        if self.cache:
            cached_data = self.cache.get('economic_indicators')
            if cached_data:
                return cached_data
        
        indicators = {
            'UNRATE': 'Unemployment Rate',
            'CPIAUCSL': 'CPI (Inflation)',
            'DFF': 'Fed Funds Rate',
            'DGS10': '10-Year Treasury Yield',
            'DGS30': '30-Year Treasury Yield',
            'UMCSENT': 'Consumer Sentiment', 
            'HOUST': 'Housing Starts',
            'ICSA': 'Initial Jobless Claims',
            'MORTGAGE30US': '30-Year Mortgage Rate',
            'EXHOSLUSM495S': 'Existing Home Sales',
            'PCE': 'Personal Consumption Expenditure',
            'PSAVERT': 'Personal Savings Rate',
            'M2SL': 'M2 Money Supply'
        }
        
        economic_data = {}
        for series_id, name in indicators.items():
            try:
                data = self.fred.get_series(series_id)
                if not data.empty:
                    current = data.iloc[-1]
                    previous = data.iloc[-2] if len(data) > 1 else current
                    change = current - previous
                    
                    economic_data[name] = {
                        'current': round(current, 2),
                        'change': round(change, 2),
                        'date': data.index[-1].strftime('%Y-%m-%d')
                    }
                    print(f"✓ Successfully fetched {name}")
            except Exception as e:
                print(f"✗ Error fetching {name}: {str(e)[:100]}")
        
        # Cache the result
        if self.cache and economic_data:
            self.cache.set('economic_indicators', economic_data)
                
        return economic_data
    
    def fetch_all_data(self):
        # """Fetch all data and combine"""
        # print("Fetching market data...")
        # market_data = self.fetch_market_data()
        
        print("\nFetching economic indicators...")
        economic_data = self.fetch_economic_indicators()
        
        return {
            'timestamp': datetime.now().isoformat(),
            # 'market': market_data,
            'economic': economic_data
        }

if __name__ == '__main__':
    fetcher = EconomicDataFetcher(use_cache=True, cache_duration_hours=24)
    data = fetcher.fetch_all_data()
    
    # Print to see what we got
    import json
    print("\n" + "="*50)
    print("FINAL DATA:")
    print("="*50)
    print(json.dumps(data, indent=2))