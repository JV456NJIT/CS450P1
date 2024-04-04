import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go  
import pandas as pd
import os
from dash.dependencies import Input, Output
import json
import os
from pathlib import Path
import os
import seaborn as sns
import matplotlib.pyplot as plt

dataset_file = "Sleep_health_and_lifestyle_dataset.csv"
if not os.path.exists(dataset_file):
    import kaggle as kg
    Path("~/.kaggle").expanduser().mkdir(exist_ok=True)
    USERNAME = "jv456njit"
    API_KEY = "f9880bc67181e914a313cf4f23ba1656"

    with open(Path("~/.kaggle/kaggle.json").expanduser(), "w") as f:
        json.dump({"username": f"{USERNAME}", "key": f"{API_KEY}"}, f)

    os.chmod(Path("~/.kaggle/kaggle.json").expanduser(), 0o600)

    kg.api.authenticate()

    dataset_name = "uom190346a/sleep-health-and-lifestyle-dataset"
    path_to_save = "."

    kg.api.dataset_download_files(dataset=dataset_name, path=path_to_save, unzip=True)
else:
    print("Dataset already exists")

df = pd.read_csv(dataset_file)
df['BMI Category'] = df['BMI Category'].replace({'Overweight': 'Overweight', 'Obese': 'Overweight', 'Normal': 'Normal', 'Normal Weight': 'Normal'})


app = dash.Dash(__name__)
server = app.server

# Calculate average sleep duration and quality for each age group and occupation
avg_sleep = df.groupby(['Age', 'Occupation'])[['Sleep Duration', 'Quality of Sleep']].mean().reset_index()

app.layout = html.Div([
    html.Br(),
    html.H1('Exploring Sleep Health and Lifestyle: An Interactive Dashboard', style={'text-align': 'center'}),
    html.Br(),
    html.Div([
        html.H2('Demographics'),
        dcc.Checklist(
            id='checkbox',
            options=[
                {'label': 'Sleep Duration', 'value': 'Sleep Duration'},
                {'label': 'Quality of Sleep', 'value': 'Quality of Sleep'}
            ],
            value=['Sleep Duration', 'Quality of Sleep']
        ),
        dcc.Graph(id='graph')
    ], id='div-graph', style={'background-color': '#f0f0f0', 'color': '#000', 'border': '1px solid #000', 'padding': '10px'}),

    html.Div([
        html.H2('Lifestyle Factors'),
        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in ['Physical Activity Level', 'Stress Level']],
                value='Physical Activity Level',
                style={'width': '48%', 'display': 'inline-block'}
            ),
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in ['Quality of Sleep']],
                value='Quality of Sleep',
                 style={'width': '48%', 'display': 'inline-block'}
            ), 
        ], style={'display': 'flex',}),
        dcc.Graph(id='scatter')
    ], id='div-scatter', style={'background-color': '#f0f0f0', 'color': '#000', 'border': '1px solid #000', 'padding': '10px'}),

    html.Div([
        html.H2('BMI Category Distribution'),
        html.Div([
        dcc.Dropdown(
            id='bmi-category',
            options=[{'label': i, 'value': i} for i in df['BMI Category'].unique()],
            value='Normal',
            style={'width': '48%', 'display': 'inline-block'}
        ),
        dcc.Dropdown(
            id='second-category',
            options=[{'label': i, 'value': i} for i in ['Age', 'Gender', 'Occupation']],
            value='Age',
            style={'width': '48%', 'display': 'inline-block'}
        ),
        ], style={'display': 'flex'}),
        dcc.Graph(id='bmi-graph')
    ], id='div-bmi-graph', style={'background-color': '#f0f0f0', 'color': '#000', 'border': '1px solid #000', 'padding': '10px'}),

    html.Div([
        html.H2('Daily Steps vs Selected Factor'),
        dcc.RadioItems(
            id='factor-radioitem',
            options=[{'label': i, 'value': i} for i in ['Sleep Duration', 'Quality of Sleep', 'Physical Activity Level', 'Stress Level']],
            value='Sleep Duration'
        ),
        dcc.Graph(id='box-plot')
    ], id='div-box-plot', style={'background-color': '#f0f0f0', 'color': '#000', 'border': '1px solid #000', 'padding': '10px'}),
])

@app.callback(
    Output('graph', 'figure'),
    [Input('checkbox', 'value')]
)
def update_graph(selected_checkboxes):
    if selected_checkboxes:
        fig = px.bar(avg_sleep.melt(id_vars=['Age', 'Occupation'], value_vars=selected_checkboxes), 
                     x='Occupation', y='value', color='Age', facet_row='variable', barmode='group')
    else:
        fig = px.scatter() 
    return fig

@app.callback(
    Output('scatter', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value')]
)
def update_scatter(xaxis_column_name, yaxis_column_name):
    fig = px.scatter(df, x=xaxis_column_name, y=yaxis_column_name, color='Age')
    fig.update_traces(marker=dict(size=15))

    return fig


@app.callback(
    Output('bmi-graph', 'figure'),
    [Input('bmi-category', 'value'),
     Input('second-category', 'value')]
)
def update_bmi_graph(bmi_category, second_category):
    filtered_df = df[df['BMI Category'] == bmi_category]
    fig = px.histogram(filtered_df, x=second_category, histnorm='percent')
    fig.update_yaxes(title_text='Percentage')
    return fig

@app.callback(
    Output('box-plot', 'figure'),
    [Input('factor-radioitem', 'value')]
)
def update_box_plot(selected_factor):
    fig = go.Figure()
    fig.add_trace(go.Box(y=df[selected_factor], x=df['Daily Steps'], name=selected_factor))
    fig.update_layout(title='Daily Steps vs Selected Factor', xaxis_title='Daily Steps', yaxis_title='Factor Value')
    return fig
if __name__ == '__main__':
    app.run_server(debug=True, port=8051,)
