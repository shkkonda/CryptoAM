import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

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

    # Resample the DataFrame by day and take the last value for each day
    df = df.resample('D').last()

    return df

def calculate_index(coin_splits):
    """
    Calculates the value of a hypothetical crypto index based on the input percentage splits.
    """
    index = []
    for date, row in historical_prices['Bitcoin'].iterrows():
        total_value = 0
        for coin, percent in coin_splits.items():
            price = historical_prices[coin].loc[date]['price']
            value = percent/100 * price
            total_value += value
        index.append(total_value)
    # Normalize the index values to start from 100
    normalized_index = [100*(i/index[0]) for i in index]
    return normalized_index

# Define the app layout
st.title('Crypto Index Tracker')

# Define session state
session_state = st.session_state.get(password=None)

if session_state.password:
    # User is logged in
    st.write(f"Logged in as {session_state.username}")
    if st.button('Logout'):
        session_state.password = None
        st.write('Logged out successfully!')
    else:
        # Fetch the historical prices for each cryptocurrency
        historical_prices = {}
        for coin, coin_id in COINS.items():
            historical_prices[coin] = fetch_historical_prices(coin_id)

        # Calculate the index value for each day
        coin_splits = {'Bitcoin': 0.65, 'Ethereum': 0.30, 'Litecoin': 0.05}
        index_values = calculate_index(coin_splits)

        # Create a DataFrame of the historical index values
        index_data = {'date': historical_prices['Bitcoin'].index, 'value': index_values}
        index_df = pd.DataFrame(index_data)
        index_df.set_index('date', inplace=True)

        # Calculate the index value for each day using an annual growth rate of 15%
        start_date = historical_prices['Bitcoin'].index[0]
        end_date = historical_prices['Bitcoin'].index[-1]
        days = (end_date - start_date).days
        annual_rate = 0.15
        daily_rate = (1 + annual_rate) ** (1/365)
        xirr_values = [100 * daily_rate**(i) for i in range(days+1)]

        # Plot the historical index values
        fig = go.Figure()

        crypto_index = go.Scatter(x=index_df.index, y=index_df['value'], name='Crypto Index')
        crypto_index_text = f"Crypto Index: ${index_df['value'].iloc[-1]:,.2f}"
        crypto_index.update(text=crypto_index_text)

        fixed_returns = go.Scatter(x=index_df.index, y=xirr_values, name='Fixed Returns')
        fixed_returns_text = f"${xirr_values[-1]:,.2f}"
        text_array = [None] * (len(xirr_values) - 1)
        text_array.append(fixed_returns_text)
        # Set the marker parameter to None for all but the last data point
        # Set the marker size for all data points except the last one to 0
        marker_size = [0] * (len(xirr_values) - 1)

        # Set the marker size for the last data point to 10
        marker_size.append(10)
        fixed_returns.update(text=text_array, mode='lines+markers+text', textposition='top center', marker={'color': 'red', 'size': marker_size})

        fig.add_trace(crypto_index)
        fig.add_trace(fixed_returns)

        fig.update_layout(title='Historical Crypto Index', xaxis_title='Date', yaxis_title='Value (USD)')

        st.plotly_chart(fig)
else:
    # User is not logged in
    username = st.text_input('Username:')
    password = st.text_input('Password:', type='password')

    if st.button('Login'):
        if username == 'admin' and password == 'password':
            session_state.username = username
            session_state.password = password
            st.success('Logged in successfully!')
        else:
            st.error('Incorrect username or password')
