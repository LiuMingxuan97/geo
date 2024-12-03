"""
URL configuration for geo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.urls import path
from ninja import NinjaAPI
from geo2img.views import router as geo2img_router
from img2geo.views import router as img2geo_router


api = NinjaAPI()
api.add_router("", geo2img_router)
api.add_router("", img2geo_router)

urlpatterns = [
    path('transform/', api.urls)
]
