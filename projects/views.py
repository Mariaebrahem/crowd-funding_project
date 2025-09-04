from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils import timezone
from django.db import transaction
from django.db.models import Prefetch, Avg
from projects.models import Project, Category, Comment, ProjectImage, Rating
from projects.forms import (
    ProjectForm,
    CommentForm,
    DonationForm,
    ReportProjectForm,
    ReportCommentForm,
)


class HomePageView(TemplateView):
    template_name = "profile/home.html"

    def get_homepage_data(self):
        images_prefetch = Prefetch(
            "images",
            queryset=ProjectImage.objects.order_by("id"),
            to_attr="ordered_images",
        )

        top_rated_projects = Project.objects.prefetch_related(images_prefetch).order_by(
            "-total_rating"
        )[:5]
        latest_projects = Project.objects.prefetch_related(images_prefetch).order_by(
            "-created_at"
        )[:5]
        featured_projects = (
            Project.objects.prefetch_related(images_prefetch)
            .filter(is_featured=True)
            .order_by("-created_at")[:5]
        )
        categories = Category.objects.all()

        return {
            "top_rated_projects": top_rated_projects,
            "latest_projects": latest_projects,
            "featured_projects": featured_projects,
            "categories": categories,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_homepage_data())
        return context