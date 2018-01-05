'''
Created on Dec 9, 2017

@author: jivan
'''
import json
import logging

from django.http.response import HttpResponse
from django.shortcuts import render, render_to_response

from meditate.models import SaleItem, Order, OrderItem
from django.core.handlers.exception import response_for_exception


logger = logging.getLogger(__name__)


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


def add_order_item(request, saleItemName):
    try:
        sessionId = request.session.session_key
        saleItem = SaleItem.objects.get(name=saleItemName)
        order, _ = Order.objects.get_or_create(sessionId=sessionId)
        item, _ = OrderItem.objects.get_or_create(order=order, saleItem=saleItem)
        item.count = item.count + 1
        item.save()
        resp = HttpResponse(status=200)
    except Exception as ex:
        logger.error('Problem adding item to order: {0}'.format(ex))
        resp = HttpResponse(status=500)
 
    return resp


def remove_order_item(request, saleItemName):
    try:
        sessionId = request.session.session_key
        saleItem = SaleItem.objects.get(name=saleItemName)
        order, _ = Order.objects.get_or_create(sessionId=sessionId)
        item, _ = OrderItem.objects.get_or_create(order=order, saleItem=saleItem)
        item.count = item.count - 1 if item.count > 0 else 0
        item.save()
        resp = HttpResponse(status=200)
    except Exception as ex:
        logger.error('Problem adding item to order: {0}'.format(ex))
        resp = HttpResponse(status=500)
 
    return resp


def get_order_count(request, saleItemName=None):
    try:
        sessionId = request.session.session_key
        order, _ = Order.objects.get_or_create(sessionId=sessionId)
        orderCount = 0

        # Count total of all items in order  
        if saleItemName is None:
            for item in order.orderitem_set.all():
                orderCount += item.count
        # Just count the named item
        else:
            try:
                orderCount = OrderItem.objects.get(
                    order__sessionId=sessionId, saleItem__name=saleItemName).count
            except:
                pass
        
        jsonText = json.dumps({'count': orderCount})
        resp = HttpResponse(jsonText, content_type="application/json")
    except Exception as ex:
        logger.error('get_order_count() problem: {0}'.format(ex))
        resp = HttpResponse(status=500)

    return resp


def log_javascript(request, msg):
    logger.error(msg)


def order_summary(request):
    sessionId = request.session.session_key
    order = Order.objects.get(sessionId=sessionId)
    context = {'request': request, "order": order}
    resp = render_to_response('order_summary.html', context)
    return resp
