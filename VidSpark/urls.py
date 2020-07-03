"""VidSpark URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="VidSpark API",
        default_version='v1',
        description="Automatic Indexer",
        contact=openapi.Contact(email="support@vidspark.com"),
        license=openapi.License(name="MIT License"),
    ),
    validators=['flex'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

admin.site.site_header = "VidSpark Administration"
admin.site.site_title = "VidSpark Administration"
admin.site.index_title = "Admin"

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui('cache_timeout=None'), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=None),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=None),
         name='schema-redoc'),
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('', admin.site.urls),
    path('api/user/', include('drf_user.urls'))
]

