"""
Data model for Spotify streaming history records.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class SpotifyStreamingRecord:
    """Data model for a single Spotify streaming record."""
    ts: str  # ISO format timestamp
    platform: Optional[str]
    ms_played: int
    conn_country: Optional[str]
    ip_addr: Optional[str]
    master_metadata_track_name: Optional[str]
    master_metadata_album_artist_name: Optional[str]
    master_metadata_album_album_name: Optional[str]
    spotify_track_uri: Optional[str]
    episode_name: Optional[str]
    episode_show_name: Optional[str]
    spotify_episode_uri: Optional[str]
    audiobook_title: Optional[str]
    audiobook_uri: Optional[str]
    audiobook_chapter_uri: Optional[str]
    audiobook_chapter_title: Optional[str]
    reason_start: Optional[str]
    reason_end: Optional[str]
    shuffle: Optional[bool]
    skipped: Optional[bool]
    offline: Optional[bool]
    offline_timestamp: Optional[int]
    incognito_mode: Optional[bool]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SpotifyStreamingRecord':
        """Create a record from a dictionary (JSON object)."""
        return cls(
            ts=data.get('ts', ''),
            platform=data.get('platform'),
            ms_played=data.get('ms_played', 0),
            conn_country=data.get('conn_country'),
            ip_addr=data.get('ip_addr'),
            master_metadata_track_name=data.get('master_metadata_track_name'),
            master_metadata_album_artist_name=data.get('master_metadata_album_artist_name'),
            master_metadata_album_album_name=data.get('master_metadata_album_album_name'),
            spotify_track_uri=data.get('spotify_track_uri'),
            episode_name=data.get('episode_name'),
            episode_show_name=data.get('episode_show_name'),
            spotify_episode_uri=data.get('spotify_episode_uri'),
            audiobook_title=data.get('audiobook_title'),
            audiobook_uri=data.get('audiobook_uri'),
            audiobook_chapter_uri=data.get('audiobook_chapter_uri'),
            audiobook_chapter_title=data.get('audiobook_chapter_title'),
            reason_start=data.get('reason_start'),
            reason_end=data.get('reason_end'),
            shuffle=data.get('shuffle'),
            skipped=data.get('skipped'),
            offline=data.get('offline'),
            offline_timestamp=data.get('offline_timestamp'),
            incognito_mode=data.get('incognito_mode')
        )
    
    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            'ts': self.ts,
            'platform': self.platform,
            'ms_played': self.ms_played,
            'conn_country': self.conn_country,
            'ip_addr': self.ip_addr,
            'master_metadata_track_name': self.master_metadata_track_name,
            'master_metadata_album_artist_name': self.master_metadata_album_artist_name,
            'master_metadata_album_album_name': self.master_metadata_album_album_name,
            'spotify_track_uri': self.spotify_track_uri,
            'episode_name': self.episode_name,
            'episode_show_name': self.episode_show_name,
            'spotify_episode_uri': self.spotify_episode_uri,
            'audiobook_title': self.audiobook_title,
            'audiobook_uri': self.audiobook_uri,
            'audiobook_chapter_uri': self.audiobook_chapter_uri,
            'audiobook_chapter_title': self.audiobook_chapter_title,
            'reason_start': self.reason_start,
            'reason_end': self.reason_end,
            'shuffle': self.shuffle,
            'skipped': self.skipped,
            'offline': self.offline,
            'offline_timestamp': self.offline_timestamp,
            'incognito_mode': self.incognito_mode
        }
    
    def get_unique_key(self) -> tuple:
        """Generate a unique key for deduplication.
        Uses timestamp, track/episode URI, and ms_played as unique identifier.
        """
        content_uri = self.spotify_track_uri or self.spotify_episode_uri or self.audiobook_uri
        return (self.ts, content_uri, self.ms_played)

