# =========================
# Imports
# =========================
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# =========================
# Daten laden und vorbereiten
# =========================
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
spacex_df = pd.read_csv(URL)

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# =========================
# Dash App initialisieren
# =========================
app = Dash(__name__)

# =========================
# Dropdown Optionen definieren
# =========================
launch_sites = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site}
    for site in spacex_df['Launch Site'].unique()
]

# =========================
# Layout definieren
# =========================
app.layout = html.Div(children=[

    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    dcc.Dropdown(
        id='site-dropdown',
        options=launch_sites,
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    html.Br(),

    dcc.Graph(id='success-pie-chart'),

    html.Br(),

    html.P("Payload range (Kg):"),

    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=max_payload,
        step=1000,
        marks={
            0: '0',
            int(max_payload/2): str(int(max_payload/2)),
            int(max_payload): str(int(max_payload))
        },
        value=[min_payload, max_payload]
    ),

    html.Br(),

    dcc.Graph(id='success-payload-scatter-chart')
])

# =========================
# Callback: Pie Chart
# =========================
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):

    if selected_site == 'ALL':
        df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()

        fig = px.pie(
            df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        df = df['class'].value_counts().reset_index()
        df.columns = ['class', 'count']

        fig = px.pie(
            df,
            values='count',
            names='class',
            title=f'Success vs Failure for {selected_site}'
        )

    return fig

# =========================
# Callback: Scatter Plot
# =========================
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(selected_site, payload_range):

    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site != 'ALL':
        filtered_df = filtered_df[
            filtered_df['Launch Site'] == selected_site
        ]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload vs. Launch Outcome'
    )

    return fig

# =========================
# App starten (Script-Modus)
# =========================
if __name__ == '__main__':
    app.run(debug=True)