from django.db import models
from django.utils import timezone
from django.db.models import Avg, Count
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"Category {self.name}"


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    details = models.TextField(blank=False, null=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="projects",
        blank=False,
        null=False,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="projects", blank=False, null=False
    )
    total_donations = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    cap = models.DecimalField(max_digits=10, decimal_places=2)
    tags = models.ManyToManyField(Tag, related_name="projects", blank=True)
    start_time = models.DateField(blank=False, null=False)
    end_time = models.DateField(null=True, blank=True)
    total_rating = models.FloatField(default=0.0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def show_url(self):
        return reverse("view_projects")

    @property
    def current_donation(self):
        return sum(donation.amount for donation in self.donations.all())

    @property
    def progress_percentage(self):
          if self.cap and self.cap > 0:
              return (self.total_donations / self.cap) * 100
          return 0

    @property
    def rating_count(self):
        reviews = self.ratings.aggregate(count=Count("id"))
        return reviews["count"] or 0

    @property
    def is_active(self):
        now = timezone.now().date()
        if self.start_time and self.end_time:
            return self.start_time <= now <= self.end_time and not self.is_cancelled
        return False

    @property
    def days_remaining(self):
        if self.end_time:
            remaining = (self.end_time - timezone.now().date()).days
            return remaining if remaining > 0 else 0
        return 0

    @property
    def can_cancel(self):
        return self.progress_percentage < 25 and self.is_active

    is_cancelled = models.BooleanField(default=False)


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="projects/")
    index = models.PositiveSmallIntegerField(default=0)  # Added for ordering

    def __str__(self):
        return str(self.image)


class Rating(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    rating = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} by {self.user.username} on {self.project.title}"


class Comment(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(null=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.parent:
            return f"Reply by {self.user.username} on comment {self.parent.id}"
        return f"Comment by {self.user.username} on {self.project.title}"


class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="donations"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} donated ${self.amount} to {self.project.title}"


class ReportProject(models.Model):
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reported_projects"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_reports"
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Project Report on '{self.project.title}' by {self.reporter.username}"




class ReportComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_reports")
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reported_comments")  # ✅ أضف السطر دا
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment Report by {self.reporter.username}"

    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="comment_reports"
    )
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reported_comments"
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment Report on comment #{self.comment.id} by {self.reporter.username}"


