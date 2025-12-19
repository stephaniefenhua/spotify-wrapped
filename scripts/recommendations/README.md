# Recommendation System

A personalized music recommendation engine that analyzes your Spotify listening history and generates recommendations based on your favorite artists.

## Features

- **Analyzes your listening patterns** from your streaming history
- **Gets top tracks from your favorite artists** - discovers songs you might have missed
- **Uses Spotify API** (only non-deprecated endpoints)
- **Excludes already-played tracks** (optional)

## Important: Spotify API Limitations

**For apps created after November 27, 2024**: Spotify has deprecated several API endpoints:

| Endpoint | Status | Impact |
|----------|--------|--------|
| `audio-features` | ❌ Deprecated | Cannot analyze audio characteristics |
| `recommendations` | ❌ Deprecated | Cannot use Spotify's recommendation engine |
| `related-artists` | ❌ Deprecated | Cannot discover similar artists |
| `track` | ✅ Works | Get track info |
| `artists` | ✅ Works | Get artist info |
| `artist_top_tracks` | ✅ Works | Get artist's top tracks |
| `search` | ✅ Works | Search for tracks |

**Our workaround**: Instead of using deprecated endpoints, this system:
1. Identifies artists from your top-played tracks
2. Gets the top tracks from those artists
3. Recommends tracks you might not have heard from artists you already love

## Setup

### 1. Get Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in app details (name, description, etc.)
5. Copy your **Client ID** and **Client Secret**

### 2. Set Environment Variables

```bash
export SPOTIPY_CLIENT_ID='your_client_id_here'
export SPOTIPY_CLIENT_SECRET='your_client_secret_here'
```

Or add to your `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export SPOTIPY_CLIENT_ID="your_client_id_here"' >> ~/.zshrc
echo 'export SPOTIPY_CLIENT_SECRET="your_client_secret_here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Credentials

```bash
python3 scripts/recommendations/verify_credentials.py
```

## Usage

### Basic Usage

Generate 20 personalized recommendations:

```bash
python3 scripts/recommendations/recommendation_engine.py
```

### Options

```bash
# Generate 50 recommendations
python3 scripts/recommendations/recommendation_engine.py -n 50

# Include tracks you've already played
python3 scripts/recommendations/recommendation_engine.py --include-played
```

## How It Works

1. **Analyzes your top tracks** - Identifies your most-played tracks from your streaming history
2. **Extracts artists** - Finds the artists behind your favorite tracks
3. **Gets top tracks** - Fetches each artist's most popular tracks using `artist_top_tracks`
4. **Filters results** - Excludes tracks you've already listened to (optional)
5. **Presents recommendations** - Shows tracks with Spotify links

## Files

- `spotify_api_client.py` - Client for interacting with Spotify Web API (non-deprecated endpoints only)
- `recommendation_engine.py` - Main recommendation engine and CLI
- `verify_credentials.py` - Script to verify your API credentials work
- `README.md` - This file

## Troubleshooting

### "Spotify API credentials required"
- Make sure you've set the environment variables
- Restart your terminal after setting them
- Verify with: `echo $SPOTIPY_CLIENT_ID`

### "No recommendations found"
- Make sure you've run `parse_spotify_data.py` first
- Check that your database has track URIs
- Try with `--include-played` to see if any tracks are found

### 403 or 404 errors
- If you see these on `audio-features`, `recommendations`, or `related-artists` endpoints, that's expected - these are deprecated
- The recommendation system is designed to work without these endpoints
- Only `track`, `artists`, `artist_top_tracks`, and `search` are used

### Rate limit errors
- The script includes delays to respect rate limits
- If you hit limits, wait a few minutes and try again
