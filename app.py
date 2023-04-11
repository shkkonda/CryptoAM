import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

# Define the CoinGecko API endpoint and parameters
API_ENDPOINT = 'https://api.coingecko.com/api/v3/coins'
COINS = {
    'Bitcoin': 'bitcoin',
    'Ethereum': 'ethereum',
    'Litecoin': 'litecoin'
}

def fetch_historical_prices(coin_id):
    """
    Fetches the historical prices for the given coin using the CoinGecko API.
    """
    # Define the API query parameters
    params = {
        'vs_currency': 'usd',
        'days': 30
    }

    # Send the API request
    url = f'{API_ENDPOINT}/{coin_id}/market_chart'
    response = requests.get(url, params=params)

    # Parse the API response into a DataFrame
    data = response.json()['prices']
    df = pd.DataFrame(data, columns=['time', 'price'])

    # Convert the timestamp column to datetime and set it as the index
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)

    return df

def calculate_index(coin_splits):
    """
    Calculates the value of a hypothetical crypto index based on the input percentage splits.
    """
    common_dates = set.intersection(*[set(df.index) for df in historical_prices.values()])
    index = []
    for date in common_dates:
        total_value = 0
        for coin, percent in coin_splits.items():
            price = historical_prices[coin].loc[date]['price']
            value = percent/100 * price
            total_value += value
        index.append(total_value)
    return index

# Define the app layout
st.title('Crypto Index Tracker')

with st.form(key='coin_splits'):
    st.header('Input Crypto Percentage Splits')
    btc_percent = st.slider('Bitcoin', 0, 100, 33)
    eth_percent = st.slider('Ethereum', 0, 100, 33)
    ltc_percent = st.slider('Litecoin', 0, 100, 33)

    submitted = st.form_submit_button('Calculate Index')

if submitted:
    # Fetch the historical prices for each cryptocurrency
    historical_prices = {}
    for coin, coin_id in COINS.items():
        historical_prices[coin] = fetch_historical_prices(coin_id)

    # Calculate the index value for each common date
    coin_splits = {'Bitcoin': btc_percent, 'Ethereum': eth_percent, 'Litecoin': ltc_percent}
    index_values = calculate_index(coin_splits)

    # Create a DataFrame of the historical index values
    common_dates = sorted(set.intersection(*[set(df.index) for df in historical_prices.values()]))
    index_data = {'date': common_dates, 'value': index_values}
    index_df = pd.DataFrame(index_data)
    index_df.set_index('date', inplace=True)

    # Plot the historical index values
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=index_df.index, y=index_df['value'], name='Crypto Index'))

    # Update the plot layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        title=f'Crypto Prices and Index (BTC={btc_percent}, ETH={eth_percent}, LTC={ltc_percent})'
    )

    # Display the plot
    st.plotly_chart(fig)
