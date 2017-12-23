from django.db import models

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete='cascade')
    saleItem = models.ForeignKey('SaleItem', on_delete=models.PROTECT)
    coupons = models.ManyToManyField('Coupon')


class Order(models.Model):
    sessionId = models.CharField(max_length=100)


class SaleItem(models.Model):
    deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=80, unique=True)
    desc = models.CharField(max_length=500)
    img = models.CharField(max_length=100) # should be a filename in 'static/'
    price = models.DecimalField(decimal_places=2, max_digits=3)


class Coupon(models.Model):
    deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=80)
    items = models.ManyToManyField('SaleItem')
    dollarsOff = models.DecimalField(decimal_places=4, max_digits=10)
    percentOff = models.DecimalField(decimal_places=4, max_digits=7)
