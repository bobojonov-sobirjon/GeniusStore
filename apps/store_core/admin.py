"""Django admin for Prisma-backed store tables (unmanaged models)."""
from __future__ import annotations

import nested_admin
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from apps.common.media_urls import media_url
from apps.store_core import models as m
from apps.store_core.admin_forms import ProductImageForm, ProductSpecItemForm, ProductSpecItemNestedForm
from apps.store_core.category_specs import spec_field_names_for_category


class WhaleStoreAdminMixin:
    """Whale Store UI: slide-out drawer for simple add forms."""

    drawer_add = True
    change_list_template = 'admin/whale/change_list.html'
    change_form_template = 'admin/whale/change_form.html'

    class Media:
        css = {'all': ('admin/css/custom_admin.css',)}
        js = ('admin/js/admin_drawer.js',)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['is_drawer'] = request.GET.get('_drawer') == '1'
        extra_context['drawer_add'] = getattr(self, 'drawer_add', False)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['drawer_add'] = getattr(self, 'drawer_add', False)
        return super().changelist_view(request, extra_context)

    def _drawer_close_response(self):
        return HttpResponse(
            '<script>window.parent.postMessage({type:"whale-drawer-close", success:true}, "*");</script>'
        )

    def response_add(self, request, obj, post_url_continue=None):
        if request.GET.get('_drawer') == '1':
            return self._drawer_close_response()
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if request.GET.get('_drawer') == '1':
            return self._drawer_close_response()
        return super().response_change(request, obj)


@admin.register(m.StoreUser)
class StoreUserAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    drawer_add = False
    list_display = ('email', 'phone', 'first_name', 'last_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('email', 'phone', 'first_name', 'last_name', 'middle_name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('email', 'phone', 'first_name', 'last_name', 'middle_name', 'avatar', 'password'),
        }),
        ('Системные поля', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        if obj is not None:
            fields.append('password')
        return fields


@admin.register(m.StoreAdmin)
class StoreAdminAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('username', 'id')
    search_fields = ('username',)
    ordering = ('username',)
    readonly_fields = ('id',)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('id', 'password')
        return ('id',)


@admin.register(m.Category)
class CategoryAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'icon')


@admin.register(m.Brand)
class BrandAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'image')


@admin.register(m.ProductModel)
class ProductModelAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name',)


@admin.register(m.Condition)
class ConditionAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name',)


@admin.register(m.SimType)
class SimTypeAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name',)


@admin.register(m.Color)
class ColorAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('color_preview', 'name', 'hex', 'created_at')
    search_fields = ('name', 'hex')
    ordering = ('name',)
    fields = ('name', 'hex')

    @admin.display(description='')
    def color_preview(self, obj):
        hex_color = obj.hex or '#cccccc'
        return format_html(
            '<span style="display:inline-block;width:22px;height:22px;border-radius:50%;'
            'background:{};border:1px solid #d1d5db;"></span>',
            hex_color,
        )


@admin.register(m.Memory)
class MemoryAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name',)


class ProductVariantSimTypeInline(admin.TabularInline):
    model = m.ProductVariantSimType
    extra = 0
    autocomplete_fields = ('sim_type',)


class ProductImageInline(admin.TabularInline):
    model = m.ProductImage
    form = ProductImageForm
    extra = 1
    classes = ('whale-card',)
    fields = ('preview', 'color', 'image', 'alt', 'sort_order', 'is_primary')
    readonly_fields = ('preview',)
    autocomplete_fields = ('color',)
    verbose_name = 'Фото'
    verbose_name_plural = 'Изображения по цветам (для смены фото на сайте укажите цвет)'

    @admin.display(description='Превью')
    def preview(self, obj):
        if obj.image:
            url = media_url(obj.image) or obj.image.url
            return format_html(
                '<img src="{}" alt="" '
                'style="max-height:56px;max-width:80px;border-radius:8px;object-fit:cover;">',
                url,
            )
        return '—'


class ProductVariantInline(admin.StackedInline):
    model = m.ProductVariant
    extra = 0
    show_change_link = False
    classes = ('whale-card',)
    fields = (
        'memory', 'color', 'sim_type', 'price', 'old_price',
        'discount', 'is_available', 'description', 'images',
    )
    autocomplete_fields = ('memory', 'color', 'sim_type')


class ProductSpecItemNestedInline(nested_admin.NestedTabularInline):
    model = m.ProductSpecItem
    form = ProductSpecItemNestedForm
    extra = 1
    min_num = 0
    classes = ('whale-card', 'nested-spec-items')
    fields = ('sort_order', 'label', 'variant_source', 'values_text')
    ordering = ('sort_order', 'label')
    verbose_name = 'Строка'
    verbose_name_plural = 'Название и значения'


class ProductSpecGroupNestedInline(nested_admin.NestedStackedInline):
    model = m.ProductSpecGroup
    inlines = (ProductSpecItemNestedInline,)
    extra = 1
    min_num = 0
    sortable_field_name = 'sort_order'
    classes = ('whale-card', 'nested-spec-group')
    fields = ('sort_order', 'title')
    ordering = ('sort_order', 'title')
    verbose_name = 'Характеристика'
    verbose_name_plural = (
        'Характеристики — добавьте блок (Основные характеристики, Корпус…), '
        'внутри укажите Название и Значения'
    )


class ProductSpecItemInline(admin.TabularInline):
    """Строки при редактировании группы отдельно."""
    model = m.ProductSpecItem
    form = ProductSpecItemNestedForm
    fk_name = 'group'
    extra = 1
    classes = ('whale-card',)
    fields = ('sort_order', 'label', 'variant_source', 'values_text')
    ordering = ('sort_order', 'label')
    verbose_name = 'Строка'
    verbose_name_plural = 'Название и значения'


@admin.register(m.ProductSpecGroup)
class ProductSpecGroupAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    drawer_add = False
    list_display = ('title', 'product', 'sort_order', 'created_at')
    list_filter = ('product__category', 'product__brand')
    search_fields = ('title', 'product__title', 'product__slug')
    autocomplete_fields = ('product',)
    ordering = ('product__title', 'sort_order')
    inlines = (ProductSpecItemInline,)
    fields = ('product', 'sort_order', 'title')


@admin.register(m.Product)
class ProductAdmin(WhaleStoreAdminMixin, nested_admin.NestedModelAdmin):
    class Media(WhaleStoreAdminMixin.Media, nested_admin.NestedModelAdmin.Media):
        pass

    drawer_add = False
    list_display = ('title', 'brand', 'category', 'is_available', 'slug', 'created_at')
    list_filter = ('category', 'is_available', 'is_new', 'is_hit', 'brand')
    search_fields = ('title', 'slug', 'article', 'description')
    autocomplete_fields = ('brand', 'category', 'condition', 'product_model')
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = (ProductImageInline, ProductVariantInline, ProductSpecGroupNestedInline)

    _BASE_FIELDSETS = (
        ('Основная информация', {
            'fields': ('title', 'article', 'description'),
            'classes': ('whale-card', 'whale-basic-info'),
        }),
        ('Категория и бренд', {
            'fields': ('brand', 'category'),
            'classes': ('whale-card',),
        }),
        ('Настройки товара', {
            'fields': (('is_new', 'is_hit', 'is_bt'), 'is_available', 'rating', 'slug'),
            'classes': ('whale-card', 'whale-product-settings'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        category_slug = None
        if obj and obj.category_id:
            category_slug = obj.category.slug
        spec_names = spec_field_names_for_category(category_slug)
        spec_fields = tuple(spec_names)
        spec_title = 'Дополнительные характеристики'
        if obj and obj.category_id:
            spec_title = f'Характеристики — {obj.category.name}'
        elif not obj:
            spec_title = 'Дополнительные характеристики (после сохранения подстроятся под категорию)'

        return (
            self._BASE_FIELDSETS[0],
            self._BASE_FIELDSETS[1],
            (spec_title, {
                'fields': spec_fields,
                'classes': ('whale-card', 'whale-specs-grid'),
                'description': (
                    'Набор полей зависит от категории (смартфоны, пылесосы и т.д.). '
                    'Память и цвет задаются во вкладке вариантов.'
                ),
            }),
            self._BASE_FIELDSETS[2],
        )


@admin.register(m.ProductImage)
class ProductImageAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    drawer_add = False
    form = ProductImageForm
    list_display = ('preview_thumb', 'product', 'color', 'alt', 'sort_order', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'color', 'product__category', 'product__brand')
    search_fields = ('product__title', 'product__slug', 'alt')
    autocomplete_fields = ('product', 'color')
    ordering = ('product__title', 'sort_order')
    readonly_fields = ('preview_thumb', 'created_at')
    fields = (
        'product', 'color', 'image', 'preview_thumb',
        'alt', 'sort_order', 'is_primary', 'created_at',
    )

    @admin.display(description='Фото')
    def preview_thumb(self, obj):
        if obj.image:
            url = media_url(obj.image) or obj.image.url
            return format_html(
                '<img src="{}" alt="" '
                'style="max-height:120px;max-width:160px;border-radius:10px;object-fit:cover;">',
                url,
            )
        return '—'


@admin.register(m.ProductVariant)
class ProductVariantAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    drawer_add = False
    list_display = (
        'product', 'category_tag', 'memory', 'color_tag',
        'price', 'old_price', 'discount', 'is_available',
    )
    list_editable = ('price', 'old_price', 'discount', 'is_available')
    list_filter = ('product__category', 'memory', 'color', 'is_available')
    search_fields = ('product__title', 'product__slug', 'id')
    autocomplete_fields = ('product', 'memory', 'color', 'sim_type')
    ordering = ('product__title', 'memory__name', 'color__name')
    list_per_page = 50
    inlines = (ProductVariantSimTypeInline,)

    @admin.display(description='Категория')
    def category_tag(self, obj):
        return obj.product.category if obj.product_id else '—'

    @admin.display(description='Цвет')
    def color_tag(self, obj):
        if not obj.color_id:
            return '—'
        hex_color = obj.color.hex or '#cccccc'
        return format_html(
            '<span class="color-dot" style="background:{}"></span> {}',
            hex_color,
            obj.color.name,
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        product_count = m.Product.objects.count()
        variant_count = m.ProductVariant.objects.count()
        extra_context['title'] = 'Управление ценами'
        extra_context['subtitle'] = f'{product_count} товаров • {variant_count} вариантов'
        return super().changelist_view(request, extra_context)


class OrderItemInline(admin.TabularInline):
    model = m.OrderItem
    extra = 0
    show_change_link = False
    autocomplete_fields = ('product_variant',)
    readonly_fields = ('unit_price', 'line_total', 'created_at')
    fields = ('product_variant', 'quantity', 'unit_price', 'line_total', 'created_at')


@admin.register(m.StoreOrder)
class StoreOrderAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    drawer_add = False
    list_display = ('id', 'full_name', 'email', 'phone', 'total_sum', 'delivery_type', 'items_count', 'created_at')
    list_filter = ('delivery_type', 'created_at')
    search_fields = ('id', 'full_name', 'email', 'phone', 'user__email')
    autocomplete_fields = ('user',)
    ordering = ('-created_at',)
    readonly_fields = ('id', 'total_sum', 'created_at', 'updated_at')
    inlines = (OrderItemInline,)
    fieldsets = (
        (None, {
            'fields': ('id', 'full_name', 'email', 'phone', 'user', 'total_sum', 'delivery_type', 'created_at', 'updated_at'),
            'classes': ('whale-card',),
        }),
        ('Адрес доставки', {
            'fields': ('apartment', 'entrance', 'floor'),
            'classes': ('whale-card',),
        }),
    )

    @admin.display(description='Позиций')
    def items_count(self, obj: m.StoreOrder) -> int:
        return obj.items.count()


@admin.register(m.BlogCategory)
class BlogCategoryAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name',)


class BlogStepsInline(admin.StackedInline):
    model = m.BlogSteps
    extra = 0
    show_change_link = False
    fields = ('title', 'content')


@admin.register(m.Blog)
class BlogAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    drawer_add = False
    list_display = ('title', 'blog_category', 'slug', 'created_at')
    list_filter = ('blog_category', 'created_at')
    search_fields = ('title', 'slug', 'content')
    autocomplete_fields = ('blog_category',)
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = (BlogStepsInline,)
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'blog_category', 'image', 'slug'),
            'classes': ('whale-card',),
        }),
    )


class ServiceModelInline(admin.TabularInline):
    model = m.ServiceModel
    extra = 0
    show_change_link = False
    prepopulated_fields = {'slug': ('name',)}


@admin.register(m.ServiceBrand)
class ServiceBrandAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    drawer_add = False
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'image')
    inlines = (ServiceModelInline,)


@admin.register(m.Banner)
class BannerAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'img_pc', 'img_mobile'),
            'classes': ('whale-card',),
        }),
    )


@admin.register(m.Info)
class InfoAdmin(WhaleStoreAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    fields = ('name', 'description')
