# Healthcare KPI Inference Report

> Replace bracketed prompts with findings from the completed dashboard. Do not present synthetic patterns as real clinical evidence.

## Dataset and scope
- Period: 1 January 2022 to 17 November 2026
- Source: synthetic data generated with Python, Pandas and Faker
- Tables: patients, hospitals, physicians, appointments, admissions

## 1. Patient satisfaction
- Observed trend: [state increase/decrease/stability and months]
- Hospital/specialty comparison: [identify strongest and weakest groups]
- Possible explanation: Longer waits and peak demand may contribute to lower satisfaction.
- Suggested action: Review staffing and patient communication during high-demand periods.

## 2. Average length of stay
- Observed trend: [state trend and months]
- Hospital comparison: [identify variation]
- Possible explanation: Differences in case mix and seasonal admission demand may affect stay duration.
- Suggested action: Review discharge planning and diagnosis-specific pathways.

## 3. Hospital readmission rate
- Observed trend: [state trend and months]
- Hospital comparison: [identify variation]
- Possible explanation: Repeat admissions may reflect seasonal illness patterns or differences in follow-up care.
- Suggested action: Strengthen post-discharge follow-up for patients at higher risk.

## 4. Physician productivity
- Observed trend: [state trend and months]
- Physician/specialty comparison: [identify variation]
- Possible explanation: Demand, physician availability and holiday periods may influence completed consultations.
- Suggested action: Align roster capacity with observed demand.

## 5. Patient wait time
- Observed trend: [state trend and months]
- Hospital comparison: [identify variation]
- Possible explanation: Appointment demand and staffing capacity may explain peak waiting periods.
- Suggested action: Adjust appointment slots and staffing during high-demand periods.

## Overall conclusion
[Summarize the strongest evidence-backed patterns across the five KPIs.]

## Limitations
This is a synthetic demonstration dataset. Seasonal relationships were intentionally introduced for analytics practice and do not establish real-world clinical causation. Readmission is operationally defined as a subsequent admission for the same patient within 30 days of discharge; only discharges with a complete 30-day observation window are included.
