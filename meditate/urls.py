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
from meditate.views import (
    homepage, why_meditate, about_author, sample, buy_book, subscribe_mentoring,
    add_order_item, remove_order_item, log_javascript, log_visit, get_order_count, order_summary,
    stripe_charge, paypal_charge, order_complete, set_order_address, contact_send_message,
    reflections, ReflectionsFeed, visit_charts
)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', homepage),
    path('why_meditate', why_meditate),
    path('sample/', sample),
    path('about_author/', about_author),
    path('buy_book', buy_book, name='buy_book'),
    path('subscribe', subscribe_mentoring, name='subscribe_mentoring'),
    path('add_order_item/<str:saleItemName>', add_order_item, name='add_order_item'),
    path('remove_order_item/<str:saleItemName>', remove_order_item, name='remove_order_item'),
    path('get_order_count/<str:saleItemName>', get_order_count, name='single_item_count'),
    path('get_order_count', get_order_count, name='all_item_count'),
    path('set_order_address', set_order_address, name='set_order_address'),
    path('contact_send_message', contact_send_message, name='contact_send_message'),
    path('log_javascript/<str:msg>', log_javascript, name='log_javascript'),
    path('log_visit/<str:page_name>', log_visit, name='log_visit'),
    path('order_summary', order_summary, name='order_summary'),
    path('stripe_charge', stripe_charge, name='stripe_charge'),
    path('paypal_charge', paypal_charge, name='paypal_charge'),
    path('order_complete', order_complete, name='order_complete'),
    path('reflections', reflections, name='reflections'),
    path('reflections/<str:title_slug>', reflections, name='single_reflection'),
    # Match the url layout on Weebly so links to this feed aren't broken on switch to this site.
    path('4/feed', ReflectionsFeed(), name='reflections_feed'),
    path('1/feed', ReflectionsFeed()),   # This is where weebly had the homepage-as-a-blog feed mapped to.
    path('visit_charts/<int:days_back>', visit_charts),
    path('visit_charts', visit_charts, name='visit_charts'),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
