from django.contrib import admin

from .models import Advertisement, Partner, TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "order")
    list_editable = ("order",)
    search_fields = ("name", "role")


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "website_url", "order")
    list_editable = ("order",)
    search_fields = ("name",)


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("title", "placement", "start_date", "end_date", "is_active", "clicks_count")
    list_filter = ("placement", "is_active")
    search_fields = ("title",)
