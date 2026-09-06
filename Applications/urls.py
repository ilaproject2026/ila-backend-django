from django.urls import path, include

v1_patterns = [
    path('auth/', include('Applications.Authentication.auth_urls')),
    path('', include('Applications.ILA_WEB.urls')),
]

urlpatterns = [
    # Support both /api/v1/... and /api/...
    path('v1/', include(v1_patterns)),
    path('', include(v1_patterns)),
]