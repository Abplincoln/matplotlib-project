import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

df = pd.read_csv('fifa_world_cup_2026_player_performance.csv')

player_df = df.drop_duplicates(subset='player_id', keep='first')[
    ['player_id', 'player_name', 'team', 'position', 'nationality',
     'total_goals_tournament', 'total_assists_tournament',
     'tournament_rating', 'possession_impact', 'pressure_resistance',
     'creativity_score', 'consistency_score', 'clutch_performance_score',
     'player_of_match_awards']
]

teams = sorted(player_df['team'].unique())

team_stats = player_df.groupby('team').agg(
    avg_rating=('tournament_rating', 'mean'),
    total_goals=('total_goals_tournament', 'sum'),
    total_assists=('total_assists_tournament', 'sum')
).reset_index()

team_rating_fig = px.bar(
    team_stats.sort_values('avg_rating', ascending=True),
    x='avg_rating', y='team', orientation='h',
    title='Average Tournament Rating by Team',
    color='avg_rating', color_continuous_scale='Blues'
)

team_goals_fig = px.bar(
    team_stats.sort_values('total_goals', ascending=True),
    x='total_goals', y='team', orientation='h',
    title='Total Goals by Team',
    color='total_goals', color_continuous_scale='Greens'
)

app = Dash(__name__)
server = app.server

app.layout = html.Div([

    html.H1("FIFA World Cup — Team & Player Comparison", style={'textAlign': 'center'}),

    html.H2("Team Comparison", style={'paddingLeft': '20px'}),

    html.Div([
        dcc.Graph(id='team-rating-bar', figure=team_rating_fig, style={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='team-goals-bar', figure=team_goals_fig, style={'width': '49%', 'display': 'inline-block'}),
    ]),

    html.Hr(),

    html.H2("Player Comparison by Team", style={'paddingLeft': '20px'}),

    html.Div([
        html.Label("Select Team"),
        dcc.Dropdown(
            id='team-filter',
            options=[{'label': t, 'value': t} for t in teams],
            value=teams[0],
            clearable=False
        )
    ], style={'width': '30%', 'padding': '10px'}),

    dcc.Graph(id='player-rating-bar'),

    dcc.Graph(id='player-goals-assists-bar'),

])


@app.callback(
    Output('player-rating-bar', 'figure'),
    Output('player-goals-assists-bar', 'figure'),
    Input('team-filter', 'value'),
)
def update_player_comparison(selected_team):

    team_players = player_df[player_df['team'] == selected_team]

    rating_fig = px.bar(
        team_players.sort_values('tournament_rating', ascending=True),
        x='tournament_rating', y='player_name', orientation='h',
        title=f'{selected_team} — Players by Tournament Rating',
        color='tournament_rating', color_continuous_scale='Purples'
    )

    melted = team_players.melt(
        id_vars='player_name',
        value_vars=['total_goals_tournament', 'total_assists_tournament'],
        var_name='stat', value_name='value'
    )
    goals_assists_fig = px.bar(
        melted, x='player_name', y='value', color='stat',
        barmode='group',
        title=f'{selected_team} — Goals vs Assists by Player'
    )

    return rating_fig, goals_assists_fig


import os

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))