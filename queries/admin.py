from django.contrib import admin

# Register your models here.
from .models import FacialExpressionQuery  # Import your model


# Register your models here.
@admin.register(FacialExpressionQuery)
class FacialExpressionQueryAdmin(admin.ModelAdmin):
    list_display = (
        "subject_name",
        "user",
        "detected_expression",
        "created_at",
        "filename",
    )
    list_filter = ("user", "detected_expression", "created_at")
    search_fields = (
        "subject_name",
        "notes",
        "user__username",
    )  # Allows searching by related user's username
    readonly_fields = (
        "created_at",
        "updated_at",
    )  # Fields that shouldn't be editable in admin
