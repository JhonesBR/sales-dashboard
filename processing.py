import pandas as pd
import datetime

def get_holiday(holiday_df, date, city, state):
    '''
    Parameters
    ----------
    holiday_df : pd.DataFrame
        The dataframe with holidays.
    date : str
        Date in the format '%Y-%m-%d'.
    city : str
        The city name.
    state : str
        The state name.

    Returns
    -------
    Name of the holiday if the date is a holiday, otherwise an empty string.
    '''

    date_df = holiday_df[holiday_df['date'] == date]
    if date_df.empty:
        return ''
    
    if date_df['transferred'].values[0] == True:
        return ''

    if date_df['locale'].values[0] == 'National':
        return date_df['description'].values[0]

    if date_df['locale'].values[0] == 'Regional' and date_df['locale_name'].values[0] == state:
        return date_df['description'].values[0]

    if date_df['locale'].values[0] == 'Local' and date_df['locale_name'].values[0] == city:
        return date_df['description'].values[0]

    return ''


def sales_n_days_before(sales:pd.DataFrame, date:str, n:int, dateformat:str='%Y-%m-%d') -> float:
    '''
    Parameters
    ----------
    sales : pd.DataFrame
        The dataframe with sales.
    date : str
        Date in the format '%Y-%m-%d' or format specified in dateformat.
    n : int
        Number of days before the date.
    dateformat : str (optional)
        The format of the date. The default is '%Y-%m-%d'.

    Returns
    -------
    The sum of sales of the last n days before the date.
    '''

    min_date = datetime.datetime.strptime(date, dateformat) - datetime.timedelta(days=n)

    date_df = sales.loc[sales['date'] >= min_date]
    date_df = date_df.loc[date_df['date'] <= date]

    if date_df.empty:
        return 0

    return date_df['sales'].sum()


def get_month_sales_by_weekday(sales:pd.DataFrame, month:str) -> pd.DataFrame:
    '''
    Parameters
    ----------
    sales : pd.DataFrame
        The dataframe with sales.
    month : str
        The month name in English with the first letter capital.

    Returns
    -------
    A dataframe with the average sales per weekday.
    '''

    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    month_sales = sales.loc[sales['month'] == month]
    month_sales_by_weekday = month_sales.groupby('weekday')['sales'].mean().reset_index()

    for weekday in weekday_order:
        if weekday not in month_sales_by_weekday['weekday'].values:
            month_sales_by_weekday = pd.concat([month_sales_by_weekday, pd.DataFrame({'weekday': [weekday], 'sales': [0]})], ignore_index=True)
        month_sales_by_weekday = month_sales_by_weekday.sort_values('weekday')

    month_sales_by_weekday = month_sales_by_weekday.set_index('weekday')
    month_sales_by_weekday = month_sales_by_weekday.reindex(weekday_order)

    return month_sales_by_weekday