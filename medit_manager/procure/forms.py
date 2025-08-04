from django import forms
from django.forms import inlineformset_factory, ClearableFileInput
from .models import ProcurementRecord, PurchasedItem

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]

class ProcurementRecordForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        label="Tài liệu đính kèm"
    )

    import_file = forms.FileField(
        required=False,
        label="Import danh sách món (Excel)"
    )

    class Meta:
        model = ProcurementRecord
        fields = ['title', 'description','is_paid']
        
class PurchasedItemForm(forms.ModelForm):
    class Meta:
        model = PurchasedItem
        fields = ['name', 'unit', 'quantity', 'unit_price']
        
PurchasedItemFormSet = inlineformset_factory(
    ProcurementRecord,
    PurchasedItem,
    form=PurchasedItemForm,
    extra=1,
    can_delete=True
)
