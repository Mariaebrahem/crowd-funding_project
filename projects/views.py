from django.db import models
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.formats import date_format
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from projects.filters import ProjectFilter
from projects.models import Rating
from projects.models import (
    Project,
    Category,
    Comment,
    ProjectImage,
    Donation,
    ReportComment,
)
from projects.forms import (
    ProjectForm,
    CommentForm,
    DonationForm,
    ReportProjectForm,
    ReportCommentForm,
    ProjectImageFormSet,
)


class HomePageView(TemplateView):
    template_name = "profile/home.html"

    def get_homepage_data(self):
        images_prefetch = models.Prefetch(
            "images", queryset=ProjectImage.objects.order_by("id")
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
        categories = Category.objects.all().annotate(
            projects_count=models.Count("projects")
        )

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
            .filter(parent__isnull=True)
            .order_by("-created_at"),
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
            "user_rating": Rating.objects.filter(
                user=self.request.user, project=self.object
            ).first(),
        }
        ctx.update(extra_ctx)
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_create.html"

    def get_success_url(self):
        return reverse("project-detail", kwargs={"pk": self.object.pk})

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

        print(self.object)

        if tags := form.cleaned_data.get("tags"):
            self.object.tags.set(tags)

        formset = ProjectImageFormSet(
            self.request.POST, self.request.FILES, instance=self.object
        )
        print(self.request.FILES)
        print(formset.is_valid())
        print(formset.errors)
        if formset.is_valid():
            print(formset.is_valid())
            formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


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

        formatted_date = obj.created_at.strftime("%b. %d, %Y, %I:%M %p")
        formatted_date = formatted_date.replace("AM", "a.m.").replace("PM", "p.m.")

        data = {
            "pk": obj.pk,
            "comment": obj.comment,
            "parent": obj.parent_id,
            "created_at": formatted_date,
            "user_name": self.request.user.get_full_name(),
        }

        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


class CommentReplyCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = None
    login_url = "/users/login/"
    redirect_field_name = "redirect_to"

    def get_parent_comment(self):
        return get_object_or_404(
            Comment.objects.filter(project__pk=self.kwargs["pk"]),
            pk=self.kwargs["comment_pk"],
        )

    def form_valid(self, form):
        parent = self.get_parent_comment()

        obj = form.save(commit=False)
        obj.project_id = self.kwargs["pk"]
        obj.user = self.request.user
        obj.parent = parent
        obj.save()

        formatted_date = obj.created_at.strftime("%b. %d, %Y, %I:%M %p")
        formatted_date = formatted_date.replace("AM", "a.m.").replace("PM", "p.m.")

        data = {
            "pk": obj.pk,
            "comment": obj.comment,
            "parent": obj.parent_id,
            "created_at": formatted_date,
            "user_name": self.request.user.get_full_name(),
        }

        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


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

        return JsonResponse(
            {"success": True, "comment_id": comment.id, "reason": report.reason}
        )

    def form_invalid(self, form):
        return JsonResponse(
            {"success": False, "error": "Invalid form data."}, status=400
        )


class ReportProjectCreateView(LoginRequiredMixin, CreateView):
    form_class = ReportProjectForm
    template_name = None

    def form_valid(self, form):
        project = get_object_or_404(Project, **{"pk": self.kwargs["pk"]})

        report = form.save(commit=False)
        report.project = project
        report.reporter = self.request.user
        report.save()

        return JsonResponse(
            {"success": True, "project_id": project.id, "reason": report.reason}
        )

    def form_invalid(self, form):
        return JsonResponse(
            {"success": False, "error": "Invalid form data."}, status=400
        )


class RatingCreateView(LoginRequiredMixin, CreateView):
    pass

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class DonationCreateView(LoginRequiredMixin, CreateView):
    form_class = DonationForm
    template_name = "projects/donate.html"
    login_url = "/users/login/"

    def dispatch(self, request, *args, **kwargs):
        self.project_id = self.kwargs.get("pk")
        self.project = get_object_or_404(
            Project.objects.annotate(donations_count=models.Count("donations")).all(),
            pk=self.project_id,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"project": self.project})
        return kwargs

    def form_valid(self, form):
        donation = form.save(commit=False)
        donation.project = self.project
        donation.user = self.request.user
        donation.save()

        self.project.total_donations += donation.amount
        self.project.save()

        return JsonResponse(
            {
                "success": True,
                "total_donations": self.project.total_donations,
                "total_donations_count": self.project.donations_count + 1,
                "amount": donation.amount,
            }
        )

    def form_invalid(self, form):
        return JsonResponse({"success": False, "error": form.errors}, status=400)


class CategoryDetailView(DetailView):
    model = Category
    template_name = "projects/category_detail.html"
    context_object_name = "obj"

    def get_queryset(self):
        return Category.objects.all().annotate(projects_count=models.Count("projects"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = (
            Project.objects.filter(category=self.object)
            .prefetch_related("images", "tags")
            .all()
        )
        return context


class ProjectRatingView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ["total_rating"]
    template_name = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        rating = int(request.POST.get("rating", 0))

        if 1 <= rating <= 5:
            r, c = Rating.objects.update_or_create(
                user=self.request.user, project=self.object, defaults={"rating": rating}
            )
            self.object.total_rating = Rating.objects.filter(
                project=self.object
            ).aggregate(models.Avg("rating"))["rating__avg"]
            self.object.save()

            return JsonResponse(
                {
                    "success": True,
                    "new_total_rating": self.object.total_rating,
                    "rating": float(r.rating),
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Rating must be between 1 and 5."},
                status=400,
            )
