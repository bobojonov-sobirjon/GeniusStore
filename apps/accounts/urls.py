from django.urls import path

from apps.accounts.views import (
    AdminCreateView,
    AuthAdminLoginView,
    AuthRefreshView,
    UserChangeAvatarView,
    UserChangePasswordView,
    UserDetailView,
    UserLoginView,
    UserLogoutView,
    UserResetPasswordView,
    UserRootView,
)

urlpatterns = [
    path('auth/refresh', AuthRefreshView.as_view(), name='auth-refresh'),
    path('auth/login-admin', AuthAdminLoginView.as_view(), name='auth-login-admin'),
    path('admin', AdminCreateView.as_view(), name='admin-create'),
    path('users', UserRootView.as_view(), name='users-root'),
    path('users/login', UserLoginView.as_view(), name='users-login'),
    path('users/logout', UserLogoutView.as_view(), name='users-logout'),
    path('users/reset-password', UserResetPasswordView.as_view(), name='users-reset-password'),
    path('users/change-avatar', UserChangeAvatarView.as_view(), name='users-change-avatar'),
    path('users/pass/<str:old>/<str:new>', UserChangePasswordView.as_view(), name='users-change-password'),
    path('users/<str:pk>', UserDetailView.as_view(), name='users-detail'),
]
