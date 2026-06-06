from django.contrib import admin
from django.utils.html import format_html

from apps.common.media_urls import media_url
from apps.storefront.models import CartItem, Favorite, Review, SiteSettings


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'variant_id', 'created_at')
    search_fields = ('user_id', 'variant_id')
    readonly_fields = ('id', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'variant_id', 'quantity', 'updated_at')
    search_fields = ('user_id', 'variant_id')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('preview_thumb', 'author_name', 'rating', 'source', 'is_published', 'created_at')
    list_filter = ('source', 'is_published', 'rating')
    search_fields = ('author_name', 'text')
    readonly_fields = ('id', 'preview_thumb', 'created_at')
    fields = (
        'author_name', 'text', 'rating', 'source', 'video_url',
        'thumbnail', 'preview_thumb', 'is_published', 'id', 'created_at',
    )

    @admin.display(description='Превью')
    def preview_thumb(self, obj: Review):
        if obj.thumbnail:
            url = media_url(obj.thumbnail) or obj.thumbnail.url
            return format_html(
                '<img src="{}" alt="" '
                'style="max-height:120px;max-width:160px;border-radius:10px;object-fit:cover;">',
                url,
            )
        return '—'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'updated_at')

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
