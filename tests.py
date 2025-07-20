import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# Load final merged dataset (diseases + names + medications)
df = pd.read_excel("C:/Users/Louay/Desktop/new system/merged_disease_data.xlsx")


# Convert date to datetime
df["تاريخ المرض"] = pd.to_datetime(df["تاريخ المرض"])

st.set_page_config(page_title="Lifelong Disease Insights", layout="wide")
st.title("📊 Lifelong Disease Insights Dashboard")

# =============================
# 1. Patient Profile & Timeline
# =============================
st.header("1. 📋 Patient Profile & Timeline")
selected_name = st.selectbox("🔍 Select a patient", df["Real_Name"].dropna().unique())
patient_data = df[df["Real_Name"] == selected_name].sort_values(by="تاريخ المرض")
st.subheader("🩺 Disease History")
st.dataframe(patient_data[["نوع المرض", "تاريخ المرض", "disease_category"]])

#st.subheader("💊 Medications")
#st.text(patient_data["Medications"].iloc[0] if pd.notna(patient_data["Medications"].iloc[0]) else "No medications found")

#fig1, ax1 = plt.subplots()
#sns.scatterplot(data=patient_data, x="تاريخ المرض", y="نوع المرض", ax=ax1)
#plt.xticks(rotation=45)
#st.pyplot(fig1)

# =============================
# 2. Most Common Diseases
# =============================
st.header("2. 📊 Most Common Diseases")
top_diseases = df["نوع المرض"].value_counts().head(10)
st.bar_chart(top_diseases)

# =============================
# 3. Disease Trend Over Time
# =============================
st.header("3. 📅 Disease Cases Over Time")
monthly = df.groupby(df["تاريخ المرض"].dt.to_period("M")).size()
monthly.index = monthly.index.astype(str)
st.line_chart(monthly)

# =============================
# 4. Disease Categories (Bar Chart)
# =============================
st.header("4. 📂 Disease Category Distribution")
category_counts = df["disease_category"].value_counts()
st.bar_chart(category_counts)

# =============================
# 5. Patient Count per Disease
# =============================
st.header("5. 👥 Patient Count per Disease")
disease_patient_counts = df.groupby("نوع المرض")["Real_Name"].nunique().sort_values(ascending=False)
st.dataframe(disease_patient_counts.reset_index().rename(columns={"Real_Name": "Patient Count"}))

# =============================
# 6. Filter by Date Range
# =============================
st.header("6. 📆 Filter by Diagnosis Date")
start = st.date_input("From", df["تاريخ المرض"].min())
end = st.date_input("To", df["تاريخ المرض"].max())
filtered = df[(df["تاريخ المرض"] >= pd.to_datetime(start)) & (df["تاريخ المرض"] <= pd.to_datetime(end))]
st.dataframe(filtered)

# =============================
# 7. Search by Name or Disease
# =============================
st.header("7. 🔎 Search")
query = st.text_input("Search by real name or disease:")
if query:
    results = df[
        df["Real_Name"].str.contains(query, case=False, na=False) |
        df["نوع المرض"].str.contains(query, case=False, na=False)
    ]
    st.dataframe(results)

# =============================
# 8. Disease Trend by Category
# =============================
st.header("8. 📈 Disease Trend by Category")
selected_cat = st.selectbox("Select Category", df["disease_category"].dropna().unique())
cat_df = df[df["disease_category"] == selected_cat]
cat_trend = cat_df.groupby(cat_df["تاريخ المرض"].dt.to_period("M")).size()
cat_trend.index = cat_trend.index.astype(str)
st.line_chart(cat_trend)

# =============================
# 9. Summary Metrics
# =============================
st.header("9. 🧮 Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Patients", df["Real_Name"].nunique())
col2.metric("Unique Diseases", df["نوع المرض"].nunique())
col3.metric("Disease Categories", df["disease_category"].nunique())