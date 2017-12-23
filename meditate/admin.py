from django.contrib import admin
from meditate.models import OrderItem, Order, SaleItem, Coupon

admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(SaleItem)
admin.site.register(Coupon)
