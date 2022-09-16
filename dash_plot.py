from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import dash_daq as daq

external_stylesheets = [
    # Dash CSS
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    'https://codepen.io/chriddyp/pen/brPBPO.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

DF = pd.read_csv('data/walls.csv', skipinitialspace=True)

print('Initial size', DF.shape)

# convert to dates, times
DF['scrape_date'] = pd.to_datetime(DF['scrape_date']).dt.date
DF['scrape_time'] = pd.to_datetime(DF['scrape_time']).dt.time

# filter by max count for each day
DF['count'] = DF.groupby(['name', 'scrape_date'])[
    'count'].transform('max')
DF.drop_duplicates(inplace=True, subset=['name', 'scrape_date'])

print('Filtered size', DF.shape)

DF.sort_values(by=['name', 'scrape_date'], inplace=True)

app.layout = html.Div(children=[
    html.H1(children='UkWalls Data', style={'textAlign': 'center'}),

    # add input for expressions to match
    html.Div(['Match Expressions (comma separated): ',
              dcc.Input(id='wall-name-input', type='text', value='awe, liv, spider', debounce=True)], style={'textAlign': 'center'}),

    # add input for days to match
    html.Div(['Number of days: ',
              dcc.Input(id='num-days-input', type='number', value=30)], style={'textAlign': 'center'}),

    # add input for days to match
    html.Div(['Use Percentage Full: ', daq.BooleanSwitch(
        id='use-percent-input', on=False)], style={'textAlign': 'center'}),

    dcc.Graph(id='example-graph')],
    style={'height': '100%'})


@app.callback(
    Output(component_id='example-graph', component_property='figure'),
    [Input(component_id='wall-name-input', component_property='value'),
     Input(component_id='num-days-input', component_property='value'),
     Input('use-percent-input', component_property='on')]
)
def update_graph(wall_name_input, num_days_input, use_pct_input):
    # create regex from matching patterns
    matches = [s.strip() for s in wall_name_input.split(',')]
    matches = [s for s in matches if s]
    pattern = f'({"|".join(matches)})' if matches else '(.*)'

    # filter to matching walls
    df = DF.loc[DF['name'].str.contains(pattern, regex=True, case=False)]

    # filter to last n days
    days = num_days_input
    df = df.loc[df['scrape_date'] >= pd.to_datetime(
        'today').date() - pd.Timedelta(days=days - 1)]

    title = f'UkWalls Data for walls matching [{wall_name_input}] in last {num_days_input} days'
    x_axis_title = 'Date'
    y_axis_title = 'Count at Peak'
    legend_title = 'Wall Name'

    column = 'count'

    if use_pct_input:
        # add a column for pct_full
        df['pct_full'] = (100 * df['count'] / df['capacity']).round(2)
        y_axis_title = 'Percent Full at Peak'
        column = 'pct_full'

    fig = px.line(df, x="scrape_date", y=column, color="name",
                  custom_data=['count', 'capacity', 'time'], markers=True)

    fig.update_layout(title=title, title_x=0.5, xaxis_title=x_axis_title,
                      yaxis_title=y_axis_title, legend_title=legend_title, height=800)

    fig.update_traces(patch={"line": {'dash': 'dot'}})

    fig.update_traces(
        hovertemplate="<br>".join([
            "Date: %{x}",
            "Percent Full: %{y}",
            "Count: %{customdata[0]}",
            "Capacity: %{customdata[1]}",
            "Time: %{customdata[2]}",
        ])
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
