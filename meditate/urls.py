"""meditate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from meditate.views import homepage, why_meditate, about_author, sample, buy_book, subscribe_mentoring

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', homepage),
    path('why_meditate', why_meditate),
    path('sample/', sample),
    path('about_author/', about_author),
    path('buy_book', buy_book),
    path('subscribe', subscribe_mentoring),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
