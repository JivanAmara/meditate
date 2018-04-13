from django.db import models
from django.utils.text import slugify

class OrderAddress(models.Model):
    name = models.CharField(max_length=40)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=18, null=True, blank=True)
    addr1 = models.CharField(max_length=80)
    addr2 = models.CharField(max_length=80)
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=30)
    postal_code = models.CharField(max_length=7)


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
    processed = models.BooleanField(default=False)


class SaleItem(models.Model):
    needsAddress = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=80, unique=True)
    desc = models.CharField(max_length=500)
    img = models.CharField(max_length=100) # should be a filename in 'static/'
    price = models.DecimalField(decimal_places=2, max_digits=5)

    def __str__(self):
        return self.name

class Coupon(models.Model):
    deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=80)
    items = models.ManyToManyField('SaleItem')
    dollarsOff = models.DecimalField(decimal_places=4, max_digits=10)
    percentOff = models.DecimalField(decimal_places=4, max_digits=7)


class Reflection(models.Model):
    title = models.CharField(max_length=100)
    title_slug = models.CharField(default="", blank=True, max_length=100)
    content = models.TextField()
    pub_time = models.DateTimeField()

    def __str__(self):
        return "{} ({})".format(self.title, self.pub_time.strftime('%Y-%m-%d %H:%M'))

    def save(self, *args, **kwargs):
        self.title_slug = slugify(self.title)
        super(Reflection, self).save(*args, **kwargs)
