'''
Created on Dec 9, 2017

@author: jivan
'''
from django.shortcuts import render


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
    resp = render(request, 'buy_book.html')
    return resp

def subscribe_mentoring(request):
    resp = render(request, 'subscribe_mentoring.html')
    return resp
