"""
Spotify API client for fetching track metadata and recommendations.

Note: Several Spotify API endpoints are deprecated for apps created after Nov 27, 2024:
- audio-features (deprecated)
- recommendations (deprecated)
- related-artists (deprecated)

This client only uses endpoints that are still available:
- track (get track info)
- artists (get artist info)
- artist_top_tracks (get artist's top tracks)
- search (search for tracks)
"""
import os
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict, Optional


class SpotifyAPIClient:
    """Client for interacting with Spotify Web API."""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize Spotify API client.
        
        Args:
            client_id: Spotify Client ID (or set SPOTIPY_CLIENT_ID env var)
            client_secret: Spotify Client Secret (or set SPOTIPY_CLIENT_SECRET env var)
        """
        self.client_id = client_id or os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SPOTIPY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Spotify API credentials required. Set SPOTIPY_CLIENT_ID and "
                "SPOTIPY_CLIENT_SECRET environment variables, or pass them as arguments."
            )
        
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            
            # Test authentication by making a simple request
            try:
                self.sp.search('test', limit=1, type='track')
            except Exception as auth_error:
                raise ValueError(
                    f"Failed to authenticate with Spotify API. "
                    f"Please verify your Client ID and Client Secret are correct. "
                    f"Error: {auth_error}"
                )
        except spotipy.exceptions.SpotifyException as e:
            raise ValueError(
                f"Spotify API error: {e}. "
                f"Please check your credentials at https://developer.spotify.com/dashboard"
            )
    
    # Deprecated endpoints removed:
    # - audio_features (deprecated Nov 2024)
    # - recommendations (deprecated 2024)
    # - related_artists (deprecated 2024)
    
    def get_track_info(self, track_uri: str) -> Optional[Dict]:
        """Get track information including genres.
        
        Args:
            track_uri: Spotify track URI
        
        Returns:
            Dictionary with track info, or None if not found
        """
        try:
            track_id = track_uri.split(':')[-1]
            track = self.sp.track(track_id)
            
            # Get artist info to extract genres
            artist_ids = [artist['id'] for artist in track['artists']]
            artists = self.sp.artists(artist_ids)['artists']
            
            # Collect genres from all artists
            genres = set()
            for artist in artists:
                genres.update(artist.get('genres', []))
            
            return {
                'name': track['name'],
                'artists': [a['name'] for a in track['artists']],
                'album': track['album']['name'],
                'genres': list(genres),
                'popularity': track['popularity'],
                'release_date': track['album']['release_date'],
                'uri': track_uri
            }
        except Exception as e:
            print(f"Error fetching track info for {track_uri}: {e}")
            return None
    
    
    # get_related_artists removed - endpoint deprecated for apps created after Nov 2024
    
    def get_artist_top_tracks(self, artist_id: str, country: str = 'US') -> List[Dict]:
        """Get top tracks for an artist.
        
        Args:
            artist_id: Spotify artist ID
            country: Country code for track availability
        
        Returns:
            List of top tracks
        """
        try:
            # Extract ID from URI if needed
            if ':' in artist_id:
                artist_id = artist_id.split(':')[-1]
            
            result = self.sp.artist_top_tracks(artist_id, country=country)
            return result.get('tracks', [])
        except Exception as e:
            print(f"Error getting artist top tracks: {e}")
            return []
    
    def get_recommendations(
        self,
        seed_tracks: Optional[List[str]] = None,
        seed_artists: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 20,
        **kwargs
    ) -> List[Dict]:
        """Get track recommendations based on your listening history.
        
        NOTE: The recommendations endpoint was deprecated by Spotify in 2024.
        This method uses an alternative approach: getting top tracks from
        artists in your listening history.
        
        Args:
            seed_tracks: List of track URIs or IDs (used to find artists)
            seed_artists: List of artist URIs or IDs
            seed_genres: List of genres (ignored - not supported)
            limit: Number of recommendations (1-100)
        
        Returns:
            List of recommended tracks from your favorite artists
        """
        # Alternative approach since recommendations endpoint is deprecated
        # Strategy: Get artists from seed tracks, then get their top tracks
        
        try:
            artist_ids = set()
            
            # Extract artist IDs from seed tracks
            if seed_tracks:
                if isinstance(seed_tracks, str):
                    seed_tracks = seed_tracks.split(',')
                if not isinstance(seed_tracks, list):
                    seed_tracks = [seed_tracks]
                
                # Randomly sample from a larger pool of seed tracks for variety
                seed_pool = seed_tracks[:20]  # Use top 20 tracks as pool
                random.shuffle(seed_pool)
                selected_seeds = seed_pool[:8]  # Pick 8 random tracks from pool
                
                print(f"Finding artists from {len(selected_seeds)} randomly selected seed tracks...")
                for track_uri in selected_seeds:
                    track_id = track_uri.split(':')[-1] if ':' in track_uri else track_uri
                    try:
                        track = self.sp.track(track_id)
                        if track and track.get('artists'):
                            for artist in track['artists']:
                                artist_ids.add(artist['id'])
                    except Exception as e:
                        print(f"Warning: Could not get track {track_id}: {e}")
            
            # Add any directly provided artist IDs
            if seed_artists:
                if isinstance(seed_artists, str):
                    seed_artists = seed_artists.split(',')
                if not isinstance(seed_artists, list):
                    seed_artists = [seed_artists]
                for artist_uri in seed_artists:
                    artist_id = artist_uri.split(':')[-1] if ':' in artist_uri else artist_uri
                    artist_ids.add(artist_id)
            
            if not artist_ids:
                print("Error: Could not extract any artist IDs from seeds")
                return []
            
            print(f"Found {len(artist_ids)} unique artists from your top tracks")
            
            # Note: The related-artists endpoint is also deprecated for new apps (post Nov 2024)
            # So we directly use the artists from your listening history
            # This actually gives more personalized results based on YOUR taste
            
            print(f"Getting top tracks from these artists...")
            
            # Shuffle artist order for variety
            artist_list = list(artist_ids)
            random.shuffle(artist_list)
            
            # Get top tracks from artists in your listening history
            all_tracks = []
            
            for artist_id in artist_list:
                try:
                    top_tracks = self.get_artist_top_tracks(artist_id)
                    # Shuffle top tracks to not always get the same ones
                    shuffled_tracks = list(top_tracks)
                    random.shuffle(shuffled_tracks)
                    all_tracks.extend(shuffled_tracks)
                except Exception as e:
                    print(f"Warning: Could not get top tracks for artist {artist_id}: {e}")
            
            # Remove duplicates while preserving randomized order
            seen_ids = set()
            unique_tracks = []
            for track in all_tracks:
                if track['id'] not in seen_ids:
                    seen_ids.add(track['id'])
                    unique_tracks.append(track)
            
            # Take requested number of recommendations
            recommendations = unique_tracks[:limit]
            
            print(f"Generated {len(recommendations)} recommendations based on your favorite artists")
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            import traceback
            traceback.print_exc()
            return []

