from django.urls import path
from . import views

app_name = "procure"

urlpatterns = [
    path('',views.ProcurementRecordListView.as_view(),name='record_list'),
    path('<int:pk>/', views.ProcurementRecordDetailView.as_view(), name="record_detail"),
]
