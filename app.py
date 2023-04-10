import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

# Define the CoinMarketCap API endpoint and parameters
API_ENDPOINT = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical'
API_KEY = '4481b7f5-e43b-4fc3-889d-217a5863227a'

# Define the current prices for each cryptocurrency
CRYPTOS = {
    'Bitcoin': 'BTC',
    'Ethereum': 'ETH',
    'Litecoin': 'LTC'
}

def fetch_historical_prices(crypto):
    """
    Fetches the historical prices for the given cryptocurrency using the CoinMarketCap API.
    """
    # Define the API query parameters
    params = {
        'symbol': CRYPTOS[crypto],
        'time_start': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'time_end': datetime.now().strftime('%Y-%m-%d'),
        'interval': 'daily'
    }

    # Define the API headers
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY
    }

    # Send the API request
    response = requests.get(API_ENDPOINT, params=params, headers=headers)

    # Parse the API response into a DataFrame
    data = response.json()['data'][CRYPTOS[crypto]]['quotes']
    df = pd.DataFrame(data, columns=['time', 'price'])

    # Convert the timestamp column to datetime and set it as the index
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    return df

def calculate_index(crypto_splits):
    """
    Calculates the value of a hypothetical crypto index based on the input percentage splits.
    """
    total_value = 0
    for crypto, percent in crypto_splits.items():
        price = historical_prices[crypto].iloc[-1]['price']
        value = percent/100 * price
        total_value += value
    return total_value

# Define the app layout
st.title('Crypto Index Tracker')

with st.form(key='crypto_splits'):
    st.header('Input Crypto Percentage Splits')
    btc_percent = st.slider('Bitcoin', 0, 100, 33)
    eth_percent = st.slider('Ethereum', 0, 100, 33)
    ltc_percent = st.slider('Litecoin', 0, 100, 33)

    submitted = st.form_submit_button('Calculate Index')

if submitted:
    # Fetch the historical prices for each cryptocurrency
    historical_prices = {}
    for crypto in CRYPTOS:
        historical_prices[crypto] = fetch_historical_prices(crypto)

    # Calculate the index value based on the input
    crypto_splits = {'Bitcoin': btc_percent, 'Ethereum': eth_percent, 'Litecoin': ltc_percent}
    index_value = calculate_index(crypto_splits)

    # Plot the historical prices of each cryptocurrency and the hypothetical index value
    fig = go.Figure()
    for crypto, df in historical_prices.items():
        fig.add_trace(go.Scatter(x=df.index, y=df['price'], name=crypto))
    fig.add_trace(go.Scatter(x=[historical_prices['Bitcoin'].index[-1]], y=[index_value], name='Crypto Index'))

    # Update the plot layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        title=f'Crypto Prices and Index (BTC={btc_percent}%, ETH
