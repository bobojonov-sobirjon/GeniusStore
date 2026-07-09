from __future__ import annotations

from django import forms

from apps.store_core.models import Product, ProductCharacteristic, ProductImage, ProductVariant


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('color', 'image', 'alt', 'sort_order', 'is_primary')
        widgets = {
            'color': forms.Select(attrs={
                'class': 'whale-color-select',
                'style': 'min-width: 200px; width: 100%; max-width: 100%;',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].widget.attrs.setdefault('class', 'whale-color-select')
        self.fields['color'].widget.attrs.setdefault(
            'style', 'min-width: 200px; width: 100%; max-width: 100%;',
        )

    def clean(self):
        cleaned = super().clean()
        if self.instance.pk:
            return cleaned
        if not cleaned.get('image'):
            raise forms.ValidationError({'image': 'Загрузите изображение.'})
        return cleaned


class ProductCharacteristicForm(forms.ModelForm):
    """Плоская строка характеристики: тип + название + значение."""

    value_text = forms.CharField(
        label='Значение',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Одно значение или несколько строк для списка',
        }),
        help_text='Несколько значений — с новой строки.',
    )

    class Meta:
        model = ProductCharacteristic
        fields = ('spec_type', 'title', 'sort_order')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.setdefault(
            'placeholder', 'Серия, Память, Материал…',
        )
        if self.instance.pk and self.instance.value:
            self.fields['value_text'].initial = self.instance.value

    def clean(self):
        cleaned = super().clean()
        text = cleaned.pop('value_text', '') or ''
        cleaned['value'] = text
        return cleaned

    def save(self, commit=True):
        self.instance.value = self.cleaned_data.get('value', '')
        return super().save(commit=commit)


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        labels = {
            'description': 'Описание товара',
        }
        help_texts = {
            'description': 'Общий текст на странице товара (для всех вариантов).',
        }


class ProductVariantAdminForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = '__all__'
        labels = {
            'description': 'Описание варианта',
        }
        help_texts = {
            'memory': 'Необязательно — для товаров без объёма памяти (наушники, аксессуары).',
            'description': (
                'Текст только для этого цвета/памяти. '
                'На сайте меняется при выборе варианта.'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['memory'].required = False


class ProductVariantInlineForm(ProductVariantAdminForm):
    class Meta(ProductVariantAdminForm.Meta):
        fields = (
            'memory', 'color', 'sim_type', 'price', 'old_price',
            'discount', 'is_available', 'description', 'images',
        )
