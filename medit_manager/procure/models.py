from django.db import models
from django.utils import timezone

class ProcurementRecord(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Mã hồ sơ")
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    desciption = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    date_created = models.DateField(auto_now_add=True, verbose_name="Ngày tạo")
    
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
        
    def __str__(self):
        return self.code or self.title

class ProcurementAttachment(models.Model):
    record = models.ForeignKey(ProcurementRecord, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='procure/attachments/')
    description = models.CharField(max_length=255, blank=True, verbose_name='Mô tả tài liệu (nếu có)')
    
    def __str__(self):
        return self.file.name.split()('/')[-1]
