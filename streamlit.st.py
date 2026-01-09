import streamlit as st
import pandas as pd


st.set_page_config(layout = "wide", page_title = "OLA DASHBOARD")

st.title("OLA DASHBOARD")
fl = st.file_uploader("upload a file", type = "xlsx")
if fl is not None:
    df = pd.read_excel(fl)
df = pd.read_excel("OLA_DataSet.xlsx")

st.success("Data loaded successfully")
st.dataframe(df)

pivot_table = pd.pivot_table(
    df,
    index="Vehicle_Type",
    columns="Booking_Status",
    values="Booking_ID",   # use any column, or None
    aggfunc="count",
    fill_value=0
)

st.subheader("Pivot Table View")
st.dataframe(pivot_table)



st.title("Vehicle Type vs Booking Value (Successful)")
# Clean columns
df['Vehicle_Type'] = df['Vehicle_Type'].str.strip()
df['Booking_Status'] = df['Booking_Status'].str.strip()
df['Booking_Value'] = pd.to_numeric(df['Booking_Value'], errors='coerce')

df = df.dropna(subset=['Vehicle_Type', 'Booking_Status', 'Booking_Value'])

# ✅ FIXED FILTER
Success_df = df[df['Booking_Status'].str.lower() == 'success']

# DEBUG
st.write("Total rows:", df.shape[0])
st.write("Successful rows:", Success_df.shape[0])

# STOP if empty
if Success_df.empty:
    st.warning("No successful bookings found")
    st.stop()

# Aggregation
summary = Success_df.groupby('Vehicle_Type').agg(
    total_booking_value=('Booking_Value', 'sum'),
    avg_booking_value=('Booking_Value', 'mean'),
    successful_bookings=('Booking_Value', 'count')
).reset_index()

# Display
st.subheader("Summary Table")
st.dataframe(summary)

st.subheader("Total Booking Value by Vehicle Type")
st.bar_chart(
    summary.set_index("Vehicle_Type")["total_booking_value"]
)



st.title("Vehicle Type vs Driver Ratings ")
df.Driver_Ratings = df.Driver_Ratings.astype(str).str.strip()
df.Vehicle_Type = df.Vehicle_Type.astype(str).str.strip()
df.Driver_Ratings = pd.to_numeric(df.Driver_Ratings, errors='coerce')

df = df.dropna(subset = ['Driver_Ratings', 'Vehicle_Type'])
summary = df.groupby('Vehicle_Type').agg(
    avg_Driver_Ratings=('Driver_Ratings', 'mean'),
).reset_index()

st.subheader("Summary Table")
st.dataframe(summary)

st.subheader("Total Driver Ratings by Vehicle Type")
st.bar_chart(
    summary.set_index("Vehicle_Type")["avg_Driver_Ratings"]
)

import streamlit as st
import pandas as pd
import altair as alt

st.title("Vehicle Type vs Customer Rating")

# ---- CLEAN DATA ----
df['Vehicle_Type'] = df['Vehicle_Type'].astype(str).str.strip()
df['Customer_Rating'] = pd.to_numeric(df['Customer_Rating'], errors='coerce')

df = df.dropna(subset=['Vehicle_Type', 'Customer_Rating'])

# ---- SUMMARY ----
summary = (
    df.groupby('Vehicle_Type', as_index=False)
      .agg(avg_Customer_Rating=('Customer_Rating', 'mean'))
)

# DEBUG CHECK (VERY IMPORTANT)
st.write("Summary Data:", summary)

# ---- PIE CHART ----
pie = alt.Chart(summary).mark_arc(innerRadius=0).encode(
    theta=alt.Theta('avg_Customer_Rating:Q'),
    color=alt.Color('Vehicle_Type:N', legend=alt.Legend(title="Vehicle Type")),
    tooltip=[
        alt.Tooltip('Vehicle_Type:N'),
        alt.Tooltip('avg_Customer_Rating:Q', format='.2f')
    ]
).properties(
    width=400,
    height=400
)

st.sidebar.header("Filters")

# Vehicle Type filter
Vehicle_Type = sorted(df['Vehicle_Type'].dropna().unique())
selected_vehicle = st.sidebar.multiselect(
    "Select Vehicle Type",
    Vehicle_Type,
    default=Vehicle_Type

)

st.subheader("Average Customer Rating by Vehicle Type")
st.altair_chart(pie, use_container_width=True)

st.title("Booking Status Breakdown")
df['Booking_Status'] = df['Booking_Status'].astype(str).str.strip()
def group(Booking_Status):
    if 'Success' in Booking_Status:
        return 'Success'
    if 'Canceled by Customer' in Booking_Status:
        return 'Canceled by Customer'
    if 'Canceled by Driver' in Booking_Status:
        return 'Cancelled by Driver'
    if 'Driver not Found' in Booking_Status:
        return 'Driver Not Found'


df['Booking_Status_Grouped'] = df['Booking_Status'].apply(group)
st.subheader('Raw Booking Status')
st.write(df['Booking_Status_Grouped'].value_counts())

summary = (df.groupby('Booking_Status_Grouped')
    .size()
    .reset_index(name='count')
           )
st.dataframe(summary)
st.subheader("Total Booking Status")
st.bar_chart(
    summary.set_index("Booking_Status_Grouped")["count"]
)

st.sidebar.header("Choose your Filters:")
Booking_Status = st.sidebar.multiselect("pick your status", df['Booking_Status'].unique())
if not Booking_Status:
    df2 = df.copy()
else:
    df2 = df[df['Booking_Status'].isin(Booking_Status)]

st.sidebar.header("Filters")
Payment_Method = st.sidebar.selectbox("pick your payment method", df['Payment_Method'].unique())


st.title("Ride Distance per Day by Vehicle Type")

# Ensure correct data types
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Ride_Distance'] = pd.to_numeric(df['Ride_Distance'], errors='coerce')
df = df.dropna(subset=['Date', 'Ride_Distance', 'Vehicle_Type'])

# Group data
daily_ride = (
    df.groupby(['Date', 'Vehicle_Type'])['Ride_Distance']
      .sum()
      .reset_index()
)

# Sidebar filters
vehicle_types = st.sidebar.multiselect(
    "Select Vehicle_Type",
    options=daily_ride['Vehicle_Type'].unique(),
    default=daily_ride['Vehicle_Type'].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [daily_ride['Date'].min(), daily_ride['Date'].max()]
)

# Apply filters
filtered_df = daily_ride[
    (daily_ride['Vehicle_Type'].isin(vehicle_types)) &
    (daily_ride['Date'] >= pd.to_datetime(date_range[0])) &
    (daily_ride['Date'] <= pd.to_datetime(date_range[1]))
]

# Display
st.subheader("Daily Ride Distance Table")
st.dataframe(filtered_df)

st.subheader("Ride Distance Trend by Vehicle Type")
st.line_chart(filtered_df, x='Date', y='Ride_Distance', color='Vehicle_Type')


st.title("Ride Distance per Day")

# Ensure correct data types
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Ride_Distance'] = pd.to_numeric(df['Ride_Distance'], errors='coerce')
df = df.dropna(subset=['Date', 'Ride_Distance'])

# 🔹 REMOVE TIME PART (IMPORTANT FIX)
df['Ride_Date'] = df['Date'].dt.date
# OR use this instead:
# df['Ride_Date'] = df['Date'].dt.normalize()

# 🔹 Group by DATE (not datetime)
daily_ride = (
    df.groupby(['Ride_Date'])['Ride_Distance']
      .sum()
      .reset_index()
)


# Apply filters
filtered_df = daily_ride[
    (daily_ride['Ride_Date'] >= date_range[0]) &
    (daily_ride['Ride_Date'] <= date_range[1])
]

# Display table
st.subheader("Daily Ride Distance Table")
st.dataframe(filtered_df)

# Line chart
st.subheader("Ride Distance Trend")
st.line_chart(
    filtered_df,
    x='Ride_Date',
    y='Ride_Distance',
)

line_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
    x=alt.X('Ride_Date:T', title='Date'),
    y=alt.Y('sum(Ride_Distance):Q', title='Total Ride Distance'),
)

labels = alt.Chart(filtered_df).mark_text(
    dy=-10,
    fontSize=11
).encode(
    x='Ride_Date:T',
    y='sum(Ride_Distance):Q',
    text=alt.Text('sum(Ride_Distance):Q', format='.1f'),
)
combined_chart = line_chart + labels
st.altair_chart(combined_chart, use_container_width=True)


st.title ("Revenue by Payment method")
df['Payment_Method'] = df['Payment_Method'].astype('category')
df['Booking_Value'] = pd.to_numeric(df['Booking_Value'], errors='coerce')
df.dropna(subset=['Payment_Method'], inplace=True)
st.subheader("Revenue by Vehicle Type")


line_chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X('Payment_Method', title='Payment Method'),
    y=alt.Y('sum(Booking_Value)', title='Booking Value'),
)
labels = alt.Chart(df).mark_text(
    dy=-10,
    fontSize=11
).encode(
    x='Payment_Method',
    y='sum(Booking_Value)',
    text=alt.Text('sum(Booking_Value):Q', format='.1f'),
)
combined_chart = line_chart + labels
st.altair_chart(combined_chart, use_container_width=True)


import numpy as np

st.title("Rating Distribution by Bins")

# Ensure ratings are numeric
df['Driver_Ratings'] = pd.to_numeric(df['Driver_Ratings'], errors='coerce')
df['Customer_Rating'] = pd.to_numeric(df['Customer_Rating'], errors='coerce')

# Drop invalid rows
df = df.dropna(subset=['Driver_Ratings', 'Customer_Rating', 'Vehicle_Type'])

# Define bins and labels
bins = [0, 1, 2, 3, 4, 5]
labels = [
    '0.0 - 1.0',
    '1.1 - 2.0',
    '2.1 - 3.0',
    '3.1 - 4.0',
    '4.1 - 5.0'
]

# Create bins
df['Driver_Rating_Bin'] = pd.cut(
    df['Driver_Ratings'],
    bins=bins,
    labels=labels,
    include_lowest=True
)

df['Customer_Rating_Bin'] = pd.cut(
    df['Customer_Rating'],
    bins=bins,
    labels=labels,
    include_lowest=True
)

# -------------------------
# Aggregation
# -------------------------

driver_summary = (
    df.groupby(['Vehicle_Type', 'Driver_Rating_Bin'])
    .size()
    .reset_index(name='Count')
)

customer_summary = (
    df.groupby(['Vehicle_Type', 'Customer_Rating_Bin'])
    .size()
    .reset_index(name='Count')
)

# -------------------------
# Streamlit Display
# -------------------------

st.subheader("Driver Rating Distribution")
st.dataframe(driver_summary)

st.subheader("Customer Rating Distribution")
st.dataframe(customer_summary)

import altair as alt

st.subheader("Driver Rating Distribution by Vehicle Type")

driver_bar = alt.Chart(driver_summary).mark_bar().encode(
    x=alt.X(
        'Driver_Rating_Bin:N',
        title='Driver Rating Bins',
        sort=labels
    ),
    y=alt.Y(
        'Count:Q',
        title='Number of Rides'
    ),
    color=alt.Color(
        'Vehicle_Type:N',
        legend=alt.Legend(title="Vehicle Type")
    ),
    tooltip=['Vehicle_Type', 'Driver_Rating_Bin', 'Count']
).properties(
    width=700,
    height=400
)

st.altair_chart(driver_bar, use_container_width=True)



st.subheader("Customer Rating Distribution by Vehicle Type")

customer_bar = alt.Chart(customer_summary).mark_bar().encode(
    x=alt.X(
        'Customer_Rating_Bin:N',
        title='Customer Rating Bins',
        sort=labels
    ),
    y=alt.Y(
        'Count:Q',
        title='Number of Rides'
    ),
    color=alt.Color(
        'Vehicle_Type:N',
        legend=alt.Legend(title="Vehicle Type")
    ),
    tooltip=['Vehicle_Type', 'Customer_Rating_Bin', 'Count']
).properties(
    width=700,
    height=400
)

st.altair_chart(customer_bar, use_container_width=True)

