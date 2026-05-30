from __future__ import annotations

from django import forms

from apps.common.file_storage import delete_media_relative, save_upload_file
from apps.store_core.models import ProductImage


class ProductImageForm(forms.ModelForm):
    upload = forms.ImageField(label='Изображение', required=False)

    class Meta:
        model = ProductImage
        fields = ('alt', 'sort_order', 'is_primary')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.path:
            self.fields['upload'].help_text = f'Текущий файл: {self.instance.path}'

    def clean(self):
        cleaned = super().clean()
        if self.instance.pk:
            return cleaned
        if not cleaned.get('upload'):
            raise forms.ValidationError({'upload': 'Загрузите изображение.'})
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        upload = self.cleaned_data.get('upload')
        if upload:
            if obj.path:
                delete_media_relative(obj.path)
            obj.path = save_upload_file('image', upload)
        if commit:
            obj.save()
        return obj
