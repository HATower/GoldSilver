# Streamlit interface
st.title("Gold :sports_medal: and Silver 🥈 Profit/Loss Calculator")

# User selection or creation
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
    # Initialize `user_data` for anonymous users
    user_data = {"gold_quantity": 0.0, "silver_quantity": 0.0, "gold_price": 0.0, "silver_price": 0.0}
    st.info("You are calculating anonymously. Your data will not be saved.")

# Fetch current prices (once a day or on-demand)
gold_price_per_gram, silver_price_per_gram = get_prices()

if gold_price_per_gram is not None and silver_price_per_gram is not None:
    # Display current prices
    st.header("Current Prices")
    st.write(f"Gold Price :sports_medal: €{gold_price_per_gram:.2f} per gram")
    st.write(f"Silver Price 🥈: €{silver_price_per_gram:.2f} per gram")

    # User inputs for quantities and purchase prices (pre-filled with saved data)
    st.header("Your Portfolio")
    
    # Ensure that `user_data` exists before using `.get()`
    gold_quantity = st.number_input(
        "Enter the quantity of gold you own (in grams):", 
        min_value=0.0, 
        value=user_data.get("gold_quantity", 0.0)
    )
    silver_quantity = st.number_input(
        "Enter the quantity of silver you own (in grams):", 
        min_value=0.0, 
        value=user_data.get("silver_quantity", 0.0)
    )
    
    st.header("Purchase Prices")
    
    gold_purchase_price = st.number_input(
        "Enter the price you bought gold for (per gram, in EUR):", 
        min_value=0.0, 
        value=user_data.get("gold_price", 0.0)
    )
    
    silver_purchase_price = st.number_input(
        "Enter the price you bought silver for (per gram, in EUR):", 
        min_value=0.0, 
        value=user_data.get("silver_price", 0.0)
    )

    # Save button to persist data under the user's pseudo
    if pseudo and st.button("Save Data"):
        all_user_data[selected_pseudo] = {
            "gold_quantity": gold_quantity,
            "silver_quantity": silver_quantity,
            "gold_price": gold_purchase_price,
            "silver_price": silver_purchase_price,
        }
        save_all_data(all_user_data)
        st.success(f"Your data has been saved under the pseudo '{selected_pseudo}'!")

    # Calculate profit or loss
    if st.button("Calculate Profit/Loss"):
        # Gold calculations
        gold_current_value = gold_quantity * gold_price_per_gram
        gold_purchase_value = gold_quantity * gold_purchase_price
        gold_profit_loss = gold_current_value - gold_purchase_value

        # Silver calculations
        silver_current_value = silver_quantity * silver_price_per_gram
        silver_purchase_value = silver_quantity * silver_purchase_price
        silver_profit_loss = silver_current_value - silver_purchase_value

        total_profit_loss = gold_profit_loss + silver_profit_loss

        # Display results in a visually appealing way
        st.header("Profit/Loss Results")
        
        # Gold results 🪙
        if gold_quantity > 0:
            st.subheader("Gold :sports_medal:")
            st.metric(label="Current Value (€)", value=f"{gold_current_value:.2f}")
            st.metric(label="Purchase Value (€)", value=f"{gold_purchase_value:.2f}")
            
            if gold_profit_loss > 0:
                st.success(f"Profit: €{gold_profit_loss:.2f}")
            elif gold_profit_loss < 0:
                st.error(f"Loss: €{abs(gold_profit_loss):.2f}")
        
        # Silver results 🥈
        if silver_quantity > 0:
            st.subheader("Silver 🥈")
            st.metric(label="Current Value (€)", value=f"{silver_current_value:.2f}")
            st.metric(label="Purchase Value (€)", value=f"{silver_purchase_value:.2f}")
            
            if silver_profit_loss > 0:
                st.success(f"Profit: €{silver_profit_loss:.2f}")
            elif silver_profit_loss < 0:
                st.error(f"Loss: €{abs(silver_profit_loss):.2f}")

        # Total profit/loss summary in a visible way
        st.header("Total Profit/Loss")
        
        if total_profit_loss > 0:
            st.success(f"🎉 Total Profit: €{total_profit_loss:.2f}")
        elif total_profit_loss < 0:
            total_lost_gold = abs(min(gold_profit_loss, 0))
            total_lost_silver = abs(min(silver_profit_loss, 0))
            
            st.error(f"💔 Total Loss: €{abs(total_profit_loss):.2f}")
            
            # Breakdown of losses by metal
            if total_lost_gold > 0:
                st.write(f":sports_medal: Gold Loss: €{total_lost_gold:.2f}")
            if total_lost_silver > 0:
                st.write(f"🥈 Silver Loss: €{total_lost_silver:.2f}")
