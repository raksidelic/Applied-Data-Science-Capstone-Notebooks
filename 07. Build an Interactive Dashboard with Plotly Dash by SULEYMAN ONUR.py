# Import required packages
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

# Read the SpaceX Launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = Dash(__name__)

# Application layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),

    # Create an outer division
    html.Div([
        # Add a division
        html.Div([
            # Create a division for adding dropdown helper text for launch site
            html.Div(
                [
                    html.H2('Launch Site:', style={'margin-right': '1em'}),
                ]
            ),

            # The default select value is for ALL sites
            # Add a dropdown
            dcc.Dropdown(id='site-dropdown',
                         options=[
                             {'label': 'All Sites', 'value': 'ALL'},
                             {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                             {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                             {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                             {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                         ],
                         value='ALL',
                         placeholder="Select a Launch Site",
                         searchable=True,
                         style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
                         )
            # Place them next to each other using the division style
        ], style={'display': 'flex'}),
    ]),

    # Define the graphs and their order.

    # Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.P("Payload range (Kg):"),
    # Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=2500,
                    marks={0: '0',
                           2500: '2500',
                           5000: '5000',
                           7500: '7500',
                           10000: '10000'},
                    value=[min_payload, max_payload]),

    # Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
# Add computation to callback function and return graph
def get_pie_chart(site_dropdown):
    filtered_df = spacex_df
    if site_dropdown == 'ALL':
        fig = px.pie(filtered_df, values='class',
                     names='Launch Site',
                     title='Launch Success Rate by Launch Sites')
        return fig
    else:
        # Return the outcomes pie chart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == site_dropdown]
        filtered_df = filtered_df.groupby(['Launch Site', 'class']).size().reset_index(name='class-count')
        fig = px.pie(filtered_df, values='class-count', names='class', title=f'Launch Success Rate of {site_dropdown}')
        return fig


# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
# Add computation to callback function and return graph
def get_scatter_chart(site_dropdown, payload_slider):
    low, high = payload_slider
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    if site_dropdown == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for all sites')
        return fig
    else:
        # Return the outcomes scatter chart for a selected site
        filtered_df1 = filtered_df[filtered_df['Launch Site'] == site_dropdown]
        fig = px.scatter(filtered_df1, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for {site_dropdown}')
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
