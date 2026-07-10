from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def add_comment(request):
    return HttpResponse("Ajouter un commentaire")