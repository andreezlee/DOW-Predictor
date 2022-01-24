import yfinance as yf
import MySQLdb
from datetime import date, timedelta, datetime

# Helper function to linearly interpolate missing values
# Return list of (date, float) tuples
def fill_database_gaps(date1, value1, date2, value2):
    time_interval=(date2 - date1).days
    value_delta=(value2 - value1)/time_interval

    gap_values=list()
    for i in range(1, time_interval):
        gap_values.append((date1 + timedelta(days=i), value_delta * i + value1))
    return gap_values

# Converts from date type to "D Month YYYY"
def convert_date(date_arg):
    new_string=date_arg.strftime("%d %b %Y")
    if new_string[0]=="0": # Remove front zero if applicable
        return new_string[1:]
    return new_string

# Creates percentage change from old value to new value
def percentage_change(old_value, new_value):
    return (new_value - old_value) / old_value

# Get DOW Jones closing values for past several years
def create_financial_data():
    sql_cxn = MySQLdb.connect('localhost','root','gwailo98(*','predictor')
    cursor = sql_cxn.cursor()

    all_data=yf.download('DJI','2016-01-01', date.today().strftime("%Y-%m-%d"))

    values_dict=all_data['Close'].to_dict()

    # Add data entries to database
    insert_query="INSERT INTO dji_data (sample_date, dow_jones, percent_change, estimate) VALUES (%s, %s, %s, %s)"
    prev_date=date(2015, 12, 31)
    prev_value=17425
    for i in values_dict: # i is a datetime object of midnight for that date
        d=i.date()
        if (d - prev_date).days > 1:
            filler_list=fill_database_gaps(prev_date, prev_value, d, values_dict[i])
            for (fill_date, fill_value) in filler_list:
                percent_change=percentage_change(prev_value, fill_value)
                query_data=(convert_date(fill_date), fill_value, percent_change, 1)
                cursor.execute(insert_query, query_data)
                prev_date=fill_date
                prev_value=fill_value
        percent_change=percentage_change(prev_value, values_dict[i])
        query_data=(convert_date(d), values_dict[i], percent_change, 0)
        cursor.execute(insert_query, query_data)
        prev_date=d
        prev_value=values_dict[i]

    sql_cxn.commit()
    cursor.close()
    sql_cxn.close()

if __name__ == "__main__":
    create_financial_data()

