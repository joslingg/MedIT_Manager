from django.contrib import admin
from .models import ProcurementAttachment, ProcurementRecord

admin.site.register(ProcurementRecord)
admin.site.register(ProcurementAttachment)