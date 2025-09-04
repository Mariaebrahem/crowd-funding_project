from django.db import models
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from projects.models import Project, Category, Comment, ProjectImage, Donation
from projects.filters import ProjectFilter
from django.utils import timezone
from django.utils.formats import date_format 
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
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


class ProjectListView(ListView):
    template_name = "projects/project_list.html"
    paginate_by = 50
    context_object_name = "list"

    def get_queryset(self):
        filter = ProjectFilter(
            self.request.GET, Project.objects.prefetch_related("images", "tags").all()
        )
        return filter.qs


class ProjectDetailView(DetailView):
    template_name = "projects/project_detail.html"
    context_object_name = "obj"

    def get_queryset(self):
        comments_prefetch = models.Prefetch(
            "comments",
            queryset=Comment.objects.select_related("parent")
            .prefetch_related("replies")
            .filter(parent__isnull=True).order_by("-created_at"),
        )
        return (
            Project.objects.all()
            .select_related("category", "user")
            .prefetch_related("images", "tags", "donations", comments_prefetch)
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        extra_ctx = {
            "donation_percentage": (
                self.object.total_donations // self.object.cap if self.object.cap else 0
            ),
            "days_to_go": (self.object.end_time - timezone.now().date()).days,
        }
        ctx.update(extra_ctx)
        return ctx


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_create.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.request.POST:
            ctx["formset"] = ProjectImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            ctx["formset"] = ProjectImageFormSet(instance=self.object)

        return ctx

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        if tags := form.cleaned_data.get("tags"):
            self.object.tags.set(tags)

        formset = ProjectImageFormSet(
            self.request.POST, self.request.FILES, instance=self.object
        )

        if formset.is_valid():
            formset.save()

        return redirect("projects")










class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = None
    login_url = "/users/login/"
    redirect_field_name = "redirect_to"

    def get_project(self):
        return get_object_or_404(Project, pk=self.kwargs["pk"])

    def form_valid(self, form):
        project = self.get_project()

        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.project = project
        obj.save()

        formatted_date = date_format(obj.created_at, format='F j, Y \\a\\t g:i A')  

        data = {
            "pk": obj.pk,
            "comment": obj.comment,
            "parent": obj.parent_id,
            "created_at": formatted_date,
            "user_name": self.request.user.get_full_name()
        }

        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    













@csrf_exempt
@require_POST
@login_required
def add_reply(request):
    parent_comment_id = request.POST.get("comment_id")
    comment_text = request.POST.get("comment")

    try:
        parent_comment = Comment.objects.get(id=parent_comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({"success": False, "error": "Comment not found"})

    reply = Comment.objects.create(
        user=request.user,
        project=parent_comment.project,
        comment=comment_text,
        parent=parent_comment
    )

    formatted_date = date_format(reply.created_at, format='F j, Y \\a\\t g:i A')

    data = {
        "success": True,
        "comment": reply.comment,
        "created_at": formatted_date,
        "user_full_name": request.user.get_full_name()
    }

    return JsonResponse(data)









from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Comment, ReportComment


@csrf_exempt
@login_required
def flag_comment(request):
    if request.method == "POST":
        comment_id = request.POST.get("comment_id")
        reason = request.POST.get("reason", "No reason provided")

       
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"success": False, "error": "Comment not found."})

        
        ReportComment.objects.create(
            comment=comment,
            reporter=request.user,
            reason=reason
        )

        return JsonResponse({
            "success": True,
            "message": "Comment has been flagged successfully."
        })

    return JsonResponse({"success": False, "error": "Invalid request method."})







    

from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Comment
from .forms import ReportCommentForm
from django.contrib.auth.mixins import LoginRequiredMixin

class ReportCommentCreateView(LoginRequiredMixin, CreateView):
    form_class = ReportCommentForm
    template_name = None
    login_url = "/users/login/"

    def form_valid(self, form):
        comment_id = self.request.POST.get("comment_id")
        comment = get_object_or_404(Comment, pk=comment_id)

        report = form.save(commit=False)
        report.comment = comment
        report.reporter = self.request.user
        report.save()

        return JsonResponse({
            "success": True,
            "comment_id": comment.id,
            "reason": report.reason
        })

    def form_invalid(self, form):
        return JsonResponse({"success": False, "error": "Invalid form data."}, status=400)







class ReportProjectCreateView(LoginRequiredMixin, CreateView):
    form_class = ReportProjectForm
    template_name = None
    login_url = "/users/login/"

    def form_valid(self, form):
        project_id = self.request.POST.get("project_id")
        project = get_object_or_404(Project, pk=project_id)

        report = form.save(commit=False)
        report.project = project
        report.reporter = self.request.user
        report.save()

        return JsonResponse({
            "success": True,
            "project_id": project.id,
            "reason": report.reason
        })

    def form_invalid(self, form):
        return JsonResponse({"success": False, "error": "Invalid form data."}, status=400)

    form_class = ReportProjectForm
    template_name = None  

    def form_valid(self, form):
        project_id = self.request.POST.get("project_id")
        reason = self.request.POST.get("reason")

        project = get_object_or_404(Project, pk=project_id)

        report = form.save(commit=False)
        report.project = project
        report.reporter_id = self.request.user.id
        report.save()

        data = {
            "success": True,
            "project_id": project.id,
            "reason": report.reason,
        }

        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({
            "success": False,
            "error": "Invalid form data."
        }, status=400)



class DonationCreateView(LoginRequiredMixin, CreateView):
    form_class = DonationForm
    template_name = "projects/donate.html"
    login_url = "/users/login/"

    def dispatch(self, request, *args, **kwargs):
        self.project_id = self.kwargs.get("pk")
        self.project = get_object_or_404(Project, pk=self.project_id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        donation = form.save(commit=False)
        donation.project = self.project
        donation.user = self.request.user
        donation.save()
        messages.success(
            self.request, "Donation successful. Thank you for your support!"
        )
        return redirect("project-detail", pk=self.project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_id"] = self.project_id
        context["project"] = self.project
        return context

