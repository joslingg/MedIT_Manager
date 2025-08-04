from enum import member
from multiprocessing import context
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from .models import ProcurementRecord, ProcurementAttachment, PurchasedItem
from .forms import ProcurementRecordForm, PurchasedItemFormSet
from django.db.models import Q
from datetime import datetime
import openpyxl
from io import BytesIO
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import TemplateView
from .models import ProcurementRecord
from django.db.models import Sum


class ProcurementRecordListView(ListView):
    model = ProcurementRecord
    template_name = "procure/record_list.html"
    context_object_name = "records"
    paginate_by = 10  # phân 10 hồ sơ mỗi trang
    
    def get_queryset(self):
        qs = ProcurementRecord.objects.all()

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(code__icontains=q) | Q(title__icontains=q))

        month = self.request.GET.get("month")
        year = self.request.GET.get("year")
        if month and year:
            qs = qs.filter(date_created__month=month, date_created__year=year)
        
        is_paid = self.request.GET.get("is_paid")
        if is_paid in ["0", "1"]:
            qs = qs.filter(is_paid=bool(int(is_paid)))
        
        return qs.order_by("-date_created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        records = context["records"]
        
        # Gắn tổng tiền tính động vào từng record
        for record in records:
            record.calculated_total_cost = record.calc_total_cost()

        context["q"] = self.request.GET.get("q", "")
        context["month"] = self.request.GET.get("month", "")
        now = datetime.now()
        context["years"] = list(range(2020, now.year + 1))
        context["current_year"] = now.year
        context["months"] = [f"{i:02d}" for i in range(1, 13)]
        
        return context

class ProcurementRecordDetailView(DetailView):
    model = ProcurementRecord
    template_name = "procure/record_detail.html"
    context_object_name = "record"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_cost = sum(item.total_price() for item in self.object.items.all())
        context["total_cost"] = total_cost
        return context

class ProcurementRecordUpdateView(UpdateView):
    model = ProcurementRecord
    form_class = ProcurementRecordForm
    template_name = "procure/edit_record.html"
    success_url = reverse_lazy('procure:record_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = PurchasedItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = PurchasedItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            
            items = formset.save(commit=False)
            for item in items:
                item.record = self.object
                item.save()

            for obj in formset.deleted_objects:
                obj.delete()
                
            attachments = form.cleaned_data.get('attachments')
            if attachments:
                for file in attachments:
                    ProcurementAttachment.objects.create(
                        record=self.object,
                        file=file
                    )
                    
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
        
class ProcurementRecordCreateView(CreateView):
    model = ProcurementRecord
    form_class = ProcurementRecordForm
    template_name = "procure/record_form.html"
    success_url = reverse_lazy('procure:record_list')

    def get_context_data(self, **kwargs):
        model = ProcurementRecord
    form_class = ProcurementRecordForm
    template_name = "procure/record_form.html"
    success_url = reverse_lazy('procure:record_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = PurchasedItemFormSet(self.request.POST)
        else:
            context['formset'] = PurchasedItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if not formset.is_valid():
            return self.form_invalid(form)

        self.object = form.save()

        # Lưu file đính kèm
        attachments = form.cleaned_data.get('attachments')
        if attachments:
            for file in attachments:
                ProcurementAttachment.objects.create(record=self.object, file=file)

        # Lưu các món từ formset
        items = formset.save(commit=False)
        for item in items:
            item.record = self.object
            item.save()
        for obj in formset.deleted_objects:
            obj.delete()

        # Kiểm tra nếu có file Excel
        excel_file = self.request.FILES.get('import_file')
        if excel_file:
            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active
                for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    stt, name, unit, quantity, unit_price = row[:5]
                    if name:
                        PurchasedItem.objects.create(
                            record=self.object,
                            name=name,
                            unit=unit or '',
                            quantity=quantity or 0,
                            unit_price=unit_price or 0
                        )
            except Exception as e:
                messages.warning(self.request, f"Lỗi khi đọc Excel: {e}")

        return super().form_valid(form)

class ProcurementRecordDeleteView(DeleteView):
    model = ProcurementRecord
    template_name = "procure/delete_record.html"
    success_url = reverse_lazy('procure:record_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['record'] = self.object
        return context

class DashboardView(TemplateView):
    template_name = "procure/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_records"] = ProcurementRecord.objects.count()
        context["total_paid"] = ProcurementRecord.objects.filter(is_paid=True).aggregate(Sum("total_cost"))["total_cost__sum"] or 0
        context["total_unpaid"] = ProcurementRecord.objects.filter(is_paid=False).aggregate(Sum("total_cost"))["total_cost__sum"] or 0

        # Thống kê theo tháng trong năm hiện tại
        current_year = datetime.now().year
        monthly_data = (
            ProcurementRecord.objects
            .filter(date_created__year=current_year)
            .values_list("date_created__month")
            .annotate(total=Sum("total_cost"))
            .order_by("date_created__month")
        )
        # Tạo dict từ 1 đến 12 tháng
        monthly_totals = {month: 0 for month in range(1, 13)}
        for m, total in monthly_data:
            monthly_totals[m] = total or 0

        context["monthly_totals"] = monthly_totals
        context["current_year"] = current_year
        return context
    
def export_excel(request):
    qs = ProcurementRecord.objects.all()
    q = request.GET.get("q")
    month = request.GET.get("month")
    year = request.GET.get("year")

    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(title__icontains=q))
    if month and year:
        qs = qs.filter(date_created__month=month, date_created__year=year)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh sách hồ sơ"

    ws.append(["Mã hồ sơ", "Tiêu đề", "Tổng trị giá", "Ngày tạo"])
    for r in qs:
        ws.append([r.code, r.title, float(r.total_cost), str(r.date_created)])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="hoso_muasam.xlsx"'
    wb.save(response)
    return response