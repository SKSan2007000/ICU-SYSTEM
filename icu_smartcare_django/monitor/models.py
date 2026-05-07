from django.db import models
from django.utils import timezone


# ---------------- PATIENT ----------------
class Patient(models.Model):
    RISK_CHOICES = [
        ('Normal', 'Normal'),
        ('Moderate', 'Moderate'),
        ('High Risk', 'High Risk'),
    ]

    patient_name = models.CharField(max_length=100)
    bed_no = models.CharField(max_length=20, unique=True)
    age = models.PositiveIntegerField()

    assigned_doctor = models.CharField(max_length=100)  # ✅ ADDED

    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='Normal')
    diagnosis = models.TextField(blank=True)

    def __str__(self):
        return f"{self.bed_no} - {self.patient_name}"


# ---------------- VITALS ----------------
class Vital(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    heart_rate = models.IntegerField()
    spo2 = models.IntegerField()
    bp_systolic = models.IntegerField()
    temperature = models.FloatField()
    saline_level = models.IntegerField()
    recorded_at = models.DateTimeField(default=timezone.now)


# ---------------- ALERT ----------------
class Alert(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Cleared', 'Cleared'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=80)
    message = models.TextField()
    severity = models.CharField(max_length=20)
    priority = models.IntegerField()
    assigned_to = models.CharField(max_length=50)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    generated_at = models.DateTimeField(default=timezone.now)
    cleared_at = models.DateTimeField(null=True, blank=True)
    response_seconds = models.IntegerField(null=True, blank=True)
    attended_by = models.CharField(max_length=100, blank=True)

    action_taken = models.CharField(max_length=150, blank=True)
    medication_given = models.CharField(max_length=150, blank=True)
    remarks = models.TextField(blank=True)

    escalation_level = models.IntegerField(default=0)

    points_awarded = models.IntegerField(default=0)  # ✅ ADDED

    def __str__(self):
        return f"{self.alert_type} - {self.patient.bed_no}"


# ---------------- NURSE DEVICE ----------------
class NurseDevice(models.Model):
    nurse_name = models.CharField(max_length=100, default='Nurse A')
    watch_status = models.CharField(max_length=20, default='Active')
    battery_level = models.IntegerField(default=85)
    last_active = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nurse_name


# ---------------- STAFF SCORE ----------------
class StaffScore(models.Model):
    staff_name = models.CharField(max_length=100)
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.staff_name} - {self.total_points}"