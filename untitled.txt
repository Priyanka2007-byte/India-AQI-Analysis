# ==============================================================================
# CUTM1018: Data Analysis and Visualization Using Python
# Project: Air Quality Index (AQI) Analysis — India
# Student: Priyanka Barik | Reg No: 250301370201
# File: app.py (Plotly Dash Dashboard - Meets Requirement 3.3)
# ==============================================================================

import os
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# ------------------------------------------------------------------------------
# 1. DATA INGESTION & ROBUST FILE DISCOVERY
# ------------------------------------------------------------------------------
data_candidates = [
    "cleaned_aqi.csv",
    os.path.join("data", "cleaned_aqi.csv"),
    "city_day.csv",
    os.path.join("data", "city_day.csv")
]

DATA_PATH = None
for candidate in data_candidates:
    if os.path.exists(candidate):
        DATA_PATH = candidate
        break

if DATA_PATH is None:
    raise FileNotFoundError("Could not locate cleaned_aqi.csv or city_day.csv.")

df = pd.read_csv(DATA_PATH)

# Ensure numeric typing across monitored criteria pollutants
pollutant_cols = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'AQI']
for col in pollutant_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Retrieve unique sorted list of available Indian cities
city_options = sorted(df['City'].dropna().unique().tolist()) if 'City' in df.columns else ["Delhi", "Bengaluru", "Chennai"]
default_selected_city = "Delhi" if "Delhi" in city_options else city_options[0]

# ------------------------------------------------------------------------------
# 2. DASH APPLICATION INITIALIZATION & STYLING
# ------------------------------------------------------------------------------
app = Dash(__name__)
app.title = "India AQI Analytics Dashboard"

NAVY_HEADER = "#1e293b"
BG_CANVAS = "#f1f5f9"
CARD_BG = "#ffffff"
TEXT_COLOR = "#0f172a"
MUTED_TEXT = "#64748b"

# ------------------------------------------------------------------------------
# 3. DASHBOARD LAYOUT DEFINITION (Requirement 3.3)
# ------------------------------------------------------------------------------
app.layout = html.Div(
    style={
        'backgroundColor': BG_CANVAS,
        'minHeight': '100vh',
        'padding': '24px 32px',
        'fontFamily': 'Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif'
    },
    children=[
        # Title Banner Block
        html.Div(
            style={
                'backgroundColor': NAVY_HEADER,
                'padding': '22px 28px',
                'borderRadius': '12px',
                'marginBottom': '20px',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            },
            children=[
                html.H1(
                    "🇮🇳 India Air Quality Index (AQI) Dashboard",
                    style={'color': '#ffffff', 'margin': '0 0 6px 0', 'fontSize': '26px', 'fontWeight': '700'}
                ),
                html.P(
                    "Course: CUTM1018 | Domain 4: Environment & Climate | Author: Priyanka Barik (250301370201)",
                    style={'color': '#94a3b8', 'margin': '0', 'fontSize': '14px'}
                )
            ]
        ),

        # Filter Control Panel Card (Requirement 3.3: Filter/Selector)
        html.Div(
            style={
                'backgroundColor': CARD_BG,
                'padding': '18px 24px',
                'borderRadius': '10px',
                'marginBottom': '20px',
                'boxShadow': '0 1px 3px rgba(0, 0, 0, 0.08)',
                'display': 'flex',
                'alignItems': 'center',
                'gap': '20px',
                'flexWrap': 'wrap'
            },
            children=[
                html.Div([
                    html.Label(
                        "Select Monitored City:",
                        style={'fontWeight': '600', 'color': TEXT_COLOR, 'fontSize': '14px', 'marginBottom': '6px', 'display': 'block'}
                    ),
                    dcc.Dropdown(
                        id='city-filter-dropdown',
                        options=[{'label': c, 'value': c} for c in city_options],
                        value=default_selected_city,
                        clearable=False,
                        style={'width': '280px'}
                    )
                ]),
                html.Div([
                    html.Label(
                        "Select Focus Pollutant:",
                        style={'fontWeight': '600', 'color': TEXT_COLOR, 'fontSize': '14px', 'marginBottom': '6px', 'display': 'block'}
                    ),
                    dcc.Dropdown(
                        id='pollutant-filter-dropdown',
                        options=[{'label': p, 'value': p} for p in ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']],
                        value='PM2.5',
                        clearable=False,
                        style={'width': '220px'}
                    )
                ]),
                html.Div(
                    id='kpi-summary-container',
                    style={'marginLeft': 'auto', 'display': 'flex', 'gap': '16px'}
                )
            ]
        ),

        # Interactive Charts Grid (Requirement 3.3: At least 2 interactive Graph components)
        html.Div(
            style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(480px, 1fr))', 'gap': '20px'},
            children=[
                # Chart 1: Mean Criteria Pollutants Bar Chart
                html.Div(
                    style={
                        'backgroundColor': CARD_BG,
                        'padding': '18px',
                        'borderRadius': '10px',
                        'boxShadow': '0 1px 3px rgba(0, 0, 0, 0.08)'
                    },
                    children=[
                        dcc.Graph(id='bar-chart-criteria-pollutants')
                    ]
                ),

                # Chart 2: Selected Pollutant vs AQI Scatter Plot with OLS Trendline
                html.Div(
                    style={
                        'backgroundColor': CARD_BG,
                        'padding': '18px',
                        'borderRadius': '10px',
                        'boxShadow': '0 1px 3px rgba(0, 0, 0, 0.08)'
                    },
                    children=[
                        dcc.Graph(id='scatter-chart-pollutant-vs-aqi')
                    ]
                )
            ]
        )
    ]
)

# ------------------------------------------------------------------------------
# 4. REACTIVE CALLBACKS (Requirement 3.3: Callback updating charts)
# ------------------------------------------------------------------------------
@app.callback(
    [
        Output('bar-chart-criteria-pollutants', 'figure'),
        Output('scatter-chart-pollutant-vs-aqi', 'figure'),
        Output('kpi-summary-container', 'children')
    ],
    [
        Input('city-filter-dropdown', 'value'),
        Input('pollutant-filter-dropdown', 'value')
    ]
)
def update_aqi_dashboard(selected_city, selected_pollutant):
    city_df = df[df['City'] == selected_city].copy() if 'City' in df.columns else df.copy()

    total_days = len(city_df)
    avg_aqi = city_df['AQI'].mean() if 'AQI' in city_df.columns else 0.0
    peak_aqi = city_df['AQI'].max() if 'AQI' in city_df.columns else 0.0

    kpi_badges = [
        html.Div(
            style={'backgroundColor': '#e2e8f0', 'padding': '8px 14px', 'borderRadius': '6px', 'textAlign': 'center'},
            children=[
                html.Div("Days Monitored", style={'fontSize': '11px', 'color': MUTED_TEXT, 'fontWeight': '600'}),
                html.Div(f"{total_days:,}", style={'fontSize': '16px', 'color': TEXT_COLOR, 'fontWeight': '700'})
            ]
        ),
        html.Div(
            style={'backgroundColor': '#fee2e2', 'padding': '8px 14px', 'borderRadius': '6px', 'textAlign': 'center'},
            children=[
                html.Div("Mean AQI", style={'fontSize': '11px', 'color': '#991b1b', 'fontWeight': '600'}),
                html.Div(f"{avg_aqi:.1f}", style={'fontSize': '16px', 'color': '#b91c1c', 'fontWeight': '700'})
            ]
        ),
        html.Div(
            style={'backgroundColor': '#fef3c7', 'padding': '8px 14px', 'borderRadius': '6px', 'textAlign': 'center'},
            children=[
                html.Div("Peak AQI", style={'fontSize': '11px', 'color': '#92400e', 'fontWeight': '600'}),
                html.Div(f"{peak_aqi:.0f}", style={'fontSize': '16px', 'color': '#b45309', 'fontWeight': '700'})
            ]
        )
    ]

    # Chart 1: Bar Chart of Mean Pollutant Levels
    criteria_list = [p for p in ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'] if p in city_df.columns]
    mean_values = [city_df[p].mean() for p in criteria_list]

    bar_df = pd.DataFrame({'Pollutant': criteria_list, 'Mean_Concentration': mean_values})
    fig_bar = px.bar(
        bar_df,
        x='Pollutant',
        y='Mean_Concentration',
        color='Mean_Concentration',
        color_continuous_scale='Reds',
        labels={'Mean_Concentration': 'Mean Concentration (µg/m³)', 'Pollutant': 'Pollutant Species'},
        title=f"<b>Average Criteria Pollutant Levels: {selected_city}</b>"
    )
    fig_bar.update_layout(
        template='plotly_white',
        margin=dict(l=40, r=20, t=50, b=40),
        coloraxis_showscale=False
    )

    # Chart 2: Scatter Plot with OLS Regression Trendline
    clean_scatter_df = city_df[[selected_pollutant, 'AQI']].dropna()
    fig_scatter = px.scatter(
        clean_scatter_df,
        x=selected_pollutant,
        y='AQI',
        labels={selected_pollutant: f"{selected_pollutant} Concentration (µg/m³)", 'AQI': 'Composite AQI'},
        title=f"<b>{selected_pollutant} vs. AQI Correlation in {selected_city}</b>",
        trendline='ols',
        opacity=0.45,
        color_discrete_sequence=['#1e3a8a']
    )
    fig_scatter.update_layout(
        template='plotly_white',
        margin=dict(l=40, r=20, t=50, b=40)
    )

    return fig_bar, fig_scatter, kpi_badges

# ------------------------------------------------------------------------------
# 5. SERVER RUNTIME ENTRYPOINT
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)