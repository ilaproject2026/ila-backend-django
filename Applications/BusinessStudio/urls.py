from django.urls import path, include

urlpatterns = [
    path('studio/', include('Applications.BusinessStudio.StudioCore.studiocore_urls')),
]
