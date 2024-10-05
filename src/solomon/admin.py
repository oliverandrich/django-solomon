from django.contrib import admin

from solomon.models import SolomonToken


@admin.register(SolomonToken)
class SolomonTokenAdmin(admin.ModelAdmin):
    list_display = ("email", "ip_address", "redirect_url", "created_at", "expiry_date", "is_consumed", "is_disabled")
    search_fields = ("email",)

    @admin.display(boolean=True)
    def is_consumed(self, obj):
        return obj.consumed_at is not None

    @admin.display(boolean=True)
    def is_disabled(self, obj):
        return obj.disabled_at is not None

    def has_add_permission(self, request):  # noqa: ARG002
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ARG002
        return False
