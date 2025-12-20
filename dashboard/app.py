"""
Spotify Analytics Dashboard using Plotly Dash
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
from dash import Dash, html, dcc, callback, Output, Input, State
from dash.exceptions import PreventUpdate

# ============================================================================
# Configuration & Constants
# ============================================================================

DATA_PATH = Path(__file__).parent.parent / "spotify_streaming_history.parquet"

COLORS = {
    'background': '#f0f8ff',  # alice blue (light background)
    'card': '#ffffff',  # white cards
    'primary': '#89CFF0',  # baby blue
    'text': '#2c3e50',  # dark blue-gray for text
    'text_secondary': '#7f8c8d',  # gray for secondary text
    'accent': '#5dade2',  # slightly darker blue for accents
    'gradient_start': '#89CFF0',  # baby blue
    'gradient_end': '#a8d8ea',  # lighter baby blue
}

FONT_FAMILY = '"Helvetica Rounded", "Arial Rounded MT Bold", "Helvetica Neue", Helvetica, Arial, sans-serif'

# ============================================================================
# Data Loading
# ============================================================================

def load_data():
    """Load the Spotify streaming history data."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DATA_PATH}. "
            "Run 'python scripts/parse_spotify_data.py' first."
        )
    df = pd.read_parquet(DATA_PATH)
    df['ts'] = pd.to_datetime(df['ts'])
    df['minutes'] = df['ms_played'] / 60000
    df['year'] = df['ts'].dt.year
    return df

# Initialize data
df = load_data()
years = sorted(df['year'].unique())
year_options = [{'label': 'all time', 'value': 'all'}] + [
    {'label': str(y), 'value': y} for y in years
]

# ============================================================================
# Helper Functions - Data Processing
# ============================================================================

def filter_by_year(data, year):
    """Filter dataframe by year. Returns all data if year is 'all'."""
    if year == 'all':
        return data.copy()
    return data[data['year'] == year].copy()

def validate_top_n(top_n, max_value=100, default=10):
    """Validate and clamp top_n value."""
    if not top_n or top_n < 1:
        return default
    return min(top_n, max_value)

# ============================================================================
# Helper Functions - UI Components
# ============================================================================

def create_label(text, style_overrides=None):
    """Create a styled label component."""
    base_style = {
        'color': COLORS['text'],
        'textTransform': 'lowercase',
        'fontFamily': FONT_FAMILY,
    }
    if style_overrides:
        base_style.update(style_overrides)
    return html.Label(text, style=base_style)

def create_year_dropdown(dropdown_id, value='all'):
    """Create a year dropdown component."""
    return dcc.Dropdown(
        id=dropdown_id,
        options=year_options,
        value=value,
        style={'width': '100px', 'display': 'inline-block', 'fontFamily': FONT_FAMILY},
        clearable=False,
    )

def create_top_n_input(input_id, value=10, min_val=1, max_val=100):
    """Create a top N number input component."""
    return dcc.Input(
        id=input_id,
        type='number',
        value=value,
        min=min_val,
        max=max_val,
        style={
            'width': '70px',
            'padding': '8px 12px',
            'borderRadius': '20px',
            'border': f'1px solid {COLORS["text_secondary"]}',
            'backgroundColor': COLORS['background'],
            'color': COLORS['text'],
            'textAlign': 'center',
            'fontFamily': FONT_FAMILY,
        },
    )

def create_search_input(input_id, placeholder):
    """Create a search input component."""
    return dcc.Input(
        id=input_id,
        type='text',
        placeholder=placeholder,
        style={
            'width': '300px',
            'padding': '10px',
            'borderRadius': '20px',
            'border': f'1px solid {COLORS["text_secondary"]}',
            'backgroundColor': COLORS['background'],
            'color': COLORS['text'],
            'textTransform': 'lowercase',
            'fontFamily': FONT_FAMILY,
        },
    )

def create_stat_box(stat_id, label_text):
    """Create a stat box component."""
    card_style = {
        'backgroundColor': COLORS['card'],
        'borderRadius': '16px',
        'padding': '20px',
        'marginBottom': '20px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
        'fontFamily': FONT_FAMILY,
    }
    return html.Div([
        html.H3(id=stat_id, style={
            'color': COLORS['primary'],
            'margin': '0',
            'fontSize': '2rem',
            'fontFamily': FONT_FAMILY,
        }),
        html.P(label_text, style={
            'color': COLORS['text_secondary'],
            'margin': '5px 0 0 0',
            'textTransform': 'lowercase',
            'fontFamily': FONT_FAMILY,
        }),
    ], style={**card_style, 'textAlign': 'center', 'flex': '1', 'margin': '0 10px'})

# ============================================================================
# Helper Functions - Charts
# ============================================================================

def apply_bar_chart_styling(fig, title, y_axis_title=''):
    """Apply consistent styling to bar charts."""
    fig.update_layout(
        plot_bgcolor=COLORS['card'],
        paper_bgcolor=COLORS['card'],
        font=dict(color=COLORS['text'], family=FONT_FAMILY),
        yaxis={
            'categoryorder': 'total ascending',
            'title': y_axis_title,
            'ticksuffix': '   ',  # Add space after labels
        },
        showlegend=False,
        coloraxis_showscale=False,
        title=title,
        title_font_size=14,
        margin=dict(l=20, r=20, t=50, b=40),
    )
    fig.update_traces(
        textposition='outside',
        textfont_size=11,
    )
    return fig

def create_horizontal_bar_chart(data, x_col, y_col, color_col, text_col, 
                                 custom_data_cols, hover_template, title):
    """Create a styled horizontal bar chart."""
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        orientation='h',
        color=color_col,
        color_continuous_scale=[COLORS['gradient_end'], COLORS['primary']],
        text=text_col,
        custom_data=custom_data_cols,
    )
    fig = apply_bar_chart_styling(fig, title)
    fig.update_traces(hovertemplate=hover_template)
    return fig

# ============================================================================
# App Initialization
# ============================================================================

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "spotify analytics"

# Set favicon
favicon_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text x="50" y="75" font-size="70" text-anchor="middle" dominant-baseline="middle">🎵</text></svg>'
favicon_data_uri = 'data:image/svg+xml;charset=utf-8,' + urllib.parse.quote(favicon_svg, safe='')

app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        <link rel="icon" type="image/svg+xml" href="{favicon_data_uri}">
        {{%css%}}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

# ============================================================================
# Layout
# ============================================================================

card_style = {
    'backgroundColor': COLORS['card'],
    'borderRadius': '16px',
    'padding': '20px',
    'marginBottom': '20px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
    'fontFamily': FONT_FAMILY,
}

button_style = {
    'marginLeft': '10px',
    'padding': '10px 20px',
    'backgroundColor': COLORS['primary'],
    'color': COLORS['card'],
    'border': 'none',
    'borderRadius': '20px',
    'cursor': 'pointer',
    'fontWeight': '500',
    'textTransform': 'lowercase',
    'fontFamily': FONT_FAMILY,
}

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🎵 spotify analytics", style={
            'color': COLORS['primary'],
            'marginBottom': '5px',
            'fontSize': '2.5rem',
            'textTransform': 'lowercase',
            'fontWeight': '600',
            'fontFamily': FONT_FAMILY,
        }),
        html.P("your personal listening dashboard", style={
            'color': COLORS['text_secondary'],
            'marginTop': '0',
            'textTransform': 'lowercase',
            'fontFamily': FONT_FAMILY,
        }),
    ], style={'textAlign': 'center', 'padding': '0 0 20px 0'}),
    
    # Stats Overview
    html.Div([
        html.Div([
            create_label("year:", {'marginRight': '10px'}),
            create_year_dropdown('stats-year-dropdown'),
        ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
        html.Div([
            create_stat_box('total-plays-stat', 'total plays'),
            create_stat_box('hours-listened-stat', 'hours listened'),
            create_stat_box('unique-songs-stat', 'unique songs'),
            create_stat_box('unique-artists-stat', 'unique artists'),
        ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap', 'marginBottom': '20px'}),
    ]),
    
    # Tabs for different views
    dcc.Tabs(
        id='main-tabs',
        className='custom-tabs',
        children=[
            # Top Artists Tab
            dcc.Tab(
                label='🎤 top artists',
                className='custom-tab',
                selected_className='custom-tab--selected',
                children=[
                    html.Div([
                        html.Div([
                            create_label("year:", {'marginRight': '10px'}),
                            create_year_dropdown('artists-year-dropdown'),
                            create_label("top:", {'marginLeft': '20px', 'marginRight': '10px'}),
                            create_top_n_input('artists-top-n-input', max_val=100),
                        ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),
                        dcc.Graph(id='top-artists-chart'),
                    ], style={**card_style, 'marginTop': '20px'}),
                ],
            ),
            
            # Top Songs Tab
            dcc.Tab(
                label='🎵 top songs',
                className='custom-tab',
                selected_className='custom-tab--selected',
                children=[
                    html.Div([
                        html.Div([
                            create_label("year:", {'marginRight': '10px'}),
                            create_year_dropdown('songs-year-dropdown'),
                            create_label("top:", {'marginLeft': '20px', 'marginRight': '10px'}),
                            create_top_n_input('songs-top-n-input', max_val=100),
                            create_label("sort by:", {'marginLeft': '20px', 'marginRight': '10px'}),
                            dcc.Dropdown(
                                id='songs-sort-dropdown',
                                options=[
                                    {'label': 'plays', 'value': 'plays'},
                                    {'label': 'minutes', 'value': 'minutes'},
                                ],
                                value='plays',
                                style={'width': '120px', 'display': 'inline-block', 'fontFamily': FONT_FAMILY},
                                clearable=False,
                            ),
                        ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),
                        dcc.Graph(id='top-songs-chart'),
                    ], style={**card_style, 'marginTop': '20px'}),
                ],
            ),
            
            # Song Search Tab
            dcc.Tab(
                label='🔍 song search',
                className='custom-tab',
                selected_className='custom-tab--selected',
                children=[
                    html.Div([
                        html.Div([
                            create_search_input('song-search-input', 'enter song name...'),
                            html.Button('search', id='song-search-button', style=button_style),
                        ], style={'marginBottom': '20px'}),
                        html.Div(id='song-search-results'),
                    ], style={**card_style, 'marginTop': '20px'}),
                ],
            ),
            
            # Artist Stats Tab
            dcc.Tab(
                label='👤 artist stats',
                className='custom-tab',
                selected_className='custom-tab--selected',
                children=[
                    html.Div([
                        html.Div([
                            create_search_input('artist-search-input', 'enter artist name...'),
                            html.Button('search', id='artist-search-button', style=button_style),
                        ], style={'marginBottom': '20px'}),
                        html.Div(id='artist-search-results'),
                    ], style={**card_style, 'marginTop': '20px'}),
                ],
            ),
            
            # Podcasts Tab
            dcc.Tab(
                label='🎙️ podcasts',
                className='custom-tab',
                selected_className='custom-tab--selected',
                children=[
                    html.Div([
                        html.Div([
                            create_label("year:", {'marginRight': '10px'}),
                            create_year_dropdown('podcasts-year-dropdown'),
                            create_label("top:", {'marginLeft': '20px', 'marginRight': '10px'}),
                            create_top_n_input('podcasts-top-n-input', max_val=50),
                        ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),
                        dcc.Graph(id='top-podcasts-chart'),
                    ], style={**card_style, 'marginTop': '20px'}),
                ],
            ),
            
            # Listening Trends Tab
            dcc.Tab(
                label='📈 trends',
                className='custom-tab',
                selected_className='custom-tab--selected',
                children=[
                    html.Div([
                        dcc.Graph(id='listening-trends-chart'),
                    ], style={**card_style, 'marginTop': '20px'}),
                ],
            ),
        ],
        style={
            'backgroundColor': COLORS['background'],
            'fontFamily': FONT_FAMILY,
            'padding': '0 10px',
        },
    ),
], style={
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh',
    'padding': '20px',
    'fontFamily': FONT_FAMILY,
})

# ============================================================================
# Callbacks
# ============================================================================

@callback(
    [Output('total-plays-stat', 'children'),
     Output('hours-listened-stat', 'children'),
     Output('unique-songs-stat', 'children'),
     Output('unique-artists-stat', 'children')],
    Input('stats-year-dropdown', 'value'),
)
def update_stats(year):
    """Update the top 4 stat boxes based on selected year."""
    filtered = filter_by_year(df, year)
    
    total_plays = f"{len(filtered):,}"
    hours_listened = f"{filtered['minutes'].sum() / 60:,.1f}"
    
    # Unique songs and artists - only count tracks (exclude podcasts/audiobooks)
    tracks_only = filtered[filtered['master_metadata_track_name'].notna()]
    unique_songs = f"{tracks_only['master_metadata_track_name'].nunique():,}"
    unique_artists = f"{tracks_only['master_metadata_album_artist_name'].nunique():,}"
    
    return total_plays, hours_listened, unique_songs, unique_artists


@callback(
    Output('top-artists-chart', 'figure'),
    Input('artists-year-dropdown', 'value'),
    Input('artists-top-n-input', 'value'),
)
def update_top_artists(year, top_n):
    """Update top artists chart."""
    top_n = validate_top_n(top_n, max_value=100)
    filtered = filter_by_year(df, year)
    filtered = filtered[filtered['master_metadata_album_artist_name'].notna()]
    
    top_artists = filtered.groupby('master_metadata_album_artist_name').agg({
        'ms_played': 'sum',
        'master_metadata_track_name': 'count'
    }).reset_index()
    top_artists.columns = ['artist', 'total_ms', 'plays']
    top_artists['hours'] = (top_artists['total_ms'] / 3600000).round(1)
    top_artists = top_artists.nlargest(top_n, 'hours')
    
    title = f"top {top_n} artists by listening time" + (f" ({year})" if year != 'all' else " (all time)")
    hover_template = '<b>%{y}</b><br>hours: %{x:.1f}<br>plays: %{customdata[0]}<extra></extra>'
    
    return create_horizontal_bar_chart(
        top_artists, 'hours', 'artist', 'hours', top_artists['hours'],
        ['plays'], hover_template, title
    )


@callback(
    Output('top-songs-chart', 'figure'),
    Input('songs-year-dropdown', 'value'),
    Input('songs-top-n-input', 'value'),
    Input('songs-sort-dropdown', 'value'),
)
def update_top_songs(year, top_n, sort_by):
    """Update top songs chart."""
    top_n = validate_top_n(top_n, max_value=100)
    filtered = filter_by_year(df, year)
    filtered = filtered[filtered['master_metadata_track_name'].notna()]
    
    top_songs = filtered.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name']).agg({
        'ms_played': 'sum',
        'ts': 'count'
    }).reset_index()
    top_songs.columns = ['song', 'artist', 'total_ms', 'plays']
    top_songs['minutes'] = (top_songs['total_ms'] / 60000).round(1)
    top_songs['hours'] = (top_songs['total_ms'] / 3600000).round(1)
    
    sort_col = 'plays' if sort_by == 'plays' else 'minutes'
    top_songs = top_songs.nlargest(top_n, sort_col)
    top_songs['label'] = top_songs['song'].str.lower() + ' - ' + top_songs['artist'].str.lower()
    
    title = f"top {top_n} songs by {sort_col}" + (f" ({year})" if year != 'all' else " (all time)")
    hover_template = '<b>%{y}</b><br>plays: %{customdata[0]}<br>minutes: %{customdata[1]:.1f}<br>hours: %{customdata[2]:.1f}<extra></extra>'
    
    return create_horizontal_bar_chart(
        top_songs, sort_col, 'label', sort_col, top_songs[sort_col],
        ['plays', 'minutes', 'hours'], hover_template, title
    )


@callback(
    Output('song-search-results', 'children'),
    Input('song-search-button', 'n_clicks'),
    State('song-search-input', 'value'),
)
def search_song(n_clicks, song_name):
    """Search for songs and display results."""
    if not n_clicks or not song_name:
        return html.Div()
    
    mask = df['master_metadata_track_name'].str.lower().str.contains(song_name.lower(), na=False)
    matches = df[mask].copy()
    
    if len(matches) == 0:
        return html.P(
            f"no songs found matching '{song_name}'",
            style={'color': COLORS['text_secondary'], 'textTransform': 'lowercase', 'fontFamily': FONT_FAMILY}
        )
    
    song_stats = matches.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name']).agg({
        'ms_played': 'sum',
        'ts': 'count'
    }).reset_index()
    song_stats.columns = ['song', 'artist', 'total_ms', 'plays']
    song_stats['minutes'] = song_stats['total_ms'] / 60000
    song_stats = song_stats.sort_values('plays', ascending=False)
    
    results = []
    for _, row in song_stats.iterrows():
        results.append(html.Div([
            html.H4(row['song'].lower(), style={
                'color': COLORS['text'],
                'margin': '0 0 5px 0',
                'textTransform': 'lowercase',
                'fontFamily': FONT_FAMILY,
            }),
            html.P(row['artist'].lower(), style={
                'color': COLORS['text_secondary'],
                'margin': '0 0 10px 0',
                'textTransform': 'lowercase',
                'fontFamily': FONT_FAMILY,
            }),
            html.P([
                html.Span(f"🎧 {int(row['plays'])} plays", style={'marginRight': '20px'}),
                html.Span(f"⏱️ {row['minutes']:.1f} minutes"),
            ], style={'color': COLORS['text'], 'textTransform': 'lowercase', 'fontFamily': FONT_FAMILY}),
        ], style={
            'backgroundColor': COLORS['background'],
            'padding': '15px',
            'borderRadius': '12px',
            'marginBottom': '10px',
            'fontFamily': FONT_FAMILY,
        }))
    
    return results


@callback(
    Output('artist-search-results', 'children'),
    Input('artist-search-button', 'n_clicks'),
    State('artist-search-input', 'value'),
)
def search_artist(n_clicks, artist_name):
    """Search for artist and display stats."""
    if not n_clicks or not artist_name:
        return html.Div()
    
    mask = df['master_metadata_album_artist_name'].str.lower().str.contains(artist_name.lower(), na=False)
    matches = df[mask].copy()
    
    if len(matches) == 0:
        return html.P(
            f"no artist found matching '{artist_name}'",
            style={'color': COLORS['text_secondary'], 'textTransform': 'lowercase', 'fontFamily': FONT_FAMILY}
        )
    
    # Overall stats
    total_plays = len(matches)
    total_hours = matches['ms_played'].sum() / 3600000
    unique_songs = matches['master_metadata_track_name'].nunique()
    
    # Per-song breakdown
    song_stats = matches.groupby('master_metadata_track_name').agg({
        'ms_played': 'sum',
        'ts': 'count'
    }).reset_index()
    song_stats.columns = ['song', 'total_ms', 'plays']
    song_stats['minutes'] = (song_stats['total_ms'] / 60000).round(1)
    song_stats['hours'] = (song_stats['total_ms'] / 3600000).round(1)
    song_stats = song_stats.sort_values('plays', ascending=False)
    song_stats['song'] = song_stats['song'].str.lower()
    
    # Create chart
    fig = px.bar(
        song_stats.head(15),
        x='plays',
        y='song',
        orientation='h',
        color='plays',
        color_continuous_scale=[COLORS['gradient_end'], COLORS['primary']],
        custom_data=['minutes', 'hours'],
    )
    fig.update_layout(
        plot_bgcolor=COLORS['card'],
        paper_bgcolor=COLORS['card'],
        font=dict(color=COLORS['text'], family=FONT_FAMILY),
        yaxis={
            'categoryorder': 'total ascending',
            'ticksuffix': '   ',
        },
        showlegend=False,
        coloraxis_showscale=False,
        height=400,
        margin=dict(l=20, r=20, t=20, b=40),
    )
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>plays: %{x}<br>minutes: %{customdata[0]:.1f}<br>hours: %{customdata[1]:.1f}<extra></extra>',
    )
    
    return html.Div([
        html.Div([
            html.Div([
                html.H3(f"{total_plays:,}", style={
                    'color': COLORS['primary'],
                    'margin': '0',
                    'fontFamily': FONT_FAMILY,
                }),
                html.P("total plays", style={
                    'color': COLORS['text_secondary'],
                    'margin': '0',
                    'textTransform': 'lowercase',
                    'fontFamily': FONT_FAMILY,
                }),
            ], style={'textAlign': 'center', 'flex': '1'}),
            html.Div([
                html.H3(f"{total_hours:.1f}", style={
                    'color': COLORS['primary'],
                    'margin': '0',
                    'fontFamily': FONT_FAMILY,
                }),
                html.P("hours", style={
                    'color': COLORS['text_secondary'],
                    'margin': '0',
                    'textTransform': 'lowercase',
                    'fontFamily': FONT_FAMILY,
                }),
            ], style={'textAlign': 'center', 'flex': '1'}),
            html.Div([
                html.H3(f"{unique_songs}", style={
                    'color': COLORS['primary'],
                    'margin': '0',
                    'fontFamily': FONT_FAMILY,
                }),
                html.P("songs", style={
                    'color': COLORS['text_secondary'],
                    'margin': '0',
                    'textTransform': 'lowercase',
                    'fontFamily': FONT_FAMILY,
                }),
            ], style={'textAlign': 'center', 'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': '20px'}),
        dcc.Graph(figure=fig),
    ])


@callback(
    Output('top-podcasts-chart', 'figure'),
    Input('podcasts-year-dropdown', 'value'),
    Input('podcasts-top-n-input', 'value'),
)
def update_top_podcasts(year, top_n):
    """Update top podcasts chart."""
    top_n = validate_top_n(top_n, max_value=50)
    filtered = filter_by_year(df, year)
    filtered = filtered[filtered['episode_show_name'].notna()]
    
    if len(filtered) == 0:
        fig = go.Figure()
        fig.update_layout(
            plot_bgcolor=COLORS['card'],
            paper_bgcolor=COLORS['card'],
            font=dict(color=COLORS['text'], family=FONT_FAMILY),
            annotations=[{'text': 'no podcast data found', 'showarrow': False}]
        )
        return fig
    
    top_podcasts = filtered.groupby('episode_show_name').agg({
        'ms_played': 'sum',
        'episode_name': 'count'
    }).reset_index()
    top_podcasts.columns = ['podcast', 'total_ms', 'episodes']
    top_podcasts['hours'] = (top_podcasts['total_ms'] / 3600000).round(1)
    top_podcasts = top_podcasts.nlargest(top_n, 'hours')
    top_podcasts['podcast'] = top_podcasts['podcast'].str.lower()
    
    title = f"top {top_n} podcasts by listening time" + (f" ({year})" if year != 'all' else " (all time)")
    hover_template = '<b>%{y}</b><br>hours: %{x:.1f}<br>episodes: %{customdata[0]}<extra></extra>'
    
    return create_horizontal_bar_chart(
        top_podcasts, 'hours', 'podcast', 'hours', top_podcasts['hours'],
        ['episodes'], hover_template, title
    )


@callback(
    Output('listening-trends-chart', 'figure'),
    Input('listening-trends-chart', 'id'),
)
def update_trends(_):
    """Update listening trends chart."""
    df_trends = df.copy()
    df_trends['month'] = df_trends['ts'].dt.to_period('M').astype(str)
    
    monthly = df_trends.groupby('month').agg({
        'ms_played': 'sum',
        'master_metadata_track_name': 'count'
    }).reset_index()
    monthly.columns = ['month', 'total_ms', 'plays']
    monthly['hours'] = (monthly['total_ms'] / 3600000).round(1)
    
    fig = px.line(
        monthly,
        x='month',
        y='hours',
        markers=True,
        custom_data=['plays'],
    )
    fig.update_traces(
        line_color=COLORS['primary'],
        marker_color=COLORS['accent'],
        hovertemplate='<b>%{x}</b><br>hours: %{y:.1f}<br>plays: %{customdata[0]}<extra></extra>',
    )
    fig.update_layout(
        plot_bgcolor=COLORS['card'],
        paper_bgcolor=COLORS['card'],
        font=dict(color=COLORS['text'], family=FONT_FAMILY),
        title="listening time by month",
        title_font_size=14,
        xaxis_title="",
        yaxis_title="hours",
        margin=dict(l=20, r=20, t=50, b=40),
    )
    return fig


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎵 spotify analytics dashboard")
    print("="*60)
    print(f"\nopen your browser to: http://localhost:8050")
    print("press ctrl+c to stop the server\n")
    app.run(debug=True, port=8050)
