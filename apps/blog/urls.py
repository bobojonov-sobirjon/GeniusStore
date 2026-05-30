from django.urls import path

from apps.blog.views import (
    BlogByCatView,
    BlogCategoryDetailView,
    BlogCategoryRootView,
    BlogDetailView,
    BlogPagedView,
    BlogRootView,
    BlogSlugView,
    BlogStepsDetailView,
    BlogStepsRootView,
)

urlpatterns = [
    path('blog-category', BlogCategoryRootView.as_view()),
    path('blog-category/<str:pk>', BlogCategoryDetailView.as_view()),
    path('blog', BlogRootView.as_view()),
    path('blog/cat/<str:cat_id>', BlogByCatView.as_view()),
    path('blog/all/<int:page>/<int:limit>', BlogPagedView.as_view()),
    path('blog/slug/<slug:slug>', BlogSlugView.as_view()),
    path('blog/<str:pk>', BlogDetailView.as_view()),
    path('blog-steps', BlogStepsRootView.as_view()),
    path('blog-steps/<str:pk>', BlogStepsDetailView.as_view()),
]
