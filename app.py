import pandas as pd

# Load your Excel file
file_path = r"C:\Users\Louay\Downloads\DataSets (1) (1)\V100 الفواتير الصحية.xlsx"
df = pd.read_excel(file_path)

# Clean: remove rows with missing person ID
df = df[df['رقم الفرد للدراسة'].notnull()]

# Convert date column to datetime
df['تاريخ الفاتورة'] = pd.to_datetime(df['تاريخ الفاتورة'])

# Aggregate total dollars per person per month
df_agg = df.groupby(
    ['رقم الفرد للدراسة', pd.Grouper(key='تاريخ الفاتورة', freq='M')]
)['مجموع دولار'].sum().reset_index()

# Convert date for regression
df_agg['date_ordinal'] = df_agg['تاريخ الفاتورة'].apply(lambda x: x.toordinal())

# Store unique person IDs
unique_persons = df_agg['رقم الفرد للدراسة'].unique()

from sklearn.linear_model import LinearRegression

def predict_bill(person_id, target_date_str):
    import numpy as np
    target_date = pd.to_datetime(target_date_str)
    target_ordinal = target_date.toordinal()

    # Filter this person's data
    person_data = df_agg[df_agg['رقم الفرد للدراسة'] == person_id]

    if person_data.empty:
        return None

    X = person_data['date_ordinal'].values.reshape(-1, 1)
    y = person_data['مجموع دولار'].values

    model = LinearRegression()
    model.fit(X, y)

    pred = model.predict([[target_ordinal]])
    return max(pred[0], 0)  # Prevent negative predictions

if __name__ == "__main__":
    # Example test
    person_id = unique_persons[0]  # Pick the first person with data
    target_date = "2024-12-31"     # Test date

    prediction = predict_bill(person_id, target_date)

    if prediction is not None:
        print(f"Predicted bill for person {int(person_id)} on {target_date}: ${prediction:.2f}")
    else:
        print("No data available for prediction.")


import streamlit as st
import pandas as pd

# Cache the data loading for performance
@st.cache_data
def load_data():
    file_path = r"C:\Users\Louay\Downloads\DataSets (1) (1)\الادوية المزمنة للمستفيدين V100.xlsx"
    df = pd.read_excel(file_path)

    # Cleaning steps
    df = df[df['الاسم'].notnull()].copy()
    df['الموافقة'] = df['الموافقة'].fillna('غير مذكور')
    df['جهة الضمان'] = df['جهة الضمان'].fillna('غير معروف')
    df['تاريخ البطاقة'] = pd.to_datetime(df['تاريخ البطاقة'], errors='coerce')
    df = df[df['تاريخ البطاقة'].notnull()]
    return df

def main():
    st.title("📊 تحليل الأدوية المزمنة")

    df = load_data()

    # Sidebar filters
    st.sidebar.title("🔍 الفلاتر")

    analysis_type = st.sidebar.selectbox(
        "اختر نوع التحليل",
        ["أكثر الأدوية استخدامًا", "حسب جهة الضمان", "حسب الزمن"]
    )

    insurance_options = ["الكل"] + sorted(df["جهة الضمان"].dropna().unique().tolist())
    insurance_filter = st.sidebar.selectbox("جهة الضمان (اختياري)", options=insurance_options)

    # Filter dataframe by insurance if needed
    if insurance_filter != "الكل":
        df = df[df["جهة الضمان"] == insurance_filter]

    # Show analysis based on selection
    if analysis_type == "أكثر الأدوية استخدامًا":
        st.subheader("📌 أكثر الأدوية استخدامًا")
        top_drugs = df["DrugName"].value_counts().head(20)
        st.bar_chart(top_drugs)

    elif analysis_type == "حسب جهة الضمان":
        st.subheader("🏥 توزيع الأدوية حسب جهة الضمان")
        by_insurance = df.groupby("جهة الضمان")["DrugName"].count().sort_values(ascending=False)
        st.bar_chart(by_insurance)

    elif analysis_type == "حسب الزمن":
        st.subheader("⏳ عدد الأدوية المزمنة بمرور الوقت")
        df["شهر العلاج"] = df["تاريخ البطاقة"].dt.to_period("M").astype(str)
        monthly = df.groupby("شهر العلاج")["DrugName"].count()
        st.line_chart(monthly)

if __name__ == "__main__":
    main()

