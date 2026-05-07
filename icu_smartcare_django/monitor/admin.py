from django.contrib import admin
from .models import Patient, Vital, Alert, NurseDevice

admin.site.register(Patient)
admin.site.register(Vital)
admin.site.register(Alert)
admin.site.register(NurseDevice)
