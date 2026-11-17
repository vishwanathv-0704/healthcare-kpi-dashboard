# Healthcare KPI Analytics

## Stack
MySQL, Python, Pandas, Faker, SQLAlchemy, Streamlit and Plotly.

## Setup
1. Install MySQL and create a database user.
2. Create a virtual environment:
   `python -m venv .venv`
3. Activate it and install dependencies:
   `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and enter your MySQL credentials.
5. Run schema:
   `mysql -u root -p < sql/01_schema.sql`
6. Generate and load five years of synthetic data:
   `python generate_and_load.py`
7. Create KPI aggregate tables:
   `mysql -u root -p healthcare_analytics < sql/02_aggregates.sql`
8. Start dashboard:
   `streamlit run app.py`

## Data model
- patients: patient demographics
- hospitals: healthcare facilities
- physicians: physician and specialization, linked to hospital
- appointments: appointment timing, status and satisfaction
- admissions: admission/discharge events and diagnosis category

All primary/foreign keys use UUID strings (CHAR(36)).

## KPI definitions
- Satisfaction: average non-null satisfaction score for completed appointments.
- Length of stay: average elapsed days from admission to discharge.
- Readmission: percentage of eligible discharges followed by another admission for the same patient within 30 days. Discharges without a full 30-day observation window are excluded.
- Physician productivity: count of completed appointments per physician per month.
- Wait time: average minutes from scheduled appointment time to check-in time.

## Synthetic patterns
Appointment demand is intentionally higher in selected monsoon/winter months. Wait times rise during peak months and on Mondays; satisfaction is modestly reduced as waits increase. Admission length of stay uses a right-skewed distribution. A subset of patients receives a repeat admission 5–25 days after discharge to create measurable readmissions.

## Important
The dataset is synthetic and designed for demonstration. Seasonal patterns are assumptions, not real-world clinical findings.
