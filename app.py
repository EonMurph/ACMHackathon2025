import dash
from dash import html, dcc, Input, Output, dash_table
from user_agents import parse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from proc import process_data
from functools import cache
from datetime import date, datetime
from traffic_analysis import get_requests_from_date


@cache
def geolocate_ip(ip):
    """
    Given an ip return a tuple of coordinates
    """
    try:
        res = requests.get(
            f'http://ip-api.com/json/{ip}?fields=status,message,lat,lon', timeout=2
        ).json()
        if res['status'] == 'success':
            return res['lat'], res['lon']
    except:
        pass
    return None, None

def build_log_table_df(request_json, ip_picked="all"):
    log_rows = []
    for ip, requests in request_json.items():
        if ip_picked == "all" or ip == ip_picked:
            for req in requests:
                row = {
                    'IP Address': ip,
                    'Date': req.get('date'),
                    'Request': req.get('request').split(" ")[0].strip("\""),
                    'Return Code': req.get('return_code'),
                    'Response Size': req.get('response_size'),
                    'User Agent': parse(req.get('user_agent')).browser.family
                }
                log_rows.append(row)
    return pd.DataFrame(log_rows)


def get_request_timeseries(request_json, ip_picked="all"):
    all_requests = []
    for ip, requests in request_json.items():
        if ip == ip_picked or ip_picked=="all":
            for req in requests:
                if isinstance(req, dict) and 'date' in req and isinstance(req['date'], str):
                    try:
                        dt = datetime.strptime(req['date'], "%d/%b/%Y:%H:%M:%S")
                        all_requests.append(dt)
                    except ValueError:
                        pass

    if not all_requests:
        return pd.DataFrame(columns=['Time', 'Request Count'])

    df = pd.DataFrame({'Time': all_requests})
    df.set_index('Time', inplace=True)
    timeseries = df.resample('h').size().rename("Request Count").reset_index()
    return timeseries

def plot_request_timeseries(timeseries_df):
    return px.line(
        timeseries_df,
        x='Time',
        y='Request Count',
        title='Request Volume Over Time',
        markers=True
    )

app = dash.Dash(__name__)


app.layout = html.Div(
    [
        # sidebar
        html.Div(
            [
                html.Div(
                    [
                        html.H2('Dashboard', className='sidebar-title'),
                        html.Ul(
                            [
                                html.Li(
                                    html.A('Traffic & Usage Patterns', href='#traffic')
                                ),
                                html.Li(
                                    html.A('Errors & Status Monitoring', href='#status')
                                ),
                                html.Li(
                                    html.A('Geographic or User-Agent Data', href='#geo')
                                ),
                            ],
                            className='nav-links',
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label('Filters:'),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    value='all',
                                    id='ip-picker',
                                ),
                                dcc.DatePickerRange(
                                    id='date-picker',
                                    min_date_allowed=date(2025, 4, 17),
                                    max_date_allowed=date(2025, 5, 2),
                                    initial_visible_month=date(2025, 4, 17),
                                    start_date=date(2025, 4, 17),
                                    end_date=date(2025, 5, 2),
                                ),
                            ],
                            className='filters',
                        ),
                    ],
                ),
            ],
            className='sidebar',
        ),
        html.Div(
            [
                html.H1('NGINX/ACM Hackathon 2025', style={'textAlign': 'center'}),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label('Maximum number of IPs to show:'),
                                dcc.Slider(
                                    id='max-ips-slider',
                                    min=5,
                                    max=30,
                                    step=5,
                                    value=10,
                                    marks={
                                        i: str(i) for i in range(1, 31) if i % 5 == 0
                                    },
                                    tooltip={
                                        'placement': 'bottom',
                                        'always_visible': True,
                                    },
                                ),
                                dcc.Graph(id='ip-pie-chart', className='graph'),
                            ],
                            className='data',
                        ),
                        html.Div(
                            [
                                html.Label('Maximum number of devices to show:'),
                                dcc.Slider(
                                    id='max-devices-slider',
                                    min=5,
                                    max=20,
                                    step=5,
                                    value=10,
                                    marks={
                                        i: str(i) for i in range(1, 21) if i % 5 == 0
                                    },
                                    tooltip={
                                        'placement': 'bottom',
                                        'always_visible': True,
                                    },
                                ),
                                dcc.Graph(id='device-pie-chart', className='graph'),
                            ],
                            className='data',
                        ),
                    ],
                    className='allData',
                    id='traffic',
                ),
                html.Div([
                    html.Div([
                    html.H2("Request Volume Over Time", style={'textAlign': 'center'}),
                    dcc.Graph(id='request-time-chart', className="graph")], className="data")
                ], className="allData", id="request-timeseries"),

                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id='status-pie-chart', className='graph')],
                            className='data',
                        ),
                        html.Div(
                            [
                                html.Label('Maximum number of endpoints to show:'),
                                dcc.Slider(
                                    id='max-endpoints-slider',
                                    min=1,
                                    max=10,
                                    step=1,
                                    value=5,
                                    marks={i: str(i) for i in range(1, 21)},
                                    tooltip={
                                        'placement': 'bottom',
                                        'always_visible': True,
                                    },
                                ),
                                dcc.Graph(id='endpoint-bar-chart', className='graph'),
                            ],
                            className='data',
                        ),
                    ],
                    className='allData',
                    id='status',
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label('Number of top IPs to plot on map:'),
                                dcc.Slider(
                                    id='top-n-ip-slider',
                                    min=1,
                                    max=50,
                                    step=1,
                                    value=10,
                                    marks={i: str(i) for i in range(1, 51)},
                                    tooltip={
                                        'placement': 'bottom',
                                        'always_visible': True,
                                    },
                                ),
                                dcc.Graph(id='ip-map-chart', className='graph'),
                            ],
                            className='data',
                        )
                    ],
                    className='allData',
                    id='geo',
                ),
                html.Div([
                html.Div([
                html.H2("Detailed Request Logs", style={'textAlign': 'center'}),
                dash.dash_table.DataTable(
                    id='log-table',
                    columns=[
                        {"name": col, "id": col} for col in
                        ['IP Address', 'Date', 'Request', 'Return Code', 'Response Size', 'User Agent']
                    ],
                    style_table={'overflowX': 'auto', 'maxHeight': '500px', 'overflowY': 'scroll'},
                    style_header={'backgroundColor': '#1a1c2c', 'color': 'white', 'fontWeight': 'bold'},
                    style_cell={'backgroundColor': '#2c3155', 'color': 'white', 'textAlign': 'left'},
                    page_size=20
                )
            ], className='data')
            ], className='allData', id='log-view'),
            ]
        ),
    ],
    className='main-content',
)


@app.callback(
    # have to be in this order
    Output('ip-pie-chart', 'figure'),
    Output('endpoint-bar-chart', 'figure'),
    Output('ip-map-chart', 'figure'),
    Output('device-pie-chart', 'figure'),
    Output('status-pie-chart', 'figure'),
    Output('request-time-chart', 'figure'),
    Output('ip-picker', 'options'),
    Output('log-table', 'data'),

    Input('max-ips-slider', 'value'),
    Input('max-endpoints-slider', 'value'),
    Input('top-n-ip-slider', 'value'),
    Input('max-devices-slider', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('ip-picker', 'value'),
)
def update_charts(
    max_ips, max_endpoints, top_n_ips, max_devices, start_date, end_date, ip_picked
):
    # cumulative bytes per ip address response pie chart

    # dictionaries from processing the data
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)
    ip_data, endpoint_data, traffic, device_data, status_data, request_json = process_data(
        get_requests_from_date(start_date, end_date), start_date, end_date, ip_picked
    )

    df_ip = pd.DataFrame(
        list(ip_data.items()), columns=['IP Address', 'Cumulative Size (Bytes)']
    )
    df_ip = df_ip.sort_values('Cumulative Size (Bytes)', ascending=False).head(max_ips)
    ip_pie_fig = px.pie(
        df_ip,
        names='IP Address',
        values='Cumulative Size (Bytes)',
        title=f'Top {max_ips} IPs (Cumulative Response Size in Bytes)',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    ip_pie_fig.update_traces(textposition='inside', textinfo='label+percent')

    # status code pie chart
    df_status = pd.DataFrame(
        list(status_data.items()), columns=['Status Code', 'Count']
    )
    status_pie_fig = px.pie(
        df_status,
        names='Status Code',
        values='Count',
        title='Status Code Distribution',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    status_pie_fig.update_traces(textposition='inside', textinfo='label+percent')

    # endpoints sucesses v failures
    sorted_endpoints = sorted(
        endpoint_data.items(), key=lambda x: x[1][0] + x[1][1], reverse=True
    )
    top_endpoints = sorted_endpoints[:max_endpoints]

    endpoints = [ep for ep, _ in top_endpoints]
    success_counts = [ep_data[0] for _, ep_data in top_endpoints]
    failure_counts = [ep_data[1] for _, ep_data in top_endpoints]

    endpoint_bar_fig = go.Figure(
        data=[
            go.Bar(
                name='Successes',
                x=endpoints,
                y=success_counts,
                marker_color='green',
                offsetgroup=0,
            ),
            go.Bar(
                name='Failures',
                x=endpoints,
                y=failure_counts,
                marker_color='red',
                offsetgroup=1,
            ),
        ]
    )
    endpoint_bar_fig.update_layout(
        barmode='group',
        title='Endpoints (Success v Fail)',
        yaxis_title='Number of Requests',
        xaxis_title='Endpoints',
        bargap=0.3,
    )

    # map of web traffic to specific ip
    sorted_traffic = sorted(traffic.items(), key=lambda x: x[1], reverse=True)
    top_traffic = sorted_traffic[:top_n_ips]

    geo_data = []
    for ip, count in top_traffic:
        lat, lon = geolocate_ip(ip)
        if lat is not None and lon is not None:
            geo_data.append(
                {'IP': ip, 'Traffic': count, 'Latitude': lat, 'Longitude': lon}
            )

    df_geo = pd.DataFrame(geo_data)
    log_df = build_log_table_df(request_json, ip_picked)

    if df_geo.empty:
        map_fig = go.Figure()
        map_fig.update_layout(
            title='No IP locations available', mapbox_style='open-street-map'
        )
    else:
        map_fig = px.scatter_map(
            df_geo,
            lat='Latitude',
            lon='Longitude',
            size='Traffic',
            hover_name='IP',
            color='Traffic',
            size_max=30,
            zoom=2,
            map_style='open-street-map',
            color_continuous_scale=px.colors.sequential.Bluered,
        )
        map_fig.update_layout(
            title=f'Top {top_n_ips} IP Locations by Traffic',
            margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
        )

    # device distribution pie chart
    sorted_devices = sorted(device_data.items(), key=lambda x: x[1], reverse=True)
    top_devices = sorted_devices[:max_devices]

    df_device = pd.DataFrame(top_devices, columns=['Device', 'Count'])
    device_pie_fig = px.pie(
        df_device,
        names='Device',
        values='Count',
        title=f'Top {max_devices} Device Usage Distribution',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    device_pie_fig.update_traces(textposition='inside', textinfo='label+percent')
    
    # request timeseries graph
    timeseries_df = get_request_timeseries(request_json,ip_picked)
    time_fig = plot_request_timeseries(timeseries_df)

    # styling the figures
    figs = [ip_pie_fig, endpoint_bar_fig, map_fig, device_pie_fig, status_pie_fig, time_fig]
    for fig in figs:
        fig.update_layout(
            paper_bgcolor='#2c3155',
            font=dict(color='#fff'),
            legend=dict(orientation='h'),
        )

    # overwrite so legend is vertically adjacent (avoids overlapping)
    endpoint_bar_fig.update_layout(legend=dict(orientation='v'))

    ip_options = [{'label': 'All IPs', 'value': 'all'}]
    ip_options += [{'label': ip, 'value': ip} for ip in ip_data.keys()]

    # returning all the figures, append to end of the list
    return (
        ip_pie_fig,
        endpoint_bar_fig,
        map_fig,
        device_pie_fig,
        status_pie_fig,
        time_fig,
        ip_options[:20],
        log_df.to_dict('records')
    )


if __name__ == '__main__':
    app.run(debug=True)
