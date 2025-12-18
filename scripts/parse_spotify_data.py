"""
Parse Spotify streaming history JSON files, deduplicate, and create a queryable database.
"""
import json
import pandas as pd
import sys
from pathlib import Path
from typing import List, Set, Optional
# Add scripts directory to path to import spotify_data_model
sys.path.insert(0, str(Path(__file__).parent))
from spotify_data_model import SpotifyStreamingRecord


def normalize_text(text: Optional[str]) -> Optional[str]:
    """Normalize text by converting various apostrophe/quotation characters to standard apostrophe.
    
    Args:
        text: The text to normalize, can be None
        
    Returns:
        Normalized text with standard apostrophes/quotes, or None if input was None
    """
    if text is None or pd.isna(text):
        return text
    
    text = str(text)
    # Replace various apostrophe/quotation marks with standard characters
    replacements = {
        '\u2019': "'",  # Right single quotation mark (')
        '\u2018': "'",  # Left single quotation mark (')
        '\u201C': '"',  # Left double quotation mark (")
        '\u201D': '"',  # Right double quotation mark (")
        '\u201E': '"',  # Double low-9 quotation mark („)
        '\u201F': '"',  # Double high-reversed-9 quotation mark (‟)
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def load_json_file(file_path: Path) -> List[dict]:
    """Load and parse a JSON file."""
    print(f"Loading {file_path.name}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"  Loaded {len(data)} records")
    return data


def parse_records(json_data: List[dict]) -> List[SpotifyStreamingRecord]:
    """Parse JSON data into SpotifyStreamingRecord objects."""
    records = []
    for item in json_data:
        try:
            record = SpotifyStreamingRecord.from_dict(item)
            records.append(record)
        except Exception as e:
            print(f"  Warning: Failed to parse record: {e}")
            continue
    return records


def deduplicate_records(records: List[SpotifyStreamingRecord]) -> List[SpotifyStreamingRecord]:
    """Remove duplicate records based on unique key."""
    seen_keys: Set[tuple] = set()
    unique_records = []
    duplicates_count = 0
    
    for record in records:
        key = record.get_unique_key()
        if key not in seen_keys:
            seen_keys.add(key)
            unique_records.append(record)
        else:
            duplicates_count += 1
    
    print(f"Removed {duplicates_count} duplicate records")
    print(f"Total unique records: {len(unique_records)}")
    return unique_records


def create_dataframe(records: List[SpotifyStreamingRecord]) -> pd.DataFrame:
    """Convert records to pandas DataFrame."""
    data = [record.to_dict() for record in records]
    df = pd.DataFrame(data)
    
    # Convert timestamp to datetime for easier querying
    df['ts'] = pd.to_datetime(df['ts'])
    
    # Normalize text fields to use standard apostrophes/quotes
    text_columns = [
        'master_metadata_track_name',
        'master_metadata_album_artist_name',
        'master_metadata_album_album_name',
        'episode_name',
        'episode_show_name',
        'audiobook_title',
        'audiobook_chapter_title'
    ]
    
    print("Normalizing text fields (apostrophes/quotes)...")
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)
    
    # Sort by timestamp
    df = df.sort_values('ts').reset_index(drop=True)
    
    return df


def main():
    """Main function to parse all JSON files and create database."""
    # Define file paths
    base_path = Path(__file__).parent.parent
    data_path = base_path / "data"
    json_files = [
        data_path / "Streaming_History_Audio_2023-2025_0.json",
        data_path / "Streaming_History_Audio_2025_1.json",
        data_path / "Streaming_History_Video_2024-2025.json"
    ]
    
    # Check if files exist
    missing_files = [f for f in json_files if not f.exists()]
    if missing_files:
        print(f"Warning: Missing files: {[f.name for f in missing_files]}")
        json_files = [f for f in json_files if f.exists()]
    
    if not json_files:
        print("Error: No JSON files found!")
        return
    
    # Load and parse all files
    all_records = []
    for json_file in json_files:
        json_data = load_json_file(json_file)
        records = parse_records(json_data)
        all_records.extend(records)
    
    print(f"\nTotal records loaded: {len(all_records)}")
    
    # Deduplicate
    print("\nDeduplicating records...")
    unique_records = deduplicate_records(all_records)
    
    # Create DataFrame
    print("\nCreating pandas DataFrame...")
    df = create_dataframe(unique_records)
    
    # Save to parquet for efficient storage and querying
    parquet_path = base_path / "spotify_streaming_history.parquet"
    df.to_parquet(parquet_path, index=False, engine='pyarrow')
    print(f"\nSaved DataFrame to {parquet_path}")
    
    # Also save to CSV for easy inspection
    csv_path = base_path / "spotify_streaming_history.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved DataFrame to {csv_path}")
    
    # Save to SQLite for SQL querying
    sqlite_path = base_path / "spotify_streaming_history.db"
    import sqlite3
    conn = sqlite3.connect(sqlite_path)
    df.to_sql('streaming_history', conn, if_exists='replace', index=False)
    conn.close()
    print(f"Saved DataFrame to SQLite database: {sqlite_path}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)
    print(f"Total unique records: {len(df):,}")
    print(f"Date range: {df['ts'].min()} to {df['ts'].max()}")
    print(f"Total time played: {df['ms_played'].sum() / (1000 * 60 * 60):.2f} hours")
    print(f"Unique tracks: {df['spotify_track_uri'].notna().sum():,}")
    print(f"Unique episodes: {df['spotify_episode_uri'].notna().sum():,}")
    print(f"Unique audiobooks: {df['audiobook_uri'].notna().sum():,}")
    print(f"\nPlatforms: {df['platform'].value_counts().to_dict()}")
    print(f"\nTop 10 most played tracks:")
    top_tracks = df[df['master_metadata_track_name'].notna()].groupby([
        'master_metadata_track_name', 
        'master_metadata_album_artist_name'
    ])['ms_played'].sum().sort_values(ascending=False).head(10)
    for (track, artist), ms in top_tracks.items():
        print(f"  {track} by {artist}: {ms / (1000 * 60):.1f} minutes")
    
    print("\n" + "="*60)
    print("Database ready for querying!")
    print(f"  - Parquet file: {parquet_path}")
    print(f"  - CSV file: {csv_path}")
    print(f"  - SQLite database: {sqlite_path}")
    print("\nExample query:")
    print("  import pandas as pd")
    print("  df = pd.read_parquet('spotify_streaming_history.parquet')")
    print("  # or")
    print("  import sqlite3")
    print("  conn = sqlite3.connect('spotify_streaming_history.db')")
    print("  df = pd.read_sql('SELECT * FROM streaming_history', conn)")


if __name__ == "__main__":
    main()

