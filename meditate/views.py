'''
Created on Dec 9, 2017

@author: jivan
'''
import decimal
import json
import logging
import os
from pprint import pformat

from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
import stripe

from meditate.models import SaleItem, Order, OrderItem


# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'Env var STRIPE_SECRET_KEY not set')



logger = logging.getLogger(__name__)


def get_session_id(request):
    # Returns the current session id, creating a new one if necessary 
    while request.session.session_key is None:
        request.session.save()
    return request.session.session_key


def homepage(request):
    resp = render(request, 'home.html')
    return resp


def sample(request):
    resp = render(request, 'sample.html')
    return resp


def about_author(request):
    resp = render(request, 'about_author.html')
    return resp


def why_meditate(request):
    resp = render(request, 'why_meditate.html')
    return resp


def buy_book(request):
    items = []
    items.append(SaleItem.objects.get(name='eBook, PDF'))
    items.append(SaleItem.objects.get(name='Paperback'))
    context = {'items': items, 'request': request}
    resp = render_to_response('buy_book.html', context=context)
    return resp


def subscribe_mentoring(request):
    resp = render(request, 'subscribe_mentoring.html')
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
        item.count = item.count - 1 if item.count > 0 else 0
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


def log_javascript(request, msg):
    logger.error(msg)


def order_summary(request):
    sessionId = get_session_id(request)
    order, _ = Order.objects.get_or_create(sessionId=sessionId)
    context = {"order": order}
    resp = render(request, 'order_summary.html', context)
    return resp


def stripe_checkout(request, amount):
    context = RequestContext(request, {'amount': amount})
    resp = render(request, 'stripe_checkout.html', context)
#     resp = render_to_response('stripe_checkout.html', context)
    return resp


def stripe_charge(request):
    sessionId = get_session_id(request)
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

    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

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


def order_complete(request):
    sessionId = get_session_id(request)
    order = Order.objects.get(sessionId=sessionId)
    context = {'order_number': order.paymentId}
    request.session.flush()
    resp = render(request, 'order_complete.html', context)
    return resp
