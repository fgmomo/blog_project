from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Emission

EMISSIONS_PER_PAGE = 9


def index(request):
    emissions = Emission.objects.all()

    paginator = Paginator(emissions, EMISSIONS_PER_PAGE)
    emissions_page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "emissions/index.html",
        {
            "emissions": emissions_page,
            "paginator": paginator,
        }
    )


def detail(request, slug):
    emission = get_object_or_404(Emission, slug=slug)

    return render(
        request,
        "emissions/detail.html",
        {"emission": emission}
    )
