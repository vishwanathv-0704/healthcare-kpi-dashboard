import os
import uuid
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "healthcare_analytics")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    pool_pre_ping=True
)

def uid():
    return str(uuid.uuid4())

def main():
    print("Generating hospitals, physicians and patients...")
    cities = ["Chennai", "Bengaluru", "Hyderabad", "Mumbai", "Delhi",
              "Pune", "Kochi", "Coimbatore", "Jaipur", "Kolkata"]
    hospital_types = ["General", "Multi-specialty", "Teaching", "Specialty"]
    specializations = ["Cardiology", "Orthopedics", "Neurology", "Pediatrics",
                       "General Medicine", "Oncology", "Pulmonology", "Dermatology"]

    hospitals = []
    for i in range(10):
        hospitals.append({
            "hospital_id": uid(),
            "hospital_name": f"{fake.city()} {random.choice(['Medical Centre', 'Hospital', 'Health Institute'])}",
            "city": cities[i],
            "hospital_type": random.choice(hospital_types)
        })
    hospitals_df = pd.DataFrame(hospitals)

    physicians = []
    for i in range(100):
        h = hospitals[i % len(hospitals)]
        physicians.append({
            "physician_id": uid(),
            "physician_name": fake.name(),
            "specialization": random.choice(specializations),
            "hospital_id": h["hospital_id"]
        })
    physicians_df = pd.DataFrame(physicians)

    patients = []
    for _ in range(5000):
        patients.append({
        "patient_id": uid(),
        "patient_name": fake.name(),
        "age": random.randint(1, 90),
        "gender": random.choice(["Female", "Male", "Other"]),
        "city": random.choice(cities),
        "created_at": fake.date_between(
            start_date=datetime(2022, 1, 1).date(),
            end_date=datetime.today().date()
        )
    })
    patients_df = pd.DataFrame(patients)

    print("Generating 50,000 appointments (2022-Nov 2026)...")
    start = pd.Timestamp("2022-01-01")
    end = pd.Timestamp("2026-11-17")
    date_range = (end - start).days
    appts = []
    patient_ids = patients_df["patient_id"].tolist()
    physician_ids = physicians_df["physician_id"].tolist()
    hospital_for_physician = dict(zip(physicians_df.physician_id, physicians_df.hospital_id))
    physicians_by_hospital = physicians_df.groupby("hospital_id")["physician_id"].apply(list).to_dict()

    for i in range(50000):
        # More demand in winter/monsoon months; mild year-on-year growth.
        year = random.randint(2022, 2026)
        month_weights = [0.075,0.070,0.075,0.075,0.075,0.080,0.085,0.085,0.080,0.080,0.105,0.115]
        month = random.choices(range(1,13), weights=month_weights)[0]
        month = min(month, 11) if year == 2026 else month
        day = random.randint(1, 28)
        dt = pd.Timestamp(year=year, month=month, day=day,
                          hour=random.randint(8,18), minute=random.choice([0,15,30,45]))
        if dt < start or dt > end:
            dt = start + pd.Timedelta(days=random.randint(0, date_range))
        physician_id = random.choice(physician_ids)
        hospital_id = hospital_for_physician[physician_id]
        # Higher wait during demand peaks and Mondays.
        peak = dt.month in [6,7,8,11,12]
        wait = max(2, int(np.random.normal(24 + (12 if peak else 0) +
                                            (8 if dt.dayofweek == 0 else 0), 9)))
        checkin = dt + pd.Timedelta(minutes=wait)
        duration = max(10, int(np.random.normal(25, 8)))
        status = random.choices(["Completed", "Cancelled", "No-show"],
                                weights=[0.88,0.08,0.04])[0]
        checkout = checkin + pd.Timedelta(minutes=duration) if status == "Completed" else pd.NaT
        # Slightly lower satisfaction when wait is long or demand is in peak season.
        score = float(np.clip(np.random.normal(4.45 - (wait/100) - (0.18 if peak else 0), 0.42), 1, 5))
        appts.append({
            "appointment_id": uid(),
            "patient_id": random.choice(patient_ids),
            "physician_id": physician_id,
            "hospital_id": hospital_id,
            "appointment_datetime": dt.to_pydatetime(),
            "check_in_time": checkin.to_pydatetime(),
            "check_out_time": None if pd.isna(checkout) else checkout.to_pydatetime(),
            "appointment_status": status,
            "satisfaction_score": round(score, 2) if status == "Completed" and random.random() < 0.82 else None
        })
    appointments_df = pd.DataFrame(appts)

    print("Generating 10,000 admissions with deliberate 30-day readmission cases...")
    admissions = []
    diagnosis = ["Respiratory", "Cardiac", "Orthopedic", "Infection",
                 "Digestive", "Neurological", "Other"]
    # 8,500 initial admissions, then 1,500 follow-up admissions within 30 days.
    base_rows = []
    for i in range(8500):
        year = random.randint(2022, 2026)
        month = random.randint(1, 11 if year == 2026 else 12)
        day = random.randint(1, 25)
        adm = pd.Timestamp(year=year, month=month, day=day,
                           hour=random.randint(0,23))
        los = max(1, int(np.random.gamma(2.2, 2.0)))
        dis = adm + pd.Timedelta(days=los, hours=random.randint(0,10))
        p = random.choice(patient_ids)
        physician_id = random.choice(physician_ids)
        h = hospital_for_physician[physician_id]
        row = {
            "admission_id": uid(), "patient_id": p, "hospital_id": h,
            "attending_physician_id": physician_id,
            "admission_datetime": adm.to_pydatetime(),
            "discharge_datetime": dis.to_pydatetime(),
            "diagnosis_category": random.choice(diagnosis),
            "admission_status": "Discharged"
        }
        base_rows.append(row)
        admissions.append(row)

    # Pick prior admissions and create a readmission 5-25 days after discharge.
    for prior in random.sample(base_rows, 1500):
        readmit_dt = pd.Timestamp(prior["discharge_datetime"]) + pd.Timedelta(days=random.randint(5,25))
        if readmit_dt > pd.Timestamp("2026-11-17"):
            continue
        physician_id = random.choice(physicians_by_hospital[prior["hospital_id"]])
        admissions.append({
            "admission_id": uid(),
            "patient_id": prior["patient_id"],
            "hospital_id": prior["hospital_id"],
            "attending_physician_id": physician_id,
            "admission_datetime": readmit_dt.to_pydatetime(),
            "discharge_datetime": (readmit_dt + pd.Timedelta(days=random.randint(1,8))).to_pydatetime(),
            "diagnosis_category": random.choice(diagnosis),
            "admission_status": "Discharged"
        })
    admissions_df = pd.DataFrame(admissions)

    # Keep generated dates within the five-year analysis window.
    for df, col in [(appointments_df, "appointment_datetime"),
                    (admissions_df, "admission_datetime")]:
        df[col] = pd.to_datetime(df[col])
    appointments_df = appointments_df[
        appointments_df.appointment_datetime <= pd.Timestamp("2026-11-17")]
    admissions_df = admissions_df[
        admissions_df.admission_datetime <= pd.Timestamp("2026-11-17")]

    print("Loading data into MySQL (this may take a minute)...")
    with engine.begin() as conn:
        # Child tables first are cleared before parents.
        for table in ["admissions", "appointments", "physicians", "patients", "hospitals"]:
            conn.execute(text(f"DELETE FROM {table}"))
        hospitals_df.to_sql("hospitals", conn, if_exists="append", index=False, chunksize=1000)
        physicians_df.to_sql("physicians", conn, if_exists="append", index=False, chunksize=1000)
        patients_df.to_sql("patients", conn, if_exists="append", index=False, chunksize=1000)
        appointments_df.to_sql("appointments", conn, if_exists="append", index=False, chunksize=1000)
        admissions_df.to_sql("admissions", conn, if_exists="append", index=False, chunksize=1000)

    print("\nLOAD COMPLETE")
    print(f"hospitals={len(hospitals_df):,}, physicians={len(physicians_df):,}, "
          f"patients={len(patients_df):,}, appointments={len(appointments_df):,}, "
          f"admissions={len(admissions_df):,}")
    print("Date range: 2022-01-01 to 2026-11-17")
    print("Seasonality: higher winter/monsoon demand and longer waits; satisfaction responds to waits.")

if __name__ == "__main__":
    main()
