from django.shortcuts import render, redirect
from .models import ProcurementRecord
from django.template import loader
from django.views.generic import CreateView, ListView, DetailView

class ProcurementRecordListView(ListView):
    model = ProcurementRecord
    template_name = "procure/record_list.html"
    context_object_name = "records"
    
class ProcurementRecordDetailView(DetailView):
    model = ProcurementRecord
    template_name = "procure/record_detail.html"
    context_object_name = "record"
    


