import pandas as pd
from openbb import obb

class SECEdgarEnricher:
    """
    Enriches asset data with their latest SEC filings from EDGAR.
    """
    def enrich_with_sec_filings(self, assets_df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds the latest SEC filing date and type for each asset.

        Args:
            assets_df (pd.DataFrame): DataFrame with a 'symbol' column.

        Returns:
            pd.DataFrame: The original DataFrame with added columns
                          'last_filing_date' and 'last_filing_type'.
        """
        print("\nEnriching assets with latest SEC filing data...")
        filings_data = []
        
        # Make sure there are symbols to process
        if 'symbol' not in assets_df.columns or assets_df.empty:
            print("Warning: Input DataFrame is empty or missing 'symbol' column.")
            return assets_df

        for symbol in assets_df['symbol']:
            try:
                # Fetch the single most recent filing for the symbol
                filings = obb.company.filings(symbol=symbol, limit=1).to_df()
                if not filings.empty:
                    latest_filing = filings.iloc[0]
                    filings_data.append({
                        'symbol': symbol,
                        'last_filing_date': latest_filing['filing_date'],
                        'last_filing_type': latest_filing['form_type']
                    })
                    print(f"  > Fetched filing for {symbol}: {latest_filing['form_type']}")
                else:
                    # Handle cases where there are no filings
                    filings_data.append({'symbol': symbol, 'last_filing_date': None, 'last_filing_type': None})
            except Exception:
                # Handle cases where the symbol is not found or an API error occurs
                print(f"  > Could not fetch filings for {symbol}.")
                filings_data.append({'symbol': symbol, 'last_filing_date': None, 'last_filing_type': None})

        # Merge the new filing data back into the original DataFrame
        if filings_data:
            filings_df = pd.DataFrame(filings_data)
            enriched_df = pd.merge(assets_df, filings_df, on='symbol', how='left')
            return enriched_df
        
        return assets_df