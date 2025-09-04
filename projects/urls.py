from django.urls import path
from projects import views
from projects.views import ReportCommentCreateView, ReportProjectCreateView, DonationCreateView

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="projects"),
    path("create/", views.ProjectCreateView.as_view(), name="project-create"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="project-detail"),
    path("<int:pk>/comments/create/", views.CommentCreateView.as_view(), name="project-comment-create"),
    path("<int:pk>/comments/<int:comment_pk>/replies/create/", views.add_reply, name="project-comment-reply-create"),
    path("<int:pk>/comments/<int:comment_pk>/reports/create/", views.ReportCommentCreateView.as_view(), name="project-comment-reports-create"),
    path("<int:pk>/reports/create/", ReportProjectCreateView.as_view(), name="project-report-create"),
    path("<int:pk>/donations/create/", DonationCreateView.as_view(), name="project-donation-create"),
]
