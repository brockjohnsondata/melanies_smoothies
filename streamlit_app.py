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
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', {fruit_chosen},' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        

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
