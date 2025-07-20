import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display


# Load data
file_path = r"C:\Users\Louay\Desktop\new system\cleaned_disease_medicine_data.xlsx"
df = pd.read_excel(file_path)

# Prepare data
df_vis = df.dropna(subset=['تاريخ الموافقة', 'DrugName'])
df_vis['DrugName'] = df_vis['DrugName'].str.strip().str.lower()
df_vis['تاريخ الموافقة'] = pd.to_datetime(df_vis['تاريخ الموافقة'])

# Group data for medicine demand over time
df_grouped = df_vis.groupby(['تاريخ الموافقة', 'DrugName']).size().reset_index(name='count')

# Unique medicines list
medicines = sorted(df_grouped['DrugName'].unique())

st.title("Medicine Data Dashboard")

tab1, tab2, tab3, tab4 = st.tabs([
    "Medicine Demand Over Time",
    "Top Medicines Bar Chart",
    "Patient Medication Summary & Journey Timeline",
    "Search & Filter Interface"
])


with tab1:
    st.header("Medicine Demand Over Time")
    selected_medicine = st.selectbox("Select a medicine", medicines)
    df_med = df_grouped[df_grouped['DrugName'] == selected_medicine]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df_med['تاريخ الموافقة'], df_med['count'], marker='o')
    ax.set_title(f'Medicine Demand Over Time: {selected_medicine}')
    ax.set_xlabel('Approval Date')
    ax.set_ylabel('Number of Prescriptions')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    st.header("Top Medicines Bar Chart")

    min_date = df_vis['تاريخ الموافقة'].min()
    max_date = df_vis['تاريخ الموافقة'].max()

    start_date, end_date = st.date_input(
        "Select date range:",
        value=(min_date.date(), max_date.date()),
        key="date_range"
    )

    # Filter data by date
    mask = (df_vis['تاريخ الموافقة'] >= pd.to_datetime(start_date)) & (df_vis['تاريخ الموافقة'] <= pd.to_datetime(end_date))
    df_filtered = df_vis.loc[mask]

    # Aggregate counts
    top_meds = df_filtered.groupby('DrugName').size().reset_index(name='count')
    top_meds = top_meds.sort_values('count', ascending=False)

    N = st.slider("Select number of top medicines to show:", 5, 30, 10)
    top_meds = top_meds.head(N)

    fig2, ax2 = plt.subplots(figsize=(10,6))
    ax2.barh(top_meds['DrugName'][::-1], top_meds['count'][::-1])
    ax2.set_xlabel("Number of Prescriptions")
    ax2.set_title(f"Top {N} Medicines from {start_date} to {end_date}")
    plt.tight_layout()
    st.pyplot(fig2)

with tab3:
   with tab3:  # Or rename the tab accordingly
    st.header("Patient Medication Summary & Journey Timeline")

    # Input box for patient name filter
    patient_filter = st.text_input("Enter patient name to see all medications and timeline:")

    if patient_filter:
        # Filter dataframe by patient name (case-insensitive)
        filtered_df = df_vis[df_vis['Patient_Name'].str.contains(patient_filter, case=False, na=False)]

        if not filtered_df.empty:
            # Show all medication details for the filtered patient(s)
            st.subheader("Medication Details")
            st.dataframe(filtered_df[['Patient_Name', 'DrugName', 'تاريخ الموافقة', 'تاريخ انتهاء العلاج', 'رقم البطاقة']])

            # Sort data by approval date for timeline and pie chart
            filtered_df = filtered_df.sort_values('تاريخ الموافقة')

            # Timeline plot
            st.subheader("Medication History Timeline")
            fig, ax = plt.subplots(figsize=(12, 4))
            for i, (idx, row) in enumerate(filtered_df.iterrows()):
                ax.plot(row['تاريخ الموافقة'], i, 'o')
                ax.text(row['تاريخ الموافقة'], i, row['DrugName'], fontsize=9, ha='left', va='center')
            ax.set_yticks([])
            ax.set_xlabel("Approval Date")
            ax.set_title(f"Medication History Timeline for patient(s) matching '{patient_filter}'")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

            # Pie chart of medicine distribution
            st.subheader("Medicine Distribution")
            medicine_counts = filtered_df['DrugName'].value_counts()
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            # Reshape and reorder Arabic labels for proper display
            reshaped_labels = [get_display(arabic_reshaper.reshape(label)) for label in medicine_counts.index]
            
            ax2.pie(medicine_counts, labels=reshaped_labels, autopct='%1.1f%%', startangle=140)

            ax2.set_title(f"Medicine Distribution for patient(s) matching '{patient_filter}'")
            st.pyplot(fig2)

        else:
            st.write("No records found for this patient name.")
    else:
        st.write("Please enter a patient name above to view their medication details and history.")

import matplotlib.dates as mdates

with tab4:
    st.header("Search & Filter Interface")

    # Prepare autocomplete lists
    patient_names = df_vis['Patient_Name'].dropna().unique()
    medicine_names = df_vis['DrugName'].dropna().unique()

    # Patient name autocomplete (using st.text_input with suggestions)
    patient_input = st.text_input("Search by patient name", "")
    filtered_patients = [p for p in patient_names if patient_input.lower() in p.lower()]

    # Medicine name autocomplete
    medicine_input = st.text_input("Search by medicine name", "")
    filtered_meds = [m for m in medicine_names if medicine_input.lower() in m.lower()]

    # Date range filter
    min_date = df_vis['تاريخ الموافقة'].min().date()
    max_date = df_vis['تاريخ الموافقة'].max().date()
    start_date, end_date = st.date_input(
        "Select approval date range",
        value=(min_date, max_date)
    )

    # Apply filters to data
    filtered_df = df_vis.copy()

    if patient_input:
        filtered_df = filtered_df[filtered_df['Patient_Name'].str.contains(patient_input, case=False, na=False)]
    if medicine_input:
        filtered_df = filtered_df[filtered_df['DrugName'].str.contains(medicine_input, case=False, na=False)]
    if isinstance(start_date, tuple):
        start_date, end_date = start_date  # If user selects range
    filtered_df = filtered_df[
        (filtered_df['تاريخ الموافقة'] >= pd.to_datetime(start_date)) &
        (filtered_df['تاريخ الموافقة'] <= pd.to_datetime(end_date))
    ]

    # Show filtered data
    st.dataframe(filtered_df[['Patient_Name', 'DrugName', 'تاريخ الموافقة', 'تاريخ انتهاء العلاج']])