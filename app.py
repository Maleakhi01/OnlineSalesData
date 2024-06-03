import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("Online Sales Data Dashboard")

# Read the CSV file
file_path = "Online Sales Data.csv"
df = pd.read_csv(file_path)

st.sidebar.header("Please Filter Here:")

product_category = st.sidebar.multiselect(
    "Select the Product Category:",
    options=df["Product Category"].unique(),
    default=df["Product Category"].unique()
)

region = st.sidebar.multiselect(
    "Select the Region:",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

payment_method = st.sidebar.multiselect(
    "Select the Payment Method:",
    options=df["Payment Method"].unique(),
    default=df["Payment Method"].unique()
)

df_selection = df.query(
    "`Product Category` == @product_category & Region == @region & `Payment Method` == @payment_method"
)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    if "Total Revenue" in df_selection.columns:
        total_revenue = int(df_selection["Total Revenue"].sum())
        st.subheader(f"Total Revenue")
        st.subheader(f"${total_revenue}")
    else:
        st.write("The column 'Total Revenue' does not exist in the data.")
with middle_column:
    region_revenue = df_selection.groupby('Region')['Total Revenue'].sum().reset_index()
    top_region = region_revenue.loc[region_revenue['Total Revenue'].idxmax()]
    top_region_revenue = top_region["Region"]
    st.subheader(f"Top Region in Revenue")
    st.subheader(f"{top_region_revenue}")
with right_column:
    average_transactions = round(df_selection["Total Revenue"].mean(),2)
    st.subheader(f"Average Revenue per Transactions")
    st.subheader(f"${average_transactions}")

st.markdown("---")

# st.dataframe(df_selection)

left_revenue, right_revenue = st.columns(2)

with left_revenue:
    revenue_by_category = df_selection.groupby(by=["Product Category"]).sum()[["Total Revenue"]].sort_values(by="Total Revenue", ascending=False).reset_index()
        
    st.subheader(f"Revenue by Category")

    chart = alt.Chart(revenue_by_category).mark_bar(size=20).encode(
        y=alt.Y("Product Category:N", sort="-x"),
        x=alt.X("Total Revenue:Q"),
        tooltip=["Product Category", "Total Revenue"]
    ).properties(
        width=400,
        height=alt.Step(10 * len(revenue_by_category)) 
    )

    st.altair_chart(chart, use_container_width=True)

with right_revenue:
    revenue_by_region = df_selection.groupby(by=["Region"]).sum()[["Total Revenue"]].sort_values(by="Total Revenue", ascending=False).reset_index()
            
    st.subheader(f"Revenue by Region")

    chart_region = alt.Chart(revenue_by_region).mark_bar(size=20).encode(
        y=alt.Y("Region:N", sort="-x"),
        x=alt.X("Total Revenue:Q"),
        tooltip=["Region", "Total Revenue"]
    ).properties(
        width=400,
        height=alt.Step(10 * len(revenue_by_region))
    )
    st.altair_chart(chart_region, use_container_width=True)

try:
    df_selection['Date'] = pd.to_datetime(df_selection['Date'])
except Exception as e:
    st.error(f"Error occurred while converting 'Date' column to datetime: {e}")

try:
    df_selection['Month'] = df_selection['Date'].dt.month
except Exception as e:
    st.error(f"Error occurred while extracting month from 'Date' column: {e}")

try:
    revenue_by_month = df_selection.groupby('Month')['Total Revenue'].sum().reset_index()
except Exception as e:
    st.error(f"Error occurred while calculating revenue by month: {e}")

st.subheader(f"Revenue by Month")
try:
    fig = px.line(revenue_by_month, x='Month', y='Total Revenue')
    fig.update_traces(mode='markers+lines', marker=dict(size=10))
    fig.update_xaxes(title='Month', tickmode='array', tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    fig.update_yaxes(title='Total Revenue')
    st.plotly_chart(fig)
except Exception as e:
    st.error(f"Error occurred while plotting line chart: {e}")


left_transactions, right_transactions = st.columns(2)

with left_transactions:
    st.subheader(f"Transaction by Payment Method")
    transaction_counts = df_selection['Payment Method'].value_counts().reset_index()
    transaction_counts.columns = ['Payment Method', 'Transaction Count']

    chart_transaction_method = alt.Chart(transaction_counts).mark_bar(size=20).encode(
        x='Transaction Count',
        y=alt.Y('Payment Method', sort='-x'),
        tooltip=['Payment Method', 'Transaction Count']
    ).properties(
        width=600,
        height=alt.Step(10*len(transaction_counts))
    )

    st.altair_chart(chart_transaction_method, use_container_width=True)

with right_transactions:
    st.subheader(f"Transactions by Product Category")
    transaction_counts_by_product = df_selection['Product Category'].value_counts().reset_index()
    transaction_counts_by_product.columns = ['Product Category', 'Transaction Count']

    try:
        fig = go.Figure(data=[go.Pie(labels=transaction_counts_by_product['Product Category'], 
                                    values=transaction_counts_by_product['Transaction Count'])])
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error occurred: {e}")