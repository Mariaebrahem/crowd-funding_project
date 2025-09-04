from django.contrib import admin
from .models import Project, Category, Tag, ProjectImage, Rating, Comment, Donation
from .models import ReportProject, ReportComment

from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError


from django import forms


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = ["title", "details", "category", "user", "start_time", "cap"]
        for field_name in required_fields:
            self.fields[field_name].required = True


class ImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images_count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                images_count += 1
        if images_count < 3:
            raise ValidationError("You must upload at least 3 images for this project.")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class ImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3
    ordering = ["index"]
    formset = ImageInlineFormSet


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "category",
        "cap",
        "progress_percentage",
        "is_featured",
        "is_cancelled",
    )
    list_filter = ("category", "tags", "is_featured", "is_cancelled", "created_at")
    search_fields = ("title", "details", "user__username")
    autocomplete_fields = ("category",)
    filter_horizontal = ("tags",)
    inlines = [ImageInline, CommentInline]
    form = ProjectAdminForm
    readonly_fields = (
        "progress_percentage",
        "current_donation",
        
        
        "rating_count",
        "days_remaining",
        "can_cancel",
    )


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "index")
    list_filter = ("project",)
    search_fields = ("project__title",)
    autocomplete_fields = ["project"]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("project__title", "user__username")
    autocomplete_fields = ["project"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "user", "comment", "parent", "created_at")
    list_filter = ("created_at",)
    search_fields = ("comment", "user__username", "project__title")
    autocomplete_fields = ["project", "parent"]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "project", "amount", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "project__title")
    autocomplete_fields = ["project"]


@admin.register(ReportProject)
class ReportProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "project", "created_at")
    search_fields = ("reporter__username", "project__title", "reason")
    list_filter = ("created_at",)


@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "comment", "created_at")
    search_fields = ("reporter__username", "comment__comment", "reason")
    list_filter = ("created_at",)
