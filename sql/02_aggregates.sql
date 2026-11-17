USE healthcare_analytics;

DROP TABLE IF EXISTS agg_patient_satisfaction;
CREATE TABLE agg_patient_satisfaction AS
SELECT DATE_FORMAT(appointment_datetime, '%Y-%m-01') AS month,
       hospital_id,
       ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction,
       COUNT(satisfaction_score) AS survey_count
FROM appointments
WHERE appointment_status = 'Completed'
GROUP BY DATE_FORMAT(appointment_datetime, '%Y-%m-01'), hospital_id;

DROP TABLE IF EXISTS agg_length_of_stay;
CREATE TABLE agg_length_of_stay AS
SELECT DATE_FORMAT(admission_datetime, '%Y-%m-01') AS month,
       hospital_id,
       ROUND(AVG(TIMESTAMPDIFF(HOUR, admission_datetime, discharge_datetime) / 24), 2) AS avg_length_of_stay_days,
       COUNT(*) AS discharged_admissions
FROM admissions
WHERE admission_status = 'Discharged'
  AND discharge_datetime IS NOT NULL
GROUP BY DATE_FORMAT(admission_datetime, '%Y-%m-01'), hospital_id;

DROP TABLE IF EXISTS agg_readmission_rate;
CREATE TABLE agg_readmission_rate AS
SELECT DATE_FORMAT(a.discharge_datetime, '%Y-%m-01') AS month,
       a.hospital_id,
       COUNT(*) AS eligible_discharges,
       SUM(CASE WHEN EXISTS (
           SELECT 1 FROM admissions r
           WHERE r.patient_id = a.patient_id
             AND r.admission_datetime > a.discharge_datetime
             AND r.admission_datetime <= DATE_ADD(a.discharge_datetime, INTERVAL 30 DAY)
       ) THEN 1 ELSE 0 END) AS readmitted_discharges,
       ROUND(100.0 * SUM(CASE WHEN EXISTS (
           SELECT 1 FROM admissions r
           WHERE r.patient_id = a.patient_id
             AND r.admission_datetime > a.discharge_datetime
             AND r.admission_datetime <= DATE_ADD(a.discharge_datetime, INTERVAL 30 DAY)
       ) THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS readmission_rate_pct
FROM admissions a
WHERE a.admission_status = 'Discharged'
  AND a.discharge_datetime IS NOT NULL
  AND DATE_ADD(a.discharge_datetime, INTERVAL 30 DAY) <= '2026-11-17'
GROUP BY DATE_FORMAT(a.discharge_datetime, '%Y-%m-01'), a.hospital_id;

DROP TABLE IF EXISTS agg_physician_productivity;
CREATE TABLE agg_physician_productivity AS
SELECT DATE_FORMAT(a.appointment_datetime, '%Y-%m-01') AS month,
       a.physician_id,
       a.hospital_id,
       COUNT(*) AS completed_appointments
FROM appointments a
WHERE a.appointment_status = 'Completed'
GROUP BY DATE_FORMAT(a.appointment_datetime, '%Y-%m-01'), a.physician_id, a.hospital_id;

DROP TABLE IF EXISTS agg_patient_wait_time;
CREATE TABLE agg_patient_wait_time AS
SELECT DATE_FORMAT(appointment_datetime, '%Y-%m-01') AS month,
       hospital_id,
       ROUND(AVG(TIMESTAMPDIFF(MINUTE, appointment_datetime, check_in_time)), 1) AS avg_wait_minutes,
       COUNT(*) AS appointment_count
FROM appointments
WHERE appointment_status = 'Completed'
  AND check_in_time IS NOT NULL
GROUP BY DATE_FORMAT(appointment_datetime, '%Y-%m-01'), hospital_id;

-- Helpful indexes for dashboard filters.
CREATE INDEX idx_sat_month ON agg_patient_satisfaction(month);
CREATE INDEX idx_los_month ON agg_length_of_stay(month);
CREATE INDEX idx_readmit_month ON agg_readmission_rate(month);
CREATE INDEX idx_productivity_month ON agg_physician_productivity(month);
CREATE INDEX idx_wait_month ON agg_patient_wait_time(month);
