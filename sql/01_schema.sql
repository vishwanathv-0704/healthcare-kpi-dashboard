CREATE DATABASE IF NOT EXISTS healthcare_analytics;
USE healthcare_analytics;

CREATE TABLE IF NOT EXISTS patients (
    patient_id CHAR(36) PRIMARY KEY,
    patient_name VARCHAR(120) NOT NULL,
    age TINYINT UNSIGNED,
    gender VARCHAR(20),
    city VARCHAR(80),
    created_at DATE
);

CREATE TABLE IF NOT EXISTS hospitals (
    hospital_id CHAR(36) PRIMARY KEY,
    hospital_name VARCHAR(150) NOT NULL,
    city VARCHAR(80),
    hospital_type VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS physicians (
    physician_id CHAR(36) PRIMARY KEY,
    physician_name VARCHAR(120) NOT NULL,
    specialization VARCHAR(80),
    hospital_id CHAR(36) NOT NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id CHAR(36) PRIMARY KEY,
    patient_id CHAR(36) NOT NULL,
    physician_id CHAR(36) NOT NULL,
    hospital_id CHAR(36) NOT NULL,
    appointment_datetime DATETIME NOT NULL,
    check_in_time DATETIME,
    check_out_time DATETIME,
    appointment_status VARCHAR(20) NOT NULL,
    satisfaction_score DECIMAL(3,2),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (physician_id) REFERENCES physicians(physician_id),
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id),
    INDEX idx_appt_datetime (appointment_datetime),
    INDEX idx_appt_hospital (hospital_id)
);

CREATE TABLE IF NOT EXISTS admissions (
    admission_id CHAR(36) PRIMARY KEY,
    patient_id CHAR(36) NOT NULL,
    hospital_id CHAR(36) NOT NULL,
    attending_physician_id CHAR(36) NOT NULL,
    admission_datetime DATETIME NOT NULL,
    discharge_datetime DATETIME,
    diagnosis_category VARCHAR(80),
    admission_status VARCHAR(20) NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id),
    FOREIGN KEY (attending_physician_id) REFERENCES physicians(physician_id),
    INDEX idx_adm_patient_date (patient_id, admission_datetime),
    INDEX idx_adm_discharge (discharge_datetime)
);
