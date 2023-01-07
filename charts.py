import plotly.express as px
import pandas as pd
from processing import sales_n_days_before, get_month_sales_by_weekday

def update_layout(chart, hovertemplate='%{x} - %{y:.2f}', xaxis_title='', yaxis_title='', custom_colors=False):
    chart.update_traces(hovertemplate=hovertemplate)
    chart.update_xaxes(fixedrange=True)
    chart.update_yaxes(fixedrange=True)
    chart.update_layout(
        title={
            'xanchor': 'center',
            'x': 0.5,
        },
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
    )

    if not custom_colors:
        chart.update_traces(marker_color='#3b65ce')

def get_top_products_chart(data, title, xaxis_title='', yaxis_title=''):
    top_products = px.bar(
        data.groupby('family')['sales'].sum().sort_values(ascending=False).reset_index().head(10),
        x='family',
        y='sales',
        title=title,
    )
    update_layout(top_products, yaxis_title=yaxis_title)
    return top_products

def get_price_chart(sales, title, xaxis_title='', yaxis_title=''):
    price_chart = px.line(
        sales,
        x='date',
        y='sales',
        title=title,
    )
    update_layout(price_chart, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    return price_chart

def get_holiday_graph(holydays, sales, n, title, xaxis_title='', yaxis_title=''):
    holydays['sales_before'] = holydays['date'].apply(lambda x: sales_n_days_before(sales, x.strftime('%Y-%m-%d'), n))
    holydays.sort_values('sales_before', inplace=True, ascending=False)
    valid_holydays = holydays.loc[(holydays['description'].str.contains('-') == False)
                                    & (holydays['description'].str.contains('\+') == False)
                                    & (holydays['description'].str.contains('Puente') == False)
                                    & (holydays['description'].str.contains('Traslado') == False)
                                    & (holydays['description'].str.contains('Recupero') == False)]
    valid_holydays = valid_holydays.groupby('description')['sales_before'].mean().reset_index()
    top_holydays_df = valid_holydays.sort_values('sales_before', ascending=False).head(10)

    top_holydays = px.bar(
        top_holydays_df,
        x='description',
        y='sales_before',
        title=title,
    )
    update_layout(top_holydays, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    return top_holydays

def get_weekday_distribution_chart(sales, title, xaxis_title='', yaxis_title=''):
    # Generate weekday distribution graph
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sales['weekday'] = sales['date'].dt.day_name()
    weekdays_df = sales.groupby('weekday')['sales'].mean().reset_index()
    weekdays_df['weekday'] = pd.Categorical(weekdays_df['weekday'], categories=weekday_order, ordered=True)
    weekdays_df.sort_values('weekday', inplace=True)

    weekdays = px.line(
        weekdays_df,
        x='weekday',
        y='sales',
        title=title,
    )

    update_layout(weekdays, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    return weekdays

def get_weekday_distribution_by_month_chart(sales, title, xaxis_title='', yaxis_title=''):
    sales['month'] = sales['date'].dt.month_name()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    weekday_colors = ['#3faa59', '#90cf67', '#d1eb85', '#fefebd', '#fdd884', '#fa9856', '#e54d34']

    month_weekday_distribution = {}
    for month in months_order:
        if month in sales['month'].unique():
            month_weekday_distribution[month] = get_month_sales_by_weekday(sales, month)['sales'].values.tolist()

    month_weekday_distribution_df = pd.DataFrame(month_weekday_distribution, index=weekday_order)
    month_weekday_distribution_df = month_weekday_distribution_df.transpose().reset_index()
    month_weekday_distribution_df.rename(columns={'index': 'month'}, inplace=True)

    month_weekday_distribution_df = pd.melt(month_weekday_distribution_df, id_vars=['month'], value_vars=weekday_order, var_name='weekday', value_name='sales')

    month_weekday_distribution_chart = px.bar(
        month_weekday_distribution_df,
        x='sales',
        y='month',
        color='weekday',
        orientation='h',
        title=title,
    )
    for i, weekday in enumerate(weekday_order):
        month_weekday_distribution_chart.for_each_trace(
            lambda trace: trace.update(marker_color=weekday_colors[i]) if trace.name == weekday else (),
        )
    
    update_layout(month_weekday_distribution_chart, xaxis_title=xaxis_title, yaxis_title=yaxis_title, hovertemplate='Month: %{y}<br>Sales: %{x:.2f}', custom_colors=True)

    return month_weekday_distribution_chart