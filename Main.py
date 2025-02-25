import requests
from requests.structures import CaseInsensitiveDict
import streamlit as st
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "users_data.json"
PRICES_FILE = "prices.json"

# Function to fetch data from the API
def fetch_data_from_api():
    url = "https://api.metals.dev/v1/latest?api_key=Y53SYMOJDU2DYWQIU86W328QIU86W&currency=EUR&unit=g"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    api_response = requests.get(url, headers=headers)
    
    if api_response.status_code == 200:
        data = api_response.json()  # Parse JSON response
        gold_price_per_gram = data["metals"]["gold"]
        silver_price_per_gram = data["metals"]["silver"]
        return gold_price_per_gram, silver_price_per_gram
    else:
        st.error("Failed to fetch data from the API. Please check your API key or the URL.")
        return None, None

# Function to get prices (fetch only once a day)
def get_prices():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, "r") as file:
            price_data = json.load(file)
            last_fetch_time = datetime.fromisoformat(price_data["last_fetch_time"])
            if datetime.now() - last_fetch_time < timedelta(days=1):
                return price_data["gold_price_per_gram"], price_data["silver_price_per_gram"], last_fetch_time
    
    # Fetch new prices if not fetched within the last day
    gold_price_per_gram, silver_price_per_gram = fetch_data_from_api()
    if gold_price_per_gram is not None and silver_price_per_gram is not None:
        last_fetch_time = datetime.now()
        with open(PRICES_FILE, "w") as file:
            json.dump({
                "gold_price_per_gram": gold_price_per_gram,
                "silver_price_per_gram": silver_price_per_gram,
                "last_fetch_time": last_fetch_time.isoformat()
            }, file)
        return gold_price_per_gram, silver_price_per_gram, last_fetch_time
gold_price_per_gram, silver_price_per_gram, last_fetch_time = get_prices()
def is_time_to_fetch():
    current_time = datetime.now().time()
    fetch_times = [
        datetime.strptime("08:30", "%H:%M").time(),
        datetime.strptime("12:00", "%H:%M").time(),
        datetime.strptime("15:37", "%H:%M").time(),
        datetime.strptime("17:00", "%H:%M").time(),
    ]
    return current_time in fetch_times
if is_time_to_fetch() or datetime.now() - last_fetch_time > timedelta(days=1):
                gold_price_per_gram, silver_price_per_gram = fetch_data_from_api()
# Function to load all user data
def load_all_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to save all user data
def save_all_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

# Load existing user data
all_user_data = load_all_data()

# Streamlit interface
st.title("Gold :sports_medal: and Silver 🥈 Profit/Loss Calculator")

# User selection or anonymous calculation
st.header("User Management")
pseudo = st.text_input("Enter your unique pseudo (or leave blank for anonymous calculation):")

if pseudo:
    # Find matching pseudos
    matching_pseudos = [p for p in all_user_data.keys() if p.startswith(pseudo)]

    if matching_pseudos:
        selected_pseudo = st.selectbox("Select your pseudo:", matching_pseudos)
    else:
        selected_pseudo = pseudo

    # Load user data or initialize new user data
    if selected_pseudo in all_user_data:
        user_data = all_user_data[selected_pseudo]
        st.success(f"Welcome back, {selected_pseudo}!")
    else:
        user_data = {"gold_quantity": 0.0, "silver_quantity": 0.0, "gold_price": 0.0, "silver_price": 0.0}
        st.info(f"New user detected: {selected_pseudo}. Please enter your details below.")
else:
    # Anonymous calculation mode: Initialize empty user data for temporary use
    user_data = {"gold_quantity": 0.0, "silver_quantity": 0.0, "gold_price": 0.0, "silver_price": 0.0}
    st.info("You are calculating anonymously. Your data will not be saved.")

# Fetch current prices (once a day or on-demand)


if gold_price_per_gram is not None and silver_price_per_gram is not None:
    # Display current prices and last fetch time
    st.header("Current Prices")
    st.write(f"Last fetched at: {last_fetch_time.strftime('%d-%m-%Y \n %H:%M:%S')}")
    st.write(f"Gold Price :sports_medal: €{gold_price_per_gram:.2f} per gram")
    st.write(f"Silver Price 🥈: €{silver_price_per_gram:.2f} per gram")

    # Allow users to exclude metals from calculations
    include_gold = st.checkbox("Include Gold :sports_medal:", value=True)
    include_silver = st.checkbox("Include Silver 🥈", value=True)

    # User inputs for quantities and purchase prices (pre-filled with saved data)
    st.header("Your Portfolio")

    # Gold Section (only visible if included by the user)
    if include_gold:
        with st.expander("Gold :sports_medal:"):
            gold_quantity = st.number_input(
                "Enter the quantity of gold you own (in grams):", 
                min_value=0.0,
                value=user_data.get("gold_quantity", 0.0)
            )
            gold_purchase_price = st.number_input(
                "Enter the price you bought gold for (per gram, in EUR):", 
                min_value=0.0,
                value=user_data.get("gold_price", 0.0)
            )

            # Gold calculations
            gold_current_value = gold_quantity * gold_price_per_gram
            gold_purchase_value = gold_quantity * gold_purchase_price
            gold_profit_loss = gold_current_value - gold_purchase_value

            # Display Gold results
            st.metric(label="Current Value (€)", value=f"{gold_current_value:.2f}")
            st.metric(label="Purchase Value (€)", value=f"{gold_purchase_value:.2f}")
            if gold_purchase_value != 0:
                gold_profit_loss_pourcent = gold_profit_loss/gold_purchase_value
                st.metric("Gold",gold_current_value,str(gold_profit_loss_pourcent*100)+'%')
            if gold_profit_loss > 0:
                st.success(f"Profit: €{gold_profit_loss:.2f}")
            elif gold_profit_loss < 0:
                st.error(f"Loss: €{abs(gold_profit_loss):.2f}")

    # Silver Section (only visible if included by the user)
    if include_silver:
        with st.expander("Silver 🥈"):
            silver_quantity = st.number_input(
                "Enter the quantity of silver you own (in grams):", 
                min_value=0.0,
                value=user_data.get("silver_quantity", 0.0)
            )
            silver_purchase_price = st.number_input(
                "Enter the price you bought silver for (per gram, in EUR):", 
                min_value=0.0,
                value=user_data.get("silver_price", 0.0)
            )

            # Silver calculations
            silver_current_value = silver_quantity * silver_price_per_gram
            silver_purchase_value = silver_quantity * silver_purchase_price
            silver_profit_loss = silver_current_value - silver_purchase_value

            # Display Silver results
            st.metric(label="Current Value (€)", value=f"{silver_current_value:.2f}")
            st.metric(label="Purchase Value (€)", value=f"{silver_purchase_value:.2f}")
            if silver_purchase_value!=0:
                silver_profit_loss_pourcent = silver_profit_loss/silver_purchase_value
                st.metric("Silver",silver_current_value,str(silver_profit_loss_pourcent*100)+'%')
            if silver_profit_loss > 0:
                st.success(f"Profit: €{silver_profit_loss:.2f}")
                
            elif silver_profit_loss < 0:
                st.error(f"Loss: €{abs(silver_profit_loss):.2f}")

