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
from django.urls import path
from wallets import views

app_name = 'wallets'

urlpatterns = [
    path('create', views.WalletCreation.as_view(), name='wallet_creation'),
    path('list', views.WalletList.as_view(), name='wallet_list'),
    path('info/<slug:wallet_token>', views.WalletInformation.as_view(), name='wallet_information'),
    path('deposit', views.WalletDeposit.as_view(), name='wallet_deposit'),
    path('history/<slug:wallet_token>', views.WalletHistory.as_view(), name='wallet_history'),
    path('charge', views.WalletCharge.as_view(), name='wallet_charge'),
]
