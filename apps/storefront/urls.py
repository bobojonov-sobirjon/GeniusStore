from django.urls import path

from apps.storefront.views import (
    BlogRelatedView,
    CartItemView,
    CartRootView,
    ConsultationView,
    FavoriteDetailView,
    FavoriteRootView,
    ProductRelatedView,
    ProductSearchSuggestView,
    ReviewDetailView,
    ReviewRootView,
    ReviewVideoListView,
    SiteSettingsView,
)

urlpatterns = [
    path('favorites', FavoriteRootView.as_view()),
    path('favorites/<str:variant_id>', FavoriteDetailView.as_view()),
    path('cart', CartRootView.as_view()),
    path('cart/<str:variant_id>', CartItemView.as_view()),
    path('reviews', ReviewRootView.as_view()),
    path('reviews/videos', ReviewVideoListView.as_view()),
    path('reviews/<str:pk>', ReviewDetailView.as_view()),
    path('site/settings', SiteSettingsView.as_view()),
    path('consultation', ConsultationView.as_view()),
    path('product/search/<str:query>/suggest', ProductSearchSuggestView.as_view()),
    path('product/slug/<slug:slug>/related', ProductRelatedView.as_view()),
    path('blog/slug/<slug:slug>/related', BlogRelatedView.as_view()),
]
