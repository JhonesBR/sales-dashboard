#Libraries
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
from dash import Dash
import pandas as pd
import numpy as np

# Chart functions
from charts import get_weekday_distribution_by_month_chart
from charts import get_weekday_distribution_chart
from charts import get_top_products_chart
from charts import get_holiday_graph
from charts import get_price_chart

# Get data
data = pd.read_csv('data/sales.csv')
data['date'] = pd.to_datetime(data['date'])
sales = data.groupby('date')['sales'].sum().reset_index()
sales['date'] = pd.to_datetime(sales['date'])
sales.sort_values('date', inplace=True)
holydays = pd.read_csv('data/holidays_events.csv', parse_dates=['date'])

# Initialize the app with external stylesheets
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap',
        'rel': 'stylesheet',
    },
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Sales Analytics'

# Set app layout
app.layout = html.Div(
    children = [
        # Header
        html.Div(
            children = [
                html.P(
                    children='🛒',
                    className='header-emoji'
                ),
                html.H1(
                    children='Sales Analytics',
                    className='header-title'
                ),
                html.P(
                    children='Analyze sales at the country of Ecuador in different stores',
                    className='header-description'
                ),
            ],
            className = 'header'
        ),

        # Filter menu
        html.Div(
            children = [
                html.Div(
                    children = [
                        html.Div(children='Store', className='menu-title'),
                        dcc.Dropdown(
                            id='store-filter',
                            options = [
                                {'label': store, 'value': store} for store in np.sort(data['store_nbr'].unique())
                            ],
                            value='',
                            clearable=True,
                            className='dropdown',
                        ),
                    ],
                    id='store-filter-container',
                ),
                html.Div(
                    children = [
                        html.Div(
                            children='Date Range',
                            className='menu-title'
                        ),
                        dcc.DatePickerRange(
                            id='date-range',
                            min_date_allowed=data['date'].min().date(),
                            max_date_allowed=data['date'].max().date(),
                            start_date=data['date'].min().date(),
                            end_date=data['date'].max().date(),
                            display_format='DD/MM/YYYY',
                        ),
                    ],
                    id='date-filter-container',
                )
            ],
            className='menu',
        ),

        # Top products
        dcc.Graph(
            figure = get_top_products_chart(data, 'Top 10 products', yaxis_title='Number of sales'),
            config={'displayModeBar': False},
            className='card',
            id='top-products-chart',
        ),

        # Price chart
        dcc.Graph(
            figure = get_price_chart(sales, 'Sales over time', yaxis_title='Number of sales'),
            config={'displayModeBar': False},
            className='card',
            id='price-chart',
        ),

        # Sales by weekday
        dcc.Graph(
            figure = get_holiday_graph(holydays, sales, 10, 'Top 10 holydays', yaxis_title='Mean total sales 10 days before'),
            config={'displayModeBar': False},
            className='card',
            id='holiday-chart',
        ),

        # Sales by weekday
        dcc.Graph(
            figure = get_weekday_distribution_chart(sales, 'Sales by weekday', yaxis_title='Mean total sales'),
            config={'displayModeBar': False},
            className='card',
            id='weekday-distribution-chart',
        ),

        # Sales by weekday per month
        dcc.Graph(
            figure = get_weekday_distribution_by_month_chart(sales, 'Sales by weekday per month', xaxis_title='Mean total sales'),
            config={'displayModeBar': False},
            className='card',    
            id='weekday-distribution-by-month-chart',
        ),     
    ],
    className='app',
)

# Define callbacks
@app.callback(
    Output('top-products-chart', "figure"),
    Output('price-chart', "figure"),
    Output('holiday-chart', "figure"),
    Output('weekday-distribution-chart', "figure"),
    Output('weekday-distribution-by-month-chart', "figure"),
    [
        Input('store-filter', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
    ],
)
def update_charts(store, start_date, end_date):
    data_mask = (data['date'] >= start_date) & (data['date'] <= end_date)
    sales_mask = (sales['date'] >= start_date) & (sales['date'] <= end_date)

    sales_from_store = sales.copy()
    if store:
        sales_from_store = data.loc[data['store_nbr'] == store].groupby('date')['sales'].sum().reset_index()
        sales_from_store['date'] = pd.to_datetime(sales['date'])
        sales_from_store.sort_values('date', inplace=True)

        data_mask = data_mask & (data['store_nbr'] == store)

    filtered_data = data.loc[data_mask].copy()
    filtered_sales = sales.loc[sales_mask].copy()

    store_description = 'All stores' if not store else f'Store: {store}'
    filters_description = f'(Store: {store_description} | Date range: {start_date} - {end_date})'

    return (
        get_top_products_chart(filtered_data, f'Top 10 products {filters_description}', yaxis_title='Number of sales'),
        get_price_chart(filtered_sales, f'Sales over time {filters_description}', yaxis_title='Number of sales'),
        get_holiday_graph(holydays, filtered_sales, 10, f'Top 10 holydays {filters_description}', yaxis_title='Mean total sales 10 days before'),
        get_weekday_distribution_chart(filtered_sales, f'Sales by weekday {filters_description}', yaxis_title='Mean total sales'),
        get_weekday_distribution_by_month_chart(filtered_sales, f'Sales by weekday per month {filters_description}', xaxis_title='Mean total sales'),
    )

if __name__ == '__main__':
    app.run_server()