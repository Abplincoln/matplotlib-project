#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

df = pd.read_csv("C://Users//HP//Datasets//StudentsPerformance.csv") # adjust filename/path as needed
df['average_performance'] = (df['math score'] + df['reading score'] + df['writing score']) / 3

app = Dash(__name__)

app.layout = html.Div([

    html.H1("Student Performance Comparison Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Gender"),
            dcc.Dropdown(
                id='gender-filter',
                options=[{'label': 'All', 'value': 'All'}] +
                        [{'label': g, 'value': g} for g in sorted(df['gender'].unique())],
                value='All', clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Lunch Type"),
            dcc.Dropdown(
                id='lunch-filter',
                options=[{'label': 'All', 'value': 'All'}] +
                        [{'label': l, 'value': l} for l in sorted(df['lunch'].unique())],
                value='All', clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '4%'}),

        html.Div([
            html.Label("Test Prep Course"),
            dcc.Dropdown(
                id='prep-filter',
                options=[{'label': 'All', 'value': 'All'}] +
                        [{'label': p, 'value': p} for p in sorted(df['test preparation course'].unique())],
                value='All', clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '4%'}),
    ], style={'padding': '20px'}),

    html.Div(id='kpi-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '10px'}),

    html.Div([
        dcc.Graph(id='gender-bar', style={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='score-scatter', style={'width': '49%', 'display': 'inline-block'}),
    ]),

    dcc.Graph(id='prep-boxplot'),

])


@app.callback(
    Output('kpi-cards', 'children'),
    Output('gender-bar', 'figure'),
    Output('score-scatter', 'figure'),
    Output('prep-boxplot', 'figure'),
    Input('gender-filter', 'value'),
    Input('lunch-filter', 'value'),
    Input('prep-filter', 'value'),
)
def update_dashboard(selected_gender, selected_lunch, selected_prep):

    filtered_df = df.copy()
    if selected_gender != 'All':
        filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
    if selected_lunch != 'All':
        filtered_df = filtered_df[filtered_df['lunch'] == selected_lunch]
    if selected_prep != 'All':
        filtered_df = filtered_df[filtered_df['test preparation course'] == selected_prep]

    kpi_style = {
        'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '10px',
        'textAlign': 'center', 'width': '20%', 'boxShadow': '2px 2px 8px rgba(0,0,0,0.1)'
    }

    # empty filter combo -> mean() on an empty series is NaN, which renders as "nan" on the card
    def safe_mean(series):
        return series.mean() if not series.empty else 0.0

    kpis = [
        html.Div([html.H4("Students"), html.H2(f"{len(filtered_df)}")], style=kpi_style),
        html.Div([html.H4("Avg Math"), html.H2(f"{safe_mean(filtered_df['math score']):.1f}")], style=kpi_style),
        html.Div([html.H4("Avg Reading"), html.H2(f"{safe_mean(filtered_df['reading score']):.1f}")], style=kpi_style),
        html.Div([html.H4("Avg Writing"), html.H2(f"{safe_mean(filtered_df['writing score']):.1f}")], style=kpi_style),
        html.Div([html.H4("Avg Overall"), html.H2(f"{safe_mean(filtered_df['average_performance']):.1f}")], style=kpi_style),
    ]

    gender_avg = filtered_df.groupby('gender')[['math score', 'reading score', 'writing score']].mean().reset_index()
    gender_melted = gender_avg.melt(id_vars='gender', var_name='subject', value_name='avg_score')
    gender_fig = px.bar(
        gender_melted, x='subject', y='avg_score', color='gender',
        barmode='group', title='Average Scores by Gender'
    )

    scatter_fig = px.scatter(
        filtered_df, x='math score', y='reading score', color='gender',
        title='Math vs Reading Score Relationship',
        opacity=0.6
    )

    box_fig = px.box(
        filtered_df, x='test preparation course', y='average_performance',
        color='test preparation course',
        title='Overall Performance Distribution by Test Preparation Status'
    )

    return kpis, gender_fig, scatter_fig, box_fig


if __name__ == '__main__':
    app.run(debug=True, port=8053)


# In[ ]:




