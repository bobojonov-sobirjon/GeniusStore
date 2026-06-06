from django.contrib import admin
from django.utils.html import format_html

from apps.common.media_urls import media_url
from apps.storefront.models import CartItem, Favorite, Review, SiteSettings


def _admin_media_url(file_field) -> str | None:
    if not file_field:
        return None
    name = getattr(file_field, 'name', None) or str(file_field)
    if not name:
        return None
    url = media_url(name)
    if url:
        return url
    path = name if name.startswith('/') else f'/media/{name.lstrip("/")}'
    if not path.startswith('/media/'):
        path = f'/media/uploads/{name.lstrip("/")}'
    return path


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
    list_display = ('author_name', 'preview_thumb', 'rating', 'source', 'is_published', 'created_at')
    list_display_links = ('author_name',)
    list_filter = ('source', 'is_published', 'rating')
    search_fields = ('author_name', 'text')
    readonly_fields = ('id', 'created_at')
    fields = (
        'author_name', 'text', 'rating', 'source', 'video_url',
        'thumbnail', 'is_published', 'id', 'created_at',
    )

    @admin.display(description='Просмотр превью')
    def preview_thumb(self, obj: Review):
        if not obj or not obj.pk:
            return format_html('<span style="color:#9ca3af;">—</span>')
        url = _admin_media_url(obj.thumbnail)
        if not url:
            return format_html('<span style="color:#9ca3af;">нет фото</span>')
        return format_html(
            '<img src="{}" alt="" '
            'style="height:40px;width:56px;border-radius:6px;object-fit:cover;display:block;">',
            url,
        )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'updated_at')

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
