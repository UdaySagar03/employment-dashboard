import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Employment Intelligence Dashboard",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Employment Intelligence Dashboard")
st.caption("Comprehensive analysis of workforce demographics, focusing on gender equality, education, and inclusion")

# -----------------------------
# Load and Process Data
# -----------------------------

@st.cache_data
def load_data():
    male = pd.read_csv("MaleWorkingData.csv")
    female = pd.read_csv("FemaleWorkingData.csv")

    df = pd.concat([male, female], ignore_index=True)
    df.columns = df.columns.str.strip()

    df = df[['gender', 'age', 'differentlyAbledStatus',
             'educationQualification', 'primaryOccupation']]

    df = df.dropna()
    df['primaryOccupation'] = df['primaryOccupation'].astype(str).str.upper().str.strip()
    df['educationQualification'] = df['educationQualification'].astype(str).str.upper().str.strip()
    df['differentlyAbledStatus'] = df['differentlyAbledStatus'].astype(str).str.strip()
    df['gender'] = df['gender'].astype(str).str.strip().str.title()

    bins = [18, 25, 35, 45, 60, 100]
    labels = ['18-25', '26-35', '36-45', '46-60', '60+']
    df['AgeGroup'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)

    return df

df = load_data()

# -----------------------------
# Sidebar Filters (shared)
# -----------------------------

st.sidebar.header("🔧 Filters")

gender_filter = st.sidebar.multiselect(
    "Gender",
    df['gender'].unique(),
    default=df['gender'].unique()
)

occupation_filter = st.sidebar.multiselect(
    "Occupation",
    sorted(df['primaryOccupation'].unique()),
    default=sorted(df['primaryOccupation'].unique())
)

education_filter = st.sidebar.multiselect(
    "Education",
    sorted(df['educationQualification'].unique()),
    default=sorted(df['educationQualification'].unique())
)

filtered = df[
    (df['gender'].isin(gender_filter)) &
    (df['primaryOccupation'].isin(occupation_filter)) &
    (df['educationQualification'].isin(education_filter))
]

# -----------------------------
# Tabs
# -----------------------------

tab1, tab2, tab3 = st.tabs(["📖 Introduction", "📊 Dashboard", "🔮 Outcomes & Predictions"])

# ==============================
# TAB 1 — INTRODUCTION
# ==============================
with tab1:
    st.markdown("## 🧩 Problem Statement")
    st.markdown("""
    Despite decades of progress, **gender inequality in the workforce** remains a critical challenge.
    Women and differently-abled individuals continue to face barriers in accessing quality employment,
    higher education, and leadership roles. This disparity is further compounded by age demographics
    and occupational segregation.

    This dashboard investigates the following core questions:
    - Are men and women equally distributed across occupations and education levels?
    - Which age groups dominate the workforce, and does this differ by gender?
    - How inclusive is the workforce for differently-abled individuals?
    - What patterns emerge when education and occupation are analyzed together?
    """)

    st.markdown("## 🎯 Objectives")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**1. Gender Distribution Analysis** — Understand the male-to-female ratio across the workforce and identify sectors with significant imbalance.")
        st.info("**2. Education & Occupation Mapping** — Explore how education levels correlate with occupation types for both genders.")
    with col2:
        st.info("**3. Age Demographics** — Identify dominant age groups and how workforce participation changes across life stages.")
        st.info("**4. Disability Inclusion** — Measure the representation of differently-abled workers and highlight inclusion gaps.")

    st.markdown("## 📂 Dataset Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("Male Records", f"{len(df[df['gender'] == 'Male']):,}")
    with col3:
        st.metric("Female Records", f"{len(df[df['gender'] == 'Female']):,}")

    st.markdown("")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unique Occupations", f"{df['primaryOccupation'].nunique()}")
    with col2:
        st.metric("Education Levels", f"{df['educationQualification'].nunique()}")
    with col3:
        st.metric("Age Range", f"{int(df['age'].min())} – {int(df['age'].max())} yrs")

    st.markdown("## 🔬 Methodology")
    st.markdown("""
    - **Data Sources:** Two separate CSV files for male and female working populations, merged into a unified dataset.
    - **Cleaning:** Removed null values, standardized text casing, and normalized gender labels.
    - **Analysis:** Descriptive statistics, cross-tabulations, and visual comparisons across gender, age, education, and occupation.
    - **Tools:** Python · Pandas · Plotly · Streamlit
    """)

    st.markdown("---")
    st.success("👉 Navigate to the **Dashboard** tab to explore the data visually.")

# ==============================
# TAB 2 — DASHBOARD
# ==============================
with tab2:

    # --- KPIs ---
    st.header("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    total_records = len(filtered)
    male_count = len(filtered[filtered['gender'].str.lower() == 'male'])
    female_count = len(filtered[filtered['gender'].str.lower() == 'female'])
    male_pct = (male_count / total_records * 100) if total_records > 0 else 0
    female_pct = (female_count / total_records * 100) if total_records > 0 else 0
    avg_age = filtered['age'].mean()

    with col1:
        st.metric("Total Records", f"{total_records:,}")
    with col2:
        st.metric("Male Employees", f"{male_count:,}", f"{male_pct:.1f}%")
    with col3:
        st.metric("Female Employees", f"{female_count:,}", f"{female_pct:.1f}%")
    with col4:
        st.metric("Average Age", f"{avg_age:.1f} yrs")

    if male_count > 0 and female_count > 0:
        ratio = female_count / male_count
        st.caption(f"👩/👨 Gender Ratio: {ratio:.2f}")

    st.markdown("---")

    # --- Row 1: Gender & Top Occupations ---
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(
            filtered, x='gender', title='Gender Distribution',
            color='gender', color_discrete_map={'Male': '#60a5fa', 'Female': '#f472b6'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        occ = filtered['primaryOccupation'].value_counts().head(10).reset_index()
        occ.columns = ['Occupation', 'Count']
        fig = px.bar(occ, x='Occupation', y='Count', title='Top 10 Occupations',
                     color='Count', color_continuous_scale='Purples')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # --- Education & Occupation ---
    st.header("🎓 Education & Occupation Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Education Levels")
        edu_counts = filtered['educationQualification'].value_counts().head(10)
        fig = px.bar(
            x=edu_counts.values, y=edu_counts.index, orientation='h',
            title="Top Education Qualifications",
            labels={'x': 'Count', 'y': 'Education Level'},
            color=edu_counts.values, color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Occupations")
        occ_counts = filtered['primaryOccupation'].value_counts().head(10)
        fig = px.bar(
            x=occ_counts.values, y=occ_counts.index, orientation='h',
            title="Most Common Occupations",
            labels={'x': 'Count', 'y': 'Occupation'},
            color=occ_counts.values, color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Gender Equality ---
    st.header("⚖️ Gender Equality Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Occupation by Gender")
        top_occupations = filtered['primaryOccupation'].value_counts().head(10).index
        occ_gender = filtered[filtered['primaryOccupation'].isin(top_occupations)]
        cross_tab = pd.crosstab(occ_gender['primaryOccupation'], occ_gender['gender'])
        gender_cols = [c for c in ['Male', 'Female'] if c in cross_tab.columns]
        fig = px.bar(
            cross_tab.reset_index(), x='primaryOccupation', y=gender_cols,
            title="Top Occupations by Gender", barmode='group',
            color_discrete_map={'Male': '#60a5fa', 'Female': '#f472b6'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Education by Gender")
        edu_gender = pd.crosstab(filtered['educationQualification'], filtered['gender']).head(10)
        edu_gender_cols = [c for c in ['Male', 'Female'] if c in edu_gender.columns]
        fig = px.bar(
            edu_gender.reset_index(), x='educationQualification', y=edu_gender_cols,
            title="Education Levels by Gender", barmode='group',
            color_discrete_map={'Male': '#60a5fa', 'Female': '#f472b6'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # --- Diversity Metrics ---
    st.subheader("📊 Diversity Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        gender_diversity = min(male_count, female_count) / max(male_count, female_count) if max(male_count, female_count) > 0 else 0
        st.metric("Gender Diversity Index", f"{gender_diversity:.2f}")
    with col2:
        male_avg_age = filtered[filtered['gender'] == 'Male']['age'].mean()
        female_avg_age = filtered[filtered['gender'] == 'Female']['age'].mean()
        age_diff = abs(male_avg_age - female_avg_age)
        st.metric("Age Difference (M-F)", f"{age_diff:.1f} yrs")
    with col3:
        disability_rate = (filtered['differentlyAbledStatus'] != 'No').sum() / len(filtered) * 100 if len(filtered) > 0 else 0
        st.metric("Disability Inclusion Rate", f"{disability_rate:.1f}%")

    st.markdown("---")
    st.caption("Dashboard created with Streamlit & Plotly. Data analysis for workforce diversity and inclusion.")

# ==============================
# TAB 3 — OUTCOMES & PREDICTIONS
# ==============================
with tab3:
    df_full = load_data()
    male_total = len(df_full[df_full['gender'] == 'Male'])
    female_total = len(df_full[df_full['gender'] == 'Female'])
    disability_pct = (df_full['differentlyAbledStatus'] != 'No').sum() / len(df_full) * 100
    top_occ = df_full['primaryOccupation'].value_counts().idxmax()
    top_edu = df_full['educationQualification'].value_counts().idxmax()
    gender_div = min(male_total, female_total) / max(male_total, female_total)

    st.markdown("## 🔍 Key Findings")
    st.markdown("Based on the full dataset analysis, the following patterns were observed:")

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ **Dominant Occupation:** {top_occ.title()} is the most common occupation across both genders.")
        st.success(f"✅ **Top Education Level:** {top_edu.title()} is the most prevalent qualification in the workforce.")
        st.success(f"✅ **Gender Diversity Index:** {gender_div:.2f} — {'Near balanced' if gender_div > 0.8 else 'Moderate imbalance' if gender_div > 0.5 else 'Significant imbalance'} between male and female workers.")
    with col2:
        st.warning(f"⚠️ **Disability Inclusion:** Only {disability_pct:.1f}% of the workforce are differently-abled, indicating room for improvement in inclusive hiring.")
        st.warning(f"⚠️ **Gender Gap:** With {male_total:,} males vs {female_total:,} females, {'women are underrepresented' if female_total < male_total else 'men are underrepresented'} in the dataset.")
        st.warning("⚠️ **Occupational Segregation:** Certain occupations show strong gender skew, suggesting systemic barriers to entry.")

    st.markdown("---")
    st.markdown("## 🔮 Predicted Outcomes & Recommendations")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 If Current Trends Continue")
        st.markdown("""
        - The gender gap in male-dominated occupations will persist without targeted intervention.
        - Workers with higher education qualifications will continue to dominate skilled roles.
        - Differently-abled individuals will remain underrepresented unless inclusive policies are enforced.
        - The 26–45 age group will remain the core workforce segment.
        """)
    with col2:
        st.markdown("### 💡 Recommended Actions")
        st.markdown("""
        - **Policy:** Introduce gender-balanced hiring quotas in male-dominated sectors.
        - **Education:** Invest in vocational training programs targeting underrepresented groups.
        - **Inclusion:** Mandate disability-friendly workplace infrastructure and hiring incentives.
        - **Monitoring:** Establish annual workforce diversity audits to track progress.
        """)

    st.markdown("---")
    st.markdown("## 📊 Outcome Summary")

    summary_data = {
        'Metric': [
            'Gender Diversity Index',
            'Disability Inclusion Rate',
            'Female Workforce Share',
            'Male Workforce Share'
        ],
        'Current Value': [
            f"{gender_div:.2f}",
            f"{disability_pct:.1f}%",
            f"{female_total / len(df_full) * 100:.1f}%",
            f"{male_total / len(df_full) * 100:.1f}%"
        ],
        'Target (Ideal)': ['1.00', '≥ 10%', '50%', '50%'],
        'Status': [
            '🟡 Needs Improvement' if gender_div < 0.9 else '🟢 Good',
            '🔴 Critical' if disability_pct < 5 else '🟡 Moderate',
            '🟡 Below Target' if female_total / len(df_full) < 0.45 else '🟢 On Track',
            '🟢 On Track' if male_total / len(df_full) < 0.65 else '🟡 Dominant'
        ]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.caption("Predictions are based on descriptive analysis of the current dataset. For predictive modeling, machine learning models such as logistic regression or random forest classifiers are recommended.")
