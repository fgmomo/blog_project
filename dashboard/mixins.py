from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_staff


class SearchableListMixin:
    """Ajoute pagination + recherche texte (?search=) sur un champ donné."""

    paginate_by = 12
    search_field = "name"

    def get_queryset(self):
        qs = super().get_queryset()

        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(**{f"{self.search_field}__icontains": search})

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        return context
