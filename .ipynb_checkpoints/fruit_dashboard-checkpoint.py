"""
Solution to exercise #1 on Week 11
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# pandas dataframe to html table
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

app = dash.Dash(__name__, external_stylesheets=stylesheet)

server = app.server

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div([
    html.H1('Your Fruit Dashboard!', style={'textAlign': 'center'}),
    html.Div([html.H4('Number of rows to display:'),
              dcc.Slider(id="num_row_slider", min=0, max=min(10, len(df)), value=6,
              marks={i:str(i) for i in range(len(df)+1)}),
              html.H4('Select fruit to display:'),
              dcc.Checklist(options=[{'label': 'Apples', 'value': 'Apples'},
                                     {'label': 'Bananas', 'value': 'Bananas'},
                                     {'label': 'Oranges', 'value': 'Oranges'}],
                           id="fruit_select_checklist",
                           value=['Apples', 'Oranges', 'Bananas']),
             html.H4('Sort table by:'),
             dcc.Dropdown(options=[{'label': 'Fruit', 'value': 'Fruit'},
                                    {'label': 'Amount', 'value': 'Amount'},
                                    {'label': 'City', 'value': 'City'}],
                           id='sort_by_dropdown',
                           value='Fruit')],
             style={'width': '49%', 'display': 'inline-block'}),
    html.Div(html.Div(id="df_div"),
             style={'width': '49%', 'display': 'inline-block', 'float': 'right'})
    ])

# Update the table
@app.callback(
    Output(component_id='df_div', component_property='children'),
    [Input(component_id='num_row_slider', component_property='value'),
     Input(component_id='fruit_select_checklist', component_property='value'),
     Input(component_id='sort_by_dropdown', component_property='value')]
)
def update_table(num_rows_to_show, fruits_to_display, sort_by):
    x = df[df.Fruit.isin(fruits_to_display)].sort_values(sort_by, ascending=(sort_by != "Amount"))
    return generate_table(x, max_rows=num_rows_to_show)

# Update the slider max
@app.callback(
    Output(component_id='num_row_slider', component_property='max'),
    [Input(component_id='fruit_select_checklist', component_property='value')]
)
def update_slider(fruits_to_display):
    x = df[df.Fruit.isin(fruits_to_display)]
    return min(10, len(x))


if __name__ == '__main__':
    app.run_server(debug=True)
    





