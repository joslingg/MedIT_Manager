from django.contrib import admin
from .models import ProcurementRecord, PurchasedItem, ProcurementAttachment

class PurchasedItemInline(admin.TabularInline):
    model = PurchasedItem
    extra = 1
    fields = ('name', 'unit', 'quantity', 'unit_price',)
    show_change_link = True

class ProcurementAttachmentInline(admin.TabularInline):
    model = ProcurementAttachment
    extra = 1
    fields = ('file',)
    show_change_link = False

@admin.register(ProcurementRecord)
class ProcurementRecordAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'date_created', 'total_cost_display')
    search_fields = ('code', 'title')
    list_filter = ('date_created',)
    inlines = [PurchasedItemInline, ProcurementAttachmentInline]

    def total_cost_display(self, obj):
        return f"{obj.calc_total_cost():,.0f} đ"
    total_cost_display.short_description = "Tổng tiền"

@admin.register(PurchasedItem)
class PurchasedItemAdmin(admin.ModelAdmin):
    list_display = ('record', 'name', 'quantity', 'unit_price')
    search_fields = ('name',)

@admin.register(ProcurementAttachment)
class ProcurementAttachmentAdmin(admin.ModelAdmin):
    list_display = ('record', 'file')
