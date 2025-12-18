"""
Query top artists by year.
"""
import pandas as pd
import argparse
from pathlib import Path


def get_top_artists(year: int, top_n: int = 10):
    """Get top N artists by total play time for a given year.
    
    Args:
        year: The year to filter records by
        top_n: Number of top artists to return (default: 10)
    
    Returns:
        DataFrame with top N artists
    """
    # Load the database (located in parent directory)
    db_path = Path(__file__).parent.parent / 'spotify_streaming_history.parquet'
    df = pd.read_parquet(db_path)
    
    # Filter for specified year
    df_year = df[df['ts'].dt.year == year]
    
    if len(df_year) == 0:
        print(f"No records found for year {year}")
        return pd.DataFrame()
    
    # Filter out records without artist names (episodes, audiobooks, etc.)
    df_year_tracks = df_year[df_year['master_metadata_album_artist_name'].notna()]
    
    if len(df_year_tracks) == 0:
        print(f"No track records found for year {year}")
        return pd.DataFrame()
    
    # Group by artist and sum play time
    top_artists = df_year_tracks.groupby('master_metadata_album_artist_name')['ms_played'].agg([
        ('total_ms', 'sum'),
        ('play_count', 'count')
    ]).reset_index()
    
    # Convert milliseconds to hours and minutes
    top_artists['total_hours'] = top_artists['total_ms'] / (1000 * 60 * 60)
    top_artists['total_minutes'] = top_artists['total_ms'] / (1000 * 60)
    
    # Sort by total play time and get top N
    top_n_artists = top_artists.sort_values('total_ms', ascending=False).head(top_n)
    
    # Display results
    print("="*70)
    print(f"TOP {len(top_n_artists)} ARTISTS FROM {year}")
    print("="*70)
    print(f"{'Rank':<6} {'Artist':<40} {'Hours':<10} {'Minutes':<10} {'Plays':<8}")
    print("-"*70)
    
    for idx, row in enumerate(top_n_artists.itertuples(), 1):
        artist = row.master_metadata_album_artist_name
        hours = row.total_hours
        minutes = row.total_minutes
        plays = row.play_count
        
        # Truncate long artist names
        if len(artist) > 38:
            artist = artist[:35] + "..."
        
        print(f"{idx:<6} {artist:<40} {hours:<10.2f} {minutes:<10.1f} {plays:<8}")
    
    print("="*70)
    
    return top_n_artists


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get top artists for a given year')
    parser.add_argument('year', type=int, help='Year to filter records (e.g., 2025)')
    parser.add_argument('-n', '--top-n', type=int, default=10, 
                       help='Number of top artists to return (default: 10)')
    
    args = parser.parse_args()
    get_top_artists(args.year, args.top_n)

