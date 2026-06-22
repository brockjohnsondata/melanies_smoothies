import streamlit as st
import requests
import pandas as pd

st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')

cnx = st.connection("snowflake")
session = cnx.session()

# SAFE SQL QUERY
my_dataframe = session.sql("""
    SELECT FRUIT_NAME, SEARCH_ON
    FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS
""")

pd_df = my_dataframe.to_pandas()

st.dataframe(pd_df, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ''
    
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
    
        st.subheader (fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my. smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    if st.button('Submit Order'):

        session.sql(f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS
            (INGREDIENTS, NAME_ON_ORDER)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
