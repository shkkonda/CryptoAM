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
    total_value = 0
    for coin, percent in coin_splits.items():
        price = historical_prices[coin].iloc[-1]['price']
        value = percent/100 * price
        total_value += value
    return total_value

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

    # Calculate the index value based on the input
    coin_splits = {'Bitcoin': btc_percent, 'Ethereum': eth_percent, 'Litecoin': ltc_percent}
    index_value = calculate_index(coin_splits)

    # Plot the historical prices of each cryptocurrency and the hypothetical index value
    fig = go.Figure()
    for coin, df in historical_prices.items():
        fig.add_trace(go.Scatter(x=df.index, y=df['price'], name=coin))
    fig.add_trace(go.Scatter(x=[historical_prices['Bitcoin'].index[-1]], y=[index_value], name='Crypto Index'))

    # Update the plot layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        title=f'Crypto Prices and Index (BTC={btc_percent}, ETH={eth_percent}, LTC={ltc_percent})'
    )

    # Display the plot
    st.plotly_chart(fig)
