# Spotify Streaming History Analysis
<img width="1314" height="814" alt="image" src="https://github.com/user-attachments/assets/79e67154-5075-461b-ae5d-057eb85faf22" />
A Python toolkit for analyzing your Spotify streaming history data. Parse your exported JSON files, create queryable databases, and generate insights about your listening habits.

## Features

- **Parse and deduplicate** Spotify streaming history JSON files
- **Create multiple database formats** (Parquet, CSV, SQLite) for flexible querying
- **Interactive dashboard** with visualizations and search
- **Query scripts** for common analyses:
  - Top artists by year or all-time
  - Top songs by year or all-time
  - Top podcasts by year or all-time
  - Individual song statistics
  - Artist statistics with per-song breakdown

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Setup

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Export your Spotify data:**
   - Go to [Spotify's Privacy Settings](https://www.spotify.com/account/privacy/)
   - Request your extended streaming history data
   - Download the ZIP file when ready (may take a few days)
   - Extract the JSON files from the ZIP

4. **Organize your JSON files:**
   - Create a `data/` directory in the project root
   - Place your Spotify JSON files in the `data/` directory
   - Files should be named like:
     - `Streaming_History_Audio_*.json`
     - `Streaming_History_Video_*.json`

## Project Structure

```
spotify-analysis/
├── data/                          # Place your Spotify JSON files here
│   ├── Streaming_History_Audio_*.json
│   └── Streaming_History_Video_*.json
├── scripts/
│   ├── parse_spotify_data.py     # Main parser script
│   ├── spotify_data_model.py     # Data model definitions
│   ├── top_artists_script.py     # Top artists by year or all-time
│   ├── top_songs.py              # Top songs by year or all-time
│   ├── top_podcasts.py           # Top podcasts by year or all-time
│   ├── song_stats.py             # Individual song statistics
│   ├── artist_stats.py           # Artist statistics with per-song breakdown
│   └── query_examples.py         # Example queries
├── dashboard/
│   ├── app.py                    # Plotly Dash dashboard
│   └── assets/
│       └── styles.css            # Custom dashboard styling
├── spotify_streaming_history.parquet  # Generated database (Parquet format)
├── spotify_streaming_history.csv      # Generated database (CSV format)
├── spotify_streaming_history.db       # Generated database (SQLite format)
├── requirements.txt
└── README.md
```

## Usage

### Step 1: Parse Your Data

First, you need to parse your JSON files and create the database:

```bash
python3 scripts/parse_spotify_data.py
```

This script will:
- Load all JSON files from the `data/` directory
- Parse and deduplicate records
- Normalize text fields (apostrophes/quotes)
- Create three database files in the root directory:
  - `spotify_streaming_history.parquet` (recommended for pandas)
  - `spotify_streaming_history.csv` (human-readable)
  - `spotify_streaming_history.db` (SQLite database)

**Note:** The script automatically looks for JSON files in the `data/` directory. If your files have different names or locations, you may need to update the file paths in `parse_spotify_data.py`.

### Step 2: Use the Interactive Dashboard

The easiest way to explore your data is with the interactive dashboard:

```bash
python3 dashboard/app.py
```

Then open your browser to **http://localhost:8050**

#### Dashboard Features

| Tab | Description |
|-----|-------------|
| 🎤 **top artists** | View your most-listened artists with customizable year filter and count |
| 🎵 **top songs** | See your top songs, sorted by plays or minutes |
| 🔍 **song search** | Search for any song and see your play count and total time |
| 👤 **artist stats** | Deep dive into any artist with per-song breakdown chart |
| 🎙️ **podcasts** | View your top podcasts by listening time |
| 📈 **trends** | See your listening patterns over time |

#### Dashboard Controls

- **Year dropdown**: Filter data by year or view all-time stats
- **Top N input**: Enter any number (1-100) to customize how many results to show
- **Sort options**: Toggle between sorting by plays or minutes (for songs)
- **Search**: Type an artist or song name and click search

#### Stopping the Dashboard

Press `Ctrl+C` in the terminal to stop the dashboard server.

---

### Step 3: Query Your Data (Command Line)

Alternatively, you can use the command-line query scripts:

#### Top Artists by Year or All-Time

Get your top N artists for a specific year or all-time (defaults to all-time if no year is specified):

```bash
python3 scripts/top_artists_script.py [-y YEAR] [-n TOP_N]
```

**Examples:**
```bash
# Top 10 artists all-time (default)
python3 scripts/top_artists_script.py

# Top 5 artists all-time
python3 scripts/top_artists_script.py -n 5

# Top 10 artists from 2025
python3 scripts/top_artists_script.py -y 2025

# Top 5 artists from 2024
python3 scripts/top_artists_script.py -y 2024 -n 5

# Top 20 artists from 2023
python3 scripts/top_artists_script.py -y 2023 -n 20
```

#### Top Songs by Year or All-Time

Get your top N songs (by number of plays) for a specific year or all-time (defaults to all-time if no year is specified):

```bash
python3 scripts/top_songs.py [-y YEAR] [-n TOP_N]
```

**Examples:**
```bash
# Top 10 songs all-time (default)
python3 scripts/top_songs.py

# Top 5 songs all-time
python3 scripts/top_songs.py -n 5

# Top 10 songs from 2025
python3 scripts/top_songs.py -y 2025

# Top 5 songs from 2024
python3 scripts/top_songs.py -y 2024 -n 5
```

#### Top Podcasts by Year or All-Time

Get your top N podcasts (by listening time) for a specific year or all-time (defaults to all-time if no year is specified):

```bash
python3 scripts/top_podcasts.py [-y YEAR] [-n TOP_N]
```

**Examples:**
```bash
# Top 10 podcasts all-time (default)
python3 scripts/top_podcasts.py

# Top 5 podcasts all-time
python3 scripts/top_podcasts.py -n 5

# Top 10 podcasts from 2025
python3 scripts/top_podcasts.py -y 2025

# Top 5 podcasts from 2024
python3 scripts/top_podcasts.py -y 2024 -n 5
```

#### Song Statistics

Get detailed statistics for a specific song:

```bash
python3 scripts/song_stats.py "<SONG_NAME>" [-e]
```

**Options:**
- `-e, --exact`: Match song name exactly (case-insensitive)
- Without `-e`: Partial match search

**Examples:**
```bash
# Search for songs containing "Bloom"
python3 scripts/song_stats.py "Bloom"

# Exact match for "Stick Season"
python3 scripts/song_stats.py "Stick Season" -e

# Search for songs with apostrophes
python3 scripts/song_stats.py "That's So True"
```

#### Artist Statistics

Get comprehensive statistics for an artist, including per-song breakdown:

```bash
python3 scripts/artist_stats.py "<ARTIST_NAME>" [-e]
```

**Options:**
- `-e, --exact`: Match artist name exactly (case-insensitive)
- Without `-e`: Partial match search

**Examples:**
```bash
# Search for artists containing "Gracie"
python3 scripts/artist_stats.py "Gracie Abrams"

# Exact match for "Dabin"
python3 scripts/artist_stats.py "Dabin" -e
```

**Output includes:**
- Overall statistics (total songs, plays, listening time)
- Per-song breakdown (ranked by number of plays)

### Step 4: Custom Queries

You can also write your own queries using pandas or SQL:

#### Using Pandas (Parquet file)

```python
import pandas as pd

# Load the database
df = pd.read_parquet('spotify_streaming_history.parquet')

# Example: Find all songs from 2024
df_2024 = df[df['ts'].dt.year == 2024]

# Example: Top artists by total play time
top_artists = df.groupby('master_metadata_album_artist_name')['ms_played'].sum().sort_values(ascending=False).head(10)
```

#### Using SQLite

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('spotify_streaming_history.db')

# Run SQL query
query = """
SELECT 
    master_metadata_album_artist_name as artist,
    COUNT(*) as play_count,
    SUM(ms_played) / (1000.0 * 60 * 60) as total_hours
FROM streaming_history
WHERE master_metadata_album_artist_name IS NOT NULL
GROUP BY master_metadata_album_artist_name
ORDER BY total_hours DESC
LIMIT 10
"""

df = pd.read_sql(query, conn)
conn.close()
```

See `scripts/query_examples.py` for more examples.

## Data Model

The database contains the following key fields:

- `ts`: Timestamp of the play
- `platform`: Platform used (ios, osx, etc.)
- `ms_played`: Milliseconds played
- `master_metadata_track_name`: Song name
- `master_metadata_album_artist_name`: Artist name
- `master_metadata_album_album_name`: Album name
- `spotify_track_uri`: Spotify track URI
- `skipped`: Whether the track was skipped
- `shuffle`: Whether shuffle was enabled
- `offline`: Whether played offline
- And more...

## Troubleshooting

### "No JSON files found!"
- Make sure your JSON files are in the `data/` directory
- Check that file names match the expected pattern
- Verify the file paths in `parse_spotify_data.py` if using custom names

### "No module named 'pandas'" or "No module named 'dash'"
- Install dependencies: `pip install -r requirements.txt`

### Dashboard won't start / "Address already in use"
- Another process may be using port 8050
- Kill existing processes: `lsof -ti:8050 | xargs kill -9`
- Or run on a different port by editing `app.py`

### "No songs/artists found matching..."
- Try using partial match (remove `-e` flag)
- Check for typos in the search term
- Verify the data was parsed correctly

### Scripts can't find the database
- Make sure you've run `parse_spotify_data.py` first
- Verify the database files exist in the root directory
- Check that you're running scripts from the project root

## Notes

- **Deduplication**: The parser automatically removes duplicate records based on timestamp, track URI, and play duration
- **Text Normalization**: Apostrophes and quotation marks are normalized to standard characters during parsing
- **File Formats**: 
  - Use `.parquet` for pandas operations (fastest)
  - Use `.csv` for manual inspection
  - Use `.db` for SQL queries
