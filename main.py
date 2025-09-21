# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
from datetime import datetime

# Optional PDF export
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

st.set_page_config(page_title="Sales & Outstanding System", layout="wide")

# --- CSS ---
st.markdown(
    """
    <style>
    .reportview-container {
        background: linear-gradient(90deg, #f8fafc, #eef2ff);
    }
    .card {
        background: white;
        padding: 12px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(15,23,42,0.06);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg,#111827,#0b1220);
        color: white;
    }
    .stButton>button {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚡ Sales Tracker — Outstanding & Commission System")

# Navigation
nav = st.sidebar.radio("Navigation", ["Home", "Dashboard", "Sales Analysis", "Customer Analysis", "All Customer Outstanding"])

# Required columns
REQUIRED_COLUMNS = [
    "date", "order no", "executive name", "customer name",
    "opening balance", "sales value", "sales return",
    "sales in and out", "paid amount", "cashback", "commission"
]


# Home page
if nav == "Home":
    st.header("Welcome to Sales Tracker")
    st.markdown("""
    This application helps you track sales, outstanding amounts, and commissions.
    
    **To get started:**
    1. Upload an Excel or CSV file with the required columns
    2. Use the navigation menu to explore different views
    3. Apply filters using the sidebar options
    4. Export data using the download buttons
    
    **Required columns in your data:**
    - date, order no, executive name, customer name
    - opening balance, sales value, sales return
    - sales in and out, paid amount, cashback, commission
    """)
    
    # Show sample data structure
    sample_data = pd.DataFrame(columns=REQUIRED_COLUMNS)
    st.write("Sample data structure:")
    st.dataframe(sample_data)
    st.stop()

# Upload file
uploaded_file = st.file_uploader("Upload Excel/CSV file", type=['xlsx', 'xls', 'csv'])
df = None

def validate_and_prepare(df_raw):
    df = df_raw.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return None, missing

    # Date parse
    df['date'] = pd.to_datetime(df['date'], errors="coerce")

    # Numeric columns
    num_cols = ['opening balance','sales value','sales return',
                'sales in and out','paid amount','cashback','commission']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col].fillna(0), errors='coerce').fillna(0)

    # Outstanding
    df['outstanding'] = (
        df['opening balance'] + df['sales value']
        - df['sales return'] - df['sales in and out']
        - df['paid amount'] - df['cashback'] - df['commission']
    )

    # Commission
    df['exec_commission_calc'] = df['paid amount'] * 0.01
    return df, []

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            raw = pd.read_csv(uploaded_file)
        else:
            # Specify engine for better compatibility
            raw = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        st.error(f"File read error: {e}")
        st.stop()

    df, missing = validate_and_prepare(raw)
    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()
        
    # Show file info
    st.sidebar.success(f"File loaded successfully: {uploaded_file.name}")
    st.sidebar.info(f"Data range: {df['date'].min().date()} to {df['date'].max().date()}")
else:
    st.info("Upload your file to start.")
    st.stop()

# Date filter
min_date, max_date = df['date'].min(), df['date'].max()
date_from, date_to = st.sidebar.date_input("Date range", [min_date.date(), max_date.date()])

# Validate date range
if date_from > date_to:
    st.sidebar.error("Error: End date must be after start date.")
    st.stop()

df_filtered = df[(df['date'] >= pd.to_datetime(date_from)) & (df['date'] <= pd.to_datetime(date_to))]

# Executive filter
executives = df_filtered['executive name'].unique()
selected_executives = st.sidebar.multiselect(
    "Filter by Executive", 
    options=executives,
    default=executives
)
df_filtered = df_filtered[df_filtered['executive name'].isin(selected_executives)]

# Aggregations
total_sales = df_filtered['sales value'].sum()
total_paid = df_filtered['paid amount'].sum()
total_outstanding = df_filtered['outstanding'].sum()
total_exec_commission = df_filtered['exec_commission_calc'].sum()
team_leader_commission = total_paid * 0.002

# ---------------- PAGES ----------------
if nav == "Dashboard":
    st.header("📊 Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"{total_sales:,.2f}")
    col2.metric("Total Paid", f"{total_paid:,.2f}")
    col3.metric("Outstanding", f"{total_outstanding:,.2f}")
    col4.metric("Exec Commission", f"{total_exec_commission:,.2f}")

    st.write(f"**Team Leader Commission (0.2%): {team_leader_commission:,.2f}**")

    # Charts
    sales_exec = df_filtered.groupby('executive name').agg({'sales value':'sum','paid amount':'sum'}).reset_index()
    if not sales_exec.empty:
        fig1 = px.bar(sales_exec.melt(id_vars='executive name'), x='executive name', y='value',
                      color='variable', barmode='group', title="Sales vs Paid by Executive")
        st.plotly_chart(fig1, use_container_width=True)

    cust_out = df_filtered.groupby('customer name')['outstanding'].sum().reset_index()
    if not cust_out.empty:
        fig2 = px.pie(cust_out, names='customer name', values='outstanding', title="Outstanding by Customer")
        st.plotly_chart(fig2, use_container_width=True)

    trend = df_filtered.groupby('date').agg({'sales value':'sum','paid amount':'sum'}).reset_index()
    if not trend.empty:
        fig3 = px.line(trend, x='date', y=['sales value','paid amount'], title="Sales & Paid Trend")
        st.plotly_chart(fig3, use_container_width=True)

elif nav == "Sales Analysis":
    st.header("📈 Sales Analysis")
    exec_filter = st.multiselect("Select Executives", df_filtered['executive name'].unique())
    if exec_filter:
        df_sa = df_filtered[df_filtered['executive name'].isin(exec_filter)]
    else:
        df_sa = df_filtered

    st.dataframe(df_sa)

    # Export
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df_sa.to_excel(writer, index=False, sheet_name='sales')
    st.download_button("⬇ Download Excel", out.getvalue(), "sales_filtered.xlsx")

elif nav == "Customer Analysis":
    st.header("👥 Customer Analysis")
    
    # Add summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customers", len(df_filtered['customer name'].unique()))
    with col2:
        st.metric("Avg. Sales per Customer", f"{df_filtered.groupby('customer name')['sales value'].sum().mean():,.2f}")
    with col3:
        st.metric("Avg. Outstanding per Customer", f"{df_filtered.groupby('customer name')['outstanding'].sum().mean():,.2f}")
    
    cust = df_filtered.groupby('customer name').agg({
        'sales value':'sum','paid amount':'sum','outstanding':'sum'
    }).reset_index()
    st.dataframe(cust)

    customer = st.selectbox("Choose Customer", cust['customer name'])
    if customer:
        profile = df_filtered[df_filtered['customer name']==customer]
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sales", f"{profile['sales value'].sum():,.2f}")
        col2.metric("Total Paid", f"{profile['paid amount'].sum():,.2f}")
        col3.metric("Outstanding", f"{profile['outstanding'].sum():,.2f}")
        st.dataframe(profile)

elif nav == "All Customer Outstanding":
    st.header("💰 All Customer Outstanding")
    cust_outstanding = df_filtered.groupby('customer name')['outstanding'].sum().reset_index()
    st.dataframe(cust_outstanding)

    # Export Excel
    out2 = BytesIO()
    with pd.ExcelWriter(out2, engine='openpyxl') as writer:
        cust_outstanding.to_excel(writer, index=False, sheet_name='outstanding')
    st.download_button("⬇ Download Excel", out2.getvalue(), "outstanding.xlsx")

    # Export PDF
    if REPORTLAB_AVAILABLE and st.button("⬇ Export PDF"):
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        
        # Add title and date
        title = Paragraph("Customer Outstanding Report", styles['Title'])
        date_str = Paragraph(f"As of {datetime.now().strftime('%Y-%m-%d')}", styles['Normal'])
        
        elems = [title, date_str, Spacer(1, 12)]
        
        # Prepare data
        data = [["Customer Name", "Outstanding Amount"]]  # Header
        for _, row in cust_outstanding.iterrows():
            data.append([row['customer name'], f"{row['outstanding']:,.2f}"])
        
        # Create table with better formatting
        tbl = Table(data)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elems.append(tbl)
        doc.build(elems)
        st.download_button("Download PDF", pdf_buffer.getvalue(), "outstanding.pdf", mime="application/pdf")
    elif not REPORTLAB_AVAILABLE:
        st.warning("PDF export is not available. Please install reportlab: pip install reportlab")