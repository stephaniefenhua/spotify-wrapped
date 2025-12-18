"""
Query top songs by year or all-time.
"""
import pandas as pd
import argparse
from pathlib import Path


def get_top_songs(year: int = None, top_n: int = 10):
    """Get top N songs by number of plays for a given year or all-time.
    
    Args:
        year: The year to filter records by (None for all-time)
        top_n: Number of top songs to return (default: 10)
    
    Returns:
        DataFrame with top N songs
    """
    # Load the database (located in parent directory)
    db_path = Path(__file__).parent.parent / 'spotify_streaming_history.parquet'
    df = pd.read_parquet(db_path)
    
    # Filter for specified year if provided
    if year is not None:
        df_filtered = df[df['ts'].dt.year == year]
        
        if len(df_filtered) == 0:
            print(f"No records found for year {year}")
            return pd.DataFrame()
    else:
        df_filtered = df
    
    # Filter for tracks only (exclude episodes and audiobooks)
    df_tracks = df_filtered[
        (df_filtered['master_metadata_track_name'].notna()) &
        (df_filtered['spotify_track_uri'].notna())
    ]
    
    if len(df_tracks) == 0:
        time_period = f"year {year}" if year is not None else "all-time"
        print(f"No track records found for {time_period}")
        return pd.DataFrame()
    
    # Group by track name and artist, then sum play time
    top_songs = df_tracks.groupby([
        'master_metadata_track_name',
        'master_metadata_album_artist_name'
    ])['ms_played'].agg([
        ('total_ms', 'sum'),
        ('play_count', 'count')
    ]).reset_index()
    
    # Convert milliseconds to hours and minutes
    top_songs['total_hours'] = top_songs['total_ms'] / (1000 * 60 * 60)
    top_songs['total_minutes'] = top_songs['total_ms'] / (1000 * 60)
    
    # Sort by number of plays and get top N
    top_n_songs = top_songs.sort_values('play_count', ascending=False).head(top_n)
    
    # Display results
    time_period = f"{year}" if year is not None else "ALL-TIME"
    print("="*80)
    print(f"TOP {len(top_n_songs)} SONGS ({time_period}) - by number of plays")
    print("="*80)
    print(f"{'Rank':<6} {'Song':<35} {'Artist':<30} {'Plays':<8} {'Minutes':<10}")
    print("-"*80)
    
    for idx, row in enumerate(top_n_songs.itertuples(), 1):
        song = row.master_metadata_track_name
        artist = row.master_metadata_album_artist_name or "Unknown"
        minutes = row.total_minutes
        plays = row.play_count
        
        # Truncate long song/artist names
        if len(song) > 33:
            song = song[:30] + "..."
        if len(artist) > 28:
            artist = artist[:25] + "..."
        
        print(f"{idx:<6} {song:<35} {artist:<30} {plays:<8} {minutes:<10.1f}")
    
    print("="*80)
    
    return top_n_songs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get top songs by year or all-time')
    parser.add_argument('-y', '--year', type=int, default=None,
                       help='Year to filter records (default: all-time)')
    parser.add_argument('-n', '--top-n', type=int, default=10, 
                       help='Number of top songs to return (default: 10)')
    
    args = parser.parse_args()
    get_top_songs(args.year, args.top_n)

