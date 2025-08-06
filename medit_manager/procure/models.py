from django.db import models
from django.utils import timezone
import os

class ProcurementRecord(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Mã hồ sơ")
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Tổng trị giá")
    date_created = models.DateField(auto_now_add=True, verbose_name="Ngày tạo")
    is_paid = models.BooleanField(default=False, verbose_name="Đã thanh toán")
    
    def save(self,*args, **kargs):
        if not self.code:
            today = timezone.now().date()
            count_today = ProcurementRecord.objects.filter(date_created=today).count() + 1
            date_part = today.strftime("%d%m%y")
            self.code = f"{date_part}/{count_today}"
        super().save(*args,**kargs)
        
    class Meta:
        ordering = ['code']
        verbose_name = 'Hồ sơ' 
        verbose_name_plural = 'Hồ sơ'
    
    def calc_total_cost(self):
        total = sum(item.total_price() for item in self.items.all())
        self.total_cost = total
        self.save(update_fields=['total_cost'])  # chỉ lưu trường này
        return total
    
    def __str__(self):
        return self.code or self.title

class PurchasedItem(models.Model):
    record = models.ForeignKey(
        ProcurementRecord,
        on_delete=models.CASCADE,
        related_name="items"
    )
    name = models.CharField(max_length=255, verbose_name="Tên món")
    unit = models.CharField(max_length=50, blank=True, verbose_name="Đơn vị tính")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Đơn giá")
    
    class Meta:
        verbose_name = 'Danh sách món hàng' 
        verbose_name_plural = 'Danh sách món hàng'
        
    def total_price(self):
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"
    
class ProcurementAttachment(models.Model):
    record = models.ForeignKey(ProcurementRecord, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='procure/attachments/')
    description = models.CharField(max_length=255, blank=True, verbose_name='Mô tả tài liệu (nếu có)')
    
    class Meta:
        verbose_name = 'Tài liệu đính kèm' 
        verbose_name_plural = 'Tài liệu đính kèm'
    
    def __str__(self):
        return os.path.basename(self.file.name)