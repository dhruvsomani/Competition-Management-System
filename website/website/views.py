from django.http import HttpResponse
from django.shortcuts import render

def redirect(request):
    return HttpResponse('<meta http-equiv="refresh" content="0; url=/scores/">')