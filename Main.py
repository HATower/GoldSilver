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

# Function to get prices (fetch automatically at specific times)
def get_prices():
    current_time = datetime.now()
    fetch_times = [
        current_time.replace(hour=8, minute=30, second=0, microsecond=0),
        current_time.replace(hour=12, minute=0, second=0, microsecond=0),
        current_time.replace(hour=17, minute=0, second=0, microsecond=0),
    ]

    # Check if it's time to fetch prices
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, "r") as file:
            price_data = json.load(file)
            last_fetch_time = datetime.fromisoformat(price_data["last_fetch_time"])
            
            # Fetch prices only if it's one of the scheduled times and not already fetched recently
            if any(abs((current_time - fetch_time).total_seconds()) < 60 for fetch_time in fetch_times):
                gold_price_per_gram, silver_price_per_gram = fetch_data_from_api()
                if gold_price_per_gram is not None and silver_price_per_gram is not None:
                    with open(PRICES_FILE, "w") as file:
                        json.dump({
                            "gold_price_per_gram": gold_price_per_gram,
                            "silver_price_per_gram": silver_price_per_gram,
                            "last_fetch_time": datetime.now().isoformat()
                        }, file)
                    return gold_price_per_gram, silver_price_per_gram, datetime.now()
            else:
                return price_data["gold_price_per_gram"], price_data["silver_price_per_gram"], last_fetch_time

    # If no price file exists or it's time to fetch prices
    gold_price_per_gram, silver_price_per_gram = fetch_data_from_api()
    if gold_price_per_gram is not None and silver_price_per_gram is not None:
        with open(PRICES_FILE, "w") as file:
            json.dump({
                "gold_price_per_gram": gold_price_per_gram,
                "silver_price_per_gram": silver_price_per_gram,
                "last_fetch_time": datetime.now().isoformat()
            }, file)
        return gold_price_per_gram, silver_price_per_gram, datetime.now()

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

# Option for anonymous calculation or user login
calc_mode = st.radio("Choose mode:", ["Anonymous Calculation", "User Login/Save Data"])

if calc_mode == "User Login/Save Data":
    st.header("User Management")
    pseudo = st.text_input("Enter your unique pseudo (or type the first few letters to search):")

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

# Fetch current prices (automatically at specific times)
gold_price_per_gram, silver_price_per_gram, last_fetch_time = get_prices()

if gold_price_per_gram is not None and silver_price_per_gram is not None:
    # Display current prices and last fetch time
    st.header("Current Prices")
    st.write(f"Gold Price :sports_medal: €{gold_price_per_gram:.2f} per gram")
    st.write(f"Silver Price 🥈: €{silver_price_per_gram:.2f} per gram")
    st.write(f"Last fetched at: {last_fetch_time.strftime('%Y-%m-%d %H:%M:%S')}")

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

            if silver_profit_loss > 0:
                st.success(f"Profit: €{silver_profit_loss:.2f}")
            elif silver_profit_loss < 0:
                st.error(f"Loss: €{abs(silver_profit_loss):.2f}")

    # Save button only for logged-in users
    if calc_mode == "User Login/Save Data":
        if st.button("Save Data"):
            all_user_data[selected_pseudo] = {
                "gold_quantity": gold_quantity if include_gold else user_data.get("gold_quantity", 0),
                "silver_quantity": silver_quantity if include_silver else user_data.get("silver_quantity", 0),
                "gold_price": gold_purchase_price if include_gold else user_data.get("gold_price", 0),
                "silver_price": silver_purchase_price if include_silver else user_data.get("silver_price", 0),
            }
            save_all_data(all_user_data)
            st.success(f"Your data has been saved under the pseudo '{selected_pseudo}'!")
