from django.contrib import admin

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
    list_display = ('author_name', 'rating', 'source', 'is_published', 'created_at')
    list_filter = ('source', 'is_published', 'rating')
    search_fields = ('author_name', 'text')
    readonly_fields = ('id', 'created_at')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'updated_at')

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
