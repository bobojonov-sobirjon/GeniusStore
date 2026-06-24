from __future__ import annotations

from django import forms

from apps.store_core.models import ProductImage, ProductSpecItem


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('color', 'image', 'alt', 'sort_order', 'is_primary')

    def clean(self):
        cleaned = super().clean()
        if self.instance.pk:
            return cleaned
        if not cleaned.get('image'):
            raise forms.ValidationError({'image': 'Загрузите изображение.'})
        return cleaned


class ProductSpecItemForm(forms.ModelForm):
    values_text = forms.CharField(
        label='Значения',
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Одно значение на строку\nили несколько для списка'}),
        help_text='Каждая строка — отдельное значение (маркированный список на сайте). Игнорируется, если выбран «Источник из варианта».',
    )

    class Meta:
        model = ProductSpecItem
        fields = ('label', 'variant_source', 'sort_order')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and isinstance(self.instance.values, list):
            self.fields['values_text'].initial = '\n'.join(str(v) for v in self.instance.values)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('variant_source'):
            cleaned['values'] = []
            return cleaned
        text = cleaned.pop('values_text', '') or ''
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned['values'] = lines
        return cleaned

    def save(self, commit=True):
        self.instance.values = self.cleaned_data.get('values', [])
        return super().save(commit=commit)
