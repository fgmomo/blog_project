from django import forms

from blog.models import Category, Post
from core.models import Advertisement, Partner, TeamMember
from emissions.models import Emission
from newsletter.models import Campaign


def _style_fields(form):
    for name, field in form.fields.items():
        widget = field.widget

        if isinstance(widget, forms.CheckboxInput):
            widget.attrs["class"] = "form-check-input"
        elif isinstance(widget, forms.Select):
            widget.attrs["class"] = "form-select"
        else:
            widget.attrs["class"] = "form-control"

    return form


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ["title", "content", "image", "category", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class EmissionForm(forms.ModelForm):

    class Meta:
        model = Emission
        fields = ["title", "description", "cover_image", "host", "video_url"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class TeamMemberForm(forms.ModelForm):

    class Meta:
        model = TeamMember
        fields = ["name", "role", "photo", "order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class PartnerForm(forms.ModelForm):

    class Meta:
        model = Partner
        fields = ["name", "logo", "website_url", "order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class AdvertisementForm(forms.ModelForm):

    class Meta:
        model = Advertisement
        fields = [
            "title", "image", "link_url", "placement",
            "start_date", "end_date", "is_active",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class CampaignForm(forms.ModelForm):

    class Meta:
        model = Campaign
        fields = ["subject", "body"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)
