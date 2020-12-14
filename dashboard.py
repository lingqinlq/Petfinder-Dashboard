import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import datetime

df = pd.read_csv('dog.csv')

intro1 = 'The data come from latest 10,000 adoptable dogs from petfinder.com.' \
         'Thanks to the website provides developer API. '
intro2 = 'First you can choose your state and the size of dog to overview. The' \
         'chart will show the number of adoptable dogs in breeds (top 10 number). Then you '
intro3 = 'can choose more filters including age, gender, and breed.' \
         'The table will give you the detailed information of each adoptable dog' \
         'based on your filter.'
intro4 = 'By clicking the name of dog, you will enter to the' \
         'adopt page on petfinder.com. Good luck to find your ideal dog!'

df_withphoto = df[df['photos'].notnull()]
df_withphoto = df_withphoto[df_withphoto['country'] == 'US']

df_table = df_withphoto[['photos', 'pet_name', 'published_at', 'breeds',
                         'colors', 'age', 'gender', 'size', 'coat', 'spayed_neutered',
                         'shots_current', 'contact_email', 'contact_phone',
                         'state', 'city', 'postcode', 'url']]
df_table.reset_index(drop=True, inplace=True)

# convert published_at column in df_table to datetime format
df_table['published_at'] = df_table['published_at'].apply(lambda x: x[0:10]+' ' +x[11:19])
df_table['published_at'] = df_table['published_at'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

# extract state list
state_sorted = sorted(list(df_table['state'].unique()))

# extract sorted breed list
breed_name = df_table.groupby('breeds').size().sort_values(ascending=False)[:20]
breed_list = sorted(list(breed_name.index))

# extract breed list of dictionary
other_dic = [{'label': 'All', 'value': 'All'}, {'label': 'Other', 'value': 'Other'}]
breed_dic = [{'label': i, 'value': i} for i in breed_list]
breed_dic = other_dic + breed_dic

# pandas dataframe to html table
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns[:16]])
        ),
        html.Tbody([
            html.Tr(
                [
                html.Td(html.Img(src=dataframe.iloc[i][0],
                                 style={'height':'40%', 'width':'85%'}))] +
                [html.Td(html.A(dataframe.iloc[i][1],
                        href=dataframe.iloc[i][16],
                        target="_blank"))] +
                [html.Td(dataframe.iloc[i][col]) for col in dataframe.columns[2:16]
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={'marginLeft': 'auto', 'marginRight': 'auto'})


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1('Find Your Ideal Dog!', style={'textAlign': 'center'}),  # dashboard title
    html.Br(),
    html.B(intro1),  # dashboard intro,
    html.Br(),
    html.Br(),
    html.B(intro2),
    html.Br(),
    html.B(intro3),
    html.Br(),
    html.B(intro4),
    html.Br(),
    # filter for bar chart
    html.Div([
        # dropdown for choosing state
        html.H4('Choose your state:'),
        dcc.Dropdown(options=[{'label': i, 'value': i} for i in state_sorted],
                     id='state_by_dropdown',
                     value='NY'),
        # single choose checkboxes for choosing size
        html.H4('Select the prefered size:'),
        dcc.RadioItems(options=[{'label': 'Small', 'value': 'Small'},
                               {'label': 'Medium', 'value': 'Medium'},
                               {'label': 'Large', 'value': 'Large'}],
                      id="size_select",
                      value='Medium',
                      labelStyle={'display': 'inline-block'}),
    ],
        style={'width': '40%', 'display': 'inline-block'}),
    html.Br(),
    # bar chart
    html.Div([dcc.Graph(id='bar_fig')]),
    # filter
    html.H4('Choose filters to display detailed information:'),
    html.Div([html.H4('State:'),
              dcc.Dropdown(options=[{'label': i + ' ', 'value': i} for i in state_sorted],
                     id='dog_state',
                     value='NY'),
              html.H4('Age:'),
              dcc.Checklist(options=[{'label': 'Baby', 'value': 'Baby'},
                                    {'label': 'Young', 'value': 'Young'},
                                    {'label': 'Adult', 'value': 'Adult'},
                                    {'label': 'Senior', 'value': 'Senior'}],
                           id="age_checklist",
                           value=['Baby', 'Young', 'Adult', 'Senior']),
              html.H4('Gender:'),
              dcc.Checklist(options=[{'label': 'Female', 'value': 'Female'},
                                     {'label': 'Male', 'value': 'Male'}],
                            id="gender_checklist",
                            value=['Female', 'Male']),
              html.H4('Breed:'),
              dcc.Dropdown(options=breed_dic,
                           id='breed_by_dropdown',
                           value='All')],
             style={'width': '25%', 'display': 'inline-block'}),
    # Sort dropdown
    html.Br(),
    html.Div([html.H4('Sort by'),
              dcc.Dropdown(options=[{'label': 'Published Date', 'value': 'Published Date'},
                                    {'label': 'City', 'value': 'City'}],
                           id='sort_by_dropdown',
                           value='Published Date'),
              html.Br()],
             style={'width': '25%'}),
    # Tables
    html.Br(),
    html.Div(html.Div(id="df_div"))
])

# update bar chart
@app.callback(
    Output(component_id='bar_fig', component_property='figure'),
    [Input(component_id='state_by_dropdown', component_property='value'),
     Input(component_id='size_select', component_property='value')]
)
def update_output_div(state_by_dropdown, size_select):
    df_sub = df_table[(df_table['size'] == size_select) &
                      (df_table['state'] == state_by_dropdown)]

    count_breeds = df_sub.groupby('breeds').count()[['age']].reset_index()
    count_breeds = count_breeds.sort_values('age', ascending=False).rename(columns={'age': 'count'})[:10]

    fig = px.bar(count_breeds, x='count', y="breeds", orientation='h')

    fig.update_layout(title='number of dogs adoptable for breeds in ' + state_by_dropdown,
                      xaxis_title="Breeds",
                      yaxis_title="Number of dogs adoptable",
                      font=dict(
                          family="Courier New, monospace",
                          size=12,
                          color="RebeccaPurple")
                      )

    return fig

# Update the table
@app.callback(
    Output(component_id='df_div', component_property='children'),
    [Input(component_id='dog_state', component_property='value'),
     Input(component_id='age_checklist', component_property='value'),
     Input(component_id='gender_checklist', component_property='value'),
     Input(component_id='breed_by_dropdown', component_property='value'),
     Input(component_id='sort_by_dropdown', component_property='value')
     ]
)
def update_table(dog_state, age, gender, breed, sort_by):
    if breed == 'All':
        df_state = df_table[df_table['state'] == dog_state]
        x = df_state[(df_state['age'].isin(age)) &
                     (df_state['gender'].isin(gender))]

    elif breed == 'Other':
        df_state = df_table[df_table['state'] == dog_state]
        x = df_state[(df_state['age'].isin(age)) &
                     (df_state['gender'].isin(gender))]
        x = df_state[~(df_state['breeds'].isin(breed_list))]

    else:
        df_state = df_table[df_table['state'] == dog_state]
        x = df_state[(df_state['age'].isin(age)) &
                     (df_state['gender'].isin(gender)) &
                     (df_state['breeds'] == breed)]

    if sort_by == 'Published Date':
        x = x.sort_values('published_at', ascending=False)
    elif sort_by == 'City':
        x = x.sort_values('city')

    return generate_table(x, max_rows=50)

if __name__ == '__main__':
    app.run_server(debug=True)