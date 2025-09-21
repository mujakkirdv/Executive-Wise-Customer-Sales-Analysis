#Sales Tracker — Outstanding & Commission System
A comprehensive Streamlit-based web application for tracking sales, outstanding amounts, and calculating commissions for sales teams.

Features
Dashboard: Overview of key metrics with interactive visualizations

Sales Analysis: Detailed sales data with executive filtering

Customer Analysis: Customer-specific insights and outstanding summaries

Outstanding Reports: Comprehensive customer outstanding tracking

Data Export: Excel and PDF export capabilities

Interactive Filters: Date range and executive filtering

Installation
Clone or download the application files

Install required dependencies:

bash
pip install streamlit pandas plotly openpyxl reportlab
Usage
Run the application:

bash
streamlit run app.py
Open your browser and navigate to the provided local URL (typically http://localhost:8501)

Upload your sales data file (Excel or CSV format) with the required columns

Data Requirements
Your input file must contain these columns (case-insensitive):

date - Transaction date

order no - Order identifier

executive name - Sales representative name

customer name - Customer identifier

opening balance - Starting balance

sales value - Sales amount

sales return - Returned sales value

sales in and out - Sales adjustments

paid amount - Payments received

cashback - Cashback amounts

commission - Commission deductions

Calculations
The application automatically calculates:

Outstanding Amount:

text
Opening Balance + Sales Value - Sales Return - Sales In/Out - Paid Amount - Cashback - Commission
Executive Commission: 1% of paid amount

Team Leader Commission: 0.2% of total paid amount

Export Features
Excel Export: Download filtered data in Excel format

PDF Reports: Generate professional outstanding reports (requires reportlab)

Navigation
Home: Instructions and data requirements

Dashboard: Key metrics and visualizations

Sales Analysis: Detailed sales data with filtering

Customer Analysis: Customer-specific insights

All Customer Outstanding: Comprehensive outstanding reports

Customization
You can customize the application by:

Modifying the commission rates in the code

Adjusting the color scheme in the CSS section

Adding new visualizations using Plotly

Extending the data validation rules

Troubleshooting
Common Issues
Missing columns error: Ensure your data file contains all required columns

Date parsing issues: Check that date formats are consistent in your data

PDF export not available: Install reportlab with pip install reportlab

Data Format Tips
Use consistent date formats (YYYY-MM-DD recommended)

Ensure numeric columns contain only numbers (no text or symbols)

Use consistent naming for executives and customers

Support
For issues or questions, please check:

That your data meets the column requirements

That date formats are consistent

All required packages are installed

License
This application is provided as-is for educational and business use.

