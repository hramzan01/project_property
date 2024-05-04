import streamlit as st
import pandas as pd 
import plotly.express as px

# Home Page
# Load data
df = pd.read_csv('data/processed_data/processed_property_search.csv')


# Create Plotly figure
fig = px.scatter_mapbox(
    df,
    lat='lat',
    lon='lon',
    mapbox_style='carto-positron',
    zoom=11.5,
    hover_data={'name': True,
                'beds': True,
                'wc': True,
                'garden': True,
                'area_sft': True,
                'price': True,
                'agency': True,
                'reno_cost': True,
                'yearly_rev': True
    }
)

fig.update_traces(marker=dict(size=10))

fig.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0},
)

# Display Plotly figure in Streamlit
st.title('Property Optimiser')
st.plotly_chart(fig)
st.dataframe(df)

# Select numeric columns only
numeric_df = df.select_dtypes(include=['float64', 'int64'])

# Standardize the data
df_standardized = (numeric_df - numeric_df.mean()) / numeric_df.std()
df_standardized = df_standardized[['price','reno_cost','yearly_rev']]

# Plot the standardized data
fig2 = px.line(df_standardized, x=df.name, y=df_standardized.columns,
               labels={'value': 'Standardized Value', 'variable': 'Variable', 'index': 'Date'},
               title="Standardized Numeric Columns Over Time")

# Customize layout to hide grid lines and set transparent background
fig2.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                   plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

# Display Plotly figure in Streamlit
st.plotly_chart(fig2)
