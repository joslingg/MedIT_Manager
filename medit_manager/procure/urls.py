from django.urls import path
from .views import ProcurementRecordListView, ProcurementRecordDetailView, ProcurementRecordCreateView, ProcurementRecordUpdateView, ProcurementRecordDeleteView, DashboardView, export_excel

app_name = "procure"

urlpatterns = [
    path('', ProcurementRecordListView.as_view(), name='record_list'),
    path('<int:pk>/', ProcurementRecordDetailView.as_view(), name="record_detail"),
    path('record_form', ProcurementRecordCreateView.as_view(), name='record_form'),
    path('edit/<int:pk>/', ProcurementRecordUpdateView.as_view(), name='edit_record'),
    path('delete/<int:pk>/', ProcurementRecordDeleteView.as_view(), name='delete_record'),
    path("export_excel/", export_excel, name="export_excel"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
