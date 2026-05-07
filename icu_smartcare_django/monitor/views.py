from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Avg, Sum
from .models import Patient, Vital, Alert, NurseDevice, StaffScore
import random


# ---------------- SMART ALERT LOGIC ----------------
def analyze_alert(patient, heart_rate, spo2, bp_systolic, temperature, saline_level):
    alerts = []

    if spo2 < 90:
        alerts.append({
            'alert_type': 'Critical SpO₂ Drop',
            'message': f'SpO₂ dropped to {spo2}%. Immediate doctor and nurse attention required.',
            'severity': 'Critical',
            'priority': 1,
            'assigned_to': 'Doctor + Nurse'
        })

    if heart_rate < 50 or heart_rate > 130:
        alerts.append({
            'alert_type': 'Pulse Abnormality',
            'message': f'Pulse is {heart_rate} BPM. Emergency monitoring required.',
            'severity': 'Critical',
            'priority': 1,
            'assigned_to': 'Doctor + Nurse'
        })

    if bp_systolic < 90 or bp_systolic > 160:
        alerts.append({
            'alert_type': 'Blood Pressure Abnormal',
            'message': f'Systolic BP is {bp_systolic} mmHg.',
            'severity': 'High',
            'priority': 2,
            'assigned_to': 'Doctor + Nurse'
        })

    if temperature > 101:
        alerts.append({
            'alert_type': 'High Temperature',
            'message': f'Temperature is {temperature} °F.',
            'severity': 'Warning',
            'priority': 3,
            'assigned_to': 'Nurse'
        })

    if saline_level <= 15:
        alerts.append({
            'alert_type': 'Saline Low / Empty',
            'message': f'Saline level is {saline_level}%. Check IV line and replace saline.',
            'severity': 'Warning',
            'priority': 4,
            'assigned_to': 'Nurse'
        })

    return alerts


def create_alert_if_not_active(patient, data):
    exists = Alert.objects.filter(
        patient=patient,
        alert_type=data['alert_type'],
        status='Active'
    ).exists()

    if not exists:
        Alert.objects.create(
            patient=patient,
            alert_type=data['alert_type'],
            message=data['message'],
            severity=data['severity'],
            priority=data['priority'],
            assigned_to=data['assigned_to']
        )


def update_escalations():
    now = timezone.now()

    for alert in Alert.objects.filter(status='Active'):
        seconds = int((now - alert.generated_at).total_seconds())

        if seconds >= 90:
            level = 3
        elif seconds >= 60:
            level = 2
        elif seconds >= 30:
            level = 1
        else:
            level = 0

        if level != alert.escalation_level:
            alert.escalation_level = level
            alert.save()


# ---------------- PAGES ----------------
def dashboard(request):
    update_escalations()
    patients = Patient.objects.all().order_by('bed_no')
    active_alerts = Alert.objects.filter(status='Active').select_related('patient').order_by('priority', 'generated_at')

    latest_vitals = {}
    for patient in patients:
        latest_vitals[patient.id] = Vital.objects.filter(patient=patient).order_by('-recorded_at').first()

    return render(request, 'monitor/dashboard.html', {
        'patients': patients,
        'active_alerts': active_alerts,
        'latest_vitals': latest_vitals,
    })


def add_patient(request):
    if request.method == 'POST':
        Patient.objects.create(
            patient_name=request.POST.get('patient_name'),
            bed_no=request.POST.get('bed_no'),
            age=request.POST.get('age'),
            assigned_doctor=request.POST.get('assigned_doctor', 'Dr. Default'),
            risk_level=request.POST.get('risk_level'),
            diagnosis=request.POST.get('diagnosis')
        )
        return redirect('dashboard')

    return render(request, 'monitor/add_patient.html')


def simulate_vitals(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    heart_rate = random.randint(45, 150)
    spo2 = random.randint(84, 99)
    bp_systolic = random.randint(80, 175)
    temperature = round(random.uniform(97, 103), 1)
    saline_level = random.randint(5, 100)

    Vital.objects.create(
        patient=patient,
        heart_rate=heart_rate,
        spo2=spo2,
        bp_systolic=bp_systolic,
        temperature=temperature,
        saline_level=saline_level
    )

    alerts = analyze_alert(patient, heart_rate, spo2, bp_systolic, temperature, saline_level)

    for data in alerts:
        create_alert_if_not_active(patient, data)

    return redirect('dashboard')


def manual_alert(request, patient_id, alert_type):
    patient = get_object_or_404(Patient, id=patient_id)

    if alert_type == 'saline':
        data = {
            'alert_type': 'Saline Low / Empty',
            'message': 'Saline level is critically low. Check IV line and replace saline.',
            'severity': 'Warning',
            'priority': 4,
            'assigned_to': 'Nurse'
        }
    elif alert_type == 'spo2':
        data = {
            'alert_type': 'Critical SpO₂ Drop',
            'message': 'SpO₂ dropped below safe level.',
            'severity': 'Critical',
            'priority': 1,
            'assigned_to': 'Doctor + Nurse'
        }
    else:
        data = {
            'alert_type': 'Patient Query',
            'message': 'Patient/attendant needs nurse assistance.',
            'severity': 'Normal',
            'priority': 5,
            'assigned_to': 'Nurse'
        }

    create_alert_if_not_active(patient, data)
    return redirect('dashboard')


def nurse_room(request):
    update_escalations()
    alerts = Alert.objects.filter(status='Active').select_related('patient').order_by('priority', 'generated_at')
    return render(request, 'monitor/nurse_room.html', {'alerts': alerts})


def watch(request):
    update_escalations()

    device, _ = NurseDevice.objects.get_or_create(
        id=1,
        defaults={'nurse_name': 'Nurse A', 'watch_status': 'Active', 'battery_level': 85}
    )

    if request.method == 'POST':
        device.watch_status = request.POST.get('watch_status')
        device.battery_level = request.POST.get('battery_level')
        device.last_active = timezone.now()
        device.save()
        return redirect('watch')

    alerts = Alert.objects.filter(
        status='Active',
        assigned_to__icontains='Nurse'
    ).select_related('patient').order_by('priority', 'generated_at')

    return render(request, 'monitor/watch.html', {'alerts': alerts, 'device': device})


def doctor_dashboard(request):
    update_escalations()

    alerts = Alert.objects.filter(
        status='Active',
        assigned_to__icontains='Doctor'
    ).select_related('patient').order_by('priority', 'generated_at')

    return render(request, 'monitor/doctor.html', {'alerts': alerts})


def doctor_watch(request):
    update_escalations()

    alerts = Alert.objects.filter(
        status='Active',
        assigned_to__icontains='Doctor'
    ).select_related('patient').order_by('priority', 'generated_at')

    return render(request, 'monitor/doctor_watch.html', {'alerts': alerts})


def clear_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)

    if request.method == 'POST':
        now = timezone.now()
        response_seconds = int((now - alert.generated_at).total_seconds())

        # Score based on response time
        if response_seconds <= 30:
            points = 10
        elif response_seconds <= 60:
            points = 7
        elif response_seconds <= 90:
            points = 5
        else:
            points = 2

        attended_by = request.POST.get('attended_by', '').strip()

        alert.status = 'Cleared'
        alert.cleared_at = now
        alert.response_seconds = response_seconds
        alert.attended_by = attended_by
        alert.points_awarded = points
        alert.action_taken = request.POST.get('action_taken')
        alert.medication_given = request.POST.get('medication_given')
        alert.remarks = request.POST.get('remarks')
        alert.save()

        if attended_by:
            staff_score, created = StaffScore.objects.get_or_create(staff_name=attended_by)
            staff_score.total_points += points
            staff_score.save()

        return redirect('history')

    return render(request, 'monitor/clear_alert.html', {'alert': alert})


def history(request):
    selected_month = request.GET.get('month')

    cleared_alerts = Alert.objects.filter(status='Cleared').select_related('patient')

    if selected_month:
        year, month = selected_month.split('-')
        cleared_alerts = cleared_alerts.filter(
            cleared_at__year=int(year),
            cleared_at__month=int(month)
        )

    avg_response = cleared_alerts.aggregate(
        Avg('response_seconds')
    )['response_seconds__avg']

    staff_leaderboard = cleared_alerts.exclude(
        attended_by=''
    ).values('attended_by').annotate(
        total_points=Sum('points_awarded'),
        avg_response=Avg('response_seconds')
    ).order_by('-total_points', 'avg_response')

    cleared_alerts = cleared_alerts.order_by('-points_awarded', '-cleared_at')

    return render(request, 'monitor/history.html', {
        'cleared_alerts': cleared_alerts,
        'avg_response': avg_response,
        'selected_month': selected_month,
        'staff_leaderboard': staff_leaderboard,
    })


def seed_demo(request):
    if Patient.objects.count() == 0:
        Patient.objects.create(
            patient_name='Ramesh Kumar',
            bed_no='ICU-01',
            age=58,
            assigned_doctor='Dr. Kumar',
            risk_level='High Risk',
            diagnosis='Cardiac observation'
        )

        Patient.objects.create(
            patient_name='Meena Ravi',
            bed_no='ICU-02',
            age=46,
            assigned_doctor='Dr. Priya',
            risk_level='Moderate',
            diagnosis='Lung infection'
        )

        Patient.objects.create(
            patient_name='Arun Prakash',
            bed_no='ICU-03',
            age=62,
            assigned_doctor='Dr. Anand',
            risk_level='High Risk',
            diagnosis='Post-surgery monitoring'
        )

    NurseDevice.objects.get_or_create(
        id=1,
        defaults={'nurse_name': 'Nurse A', 'watch_status': 'Active', 'battery_level': 85}
    )

    return redirect('dashboard')