from django.urls import path, include

v1_patterns = [
    path('', include('Applications.ILA_WEB.urls')),
    path('auth/', include('Applications.Authentication.auth_urls')),
    path('', include('Applications.BusinessStudio.urls')),
    path('import-export/', include('Applications.ImportExport.urls')),
    path('global-real-estate/', include('Applications.GlobalRealEstate.urls')),
    path('corporate-admin/', include('Applications.CorporateAdmin.urls')),
    path('centralized-dashboard/', include('Applications.CorporateAdmin.urls')),
    path('centelized-dashboard/', include('Applications.CorporateAdmin.urls')),
    path('', include('Applications.CorporateAdmin.urls')),
]

urlpatterns = [
    # Support both /api/v1/... and /api/...
    path('v1/', include(v1_patterns)),
    # path('', include(v1_patterns)),
]