from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def post_like(request):
    return HttpResponse("Like article")

def comment_like(request):
    return HttpResponse("Like commentaire")