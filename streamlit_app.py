# Import python packages
import streamlit as st
import requests
import pandas as pd

# ---------------------------
# APP HEADER
# ---------------------------
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# ---------------------------
# USER INPUT
# ---------------------------
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# ---------------------------
# SNOWFLAKE CONNECTION
# ---------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# 🔥 FORCE CONTEXT (this fixes most Streamlit Snowflake issues)
session.sql("USE DATABASE smoothies").collect()
session.sql("USE SCHEMA public").collect()
session.sql("USE WAREHOUSE COMPUTE_WH").collect()

# ---------------------------
# GET DATA FROM SNOWFLAKE (SAFE SQL)
# ---------------------------
my_dataframe = session.sql("""
    SELECT FRUIT_NAME, SEARCH_ON
    FROM smoothies.public.fruit_options
""")

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Debug view
st.dataframe(pd_df, use_container_width=True)

# ---------------------------
# MULTISELECT
# ---------------------------
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    sorted(pd_df['FRUIT_NAME'].dropna().unique().tolist()),
    max_selections=5
)

# ---------------------------
# PROCESS SELECTIONS
# ---------------------------
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Safe lookup for SEARCH_ON
        match = pd_df[pd_df['FRUIT_NAME'] == fruit_chosen]

        if not match.empty:
            search_on = match['SEARCH_ON'].iloc[0]
        else:
            search_on = "Not found"

        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        # API call
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(
                "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
            )
            st.dataframe(response.json(), use_container_width=True)

        except Exception as e:
            st.error(f"API error for {fruit_chosen}: {e}")

    # ---------------------------
    # ORDER SUBMISSION
    # ---------------------------
    st.write("---")
    st.write("### Submit your order")

    if st.button('Submit Order'):

        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders
            (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """

        session.sql(my_insert_stmt).collect()

        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )
