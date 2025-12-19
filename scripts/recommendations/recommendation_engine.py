"""
Custom recommendation engine based on listening history analysis.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter
from spotify_api_client import SpotifyAPIClient


class RecommendationEngine:
    """Custom recommendation engine that analyzes listening patterns."""
    
    def __init__(self, db_path: Optional[Path] = None, api_client: Optional[SpotifyAPIClient] = None):
        """Initialize recommendation engine.
        
        Args:
            db_path: Path to parquet database file
            api_client: SpotifyAPIClient instance (optional, will prompt for credentials if not provided)
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / 'spotify_streaming_history.parquet'
        
        self.df = pd.read_parquet(db_path)
        self.api_client = api_client
        
        # Filter for tracks only
        self.df_tracks = self.df[
            (self.df['master_metadata_track_name'].notna()) &
            (self.df['spotify_track_uri'].notna())
        ].copy()
    
    def analyze_listening_patterns(self) -> Dict:
        """Analyze user's listening patterns to understand preferences.
        
        Returns:
            Dictionary with analyzed preferences
        """
        # Get top tracks by play count
        top_tracks = self.df_tracks.groupby('spotify_track_uri').agg({
            'ms_played': ['sum', 'count']
        }).reset_index()
        top_tracks.columns = ['track_uri', 'total_ms', 'play_count']
        top_tracks = top_tracks.sort_values('play_count', ascending=False)
        
        # Get top artists
        top_artists = self.df_tracks.groupby('master_metadata_album_artist_name')['ms_played'].sum().sort_values(ascending=False)
        
        # Calculate average listening metrics
        avg_listen_duration = self.df_tracks['ms_played'].mean() / 1000  # seconds
        skip_rate = self.df_tracks['skipped'].sum() / len(self.df_tracks) if 'skipped' in self.df_tracks.columns else 0
        
        return {
            'top_track_uris': top_tracks['track_uri'].head(50).tolist(),
            'top_artists': top_artists.head(20).index.tolist(),
            'avg_listen_duration': avg_listen_duration,
            'skip_rate': skip_rate,
            'total_unique_tracks': len(self.df_tracks['spotify_track_uri'].unique()),
            'total_plays': len(self.df_tracks)
        }
    
    
    def generate_recommendations(
        self,
        num_recommendations: int = 20,
        exclude_played: bool = True,
        use_custom_algorithm: bool = True
    ) -> List[Dict]:
        """Generate personalized recommendations.
        
        Args:
            num_recommendations: Number of recommendations to generate
            exclude_played: Whether to exclude tracks already in listening history
            use_custom_algorithm: Use custom algorithm vs Spotify's built-in
        
        Returns:
            List of recommended tracks with metadata
        """
        if not self.api_client:
            raise ValueError("Spotify API client required. Initialize with api_client parameter.")
        
        patterns = self.analyze_listening_patterns()
        
        if use_custom_algorithm:
            # Use custom algorithm based on listening patterns
            # Note: Audio features endpoint is deprecated for apps created after Nov 27, 2024
            # So we use seed tracks and genre-based recommendations instead
            
            # Get seed tracks from top played
            seed_tracks = patterns['top_track_uris'][:5]  # Use top 5 as seeds
            
            # Get recommendations using seed tracks
            # Spotify's algorithm will analyze these tracks and find similar ones
            recommendations = self.api_client.get_recommendations(
                seed_tracks=seed_tracks,
                limit=num_recommendations * 2,  # Get more to filter
            )
        else:
            # Use Spotify's algorithm directly
            seed_tracks = patterns['top_track_uris'][:5]
            recommendations = self.api_client.get_recommendations(
                seed_tracks=seed_tracks,
                limit=num_recommendations
            )
        
        # Filter out already played tracks if requested
        if exclude_played:
            played_uris = set(self.df_tracks['spotify_track_uri'].unique())
            recommendations = [r for r in recommendations if r['uri'] not in played_uris]
        
        # Format results
        formatted_recommendations = []
        for track in recommendations[:num_recommendations]:
            formatted_recommendations.append({
                'name': track['name'],
                'artists': ', '.join([a['name'] for a in track['artists']]),
                'album': track['album']['name'],
                'uri': track['uri'],
                'popularity': track['popularity'],
                'preview_url': track.get('preview_url'),
                'external_urls': track.get('external_urls', {}).get('spotify')
            })
        
        return formatted_recommendations
    
    def print_recommendations(self, recommendations: List[Dict]):
        """Print recommendations in a formatted way."""
        print("="*80)
        print("PERSONALIZED RECOMMENDATIONS")
        print("="*80)
        print(f"{'Rank':<6} {'Song':<40} {'Artist':<30} {'Popularity':<10}")
        print("-"*80)
        
        for idx, rec in enumerate(recommendations, 1):
            song = rec['name']
            artist = rec['artists']
            popularity = rec['popularity']
            
            if len(song) > 38:
                song = song[:35] + "..."
            if len(artist) > 28:
                artist = artist[:25] + "..."
            
            print(f"{idx:<6} {song:<40} {artist:<30} {popularity:<10}")
        
        print("="*80)
        print(f"\nSpotify Links:")
        for idx, rec in enumerate(recommendations[:10], 1):  # Show first 10 links
            if rec.get('external_urls'):
                print(f"{idx}. {rec['name']}: {rec['external_urls']}")


def main():
    """Main function to generate recommendations."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate personalized music recommendations')
    parser.add_argument('-n', '--num', type=int, default=20,
                       help='Number of recommendations (default: 20)')
    parser.add_argument('--include-played', action='store_true',
                       help='Include tracks already in listening history')
    parser.add_argument('--use-spotify-algo', action='store_true',
                       help='Use Spotify\'s algorithm instead of custom')
    
    args = parser.parse_args()
    
    # Initialize API client (will prompt for credentials if not set)
    try:
        api_client = SpotifyAPIClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo use recommendations, you need Spotify API credentials:")
        print("1. Go to https://developer.spotify.com/dashboard")
        print("2. Create an app and get Client ID and Client Secret")
        print("3. Set environment variables:")
        print("   export SPOTIPY_CLIENT_ID='your_client_id'")
        print("   export SPOTIPY_CLIENT_SECRET='your_client_secret'")
        return
    
    # Initialize recommendation engine
    engine = RecommendationEngine(api_client=api_client)
    
    # Generate recommendations
    print("Analyzing your listening patterns...")
    recommendations = engine.generate_recommendations(
        num_recommendations=args.num,
        exclude_played=not args.include_played,
        use_custom_algorithm=not args.use_spotify_algo
    )
    
    # Display results
    engine.print_recommendations(recommendations)


if __name__ == "__main__":
    main()

