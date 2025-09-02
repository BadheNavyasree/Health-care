import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Healthcare Data Dashboard", layout="wide")
st.title("Healthcare Patient Data Analysis Dashboard")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your healthcare CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    # Data preprocessing
    data['Date of Admission'] = data['Date of Admission'].replace('########', np.nan)
    data['AdmissionDate'] = pd.to_datetime(data['Date of Admission'], errors='coerce')
    if data['AdmissionDate'].notna().any():
        data['Month'] = data['AdmissionDate'].dt.to_period('M')
    else:
        data['Month'] = pd.NaT

    data['Diagnosis'] = data.get('Medical Condition', pd.Series(np.nan))

    # Sidebar filters
    st.sidebar.header("Filters")
    age_min, age_max = int(data['Age'].min()), int(data['Age'].max())
    age_range = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))
    gender_options = list(data['Gender'].dropna().unique())
    selected_genders = st.sidebar.multiselect("Select Gender(s)", gender_options, default=gender_options)
    admission_types = list(data['Admission Type'].dropna().unique())
    selected_admission_types = st.sidebar.multiselect("Select Admission Type(s)", admission_types, default=admission_types)

    # Apply filters
    filtered_data = data[
        (data['Age'] >= age_range[0]) & (data['Age'] <= age_range[1]) &
        (data['Gender'].isin(selected_genders)) &
        (data['Admission Type'].isin(selected_admission_types))
    ]

    # Show key metrics
    st.sidebar.subheader("Key Metrics")
    st.sidebar.metric("Total Patients", len(filtered_data))
    avg_billing = filtered_data['Billing Amount'].mean()
    st.sidebar.metric("Average Billing Amount", f"${avg_billing:,.2f}" if not np.isnan(avg_billing) else "N/A")

    # Main dashboard layout
    col1, col2 = st.columns(2)

    with col1:
        # Diagnosis Frequency
        st.subheader("Diagnosis Frequency")
        if 'Diagnosis' in filtered_data.columns and not filtered_data['Diagnosis'].isnull().all():
            diag_counts = filtered_data['Diagnosis'].value_counts()
            fig_diag = px.bar(diag_counts, x=diag_counts.index, y=diag_counts.values,
                              labels={"x": "Diagnosis", "y": "Count"}, title="Diagnosis Frequency")
            st.plotly_chart(fig_diag, use_container_width=True)
        else:
            st.info("No diagnosis data available.")

    with col2:
        # Monthly Patient Admissions
        st.subheader("Monthly Patient Admissions")
        if 'Month' in filtered_data.columns and filtered_data['Month'].notna().any():
            monthly_adm = filtered_data.groupby('Month').size().reset_index(name='Admissions')
            monthly_adm['Month'] = monthly_adm['Month'].dt.to_timestamp()
            fig_monthly = px.line(monthly_adm, x='Month', y='Admissions', 
                                  title="Monthly Patient Admissions")
            st.plotly_chart(fig_monthly, use_container_width=True)
        else:
            st.info("Admission date data is missing; cannot plot monthly admissions.")

    # Show raw data toggle
    if st.checkbox("Show filtered raw data"):
        st.dataframe(filtered_data)

else:
    st.info("Please upload a healthcare CSV file to get started.")
