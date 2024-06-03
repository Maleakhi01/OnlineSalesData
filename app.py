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

df['Date'] = pd.to_datetime(df['Date'])

# Extract month from the 'Date' column and create a new 'Month' column
df['Month'] = df['Date'].dt.month
df.drop(columns=['Date'], inplace=True)

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

month = st.sidebar.multiselect(
    "Select the Month:",
    options= df["Month"].unique(),
    default= df["Month"].unique()
)

df_selection = df.query(
    "`Product Category` == @product_category & Region == @region & `Payment Method` == @payment_method & Month == @month"
)


left_column, middle_column, right_column = st.columns(3)
with left_column:
    if "Total Revenue" in df_selection.columns:
        total_revenue = int(df_selection["Total Revenue"].sum())
        st.markdown(
            f"""
            <div style='
                padding: 20px;
                background-color: #f0f0f0;
                border-radius: 5px;
                box-shadow: 5px 5px 15px 5px rgba(0, 0, 0, 0.1);
            '>
                <h3 style='text-align: center;'>Total Revenue</h3>
                <h2 style='text-align: center;'>${total_revenue}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.write("The column 'Total Revenue' does not exist in the data.")
with middle_column:
    region_revenue = df_selection.groupby('Region')['Total Revenue'].sum().reset_index()
    top_region = region_revenue.loc[region_revenue['Total Revenue'].idxmax()]
    top_region_revenue = top_region["Region"]
    st.markdown(
            f"""
            <div style='
                padding: 20px;
                background-color: #f0f0f0;
                border-radius: 5px;
                box-shadow: 5px 5px 15px 5px rgba(0, 0, 0, 0.1);
            '>
                <h3 style='text-align: center;'>Top Region</h3>
                <h2 style='text-align: center;'>{top_region_revenue}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
with right_column:
    average_transactions = round(df_selection["Total Revenue"].mean(),2)
    st.markdown(
            f"""
            <div style='
                padding: 20px;
                background-color: #f0f0f0;
                border-radius: 5px;
                box-shadow: 5px 5px 15px 5px rgba(0, 0, 0, 0.1);
            '>
                <h3 style='text-align: center;'>Average Transactions</h3>
                <h2 style='text-align: center;'>${average_transactions}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

revenue_by_month = df_selection.groupby(by=["Month"]).sum()[["Total Revenue"]].reset_index()
st.subheader(f"Revenue by Month")
fig = px.line(revenue_by_month, x='Month', y='Total Revenue')
fig.update_traces(mode='markers+lines', marker=dict(size=10))
fig.update_xaxes(title='Month', tickmode='array', tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
fig.update_yaxes(title='Total Revenue')
st.plotly_chart(fig)

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
        height=425
    )

    text = chart.mark_text(
        align='center',
        baseline='middle',
        dx=2  # Adjust horizontal position of text labels
    ).encode(
        text=alt.Text("Total Revenue:Q", format=".2f"),  # Display the revenue values
    )

    # Layer text on top of the bar chart
    chart_with_text = (chart + text)

    st.altair_chart(chart_with_text, use_container_width=True)

with right_revenue:
    revenue_by_region = df_selection.groupby(by=["Region"]).sum()[["Total Revenue"]].sort_values(by="Total Revenue", ascending=False).reset_index()
            
    st.subheader(f"Revenue by Region")

    chart_region = alt.Chart(revenue_by_region).mark_bar(size=20).encode(
        y=alt.Y("Region:N", sort="-x"),
        x=alt.X("Total Revenue:Q"),
        tooltip=["Region", "Total Revenue"]
    ).properties(
        width=400,
        height=425
    )
    
    # Define text layer
    text = chart_region.mark_text(
        align='center',
        baseline='middle',
        dx=3 
    ).encode(
        text=alt.Text("Total Revenue:Q", format=".2f"),  # Display the revenue values
    )

    # Layer text on top of the bar chart
    chart_with_text = (chart_region + text)

    st.altair_chart(chart_with_text, use_container_width=True)


left_transactions, right_transactions = st.columns(2)

with left_transactions:
    st.subheader(f"Transaction by Payment Method")
    transaction_counts = df_selection['Payment Method'].value_counts().reset_index()
    transaction_counts.columns = ['Payment Method', 'Transaction Count']

    try:
        fig = go.Figure(data=[go.Pie(labels=transaction_counts['Payment Method'], 
                                    values=transaction_counts['Transaction Count'])])
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error occurred: {e}")

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


top_10_left, top_10_right = st.columns(2)

with top_10_left:
    st.subheader(f"Top 10 Products by Units Sold")
    top_products = df_selection.groupby("Product Name").sum()["Units Sold"].sort_values(ascending=False).head(10)
    st.write(top_products)

with top_10_right:
    st.subheader(f"Top 10 Products by Revenue")
    top_products_revenue = df_selection.groupby("Product Name").sum()["Total Revenue"].sort_values(ascending=False).head(10)
    st.write(top_products_revenue)

