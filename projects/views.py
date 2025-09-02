from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils import timezone
from django.db import transaction
from django.db.models import Prefetch, Avg
from projects.models import (
    Project,
    Category,
    Comment,
    Donation,
    ReportProject,
    ReportComment,
    ProjectImage,
    Rating,
)


from projects.forms import (
    ProjectForm,
    CommentForm,
    DonationForm,
    ReportProjectForm,
    ReportCommentForm,
)


class HomePageView(TemplateView):
    template_name = "projects/home.html"

    def get_homepage_data(self):
        images_prefetch = Prefetch(
            "images", queryset=ProjectImage.objects.order_by("id"), to_attr="ordered_images"
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

    def post(self, request, *args, **kwargs):
        # Handle Create Project
        if "create_project" in request.POST:
            form = ProjectForm(request.POST, request.FILES)
            if form.is_valid():
                project = form.save(commit=False)
                project.user = request.user
                project.save()

                tags = form.cleaned_data.get("tags")
                if tags:
                    project.tags.set(tags)

                images = request.FILES.getlist("images")
                for idx, img in enumerate(images):
                    ProjectImage.objects.create(project=project, file=img, index=idx)

                messages.success(request, "تم إنشاء المشروع بنجاح!")
                return redirect("home")

            else:
                messages.error(request, "هناك خطأ في إنشاء المشروع.")
                context = self.get_context_data()
                context["project_form"] = form
                return self.render_to_response(context)

        # Handle Add Comment
        elif "add_comment" in request.POST:
            form = CommentForm(request.POST)
            project_id = request.POST.get("project_id")
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.project_id = project_id
                comment.save()
                messages.success(request, "تم إضافة تعليقك.")
            else:
                messages.error(request, "تعليق غير صالح.")
            return HttpResponseRedirect(reverse("home") + f"#project-{project_id}")

        # Handle Donation
        elif "donate" in request.POST:
            form = DonationForm(request.POST)
            project_id = request.POST.get("project_id")
            if form.is_valid():
                donation = form.save(commit=False)
                donation.user = request.user
                donation.project_id = project_id
                donation.save()
                messages.success(request, "تم التبرع بنجاح، شكراً لك!")
            else:
                messages.error(request, "حدث خطأ أثناء التبرع.")
            return HttpResponseRedirect(reverse("home") + f"#project-{project_id}")

        # Handle Report Project
        elif "report_project" in request.POST:
            form = ReportProjectForm(request.POST)
            project_id = request.POST.get("project_id")
            if form.is_valid():
                report = form.save(commit=False)
                report.reporter = request.user
                report.project_id = project_id
                report.save()
                messages.success(request, "تم إرسال بلاغك عن المشروع.")
            else:
                messages.error(request, "خطأ في إرسال البلاغ.")
            return HttpResponseRedirect(reverse("home") + f"#project-{project_id}")

        # Handle Report Comment
        elif "report_comment" in request.POST:
            form = ReportCommentForm(request.POST)
            comment_id = request.POST.get("comment_id")
            if form.is_valid():
                report = form.save(commit=False)
                report.reporter = request.user
                comment = get_object_or_404(Comment, pk=comment_id)
                report.comment = comment
                report.save()
                messages.success(request, "تم إرسال بلاغك عن التعليق.")
            else:
                messages.error(request, "خطأ في إرسال البلاغ.")
            return HttpResponseRedirect(reverse("home") + f"#comment-{comment_id}")

        # Handle Add Rating
        elif "add_rating" in request.POST:
            rating_value = request.POST.get("rating")
            project_id = request.POST.get("project_id")
            if rating_value:
                try:
                    rating_value = float(rating_value)
                    with transaction.atomic():
                        project = Project.objects.select_for_update().get(pk=project_id)
                        rating, created = Rating.objects.update_or_create(
                            user=request.user,
                            project=project,
                            defaults={
                                "rating": rating_value,
                                "created_at": timezone.now(),
                            },
                        )
                        avg = (
                            Rating.objects.filter(project=project).aggregate(
                                avg=Avg("rating")
                            )["avg"]
                            or 0
                        )
                        project.total_rating = avg
                        project.save()
                    messages.success(request, "تم إضافة تقييمك.")
                except Exception as e:
                    messages.error(request, f"حدث خطأ أثناء إضافة التقييم: {str(e)}")
            else:
                messages.error(request, "التقييم غير صالح.")
            return HttpResponseRedirect(reverse("home") + f"#project-{project_id}")

        # Handle Cancel Project
        elif "cancel_project" in request.POST:
            project_id = request.POST.get("project_id")
            project = get_object_or_404(Project, pk=project_id)
            if project.user != request.user:
                return HttpResponseForbidden("ليس لديك صلاحية لإلغاء هذا المشروع.")
            if not project.can_cancel:
                messages.error(request, "لا يمكنك إلغاء هذا المشروع الآن.")
                return HttpResponseRedirect(reverse("home") + f"#project-{project_id}")

            project.is_cancelled = True
            project.save(update_fields=["is_cancelled"])
            messages.success(request, "تم إلغاء المشروع بنجاح.")
            return HttpResponseRedirect(reverse("home") + f"#project-{project_id}")

        else:
            messages.error(request, "عملية غير معروفة.")
            return redirect("home")
