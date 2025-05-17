import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from proc import process_data
from functools import cache

@cache
def geolocate_ip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,lat,lon", timeout=2).json()
        if res["status"] == "success":
            return res["lat"], res["lon"]
    except:
        pass
    return None, None

app = dash.Dash(__name__)
ip_data, endpoint_data, traffic, device_data, status_data = process_data()

app.layout = html.Div([
    html.Div([
        html.H2("Dashboard", className="sidebar-title"),
        html.Ul([
            html.Li(html.A("Traffic & Usage Patterns", href="#traffic")),
            html.Li(html.A("Errors & Status Monitoring", href="#status")),
            html.Li(html.A("Geographic or User-Agent Data", href="#geo")),
            html.Li(html.A("Security Related Insights", href="#security")),
        ], className="nav-links")
    ], className="sidebar"),
    
    html.Div([
        html.H1("NGINX/ACM Hackathon 2025", style={'textAlign': 'center'}),
    html.Div([
    html.Div([
        html.Label("Maximum number of IPs to show:"),
    dcc.Slider(
        id='max-ips-slider',
        min=5,
        max=30,
        step=5,
        value=10,
        marks={i: str(i) for i in range(1, 31) if i % 5 == 0},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
        dcc.Graph(id='ip-pie-chart', className="graph"),
    ], className="data"),

    html.Div([
        html.Label("Maximum number of endpoints to show:"),
        dcc.Slider(
            id='max-endpoints-slider',
            min=1,
            max=10,
            step=1,
            value=5,
            marks={i: str(i) for i in range(1, 21)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        dcc.Graph(id='endpoint-bar-chart', className="graph"),
    ], className="data"),

    html.Div([
    html.Label("Maximum number of devices to show:"),
    dcc.Slider(
        id='max-devices-slider',
        min=5,
        max=20,
        step=5,
        value=10,
        marks={i: str(i) for i in range(1, 21) if i % 5 == 0},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    dcc.Graph(id='device-pie-chart', className="graph")
], className="data"),


    ], className="allData", id="traffic"),

    html.Div([
        html.Div([
        dcc.Graph(id='status-pie-chart', className="graph")
        ], className="data"),
    ], className="allData", id="status"),

    html.Div([
        html.Div([
            html.Label("Number of top IPs to plot on map:"),
            dcc.Slider(
                id='top-n-ip-slider',
                min=1,
                max=50,
                step=1,
                value=10,
                marks={i: str(i) for i in range(1, 51)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            dcc.Graph(id='ip-map-chart', className="graph")], className="data")
    ], className="allData", id="geo"),

])], className="main-content")

@app.callback(
    Output('ip-pie-chart', 'figure'),
    Output('endpoint-bar-chart', 'figure'),
    Output('ip-map-chart', 'figure'),
    Output('device-pie-chart', 'figure'),
    Output('status-pie-chart', 'figure'),
    Input('max-ips-slider', 'value'),
    Input('max-endpoints-slider', 'value'),
    Input('top-n-ip-slider', 'value'),
    Input('max-devices-slider', 'value')

)
def update_charts(max_ips, max_endpoints, top_n_ips, max_devices):

    # --- PIE CHART ---
    df_ip = pd.DataFrame(list(ip_data.items()), columns=["IP Address", "Cumulative Size (Bytes)"])
    df_ip = df_ip.sort_values("Cumulative Size (Bytes)", ascending=False).head(max_ips)


    pie_fig = px.pie(
        df_ip,
        names="IP Address",
        values="Cumulative Size (Bytes)",
        title=f"Top {max_ips} IP Traffic Distribution",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    pie_fig.update_traces(textposition="inside", textinfo='label+percent')
    
    df_status = pd.DataFrame(list(status_data.items()), columns=["Status Code", "Count"])
    status_pie = px.pie(
        df_status,
        names="Status Code",
        values="Count",
        title="Status Code Distribution",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    status_pie.update_traces(textposition="inside", textinfo='label+percent')

    # --- BAR CHART ---
    sorted_endpoints = sorted(endpoint_data.items(), key=lambda x: x[1][0] + x[1][1], reverse=True)
    top_endpoints = sorted_endpoints[:max_endpoints]

    endpoints = [ep for ep, _ in top_endpoints]
    success_counts = [ep_data[0] for _, ep_data in top_endpoints]
    failure_counts = [ep_data[1] for _, ep_data in top_endpoints]

    bar_fig = go.Figure(data=[
        go.Bar(name='Successes', x=endpoints, y=success_counts, marker_color='green', offsetgroup=0),
        go.Bar(name='Failures', x=endpoints, y=failure_counts, marker_color='red', offsetgroup=1),
    ])
    bar_fig.update_layout(
        barmode='group',
        title="Endpoints (Success v Fail)",
        yaxis_title="Number of Requests",
        xaxis_title="Endpoints",
        bargap=0.3
    )

    # --- MAP CHART ---
    sorted_traffic = sorted(traffic.items(), key=lambda x: x[1], reverse=True)
    top_traffic = sorted_traffic[:top_n_ips]

    geo_data = []
    for ip, count in top_traffic:
        lat, lon = geolocate_ip(ip)
        if lat is not None and lon is not None:
            geo_data.append({
                "IP": ip,
                "Traffic": count,
                "Latitude": lat,
                "Longitude": lon
            })

    df_geo = pd.DataFrame(geo_data)

    if df_geo.empty:
        map_fig = go.Figure()
        map_fig.update_layout(title="No IP locations available", mapbox_style="open-street-map")
    else:
        map_fig = px.scatter_map(
            df_geo,
            lat="Latitude",
            lon="Longitude",
            size="Traffic",
            hover_name="IP",
            color="Traffic",
            size_max=30,
            zoom=2,
            map_style="open-street-map",
            color_continuous_scale=px.colors.sequential.Bluered
        )
        map_fig.update_layout(
            title=f"Top {top_n_ips} IP Locations by Traffic",
            margin={"r":0, "t":30, "l":0, "b":0}
        )
    # Sort and limit to top devices
    sorted_devices = sorted(device_data.items(), key=lambda x: x[1], reverse=True)
    top_devices = sorted_devices[:max_devices]

    df_device = pd.DataFrame(top_devices, columns=["Device", "Count"])
    device_fig = px.pie(
        df_device,
        names="Device",
        values="Count",
        title=f"Top {max_devices} Device Usage Distribution",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    device_fig.update_traces(textposition="inside", textinfo='label+percent') 
    
    # styling the figures
    figs = [pie_fig, bar_fig, map_fig, device_fig, status_pie]
    for fig in figs:
        fig.update_layout(paper_bgcolor='#2c3155',
                          font=dict(color="#fff"),
                          legend=dict(orientation="h"))
    bar_fig.update_layout(legend=dict(orientation="v"))

    return pie_fig, bar_fig, map_fig, device_fig, status_pie

if __name__ == '__main__':
    app.run(debug=True)
