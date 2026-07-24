from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Subscriber


def subscribe(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()

        if email:
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={"is_active": True}
            )

            if not created and not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save(update_fields=["is_active"])

            messages.success(request, "Merci ! Vous êtes inscrit à la newsletter.")

    return redirect(request.META.get("HTTP_REFERER", "home"))


def unsubscribe(request, token):

    subscriber = get_object_or_404(Subscriber, token=token)
    subscriber.is_active = False
    subscriber.save(update_fields=["is_active"])

    return render(request, "newsletter/unsubscribe.html", {"subscriber": subscriber})
