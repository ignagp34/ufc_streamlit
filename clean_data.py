import pandas as pd
import numpy as np

def clean_data():
    print("Loading data...")
    try:
        df = pd.read_csv('ufc-master.csv', sep=';')
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"Original shape: {df.shape}")

    # Select relevant columns
    cols_to_keep = [
        'Date', 'Winner', 'WeightClass', 'Gender', 'Finish', 'RedFighter', 'BlueFighter',
        'RedHeightCms', 'BlueHeightCms', 'RedReachCms', 'BlueReachCms',
        'RedAge', 'BlueAge', 'FinishRound', 'TotalFightTimeSecs',
        'RedAvgSigStrLanded', 'BlueAvgSigStrLanded',
        'RedAvgTDLanded', 'BlueAvgTDLanded',
        'RedOdds', 'BlueOdds'
    ]

    # Filter columns that exist
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    df = df[existing_cols]

    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year

    # Drop rows without a clear winner (Draws or missing)
    df = df[df['Winner'].isin(['Red', 'Blue'])]

    # Create Winner attributes
    # We want to enable analysis of the WINNER's stats
    
    def get_winner_stat(row, red_col, blue_col):
        if row['Winner'] == 'Red':
            return row[red_col]
        else:
            return row[blue_col]

    df['WinnerHeight'] = df.apply(lambda x: get_winner_stat(x, 'RedHeightCms', 'BlueHeightCms'), axis=1)
    df['WinnerReach'] = df.apply(lambda x: get_winner_stat(x, 'RedReachCms', 'BlueReachCms'), axis=1)
    df['WinnerAvgStrikes'] = df.apply(lambda x: get_winner_stat(x, 'RedAvgSigStrLanded', 'BlueAvgSigStrLanded'), axis=1)
    df['WinnerAvgTD'] = df.apply(lambda x: get_winner_stat(x, 'RedAvgTDLanded', 'BlueAvgTDLanded'), axis=1)
    df['WinnerAge'] = df.apply(lambda x: get_winner_stat(x, 'RedAge', 'BlueAge'), axis=1)
    
    # Calculate Age Difference (Winner - Loser) to see if younger/older matters
    def get_age_diff(row):
        if row['Winner'] == 'Red':
            return row['RedAge'] - row['BlueAge']
        else:
            return row['BlueAge'] - row['RedAge']
            
    df['WinnerAgeDiff'] = df.apply(get_age_diff, axis=1)
    
    # Market Efficiency
    # Favorite is the one with lower odds. 
    # Valid odds are usually non-zero.
    
    def get_betting_result(row):
        if pd.isna(row['RedOdds']) or pd.isna(row['BlueOdds']):
            return 'Unknown'
            
        r_odds = row['RedOdds']
        b_odds = row['BlueOdds']
        
        # Determine Favorite
        if r_odds < b_odds:
            favorite = 'Red'
        elif b_odds < r_odds:
            favorite = 'Blue'
        else:
            favorite = 'Even'
            
        if favorite == 'Even':
            return 'PickEm'
        
        if row['Winner'] == favorite:
            return 'Favorite'
        else:
            return 'Underdog'

    df['BettingResult'] = df.apply(get_betting_result, axis=1)

    # Clean numeric columns
    numeric_cols = ['WinnerHeight', 'WinnerReach', 'WinnerAvgStrikes', 'WinnerAvgTD', 'WinnerAge', 'TotalFightTimeSecs', 'FinishRound']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Erase catch weights
    df = df.drop(df[df['WeightClass'] == 'Catch Weight'].index)

    # Fix finish round
    df['FinishRound'] = df['FinishRound'].apply(lambda x: int(round(x/10)) if pd.notna(x) else x)

    # Fix height and reach metrics (in cms)
    def fix_metric(value):
        # If greater than 10000 (ej. 17272), it has 2 digits -> divide by 100
        if value >= 10000:
            val = value / 100.0
        # If lower (ej. 1651), 1 digit -> divide by 10
        elif value >= 1000:
            val = value / 10.0
        else:
            val = value
        return int(round(val))

    # Apply height correction to relevant columns
    metric_columns = ['RedHeightCms', 'BlueHeightCms', 'WinnerHeight','RedHeightCms', 'BlueHeightCms',
                       'WinnerHeight','RedReachCms', 'BlueReachCms', 'WinnerReach']
    for col in metric_columns:
        df[col] = df[col].apply(fix_metric)

    # Fix TotalFightTimeSecs: divide by 10
    df['TotalFightTimeSecs'] = df['TotalFightTimeSecs'].apply(lambda x: int(round(x / 10.0)) if pd.notna(x) else x)

    def fix_metric2(val, metric_type):
        if pd.isna(val) or val == 0:
            return val
        
        # Logic range: 0 a ~15 strikes per minute
        if metric_type == 'strikes':
            # 2 digits (e.g 67, 25),  x10 -> 6.7, 2.5
            if val < 100: 
                return val / 10
            # 3 digits (e.g. 717),  x100 -> 7.17
            elif val < 1000:
                return val / 100
            else:
                while val > 20:
                    val = val / 10
                return val

        elif metric_type == 'takedowns':
            if val < 100:
                return val / 100
            elif val < 1000:
                return val / 100
            else:
                while val > 15:
                    val = val / 10
                return val

    strike_cols = ['RedAvgSigStrLanded', 'BlueAvgSigStrLanded', 'WinnerAvgStrikes']
    td_cols = ['RedAvgTDLanded', 'BlueAvgTDLanded', 'WinnerAvgTD']

    for col in strike_cols:
        df[col] = df[col].apply(lambda x: fix_metric2(x, 'strikes'))

    for col in td_cols:
        df[col] = df[col].apply(lambda x: fix_metric2(x, 'takedowns'))

    # Drop rows with critical missing info for the main plots
    df_clean = df.dropna(subset=['WinnerHeight', 'WinnerReach', 'BettingResult', 'WinnerAge'])

    print(f"Cleaned shape: {df_clean.shape}")
    
    output_file = 'ufc_cleaned.csv'
    df_clean.to_csv(output_file, index=False)
    print(f"Saved cleaned data to {output_file}")

if __name__ == "__main__":
    clean_data()
