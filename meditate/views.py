'''
Created on Dec 9, 2017

@author: jivan
'''
import decimal
import grp
import stat
import hashlib
import json
import logging
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone, timedelta
import re
from pprint import pformat
import matplotlib as mpl
mpl.use('Agg')  # This is to eliminate the assumption that there's an X server running.
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from meditate.orders import send_alert
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.conf import settings
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
import stripe

from meditate.models import SaleItem, Order, OrderItem, OrderAddress, Reflection, Visit
from django.views.decorators.csrf import csrf_exempt
from django import urls
from django.views.decorators.http import require_POST
from pip._vendor.requests.sessions import session

logger = logging.getLogger(__name__)


STRIPE_SECRET_KEY = None
STRIPE_PUBLIC_KEY = None
PAYPAL_MODE = None
def ensure_payment_envvars(func):
    def wrapped_func(*args, **kwargs):
        global STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY, PAYPAL_MODE
        # See your stripe keys here: https://dashboard.stripe.com/account/apikeys
        if stripe.api_key is None:
            stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', None)
            if stripe.api_key is None:
                raise Exception('Environment variable STRIPE_SECRET_KEY not set.')

        if STRIPE_PUBLIC_KEY is None:
            STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', None)
            if STRIPE_PUBLIC_KEY is None:
                raise Exception('Environment variable STRIPE_PUBLIC_KEY not set.')

        if PAYPAL_MODE is None:
            PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox') # or 'production'
        return func(*args, **kwargs)

    return wrapped_func


def get_session_id(request):
    # Returns the current session id, creating a new one if necessary
    while request.session.session_key is None:
        request.session.save()
    return request.session.session_key


def homepage(request):
    resp = render(request, 'home.html', {'page_name': 'home'})
    return resp


def sample(request):
    resp = render(request, 'sample.html', {'page_name': 'sample'})
    return resp


def about_author(request):
    resp = render(request, 'about_author.html', {'page_name': 'about_author'})
    return resp


def why_meditate(request):
    resp = render(request, 'why_meditate.html', {'page_name': 'why_meditate'})
    return resp


def buy_book(request):
    items = SaleItem.objects.filter(sitype='book').order_by('name')
    context = {'items': items, 'page_name': 'buy_book'}
    resp = render(request, 'buy_book.html', context)
    return resp


def subscribe_mentoring(request):
    items = SaleItem.objects.filter(sitype='mentoring').order_by('name')
    context = {'items': items, 'page_name': 'subscribe_mentoring'}
    resp = render(request, 'subscribe_mentoring.html', context)
    return resp


def set_up_download_links(order):
    """ This makes symbolic links in <STATIC_ROOT>/downloads/<downloadKey>/ to items
        in meditate/downloads for users to download files from.  Also removes old <downloadKey>
        directories.
        This allows nginx to handle serving the files, but still avoid wide-open access to the
        files.
    """
    # Get any downloadable SaleItems included in this Order
    downloadables = SaleItem.objects.filter(orderitem__order=order).exclude(downloadable="")
    for d in downloadables:
        basename = os.path.basename(d.downloadable.name)
        os.makedirs(os.path.join(settings.STATIC_ROOT, 'downloads', order.downloadKey), exist_ok=True)
        symlink_loc = os.path.join(settings.STATIC_ROOT, 'downloads', order.downloadKey, basename)
        symlink_target = os.path.join(settings.MEDIA_ROOT, d.downloadable.name)
        os.symlink(symlink_target, symlink_loc)

    download_key_dirs = [
        name for name in os.listdir(os.path.join(settings.STATIC_ROOT, 'downloads'))
            if os.path.isdir(os.path.join(settings.STATIC_ROOT, 'downloads', name))
    ]

    cutoff = datetime.now(timezone.utc) - settings.VALID_DOWNLOAD_PERIOD
    old_orders = Order.objects.filter(paymentTimestamp__lt=cutoff, downloadKey__in=download_key_dirs)
    for oo in old_orders:
        shutil.rmtree(os.path.join(settings.STATIC_ROOT, 'downloads', oo.downloadKey))


def order_complete(request):
    sessionId = get_session_id(request)
    logger.info('order_complete() hit w/ sessionId "{}"'.format(sessionId))
    order = Order.objects.get(sessionId=sessionId)
    md5hasher = hashlib.md5()
    md5hasher.update(sessionId.encode('utf8'))
    key = md5hasher.hexdigest()[:12]
    order.downloadKey = key
    order.save()
    set_up_download_links(order)
    context = {'order_number': order.paymentId, 'order': order, 'page_name': 'order_complete'}
    resp = render(request, 'order_complete.html', context)
    request.session.flush()
    return resp


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def add_order_item(request, saleItemName):
    try:
        sessionId = get_session_id(request)
        saleItem = SaleItem.objects.get(name=saleItemName)
        order, _ = Order.objects.get_or_create(sessionId=sessionId)
        item, _ = OrderItem.objects.get_or_create(order=order, saleItem=saleItem)
        item.count = item.count + 1
        item.save()
        jsonText = json.dumps({'count': item.count, 'price': saleItem.price}, cls=DecimalEncoder)
        resp = HttpResponse(jsonText, content_type="application/json")
    except Exception as ex:
        logger.error('Problem adding item to order: {0}'.format(ex))
        resp = HttpResponse(status=500)

    return resp


def remove_order_item(request, saleItemName):
    try:
        sessionId = get_session_id(request)
        saleItem = SaleItem.objects.get(name=saleItemName)
        order, _ = Order.objects.get_or_create(sessionId=sessionId)
        item, _ = OrderItem.objects.get_or_create(order=order, saleItem=saleItem)
        if item.count <= 1:
            item.delete()
        else:
            item.count = item.count - 1
            item.save()

        jsonText = json.dumps({'count': item.count, 'price': saleItem.price}, cls=DecimalEncoder)
        resp = HttpResponse(jsonText, content_type="application/json")
    except Exception as ex:
        logger.error('Problem adding item to order: {0}'.format(ex))
        resp = HttpResponse(status=500)

    return resp


def get_order_count(request, saleItemName=None):
    try:
        sessionId = get_session_id(request)
        order, _ = Order.objects.get_or_create(sessionId=sessionId)
        orderCount = 0
        itemPrice = None

        # Count total of all items in order
        if saleItemName is None:
            for item in order.orderitem_set.all():
                orderCount += item.count
        # Just count the named item
        else:
            oi = OrderItem.objects.get(order__sessionId=sessionId, saleItem__name=saleItemName)
            orderCount = oi.count
            itemPrice = oi.saleItem.price

        jsonText = json.dumps({'count': orderCount, 'price': itemPrice}, cls=DecimalEncoder)
        resp = HttpResponse(jsonText, content_type="application/json")
    except Exception as ex:
        logger.error('get_order_count() problem: {0}'.format(ex))
        resp = HttpResponse(status=500)

    return resp


@require_POST
def set_order_address(request):
    try:
        # These should match OrderAddress fields.  Fields email, phone, and addr2 are optional
        sessionId = get_session_id(request)
        # Address
        a = {
            'name': request.POST.get('name', None),
            'email': request.POST.get('email', None),
            'phone': request.POST.get('phone', None),
            'addr1': request.POST.get('addr1', None),
            'addr2': request.POST.get('addr2', None),
            'city': request.POST.get('city', None),
            'state': request.POST.get('state', None),
            'country': request.POST.get('country', None),
            'zip': request.POST.get('zip', None),
        }

        required = ['name', 'addr1', 'city', 'state', 'country', 'zip']
        # map of field ids to a flag with True indicating an invalid value
        invalid = { field: val == None or val == ''
                    for field, val in a.items() if field in required }

        if any(invalid.values()):
            msg = 'missing required address field(s): {}\n{}'.format(a, invalid)
            logger.error(msg)
            jsonText = json.dumps({'detail': msg, 'invalid': invalid})
            resp = HttpResponse(jsonText, content_type='applicaton/json', status=200)
            return resp

        oa, _ = OrderAddress.objects.get_or_create(order__sessionId=sessionId)

        oa.name = a['name']
        oa.email = a['email']
        oa.phone = a['phone']
        oa.addr1 = a['addr1']
        oa.addr2 = a['addr2']
        oa.city = a['city']
        oa.state = a['state']
        oa.country = a['country']
        oa.zip = a['zip']
        oa.save()

        jsonText = json.dumps(a)
        resp = HttpResponse(jsonText, content_type='application/json', status=201)
        return resp
    except Exception as ex:
        logger.error('add_order_address() problem: {0}'.format(ex))
        resp = HttpResponse(status=500)
        return resp


@require_POST
def contact_send_message(request):
    msgData = {
        'sender_name': request.POST.get('sender_name', None),
        'sender_email': request.POST.get('sender_email', None),
        'subject': request.POST.get('subject', None),
        'message': request.POST.get('message', None),
    }

    if None in [msgData]:
        errmsg = ", ".join(["{} required".format(fieldname) for fieldname in msgData if msgData[fieldname] is not None])
        return HttpResponse(errmsg, status_code=400)

    MAIL_USER = str(os.environ.get('MAIL_USER', ''))
    MAIL_PASSWORD = str(os.environ.get('MAIL_PASSWORD', ''))
    send_alert("From: {} ({})\n---\n{}".format(msgData['sender_name'], msgData['sender_email'], msgData['message']),
        subject=msgData['subject'],
        from_addr=msgData['sender_email'],
        user=MAIL_USER,
        password=MAIL_PASSWORD
    )
    return HttpResponse(status=200)


ipv4_address = re.compile('^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
ipv6_address = re.compile('^(?:(?:[0-9A-Fa-f]{1,4}:){6}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|::(?:[0-9A-Fa-f]{1,4}:){5}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,4}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){,6}[0-9A-Fa-f]{1,4})?::)$')


def log_visit(request, page_name):
    IPv4_Len = (7, 15)

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    ip6 = ""; ip4 = ""
    if ipv4_address.fullmatch(ip):
        ip4 = ip
    elif ipv6_address.fullmatch(ip):
        ip6 = ip
    else:
        logger.warn('mal-formed ip address "{}"'.format(ip))

    v = Visit.objects.create(ip4=ip4, ip6=ip6, timestamp=datetime.now(timezone.utc), page=page_name)
    return HttpResponse(status=200)


def log_javascript(request, msg):
    logger.error(msg)
    return HttpResponse(status=200)


@ensure_payment_envvars
def order_summary(request):
    sessionId = get_session_id(request)
    order, _ = Order.objects.get_or_create(sessionId=sessionId)
    context = {
        'page_name': 'order_summary',
        'order': order,
        'STRIPE_PUBLIC_KEY': STRIPE_PUBLIC_KEY,
        'PAYPAL_MODE': PAYPAL_MODE,
    }
    resp = render(request, 'order_summary.html', context)
    return resp


def reflections(request, title_slug=None):
    if title_slug is None:
        rs = Reflection.objects.all().order_by('-pub_time')
    else:
        rs = Reflection.objects.filter(title_slug=title_slug).order_by('-pub_time')

    return render(request, 'reflections.html', {'reflections': rs, 'page_name': 'reflections'})


class ReflectionsFeed(Feed):
    description_template = 'reflections_description.html'
    title = "Meditation, Mind and Body - Reflections"
    link = "/4/feed"
    description = "Reflections arising from & about meditation."

    def items(self):
        return Reflection.objects.order_by('-pub_time')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        d = item.content[:500]
        if len(item.content) > 500:
            d += '...'
        return d

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return urls.reverse('single_reflection', kwargs={"title_slug": item.title_slug})


@ensure_payment_envvars
@csrf_exempt
def stripe_charge(request):
    sessionId = get_session_id(request)
    logger.info('stripe_charge() hit w/ sessionId: "{}"'.format(sessionId))
    order = Order.objects.get(sessionId=sessionId)
    success = False
    error_msg = ''

    # amount is the amount to charge in USD cents.
    try:
        request_args = json.loads(request.body.decode('utf8'))
        stripe_token = request_args['stripeToken']
        logger.info('Got stripeToken from json payload')
    except:
        POST = request.POST
        stripe_token = POST['stripeToken']
        logger.info('Got stripeToken from POST args')

    try:
        amount = request_args['amount']
        logger.info('Got amount from json payload')
    except:
        amount = POST['amount']
        logger.info('Got amount from POST args')

    # Create a charge: this will charge the user's card
    try:
        description = \
            "Your Order From Meditate.JivanAmara.net"
        charge = stripe.Charge.create(
            amount=int(amount),  # Amount in cents
            currency="usd",
            source=stripe_token,
            description=description
        )
        success = True
        msg = pformat(charge, indent=4)
        order.paymentId = charge.id
        order.total = decimal.Decimal(amount) / decimal.Decimal(100)
        order.paymentProvider = 'stripe'
        order.paymentTimestamp = datetime.now(timezone.utc)
        order.save()
        logger.info('Stripe Charge object:\n{}'.format(msg))
    except stripe.error.CardError as e:
        # The card has been declined
        success = False
        error_msg = 'Stripe CardError: {}'.format(pformat(e, indent=4))
        logger.info(error_msg)
    except Exception as e:
        msg = 'Unexpected Error: {}'.format(pformat(e, indent=4))
        success = False
        error_msg = msg
        logger.critical(msg)

    if success is True:
        resp = {'detail': 'ok'}
        status_code = 200
    else:
        msg = 'Stripe charge declined: {}'.format(error_msg)
        logger.error(msg)
        resp = {'detail': msg}
        status_code = 402

    return JsonResponse(resp, status=status_code)


@csrf_exempt
def paypal_charge(request):
    sessionId = get_session_id(request)
    logger.info('paypal_charge() hit w/ sessionId: "{}"'.format(sessionId))
    order, _ = Order.objects.get_or_create(sessionId=sessionId)
    order.paymentId = request.POST.get('paymentId')
    order.total = request.POST.get('amount')
    if order.paymentId == None or order.total == None:
        return JsonResponse({'detail': 'missing parameters'}, status=400)
    order.paymentProvider = 'paypal'
    order.paymentTimestamp = datetime.now(timezone.utc)
    order.save()
    logger.info('PayPal Charge Recorded: {} - {}'.format(order.total, order.paymentId))
    return JsonResponse({}, status=200)


@login_required
def visit_charts(request, days_back=30):
    plot_filename = 'stats.png'

    start_date = datetime.now(timezone.utc) - timedelta(days_back)
    # This will be of the form [ [ip, timestamp, page], ... ]
    visits_by_date = []
    for v in Visit.objects.filter(timestamp__gt=start_date).order_by('timestamp'):
        ip = v.ip6 if v.ip6 != "" else v.ip4
        visits_by_date.append([ip, v.timestamp.date(), v.page])

    # --- Count up page visits
    page_visit_count_by_date = defaultdict(int)
    page_visit_count_by_page = defaultdict(int)
    for _, date, page in visits_by_date:
        page_visit_count_by_date[date] += 1
        page_visit_count_by_page[page] += 1
    date_pcount = []
    for date, visit_count in page_visit_count_by_date.items():
        date_pcount.append([date, visit_count])
    date_pcount.sort(key=lambda d: d[0])

    page_vcount = []
    for page, visit_count in page_visit_count_by_page.items():
        page_vcount.append([page, visit_count])
    page_vcount.sort(key=lambda d: d[1], reverse=True)

    # --- Count up unique visitors
    visitor_count_by_date = defaultdict(int)
    seen_ips = defaultdict(list)
    for ip, date, _ in visits_by_date:
        if ip in seen_ips[date]:
            continue
        seen_ips[date].append(ip)
        visitor_count_by_date[date] += 1
    date_vcount = []
    for date, vcount in visitor_count_by_date.items():
        date_vcount.append([date, vcount])
    date_vcount.sort(key=lambda d: d[0])

    plt.figure(figsize=(6,12))
    ax1 = plt.subplot(311)
    plt.title('Page visits by date')
    plt.xticks(rotation=90)
    # format the ticks
    ax1.xaxis.set_major_locator(mdates.DayLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    # ax.xaxis.set_minor_locator(mdates.DayLocator())
    ax1.plot([i[0] for i in date_pcount], [i[1] for i in date_pcount], "-o")

    ax2 = plt.subplot(312)
    plt.title('Unique visitors by date')
    plt.xticks(rotation=90)
    ax2.xaxis.set_major_locator(mdates.DayLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax2.plot([i[0] for i in date_vcount], [i[1] for i in date_vcount], "-o")

    ax3 = plt.subplot(313)
    plt.title('Visit counts by page')
    plt.xticks(rotation=90)
    ax3.plot([i[0] for i in page_vcount], [i[1] for i in page_vcount], "-o")

    plt.tight_layout()

    symlink_target = os.path.join('/tmp', plot_filename)
    symlink_tmp = tempfile.mktemp()
    symlink_loc = os.path.join(settings.STATIC_ROOT, 'plots', plot_filename)

    plt.savefig(symlink_target)

    gid = grp.getgrnam(settings.STATIC_GROUP).gr_gid
    os.chown(symlink_target, -1, gid)
    os.chmod(symlink_target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)

    os.symlink(symlink_target, symlink_tmp)
    os.replace(symlink_tmp, symlink_loc)

    return HttpResponse('<img src="{}">'.format(os.path.join(settings.STATIC_URL, 'plots', plot_filename)))
