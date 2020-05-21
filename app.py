import dash
import dash_core_components as dcc
import dash_html_components as html
import pymongo
from pymongo import MongoClient
from datetime import datetime as dt
from datetime import timedelta

import plotly.graph_objects as go
import re

#MongoDB
client = MongoClient(os.environ['MONGODB_URI'])
db = client.heroku_dq1wfl9j
collection = db['proj-air-pollution']

date = dt(2020,4,22)
dateStart = date.replace(hour=0, minute=0, second=0, microsecond=0)
dateEnd = date.replace(hour=23, minute=59, second=59, microsecond=999999)

temp= []
alt = []

for i in range(0,100,10):
    alt.append(i)
    alt_temp = []
    for doc in collection.find({"date" : {'$gte' : dateStart,'$lt' : dateEnd}, "altitude" : {'$gte' : str(i-5),'$lt' : str(i+5)}}):
        alt_temp.append(float(doc['temp']))
    if(len(alt_temp) != 0):
        temp_average = sum(alt_temp) / len(alt_temp)
    else:
        temp_average = None
    temp.append(temp_average)

chart_data = go.Scatter(x=temp, y=alt, connectgaps=True, line_shape='spline')
chart_fig = go.Figure(
    data=[chart_data],
)
chart_fig.update_layout(title='Temperature vs. Altitude',
                   xaxis_title='Temperature (Celsius)',
                   yaxis_title='Altitude (Meter)')

app = dash.Dash()
app.layout = html.Div([
    html.Div([
        dcc.DatePickerSingle(
            id = 'date-picker-single',
            date = dt(2020,4,22),
            min_date_allowed=dt(2020, 4, 22),
            max_date_allowed=dt.today()
        ),
    ]),
    html.Div([
        dcc.Graph(
            id = 'temp-vs-alt',
            figure = chart_fig
        ),
    ])
])

@app.callback(
    dash.dependencies.Output('temp-vs-alt', 'figure'),
    [dash.dependencies.Input('date-picker-single', 'date')],
)
def update_output(date):
    date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
    
    dateStart = date.replace(hour=0, minute=0, second=0, microsecond=0)
    dateEnd = date.replace(hour=23, minute=59, second=59, microsecond=999999)

    new_temp = []
    new_alt = []

    for i in range(0,100,10):
        new_alt.append(i)
        alt_temp = []
        for doc in collection.find({"date" : {'$gte' : dateStart,'$lt' : dateEnd}, "altitude" : {'$gte' : str(i-5),'$lt' : str(i+5)}}):
            alt_temp.append(float(doc['temp']))
        if(len(alt_temp) != 0):
            temp_average = sum(alt_temp) / len(alt_temp)
        else:
            temp_average = None
        new_temp.append(temp_average)

    chart_data = go.Scatter(x=new_temp, y=new_alt, connectgaps=True, line_shape='spline')
    chart_fig = go.Figure(
        data=[chart_data],
    )
    chart_fig.update_layout(title='Temperature vs. Altitude',
                   xaxis_title='Temperature (Celsius)',
                   yaxis_title='Altitude (Meter)')
    return chart_fig

if __name__ == "__main__":
    app.run_server(debug=True)
