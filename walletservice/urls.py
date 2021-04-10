"""walletservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
import clients.urls
import companies.urls
import wallets.urls

# Used to automatic document our API endpoints
schema_view = get_swagger_view(title='Wallet Service API Documentation')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('documentation/', schema_view),
    path('client/', include(clients.urls, namespace="clients")),
    path('company/', include(companies.urls, namespace="companies")),
    path('wallet/', include(wallets.urls, namespace="wallets")),
]