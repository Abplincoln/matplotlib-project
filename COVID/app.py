import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

df = pd.read_json("India_covid19.json")

app = Dash(__name__)
server = app.server

app.layout = html.Div([

    html.H1("COVID-19 State-Wise Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select State"),
        dcc.Dropdown(
            id='state-filter',
            options=[{'label': 'All States', 'value': 'All'}] +
                    [{'label': s, 'value': s} for s in sorted(df['state_name'].unique())],
            value='All',
            clearable=False
        )
    ], style={'width': '30%', 'margin': '0 auto', 'paddingBottom': '20px'}),

    html.Div(id='kpi-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '10px'}),

    html.Div([
        dcc.Graph(id='covid-heatmap', style={'width': '58%', 'display': 'inline-block'}),
        dcc.Graph(id='outcome-donut', style={'width': '40%', 'display': 'inline-block'}),
    ]),

    html.Div([
        dcc.Graph(id='top10-bar'),
    ]),
])


@app.callback(
    Output('kpi-cards', 'children'),
    Output('covid-heatmap', 'figure'),
    Output('outcome-donut', 'figure'),
    Output('top10-bar', 'figure'),
    Input('state-filter', 'value'),
)
def update_dashboard(selected_state):

    if selected_state == 'All':
        filtered_df = df.copy()
    else:
        filtered_df = df[df['state_name'] == selected_state]

    kpi_style = {
        'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '10px',
        'textAlign': 'center', 'width': '20%', 'boxShadow': '2px 2px 8px rgba(0,0,0,0.1)'
    }

    kpis = [
        html.Div([html.H4("Total Positive"), html.H2(f"{filtered_df['positive'].sum():,}")], style=kpi_style),
        html.Div([html.H4("Total Active"), html.H2(f"{filtered_df['active'].sum():,}")], style=kpi_style),
        html.Div([html.H4("Total Cured"), html.H2(f"{filtered_df['cured'].sum():,}")], style=kpi_style),
        html.Div([html.H4("Total Deaths"), html.H2(f"{filtered_df['death'].sum():,}")], style=kpi_style),
    ]

    heatmap_data = filtered_df.set_index('state_name')[['positive', 'active', 'cured', 'death']]

    if len(heatmap_data) > 1:
        col_min = heatmap_data.min()
        col_max = heatmap_data.max()
        col_range = (col_max - col_min).replace(0, 1)
        color_values = (heatmap_data - col_min) / col_range
        colorbar_title = 'Relative intensity within each metric'
    else:
        color_values = heatmap_data
        colorbar_title = 'Number of Cases'

    heatmap_fig = px.imshow(
        color_values,
        color_continuous_scale='Reds',
        aspect='auto',
        title='Case Metrics by State'
    )
    heatmap_fig.update_traces(text=heatmap_data.values, texttemplate='%{text:,.0f}')
    heatmap_fig.update_coloraxes(colorbar_title=colorbar_title)
    heatmap_fig.update_layout(height=max(400, len(heatmap_data) * 25))

    outcome_totals = pd.DataFrame({
        'Outcome': ['Active', 'Cured', 'Death'],
        'Count': [filtered_df['active'].sum(), filtered_df['cured'].sum(), filtered_df['death'].sum()]
    })
    donut_fig = px.pie(
        outcome_totals, names='Outcome', values='Count', hole=0.5,
        title='Outcome Breakdown', color='Outcome',
        color_discrete_map={'Active': '#f1c40f', 'Cured': '#2ecc71', 'Death': '#e74c3c'}
    )

    top10 = df.nlargest(10, 'positive')
    bar_fig = px.bar(
        top10.sort_values('positive'),
        x='positive', y='state_name', orientation='h',
        title='Top 10 States by Positive Cases',
        color='positive', color_continuous_scale='Reds'
    )

    return kpis, heatmap_fig, donut_fig, bar_fig


import os

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))