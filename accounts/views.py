from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_ratelimit.decorators import ratelimit

from .forms import SignUpForm


def _send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    link = request.build_absolute_uri(
        f"/accounts/verifier/{uid}/{token}/"
    )

    message = render_to_string(
        "accounts/verification_email.html",
        {"user": user, "link": link},
    )

    send_mail(
        "Vérifiez votre compte OM News",
        message,
        None,
        [user.email],
    )


@ratelimit(key='ip', rate='10/m', block=True)
def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST["username"]

        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            return redirect("home")

        inactive_user = User.objects.filter(
            username=username,
            is_active=False
        ).first()

        if inactive_user:
            return render(
                request,
                "accounts/login.html",
                {
                    "error": "Votre compte n'est pas encore activé. Vérifiez votre email."
                }
            )

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Nom d'utilisateur ou mot de passe incorrect."
            }
        )

    return render(request, "accounts/login.html")


def signup_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        form = SignUpForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.is_active = False
            user.save()

            _send_verification_email(request, user)

            return render(request, "accounts/verification_sent.html")

    else:

        form = SignUpForm()

    return render(
        request,
        "accounts/signup.html",
        {
            "form": form
        }
    )


def verify_email(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])

        return render(
            request,
            "accounts/login.html",
            {
                "success": "Votre compte est activé, vous pouvez vous connecter."
            }
        )

    return render(request, "accounts/verification_invalid.html")


def logout_view(request):

    logout(request)

    return redirect("home")


def profile_edit(request):
    # La page profil vit désormais dans le tableau de bord.
    return redirect("dashboard:profile")
