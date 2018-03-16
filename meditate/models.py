from django.db import models


class OrderAddress(models.Model):
    name = models.CharField(max_length=40)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=18, null=True, blank=True)
    addr1 = models.CharField(max_length=80)
    addr2 = models.CharField(max_length=80)
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=30)
    zip = models.CharField(max_length=7)


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.PROTECT)
    count = models.IntegerField(default=0)
    saleItem = models.ForeignKey('SaleItem', on_delete=models.PROTECT)
    coupons = models.ManyToManyField('Coupon')


class Order(models.Model):
    sessionId = models.CharField(max_length=100)
    paymentProvider = models.CharField(max_length=6, default='')
    paymentId = models.CharField(max_length=100, null=True, default=None)
    total = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    address = models.OneToOneField('OrderAddress', null=True, blank=True, on_delete=models.PROTECT)


class SaleItem(models.Model):
    needsAddress = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=80, unique=True)
    desc = models.CharField(max_length=500)
    img = models.CharField(max_length=100) # should be a filename in 'static/'
    price = models.DecimalField(decimal_places=2, max_digits=4)


class Coupon(models.Model):
    deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=80)
    items = models.ManyToManyField('SaleItem')
    dollarsOff = models.DecimalField(decimal_places=4, max_digits=10)
    percentOff = models.DecimalField(decimal_places=4, max_digits=7)
