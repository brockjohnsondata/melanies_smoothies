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

# ---------------------------
# GET DATA FROM SNOWFLAKE
# ---------------------------
my_dataframe = session.sql("""
    SELECT FRUIT_NAME, SEARCH_ON
    FROM smoothies.public.fruit_options
""")

pd_df = my_dataframe.to_pandas()

st.dataframe(pd_df, use_container_width=True)

# ---------------------------
# MULTISELECT (fruit names only)
# ---------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    sorted(pd_df["FRUIT_NAME"].dropna().unique().tolist()),
    max_selections=5
)

# ---------------------------
# PROCESS ORDER
# ---------------------------
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # ---------------------------
        # SEARCH_ON VALUE (FINISHING TOUCHES REQUIREMENT)
        # ---------------------------
        match = pd_df[pd_df["FRUIT_NAME"] == fruit_chosen]

        search_on = match["SEARCH_ON"].iloc[0] if not match.empty else "Not found"

        st.write(f"Search value for {fruit_chosen}: {search_on}")

        # ---------------------------
        # API CALL (FIXED URL)
        # ---------------------------
        try:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
            )

            st.subheader(f"{fruit_chosen} Nutrition Information")
            st.dataframe(response.json(), use_container_width=True)

        except Exception as e:
            st.error(f"API error for {fruit_chosen}: {e}")

    # ---------------------------
    # SUBMIT ORDER TO SNOWFLAKE
    # ---------------------------
    st.write("---")
    st.write("### Submit your order")

    if st.button("Submit Order"):

        session.sql(f"""
            INSERT INTO smoothies.public.orders
            (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """).collect()

        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )
