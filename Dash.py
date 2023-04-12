# Imports and Global Variables
from dash import Dash, dcc, html, Input, Output, callback_context
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

# Code to make compatible with streamlit
import signal
import sys

# Import Existing Data
generation_df = pd.read_csv('ModuleData/electricity_generation.csv')
capacity_df = pd.read_csv('ModuleData/existing_and_new_capacity.csv')
costs_lineplot = pd.read_csv('ModuleData/costs_lineplot.csv')
emissions_lineplot = pd.read_csv('ModuleData/emissions_lineplot.csv')
df_nbuilt_hydro = pd.read_csv('ModuleData/df_nbuilt_hydro.csv')
df_nbuilt_vre = pd.read_csv('ModuleData/df_nbuilt_vre.csv')
df_nbuilt_fossil = pd.read_csv('ModuleData/df_nbuilt_fossil.csv')
map_df = pd.read_csv('ModuleData/transmission_map_data.csv')

# Colors
coal_color = '#343a40'
gas_color = '#6c757d'
hydro_color = '#2a648a'
solar_color = '#ef9226'
wind_color = '#8dc0cd'
nuclear_color = '#8d72b3'
other_color = '#6ba661'
battery_color = '#e7c41f'
pstorage_color = '#6a96ac'
trans_color = '#656d4a'
curtailment_color = '#c94f39'

# Checklist Options
checklist_options = ['Static Costs', 'Existing Tx', 'Planned Tx', 'Reference', 'Coal Ret. 55y',
                     'Coal Ret. 45y', 'Clean 80%']

# Data transformation for country bar plots
df_nbuilt = df_nbuilt_hydro.merge(
    df_nbuilt_vre, on=['load_zone', 'Scenario'], how='left').merge(
    df_nbuilt_fossil, on=['load_zone', 'Scenario'], how='left')[
    ['load_zone', 'Scenario', 'Hydro', 'Wind', 'SolarPV', 'SolarCSP', 'Battery', 'Coal', 'Gas']]
df_nbuilt = df_nbuilt.replace({'Optimal Tx (Reference)': 'Reference', 'Static costs': 'Static Costs',
                               'Coal ret. 55y': 'Coal Ret. 55y', 'Coal ret. 45y': 'Coal Ret. 45y'})

# Dictionary for transmission maps
legendgroupdict = {0: {'name': 'none', 'width': 0},
                   1: {'name': '1 - 100', 'width': 2},
                   2: {'name': '101 - 1000', 'width': 3},
                   3: {'name': '1001 - 2000', 'width': 4},
                   4: {'name': '2001 - 4000', 'width': 6},
                   5: {'name': '4001 - 6042', 'width': 8}}

# Data transformation for transmission maps
map_df['Existing Tx'] = map_df['Existing']
for scenario in checklist_options:
    legendgroup = []
    for row in range(map_df.shape[0]):
        if map_df.loc[row, scenario] == 0:
            legendgroup.append(0)
        elif (map_df.loc[row, scenario] >= 1) & (map_df.loc[row, scenario] <= 100):
            legendgroup.append(1)
        elif (map_df.loc[row, scenario] > 100) & (map_df.loc[row, scenario] <= 1000):
            legendgroup.append(2)
        elif (map_df.loc[row, scenario] > 1000) & (map_df.loc[row, scenario] <= 2000):
            legendgroup.append(3)
        elif (map_df.loc[row, scenario] > 2000) & (map_df.loc[row, scenario] <= 4000):
            legendgroup.append(4)
        else:
            legendgroup.append(5)
    map_df[scenario + '_legendgroup'] = legendgroup

# Dash Application Layout
app = Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])

app.layout = dbc.Container([
    html.Br(), html.Br(),
    dcc.Tabs([
        # Overview Tab
        dcc.Tab(label='Overview', children=[
            html.Div([
                html.Br(),
                html.P('This module provides readers with a way to interact and explore the results from this research.\
                        As such, all of the plots here can be manipulated to compare the various results \
                        and scenarios presented in the research.'),
                html.P('The checklists at the top of the tabs will filter in or out future development scenarios,\
                        plot legends can be interacted with the include or exclude specific energy types, all\
                        plots can be panned across by clicking and dragging on the x and y axes, and zoomed in on\
                        by clicking and dragging to select a specific area.\
                        At the top of each plot there is also a toolbar with a number of buttons, including a home\
                        that will reset the plot to its original state. Happy Exploring!')
            ]),
        ]),
        # Future New Capacity and Cost tab
        dcc.Tab(label='Future New Capacity and Cost', children=[
            html.Br(),
            html.Center(html.P('Scenario Selection', style={'font-weight': 'bold', 'font-size': 20}
                   )),
            dcc.Checklist(
                options=checklist_options,
                value=checklist_options,
                inline=True,
                id='tab_2_checklist_sync',
                inputStyle={'margin-right': '6px', 'margin-left': '20px'},
                style={'textAlign': 'center'}
            ),
            html.Center(dcc.Graph(
                id='barplot1'  # Existing and New Capacity (GW) bar plot
            )),
            html.Center(dcc.Graph(
                id='barplot2'  # Electricity Generation (TWh) bar plot
            )),
            html.Center(dcc.Graph(
                id='lineplots'  # Scenario Cost and Emissions line plot
            ))
        ]),
        # Country New-Build Capacity tab
        dcc.Tab(label='Country New-Build Capacity', children=[
            html.Br(),
            html.Center(html.P('Scenario Selection', style={'font-weight': 'bold', 'font-size': 20}
                               )),
            dcc.Checklist(options=checklist_options,
                          value=checklist_options,
                          inline=True,
                          id='tab_3_checklist_sync',
                          inputStyle={'margin-right': '6px', 'margin-left': '20px'},
                          style={'textAlign': 'center'}
                          ),
            html.Br(),
            html.Center(dcc.Graph(
                id='countries_barplot_combined'  # New Built Capacities by Country bar plot
            )),
            html.Br()
        ]),
        # Transmission maps tab
        dcc.Tab(label='Transmission Capacities', children=[
            html.Br(),
            html.Center(html.P('Scenario Selection', style={'font-weight': 'bold', 'font-size': 20}
                               )),
            dcc.Checklist(
                options=checklist_options,
                value=checklist_options,
                inline=True,
                id='tab_4_checklist_sync',
                inputStyle={'margin-right': '6px', 'margin-left': '20px'},
                style={'textAlign': 'center'}),
            html.Br(),
            html.Center(dcc.Graph(
                id='transmission_maps'
            ))
        ])
    ])
])


# End of module layout code

# Callbacks
# Callback to synchronize checklists across multiple tabs
@app.callback(
    Output("tab_2_checklist_sync", "value"),
    Output("tab_3_checklist_sync", "value"),
    Output("tab_4_checklist_sync", "value"),
    Input("tab_2_checklist_sync", "value"),
    Input("tab_3_checklist_sync", "value"),
    Input("tab_4_checklist_sync", "value"),
)
def sync_checklists(selected2, selected3, selected4):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "tab_3_checklist_sync":
        selected2 = selected3
        selected4 = selected3
    if input_id == "tab_4_checklist_sync":
        selected2 = selected4
        selected3 = selected4
    else:
        selected3 = selected2
        selected4 = selected2
    return selected2, selected3, selected4


# Callback to generate all of the plots in the 'Future New Capacity and Cost' tab
@app.callback(
    [Output('barplot1', 'figure'),
     Output('barplot2', 'figure'),
     Output('lineplots', 'figure')],
    Input('tab_2_checklist_sync', 'value'))
def plot_generation(tab_2_checklist):
    capacity_df_plot = capacity_df[capacity_df['scs'].isin(tab_2_checklist)]
    generation_df_plot = generation_df[generation_df['scs'].isin(tab_2_checklist)]

    # Add dummy columns for plotting combined plot
    capacity_df_plot["dummy_existing"] = 0
    capacity_df_plot["dummy_new"] = 0

    generation_df_plot["dummy_existing"] = 0
    generation_df_plot["dummy_new"] = 0

    ## New capacity
    # Flip this order to flip the year vs scenario grouping
    x1 = [list(capacity_df_plot.period),
          list(capacity_df_plot.scs)]

    # Existing gen capacity
    fig1 = go.Figure(go.Bar(x=x1, y=list(capacity_df_plot.Coal), name='Coal existing', marker_color=coal_color,
                            marker_pattern_shape="x", legendgroup='1', showlegend=False))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Gas), name='Gas existing', marker_color=gas_color,
                          marker_pattern_shape="x", legendgroup='1', showlegend=False))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Hydro), name='Hydro existing', marker_color=hydro_color,
                          marker_pattern_shape="x", legendgroup='1', showlegend=False))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Solar), name='Solar existing', marker_color=solar_color,
                          marker_pattern_shape="x", legendgroup='1', showlegend=False))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Wind), name='Wind existing', marker_color=wind_color,
                          marker_pattern_shape="x", legendgroup='1', showlegend=False))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Nuclear), name='Nuclear existing', marker_color=nuclear_color,
                          marker_pattern_shape="x", legendgroup='1', showlegend=False))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Other), name='Other existing', marker_color=other_color,
                          marker_pattern_shape="x", legendgroup='1', showlegend=False))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.PStorage), name='Pumped storage<br>existing',
                          marker_color=pstorage_color, marker_pattern_shape="x", legendgroup='1', showlegend=False))

    # New gen capacity
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Coal_new), name='Coal new', marker_color=coal_color))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Gas_new), name='Gas new', marker_color=gas_color))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Hydro_new), name='Hydro new', marker_color=hydro_color))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Solar_new), name='Solar new', marker_color=solar_color))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Wind_new), name='Wind new', marker_color=wind_color))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Other_new), name='Other new', marker_color=other_color))
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.Battery), name='Battery new', marker_color=battery_color))

    # Adding dummy markers
    fig1.add_trace(go.Bar(x=x1, y=list(capacity_df_plot.dummy_existing), name='Existing<br> capacity',
                          marker_color='white', marker_pattern_shape="x", legendgroup='1', showlegend=True))

    # Remove white lines separating elements of bars
    fig1.update_traces(marker_line_width=0,
                       selector=dict(type="bar"))

    fig1.update_layout(barmode="relative", font=dict(size=12),
                       width=1000, height=600, plot_bgcolor='white',  # showlegend=False)
                       legend=dict(yanchor="top", y=0.81, xanchor="left", x=1.00, traceorder='grouped+reversed'),
                       margin=dict(l=0, r=0, b=0, t=10))

    fig1['layout']['yaxis']['title'] = 'Existing and new capacity (GW)'

    # Change grid color and axis colors
    fig1.update_yaxes(gridcolor='#f5f5f5')  # linewidth=2, linecolor='black',
    fig1.update_xaxes(tickangle=270)

    ## Energy generation
    # Flip this order to flip the year vs scenario grouping
    x2 = [list(generation_df_plot.period),
          list(generation_df_plot.scs)]

    fig2 = go.Figure(
        go.Bar(x=x2, y=list(generation_df_plot.Trans_loss), name='Transmission <br>loss', marker_color=trans_color))
    fig2.add_trace(
        go.Bar(x=x2, y=list(generation_df_plot.PStorage), name='Pumped <br>storage', marker_color=pstorage_color))
    fig2.add_trace(go.Bar(x=x2, y=list(generation_df_plot.Battery), name='Battery', marker_color=battery_color))
    fig2.add_trace(go.Bar(x=x2, y=list(generation_df_plot.Coal), name='Coal', marker_color=coal_color))
    fig2.add_trace(go.Bar(x=x2, y=list(generation_df_plot.Gas), name='Gas', marker_color=gas_color))
    fig2.add_trace(go.Bar(x=x2, y=list(generation_df_plot.Nuclear), name='Nuclear', marker_color=nuclear_color))
    fig2.add_trace(go.Bar(x=x2, y=list(generation_df_plot.Hydro), name='Hydro', marker_color=hydro_color))
    fig2.add_trace(go.Bar(x=x2, y=list(generation_df_plot.Solar), name='Solar', marker_color=solar_color))
    fig2.add_trace(go.Bar(x=x2, y=list(generation_df_plot.Wind), name='Wind', marker_color=wind_color))
    fig2.add_trace(go.Bar(x=x2, y=list(generation_df_plot.Other), name='Other', marker_color=other_color))
    fig2.add_trace(
        go.Bar(x=x2, y=list(generation_df_plot.Curtailment), name='Curtailment', marker_color=curtailment_color))

    # Remove white lines separating elements of bars
    fig2.update_traces(marker_line_width=0,
                       selector=dict(type="bar"))

    fig2.update_layout(barmode="relative", yaxis_title="Electricity generation (TWh)", font=dict(size=12),
                       width=1000, height=500, plot_bgcolor='white',  # showlegend=False)
                       legend=dict(yanchor="top", y=0.91, xanchor="left", x=1.00, traceorder='reversed'),
                       margin=dict(l=0, r=0, b=0, t=0))

    # Change grid color and axis colors
    fig2.update_yaxes(gridcolor='#f5f5f5')
    fig2.update_xaxes(tickangle=270)

    # Costs and Emissions Plots
    line_style_dict = {'Static Costs': {'Color': '#e09f3e', 'Dash': 'solid', 'Legend Group': '0'},
                       'Existing Tx': {'Color': '#90be6d', 'Dash': 'dash', 'Legend Group': '1'},
                       'Planned Tx': {'Color': '#4d908e', 'Dash': 'dash', 'Legend Group': '2'},
                       'Reference': {'Color': '#766A00', 'Dash': 'solid', 'Legend Group': '3'},
                       'Coal Ret. 55y': {'Color': '#343a40', 'Dash': 'dashdot', 'Legend Group': '4'},
                       'Coal Ret. 45y': {'Color': '#766A00', 'Dash': 'dashdot', 'Legend Group': '5'},
                       'Clean 80%': {'Color': '#277da1', 'Dash': 'dot', 'Legend Group': '6'}}

    fig3 = make_subplots(rows=1, cols=2)

    for selected in tab_2_checklist:
        fig3.add_trace(go.Scatter(x=costs_lineplot['period'], y=costs_lineplot[selected], name=selected,
                                  legendgroup=line_style_dict[selected]['Legend Group'],
                                  line=dict(color=line_style_dict[selected]['Color'],
                                            dash=line_style_dict[selected]['Dash'])), row=1, col=1)
        fig3.add_trace(go.Scatter(x=emissions_lineplot['period'], y=emissions_lineplot[selected], name=selected,
                                  legendgroup=line_style_dict[selected]['Legend Group'], showlegend=False,
                                  line=dict(color=line_style_dict[selected]['Color'],
                                            dash=line_style_dict[selected]['Dash'])), row=1, col=2)

    fig3.update_xaxes(tickangle=270)
    fig3.update_yaxes(gridcolor='#f5f5f5')
    fig3.update_layout(height=500, width=1000, plot_bgcolor='white', margin=dict(l=0, r=0, b=50, t=20))
    fig3.update_yaxes(title_text="Costs (USD per MWh)", row=1, col=1)
    fig3.update_yaxes(title_text=r'GHG Emissions (MtCO$_{2}$)', row=1, col=2)

    return fig1, fig2, fig3


# Callback to generate the country bar plot in tab 3
@app.callback(
    Output('countries_barplot_combined', 'figure'),
    Input('tab_2_checklist_sync', 'value'))
def update_fig4(tab_2_checklist):
    selected_scenario_data = df_nbuilt[df_nbuilt['Scenario'].isin(tab_2_checklist)]

    # Create multi level index
    x = [
        list(selected_scenario_data.load_zone),
        list(selected_scenario_data.Scenario)
    ]
    # Add values of each power type for each observation
    fig4 = go.Figure(go.Bar(x=x, y=list(selected_scenario_data.Wind), name='Wind', marker_color=wind_color))
    fig4.add_trace(go.Bar(x=x, y=list(selected_scenario_data.SolarPV), name='Solar', marker_color=solar_color))
    fig4.add_trace(go.Bar(x=x, y=list(selected_scenario_data.Battery), name='Battery', marker_color=battery_color))
    fig4.add_trace(go.Bar(x=x, y=list(selected_scenario_data.Coal), name='Coal', marker_color=coal_color))
    fig4.add_trace(go.Bar(x=x, y=list(selected_scenario_data.Gas), name='Gas', marker_color=gas_color))
    fig4.add_trace(go.Bar(x=x, y=list(selected_scenario_data.Hydro), name='Hydro', marker_color=hydro_color))

    fig4.update_layout(barmode="stack", yaxis_title="New-built capacities (GW)", font=dict(size=11),
                       width=1300, height=800,
                       legend=dict(yanchor="top", y=0.98, xanchor="left", x=1.01))
    fig4.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)', })
    fig4.update_yaxes(showline=True, linewidth=0.2, linecolor='black', mirror=True, showgrid=True,
                      gridwidth=0.2, gridcolor='lightgrey')
    fig4.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, tickangle=270)

    return fig4

# Callback to generate all of the transmission maps in tab 4
@app.callback(
    Output('transmission_maps', 'figure'),
    Input('tab_4_checklist_sync', 'value'))
def update_fig4(tab_4_checklist):
    # Generate a plot framework with the correct dimensions, and appropriate titles
    maps = make_subplots(rows=round((len(tab_4_checklist) / 2) + 0.1), cols=2,
                         subplot_titles=tab_4_checklist,
                         vertical_spacing=0.02,
                         specs=[[{"type": "mapbox"}, {"type": "mapbox"}]] * round((len(tab_4_checklist) / 2) + 0.1))

    for scenario in tab_4_checklist:
        for row in range(map_df.shape[0]):
            # Generate the coordinate endpoints for plotting
            lat = []
            lon = []
            lat.append(map_df.loc[row, 'y_start'])
            lat.append(map_df.loc[row, 'y_end'])
            lon.append(map_df.loc[row, 'x_start'])
            lon.append(map_df.loc[row, 'x_end'])

            legend_group = map_df.loc[row, scenario + '_legendgroup']
            # Add lines to their corresponding subplots
            maps.add_trace(go.Scattermapbox(
                mode="markers+lines",
                lon=lon,
                lat=lat,
                name=legendgroupdict[legend_group]['name'],
                legendgroup=int(legend_group),
                showlegend=False,
                line={'width': legendgroupdict[legend_group]['width'],
                      'color': '#96c99f'},
                marker={'size': 4}),
                row=tab_4_checklist.index(scenario) // 2 + 1,
                col=tab_4_checklist.index(scenario) % 2 + 1)

    # Adding dummy markers
    for i in range(6):
        if i == 0:
            continue
        maps.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[0, 0],
            lat=[0, 0],
            name=legendgroupdict[i]['name'],
            legendgroup=int(i),
            showlegend=True,
            line={'width': legendgroupdict[i]['width'],
                  'color': '#96c99f'}
        ))

    # Finalize the formatting for all of the subplots
    maps.update_mapboxes(
        center=dict(lat=-17, lon=26),
        zoom=3,
        style='carto-positron')
    maps.update_layout(
        legend_title_text='Transmission (MW)',
        margin={'l': 0, 't': 30, 'b': 0, 'r': 10},
        width=950,
        height=500 * round((len(tab_4_checklist) / 2) + 0.1))
    return maps


if __name__ == '__main__':
    app.run_server(debug=True)
    def default_handler(signum, frame):
      print(f"Received signal {signum}. Exiting.")
      sys.exit(0)
    signal.signal(signal.SIGTERM, default_handler)
