"""
Solution for Week 11 Exercise #2
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1('Dice Dashboard!', style={'textAlign': 'center'}),
    html.Br(),
    html.Div(["Sides: ", dcc.Input(placeholder='Enter # sides...',
                                   id='num_sides', type='number', value=6)
              ],
             style={'width': '33%', 'display': 'inline-block'}
             ),
    html.Div(["Rolls: ", dcc.Input(placeholder='Enter # rolls...',
                                   id='num_rolls', type='number', value=250)
              ],
             style={'width': '33%', 'display': 'inline-block'}
             ),
    html.Div(["Trials: ", dcc.Input(placeholder='Enter # trials...',
                                    id='num_trials',
                                    type='number',
                                    value=5)
              ],
             style={'width': '33%', 'display': 'inline-block'}
             ),
    html.Div([dcc.Graph(id='rolls_fig')])
])

@app.callback(
    Output(component_id='rolls_fig', component_property='figure'),
    [Input(component_id='num_sides', component_property='value'),
     Input(component_id='num_rolls', component_property='value'),
     Input(component_id='num_trials', component_property='value')]
)
def update_output_div(num_sides, num_rolls, num_trials):
    
    df = pd.DataFrame({'roll' : np.arange(1,num_rolls+1)})
    
    trials = ["Trial " + str(trial + 1) for trial in range(num_trials)]
    for trial in trials:
        outcomes = np.random.choice(np.arange(1,num_sides+1), num_rolls)
        df[trial] = np.cumsum(outcomes) / df.roll 
    
    fig = px.line(df, x="roll", y=trials)
                      
    fig.update_layout(title="Running Mean Roll For A " + str(num_sides) + " Sided Die",
                      yaxis=dict(range=[.5,num_sides+.5]),
                      xaxis_title="Roll Number",
                      yaxis_title="Running Mean",
                      legend_title="Trial",
                      font=dict(
                          family="Courier New, monospace",
                          size=18,
                          color="RebeccaPurple")
                      )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)