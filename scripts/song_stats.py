"""
Query statistics for a specific song.
"""
import pandas as pd
import argparse
from pathlib import Path


def get_song_stats(song_name: str, exact_match: bool = False):
    """Get play statistics for a specific song.
    
    Args:
        song_name: The name of the song to search for
        exact_match: If True, match song name exactly (case-insensitive).
                     If False, search for partial matches (default: False)
    
    Returns:
        DataFrame with matching songs and their statistics
    """
    # Load the database (located in parent directory)
    db_path = Path(__file__).parent.parent / 'spotify_streaming_history.parquet'
    df = pd.read_parquet(db_path)
    
    # Filter for tracks only (exclude episodes and audiobooks)
    df_tracks = df[
        (df['master_metadata_track_name'].notna()) &
        (df['spotify_track_uri'].notna())
    ].copy()
    
    if len(df_tracks) == 0:
        print("No track records found in database")
        return pd.DataFrame()
    
    if exact_match:
        matches = df_tracks[
            df_tracks['master_metadata_track_name'].str.lower() == song_name.lower()
        ]
    else:
        matches = df_tracks[
            df_tracks['master_metadata_track_name'].str.lower().str.contains(
                song_name.lower(), na=False, regex=False
            )
        ]
    
    if len(matches) == 0:
        print(f"No songs found matching '{song_name}'")
        return pd.DataFrame()
    
    # Group by song name and artist to handle same song by different artists
    song_stats = matches.groupby([
        'master_metadata_track_name',
        'master_metadata_album_artist_name'
    ]).agg({
        'ms_played': ['sum', 'count']
    }).reset_index()
    
    # Flatten column names
    song_stats.columns = ['song_name', 'artist', 'total_ms', 'play_count']
    
    # Convert milliseconds to hours, minutes, and seconds
    song_stats['total_hours'] = song_stats['total_ms'] / (1000 * 60 * 60)
    song_stats['total_minutes'] = song_stats['total_ms'] / (1000 * 60)
    song_stats['total_seconds'] = song_stats['total_ms'] / 1000
    
    # Sort by play count (descending)
    song_stats = song_stats.sort_values('play_count', ascending=False)
    
    # Display results
    print("="*80)
    print(f"SONG STATISTICS FOR: '{song_name}'")
    print("="*80)
    
    if len(song_stats) > 1:
        print(f"Found {len(song_stats)} matching songs:\n")
    
    for idx, row in enumerate(song_stats.itertuples(), 1):
        song = row.song_name
        artist = row.artist or "Unknown"
        plays = row.play_count
        hours = row.total_hours
        minutes = row.total_minutes
        seconds = row.total_seconds
        
        print(f"\n{idx}. {song}")
        print(f"   Artist: {artist}")
        print(f"   Times Played: {plays}")
        print(f"   Total Time: {hours:.2f} hours ({minutes:.1f} minutes / {seconds:.0f} seconds)")
        print(f"   Average per Play: {minutes/plays:.2f} minutes")
    
    print("\n" + "="*80)
    
    return song_stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get statistics for a specific song')
    parser.add_argument('song_name', type=str, help='Name of the song to search for')
    parser.add_argument('-e', '--exact', action='store_true',
                       help='Match song name exactly (case-insensitive)')
    
    args = parser.parse_args()
    get_song_stats(args.song_name, args.exact)

