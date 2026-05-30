from django.urls import path

from apps.site_content.views import BannerDetailView, BannerRootView, InfoDetailView, InfoRootView

urlpatterns = [
    path('banner', BannerRootView.as_view()),
    path('banner/<str:pk>', BannerDetailView.as_view()),
    path('info', InfoRootView.as_view()),
    path('info/<str:pk>', InfoDetailView.as_view()),
]
