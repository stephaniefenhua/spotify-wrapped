"""
Example queries for the Spotify streaming history database.
"""
import pandas as pd
import sqlite3
from pathlib import Path


def get_db_path(filename: str) -> Path:
    """Get path to database file in parent directory."""
    return Path(__file__).parent.parent / filename


def load_parquet() -> pd.DataFrame:
    """Load data from Parquet file (fastest for pandas operations)."""
    return pd.read_parquet(get_db_path('spotify_streaming_history.parquet'))


def load_sqlite() -> sqlite3.Connection:
    """Load SQLite connection for SQL queries."""
    return sqlite3.connect(get_db_path('spotify_streaming_history.db'))


def example_queries():
    """Run example queries on the database."""
    print("="*60)
    print("EXAMPLE QUERIES")
    print("="*60)
    
    # Load data
    print("\n1. Loading data from Parquet...")
    df = load_parquet()
    print(f"   Loaded {len(df):,} records")
    
    # Example 1: Filter by date range
    print("\n2. Records from 2024:")
    df_2024 = df[df['ts'].dt.year == 2024]
    print(f"   {len(df_2024):,} records")
    
    # Example 2: Find most played artists
    print("\n3. Top 10 artists by total play time:")
    top_artists = df[df['master_metadata_album_artist_name'].notna()].groupby(
        'master_metadata_album_artist_name'
    )['ms_played'].sum().sort_values(ascending=False).head(10)
    for artist, ms in top_artists.items():
        print(f"   {artist}: {ms / (1000 * 60 * 60):.2f} hours")
    
    # Example 3: Find tracks played on specific platform
    print("\n4. Records from iOS platform:")
    ios_records = df[df['platform'] == 'ios']
    print(f"   {len(ios_records):,} records")
    
    # Example 4: Find skipped vs completed tracks
    print("\n5. Skipped vs completed tracks:")
    skipped = df[df['skipped'] == True]
    completed = df[df['skipped'] == False]
    print(f"   Skipped: {len(skipped):,} ({len(skipped)/len(df)*100:.1f}%)")
    print(f"   Completed: {len(completed):,} ({len(completed)/len(df)*100:.1f}%)")
    
    # Example 5: SQL query example
    print("\n6. Using SQLite for SQL queries:")
    conn = load_sqlite()
    sql_query = """
    SELECT 
        master_metadata_album_artist_name as artist,
        COUNT(*) as play_count,
        SUM(ms_played) / (1000.0 * 60 * 60) as total_hours
    FROM streaming_history
    WHERE master_metadata_album_artist_name IS NOT NULL
    GROUP BY master_metadata_album_artist_name
    ORDER BY total_hours DESC
    LIMIT 5
    """
    sql_result = pd.read_sql(sql_query, conn)
    print(sql_result.to_string(index=False))
    conn.close()
    
    # Example 6: Filter by specific track
    print("\n7. Find all plays of a specific track:")
    if len(df[df['master_metadata_track_name'].notna()]) > 0:
        sample_track = df[df['master_metadata_track_name'].notna()]['master_metadata_track_name'].iloc[0]
        track_plays = df[df['master_metadata_track_name'] == sample_track]
        print(f"   Track: {sample_track}")
        print(f"   Played {len(track_plays)} times")
        print(f"   Total time: {track_plays['ms_played'].sum() / (1000 * 60):.1f} minutes")
    
    print("\n" + "="*60)
    print("You can now write your own queries!")
    print("="*60)


if __name__ == "__main__":
    example_queries()

