import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="DataMart Analytics", layout="wide")
st.title("📊 DataMart Intelligence Platform")
st.markdown("Welcome to your data engineering dashboard!")

data = pd.DataFrame({
    'Category': ['Electronics', 'Books', 'Clothing', 'Home', 'Sports'],
    'Sales': [5000, 3000, 4000, 3500, 2000]
})

fig = px.bar(data, x='Category', y='Sales', title='Sales by Category')
st.plotly_chart(fig, use_container_width=True)