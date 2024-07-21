import pandas as pd
from PIL import Image
import streamlit as st
import plotly.express as px
from streamlit.components.v1 import html

st.set_page_config(page_title="Project Property")


# Background
st.markdown(
    """
    <style>
    # [data-testid="stHeader"] {
        background-color: darkpink;
    }
    </style>
    """
    """
    <style>
    [data-testid="stApp"] {
        background: linear-gradient(180deg, rgba(295, 152, 223, 1) 0%, rgba(0,0,0) 47%, rgba(0,0,0) 100%);
        height:auto;
    }
    </style>
    """
    """
    <style>
    [data-testid="stSlider"] {
        background-color: #EEF0F4;
        border-radius: 5px;
        padding: 10px;
    }
    </style>
    """
    """
    <style>
        .stPlotlyChart {
            border-radius: 10px;
            overflow: hidden; /* This is important to ensure the border radius is applied properly */
        }
    </style>
    """,
    unsafe_allow_html=True
)

with st.container():

    # HOME: Property logo
    # col1, col2, col3 = st.columns([1, 2, 1])

    # Load in images
    logo = Image.open('app/assets/logo.png')
    
    st.image(logo, use_column_width=True)
    st.markdown('')  # Empty markdown line for spacing
    st.markdown('')  # Empty markdown line for spacing
    st.markdown('')  # Empty markdown line for spacing
    st.markdown('')  # Empty markdown line for spacing
    st.markdown('')  # Empty markdown line for spacing


    # st.markdown('')
    # st.write("""Project Property&#8482; is a property crawler which helps you collect property data.""")


# Home Page
