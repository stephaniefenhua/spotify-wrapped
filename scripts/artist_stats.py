"""
Query statistics for a specific artist with per-song breakdown.
"""
import pandas as pd
import argparse
from pathlib import Path


def get_artist_stats(artist_name: str, exact_match: bool = False):
    """Get play statistics for a specific artist with per-song breakdown.
    
    Args:
        artist_name: The name of the artist to search for
        exact_match: If True, match artist name exactly (case-insensitive).
                     If False, search for partial matches (default: False)
    
    Returns:
        DataFrame with matching artists and their statistics
    """
    # Load the database (located in parent directory)
    db_path = Path(__file__).parent.parent / 'spotify_streaming_history.parquet'
    df = pd.read_parquet(db_path)
    
    # Filter for tracks only (exclude episodes and audiobooks)
    df_tracks = df[
        (df['master_metadata_track_name'].notna()) &
        (df['spotify_track_uri'].notna()) &
        (df['master_metadata_album_artist_name'].notna())
    ]
    
    if len(df_tracks) == 0:
        print("No track records found in database")
        return pd.DataFrame()
    
    # Search for matching artists
    if exact_match:
        matches = df_tracks[
            df_tracks['master_metadata_album_artist_name'].str.lower() == artist_name.lower()
        ]
    else:
        matches = df_tracks[
            df_tracks['master_metadata_album_artist_name'].str.lower().str.contains(
                artist_name.lower(), na=False, regex=False
            )
        ]
    
    if len(matches) == 0:
        print(f"No artists found matching '{artist_name}'")
        return pd.DataFrame()
    
    # Get unique artists found (in case of partial match)
    unique_artists = matches['master_metadata_album_artist_name'].unique()
    
    if len(unique_artists) > 1:
        print(f"Found {len(unique_artists)} matching artists:")
        for idx, artist in enumerate(unique_artists, 1):
            artist_plays = matches[matches['master_metadata_album_artist_name'] == artist]
            total_time = artist_plays['ms_played'].sum() / (1000 * 60 * 60)
            print(f"  {idx}. {artist} ({total_time:.2f} hours)")
        print()
    
    # Process each matching artist
    all_results = []
    
    for artist in unique_artists:
        artist_tracks = matches[matches['master_metadata_album_artist_name'] == artist]
        
        # Overall statistics for this artist
        total_plays = len(artist_tracks)
        total_ms = artist_tracks['ms_played'].sum()
        total_hours = total_ms / (1000 * 60 * 60)
        total_minutes = total_ms / (1000 * 60)
        
        # Per-song statistics
        song_stats = artist_tracks.groupby('master_metadata_track_name').agg({
            'ms_played': ['sum', 'count']
        }).reset_index()
        song_stats.columns = ['song_name', 'total_ms', 'play_count']
        song_stats['total_minutes'] = song_stats['total_ms'] / (1000 * 60)
        song_stats = song_stats.sort_values('play_count', ascending=False)
        
        unique_songs = len(song_stats)
        
        # Display results
        print("="*80)
        print(f"ARTIST STATISTICS: {artist}")
        print("="*80)
        print(f"\nOVERALL STATISTICS:")
        print(f"  Total Songs Played: {unique_songs}")
        print(f"  Total Plays: {total_plays:,}")
        print(f"  Total Listening Time: {total_hours:.2f} hours ({total_minutes:.1f} minutes)")
        print(f"  Average Time per Play: {total_minutes/total_plays:.2f} minutes")
        
        print(f"\nPER-SONG BREAKDOWN:")
        print(f"{'Rank':<6} {'Song':<40} {'Plays':<8} {'Minutes':<12}")
        print("-"*80)
        
        for idx, row in enumerate(song_stats.itertuples(), 1):
            song = row.song_name
            plays = row.play_count
            minutes = row.total_minutes
            
            # Truncate long song names
            if len(song) > 38:
                song = song[:35] + "..."
            
            print(f"{idx:<6} {song:<40} {plays:<8} {minutes:<12.1f}")
        
        print("="*80)
        
        # Store results
        all_results.append({
            'artist': artist,
            'total_plays': total_plays,
            'total_hours': total_hours,
            'total_minutes': total_minutes,
            'unique_songs': unique_songs,
            'song_breakdown': song_stats
        })
    
    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get statistics for a specific artist with per-song breakdown')
    parser.add_argument('artist_name', type=str, help='Name of the artist to search for')
    parser.add_argument('-e', '--exact', action='store_true',
                       help='Match artist name exactly (case-insensitive)')
    
    args = parser.parse_args()
    get_artist_stats(args.artist_name, args.exact)

