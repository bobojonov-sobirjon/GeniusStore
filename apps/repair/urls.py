from django.urls import path

from apps.repair.views import (
    ServiceBrandByModelView,
    ServiceBrandCreateView,
    ServiceBrandDetailView,
    ServiceBrandModelsView,
    ServiceBrandPageView,
    ServiceBrandSlugView,
    ServiceDetailView,
    ServiceModelDetailView,
    ServiceModelPageView,
    ServiceModelRootView,
    ServiceModelSlugView,
    ServicePageView,
    ServiceRootView,
    ServiceSlugView,
)

urlpatterns = [
    path('service-brand', ServiceBrandCreateView.as_view()),
    path('service-brand/page/<int:page>/<int:limit>', ServiceBrandPageView.as_view()),
    path('service-brand/by-model', ServiceBrandByModelView.as_view()),
    path('service-brand/service-brand/<str:brand_id>', ServiceBrandModelsView.as_view()),
    path('service-brand/model/<slug:slug>', ServiceBrandSlugView.as_view()),
    path('service-brand/<str:pk>', ServiceBrandDetailView.as_view()),
    path('service-model', ServiceModelRootView.as_view()),
    path('service-model/page/<int:page>/<int:limit>', ServiceModelPageView.as_view()),
    path('service-model/slug/<slug:slug>', ServiceModelSlugView.as_view()),
    path('service-model/<str:pk>', ServiceModelDetailView.as_view()),
    path('service', ServiceRootView.as_view()),
    path('service/page/<int:page>/<int:limit>', ServicePageView.as_view()),
    path('service/slug/<slug:slug>', ServiceSlugView.as_view()),
    path('service/<str:pk>', ServiceDetailView.as_view()),
]
