from django.urls import path
from .views import ProcurementRecordListView, ProcurementRecordDetailView, ProcurementRecordCreateView, export_excel, export_excel

app_name = "procure"

urlpatterns = [
    path('', ProcurementRecordListView.as_view(), name='record_list'),
    path('<int:pk>/', ProcurementRecordDetailView.as_view(), name="record_detail"),
    path('record_form', ProcurementRecordCreateView.as_view(), name='record_form'),
    path("export_excel/", export_excel, name="export_excel"),
]
