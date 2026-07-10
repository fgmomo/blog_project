from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm


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

            form.save()

            return redirect("login")

    else:

        form = SignUpForm()

    return render(
        request,
        "accounts/signup.html",
        {
            "form": form
        }
    )


def logout_view(request):

    logout(request)

    return redirect("home")