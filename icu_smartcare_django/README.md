# Real-Time ICU Patient Monitoring and Smart Alert Management System

## Run Steps

### 1. Open project folder in VS Code
```bash
cd icu_smartcare_django
```

### 2. Create virtual environment
```bash
python -m venv env
```

### 3. Activate virtual environment

Windows CMD:
```bash
env\Scripts\activate
```

Windows PowerShell:
```bash
env\Scripts\Activate.ps1
```

### 4. Install Django
```bash
pip install django
```

### 5. Create database tables
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run server
```bash
python manage.py runserver
```

### 7. Open browser
```text
http://127.0.0.1:8000/
```

### 8. Demo setup
Click "Load Demo Patients", then test:
- Saline Low
- SpO₂ Critical
- Patient Query
- Nurse Watch
- Nurse Room Display
- Doctor Dashboard
- Alert Clearance
- Alert History

## Demo Logic

- Saline Low / Patient Query goes to Nurse Watch + Nurse Room Display
- Critical SpO₂ / Pulse / BP goes to Doctor + Nurse
- If alert is not cleared:
  - 30 seconds: Escalation Level 1
  - 60 seconds: Escalation Level 2
  - 90 seconds: Escalation Level 3
- Cleared alerts store action taken, medication, remarks, and response time

## Data Structures Used

- Priority Queue: Active alert ordering by priority
- Queue: Nurse task handling
- Stack: Recent alert concept
- Hash Map: Bed/patient lookup concept
- List/Table: Patient and alert records
