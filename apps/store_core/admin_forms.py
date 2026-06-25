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


def _values_from_text(text: str) -> list[str]:
    return [line.strip() for line in (text or '').splitlines() if line.strip()]


class ProductSpecItemNestedForm(forms.ModelForm):
    """Строка внутри блока характеристик: только название и значения."""

    values_text = forms.CharField(
        label='Значения',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Одно значение или несколько строк для списка',
        }),
        help_text='Пусто, если выбран «Источник из варианта». Несколько значений — с новой строки.',
    )

    class Meta:
        model = ProductSpecItem
        fields = ('label', 'variant_source', 'sort_order')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['label'].widget.attrs.setdefault(
            'placeholder', 'Серия, Память, Материал…',
        )
        if self.instance.pk and isinstance(self.instance.values, list):
            self.fields['values_text'].initial = '\n'.join(str(v) for v in self.instance.values)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('variant_source'):
            cleaned['values'] = []
        else:
            text = cleaned.pop('values_text', '') or ''
            cleaned['values'] = _values_from_text(text)
        return cleaned

    def save(self, commit=True):
        self.instance.values = self.cleaned_data.get('values', [])
        return super().save(commit=commit)


class ProductSpecItemForm(ProductSpecItemNestedForm):
    """Плоская таблица (резерв) — с полями группы."""

    group_title = forms.CharField(
        label='Группа',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Основные характеристики'}),
    )
    group_sort_order = forms.IntegerField(
        label='№ группы',
        required=False,
        min_value=0,
        initial=0,
    )

    class Meta(ProductSpecItemNestedForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.group_title:
                self.fields['group_title'].initial = self.instance.group_title
            elif self.instance.group_id:
                self.fields['group_title'].initial = self.instance.group.title
            self.fields['group_sort_order'].initial = (
                self.instance.group_sort_order
                if self.instance.group_sort_order is not None
                else (self.instance.group.sort_order if self.instance.group_id else 0)
            )

    def clean(self):
        cleaned = forms.ModelForm.clean(self)
        group_title = (cleaned.get('group_title') or '').strip()
        if not group_title and self.instance.group_id:
            group_title = self.instance.group.title
        if not group_title:
            raise forms.ValidationError({'group_title': 'Укажите название группы.'})
        cleaned['group_title'] = group_title
        sort_raw = cleaned.get('group_sort_order')
        cleaned['group_sort_order'] = max(0, int(sort_raw)) if sort_raw is not None else 0

        if cleaned.get('variant_source'):
            cleaned['values'] = []
        else:
            text = cleaned.pop('values_text', '') or ''
            cleaned['values'] = _values_from_text(text)
        return cleaned

    def save(self, commit=True):
        self.instance.group_title = self.cleaned_data['group_title']
        self.instance.group_sort_order = self.cleaned_data['group_sort_order']
        self.instance.values = self.cleaned_data.get('values', [])
        return forms.ModelForm.save(self, commit=commit)
