import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

df = pd.read_csv("buenos-aires-real-estate-1.csv")

def extract_neighborhood(location_string):
    parts = [p for p in location_string.split('|') if p != '']
    if len(parts) >= 1:
        return parts[-1]
    return 'Unknown'

df['neighborhood'] = df['place_with_parent_names'].apply(extract_neighborhood)

df[['lat', 'lon']] = df['lat-lon'].str.split(',', n=1, expand=True)
df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

app = Dash(__name__)
server = app.server

app.layout = html.Div([

    html.H1("Buenos Aires Real Estate Market Explorer",
            style={'textAlign': 'center', 'fontFamily': 'Georgia, serif', 'color': '#2c3e50'}),

    html.Div([
        html.Div([
            html.Label("Property Type"),
            dcc.Dropdown(
                id='type-filter',
                options=[{'label': 'All Types', 'value': 'All'}] +
                        [{'label': t, 'value': t} for t in sorted(df['property_type'].unique())],
                value='All',
                clearable=False
            )
        ], style={'width': '45%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Operation"),
            dcc.Dropdown(
                id='operation-filter',
                options=[{'label': 'All', 'value': 'All'}] +
                        [{'label': o, 'value': o} for o in sorted(df['operation'].unique())],
                value='All',
                clearable=False
            )
        ], style={'width': '45%', 'display': 'inline-block', 'marginLeft': '4%'}),
    ], style={'padding': '20px'}),

    html.Div(id='kpi-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '10px'}),

    dcc.Graph(id='price-map'),

    html.Div([
        dcc.Graph(id='price-histogram', style={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='type-price-bar', style={'width': '49%', 'display': 'inline-block'}),
    ]),

    dcc.Graph(id='neighborhood-bar'),

])


@app.callback(
    Output('kpi-cards', 'children'),
    Output('price-map', 'figure'),
    Output('price-histogram', 'figure'),
    Output('type-price-bar', 'figure'),
    Output('neighborhood-bar', 'figure'),
    Input('type-filter', 'value'),
    Input('operation-filter', 'value'),
)
def update_dashboard(selected_type, selected_operation):

    filtered_df = df.copy()
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['property_type'] == selected_type]
    if selected_operation != 'All':
        filtered_df = filtered_df[filtered_df['operation'] == selected_operation]

    price_valid = filtered_df.dropna(subset=['price_aprox_usd'])

    kpi_style = {
        'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '10px',
        'textAlign': 'center', 'width': '20%', 'boxShadow': '2px 2px 8px rgba(0,0,0,0.1)',
        'backgroundColor': '#fafafa'
    }

    def safe_mean(series):
        return series.mean() if not series.empty else 0.0

    kpis = [
        html.Div([html.H4("Listings"), html.H2(f"{len(filtered_df):,}")], style=kpi_style),
        html.Div([html.H4("Avg Price (USD)"), html.H2(f"${safe_mean(price_valid['price_aprox_usd']):,.0f}")], style=kpi_style),
        html.Div([html.H4("Avg Price/m²"), html.H2(f"${safe_mean(filtered_df['price_usd_per_m2'].dropna()):,.0f}")], style=kpi_style),
        html.Div([html.H4("Avg Surface (m²)"), html.H2(f"{safe_mean(filtered_df['surface_total_in_m2'].dropna()):,.0f}")], style=kpi_style),
    ]

    map_df = filtered_df.dropna(subset=['lat', 'lon', 'price_aprox_usd'])
    map_fig = px.scatter_map(
        map_df, lat='lat', lon='lon',
        color='price_aprox_usd', size='price_aprox_usd', size_max=10,
        color_continuous_scale='Viridis',
        hover_name='neighborhood',
        hover_data={'price_aprox_usd': ':,.0f', 'lat': False, 'lon': False},
        zoom=10, height=500,
        map_style='open-street-map',
        title='Listings by Location & Price (USD)'
    )
    map_fig.update_layout(margin={'r': 0, 't': 40, 'l': 0, 'b': 0})

    hist_fig = px.histogram(
        price_valid, x='price_aprox_usd', nbins=50,
        title='Price Distribution (USD)',
        color_discrete_sequence=['#3498db']
    )
    hist_fig.update_layout(xaxis_title='Price (USD)', yaxis_title='Number of Listings')

    type_avg = price_valid.groupby('property_type')['price_aprox_usd'].mean().reset_index()
    type_fig = px.bar(
        type_avg.sort_values('price_aprox_usd'),
        x='price_aprox_usd', y='property_type', orientation='h',
        title='Average Price by Property Type',
        color='price_aprox_usd', color_continuous_scale='Teal'
    )

    neighborhood_avg = filtered_df.dropna(subset=['price_usd_per_m2']).groupby('neighborhood')['price_usd_per_m2'].mean()
    top10_neighborhoods = neighborhood_avg.nlargest(10).reset_index()
    neighborhood_fig = px.bar(
        top10_neighborhoods.sort_values('price_usd_per_m2'),
        x='price_usd_per_m2', y='neighborhood', orientation='h',
        title='Top 10 Most Expensive Neighborhoods (Price per m²)',
        color='price_usd_per_m2', color_continuous_scale='Magenta'
    )

    return kpis, map_fig, hist_fig, type_fig, neighborhood_fig


import os

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))