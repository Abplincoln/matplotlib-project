#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

df = pd.read_csv('C://Users//HP//Datasets//fifa_world_cup_2026_player_performance.csv')  # adjust to your actual file name/path

print(df.columns.tolist())   # shows all column names
print(df.head())              # shows first 5 rows so I can see the actual structure


# In[1]:


import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

df = pd.read_csv('fifa_world_cup_2026_player_performance.csv')  # adjust filename/path as needed

# Tournament-level columns (total_goals_tournament, tournament_rating, etc.) repeat
# on every match-row for a player. Summing/averaging the raw df would multiply each
# player's totals by however many matches they played. We keep only the first row
# per player, since tournament totals are identical across all of that player's rows.
player_df = df.drop_duplicates(subset='player_id', keep='first')[
    ['player_id', 'player_name', 'team', 'position', 'nationality',
     'total_goals_tournament', 'total_assists_tournament',
     'tournament_rating', 'possession_impact', 'pressure_resistance',
     'creativity_score', 'consistency_score', 'clutch_performance_score',
     'player_of_match_awards']
]

teams = sorted(player_df['team'].unique())

# Team-level comparison doesn't depend on any filter, so it's computed once here
# rather than recomputed on every dropdown change inside a callback.
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


if __name__ == '__main__':
    app.run(debug=True, port=8054)


# In[ ]:





# In[ ]:





# In[ ]:




