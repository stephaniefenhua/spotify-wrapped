"""
Query top podcasts by year (or all-time).
"""
import pandas as pd
import argparse
from pathlib import Path


def get_top_podcasts(year: int = None, top_n: int = 10):
    """Get top N podcasts by total listening time for a given year or all-time.
    
    Args:
        year: The year to filter records by (None for all-time)
        top_n: Number of top podcasts to return (default: 10)
    
    Returns:
        DataFrame with top N podcasts
    """
    # Load the database (located in parent directory)
    db_path = Path(__file__).parent.parent / 'spotify_streaming_history.parquet'
    df = pd.read_parquet(db_path)
    
    # Filter for episodes only (podcasts)
    df_episodes = df[
        (df['episode_name'].notna()) &
        (df['spotify_episode_uri'].notna())
    ]
    
    if len(df_episodes) == 0:
        print("No podcast/episode records found in database")
        return pd.DataFrame()
    
    # Filter by year if specified
    if year is not None:
        df_episodes = df_episodes[df_episodes['ts'].dt.year == year]
        
        if len(df_episodes) == 0:
            print(f"No podcast records found for year {year}")
            return pd.DataFrame()
    
    # Group by show name and sum listening time
    podcast_stats = df_episodes.groupby('episode_show_name').agg({
        'ms_played': ['sum', 'count']
    }).reset_index()
    
    # Flatten column names
    podcast_stats.columns = ['show_name', 'total_ms', 'episode_count']
    
    # Convert milliseconds to hours and minutes
    podcast_stats['total_hours'] = podcast_stats['total_ms'] / (1000 * 60 * 60)
    podcast_stats['total_minutes'] = podcast_stats['total_ms'] / (1000 * 60)
    
    # Sort by total listening time and get top N
    top_podcasts = podcast_stats.sort_values('total_ms', ascending=False).head(top_n)
    
    # Display results
    time_period = f"{year}" if year is not None else "ALL-TIME"
    print("="*80)
    print(f"TOP {len(top_podcasts)} PODCASTS ({time_period})")
    print("="*80)
    print(f"{'Rank':<6} {'Podcast':<50} {'Hours':<10} {'Minutes':<10} {'Episodes':<10}")
    print("-"*80)
    
    for idx, row in enumerate(top_podcasts.itertuples(), 1):
        show_name = row.show_name or "Unknown"
        hours = row.total_hours
        minutes = row.total_minutes
        episodes = row.episode_count
        
        # Truncate long podcast names
        if len(show_name) > 48:
            show_name = show_name[:45] + "..."
        
        print(f"{idx:<6} {show_name:<50} {hours:<10.2f} {minutes:<10.1f} {episodes:<10}")
    
    print("="*80)
    
    return top_podcasts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get top podcasts by listening time')
    parser.add_argument('-n', '--top-n', type=int, default=10, 
                       help='Number of top podcasts to return (default: 10)')
    parser.add_argument('-y', '--year', type=int, default=None,
                       help='Year to filter records (default: all-time)')
    
    args = parser.parse_args()
    get_top_podcasts(args.year, args.top_n)

