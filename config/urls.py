from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.decorators.cache import never_cache
from django.views.static import serve
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.common.views import APIView


def redirect_legacy_customuser_admin(request, rest=''):
    """Legacy URL: accounts.CustomUser is not used; store users live in store_core.StoreUser."""
    suffix = rest.strip('/')
    target = '/admin/store_core/storeuser/'
    if suffix:
        target = f'{target}{suffix}/'
    query = request.META.get('QUERY_STRING', '')
    if query:
        target = f'{target}?{query}'
    return redirect(target)


@extend_schema(tags=['Система'])
class ApiHealthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Проверка доступности API',
        description='Лёгкий GET без БД: возвращает `{"status":"ok"}` для балансировщиков и мониторинга.',
    )
    async def get(self, request):
        return Response({'status': 'ok'})


urlpatterns = [
    re_path(
        r'^admin/accounts/customuser(?:/(?P<rest>.*))?$',
        redirect_legacy_customuser_admin,
    ),
    path('_nested_admin/', include('nested_admin.urls')),
    path('admin/', admin.site.urls),
    path('api/health', ApiHealthView.as_view()),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.catalog.urls')),
    path('api/', include('apps.blog.urls')),
    path('api/', include('apps.repair.urls')),
    path('api/', include('apps.site_content.urls')),
    path('api/', include('apps.storefront.urls')),
]

urlpatterns += [
    path('schema/', never_cache(SpectacularAPIView.as_view()), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
