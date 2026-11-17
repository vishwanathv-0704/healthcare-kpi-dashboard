
USE healthcare_analytics;

-- 1. Daily patient satisfaction
DROP TABLE IF EXISTS agg_daily_patient_satisfaction;

CREATE TABLE agg_daily_patient_satisfaction AS
SELECT
    DATE(appointment_datetime) AS metric_date,
    hospital_id,
    AVG(satisfaction_score) AS avg_satisfaction,
    COUNT(satisfaction_score) AS survey_count
FROM appointments
WHERE appointment_status = 'Completed'
GROUP BY DATE(appointment_datetime), hospital_id;


-- 2. Daily average length of stay
DROP TABLE IF EXISTS agg_daily_length_of_stay;

CREATE TABLE agg_daily_length_of_stay AS
SELECT
    DATE(discharge_datetime) AS metric_date,
    hospital_id,
    AVG(TIMESTAMPDIFF(
        HOUR, admission_datetime, discharge_datetime
    ) / 24) AS avg_length_of_stay_days,
    COUNT(*) AS discharged_admissions
FROM admissions
WHERE admission_status = 'Discharged'
  AND discharge_datetime IS NOT NULL
GROUP BY DATE(discharge_datetime), hospital_id;


-- 3. Daily hospital readmission rate
DROP TABLE IF EXISTS agg_daily_readmission_rate;

CREATE TABLE agg_daily_readmission_rate AS
SELECT
    DATE(a.discharge_datetime) AS metric_date,
    a.hospital_id,
    COUNT(*) AS eligible_discharges,
    SUM(
        CASE WHEN EXISTS (
            SELECT 1
            FROM admissions r
            WHERE r.patient_id = a.patient_id
              AND r.admission_datetime > a.discharge_datetime
              AND r.admission_datetime <= DATE_ADD(
                  a.discharge_datetime, INTERVAL 30 DAY
              )
        )
        THEN 1 ELSE 0 END
    ) AS readmitted_discharges
FROM admissions a
WHERE a.admission_status = 'Discharged'
  AND a.discharge_datetime IS NOT NULL
  AND DATE_ADD(a.discharge_datetime, INTERVAL 30 DAY)
      <= '2026-11-17'
GROUP BY DATE(a.discharge_datetime), a.hospital_id;


-- 4. Daily physician productivity
DROP TABLE IF EXISTS agg_daily_physician_productivity;

CREATE TABLE agg_daily_physician_productivity AS
SELECT
    DATE(appointment_datetime) AS metric_date,
    physician_id,
    hospital_id,
    COUNT(*) AS completed_appointments
FROM appointments
WHERE appointment_status = 'Completed'
GROUP BY DATE(appointment_datetime), physician_id, hospital_id;


-- 5. Daily patient wait time
DROP TABLE IF EXISTS agg_daily_patient_wait_time;

CREATE TABLE agg_daily_patient_wait_time AS
SELECT
    DATE(appointment_datetime) AS metric_date,
    hospital_id,
    AVG(TIMESTAMPDIFF(
        MINUTE, appointment_datetime, check_in_time
    )) AS avg_wait_minutes,
    COUNT(*) AS appointment_count
FROM appointments
WHERE appointment_status = 'Completed'
  AND check_in_time IS NOT NULL
GROUP BY DATE(appointment_datetime), hospital_id;
