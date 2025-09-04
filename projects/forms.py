from django import forms
from .models import Project, Comment, Donation, ReportProject, ReportComment

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "details",
            "category",
            "tags",
            "cap",
            "start_time",
            "end_time",
        ]


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ["image"]


ProjectImageFormSet = inlineformset_factory(
    Project,
    ProjectImage,
    form=ProjectImageForm,
    can_order=True,
    min_num=1,
    max_num=5,
    can_delete=True,
)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment', 'parent']

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount']

class ReportProjectForm(forms.ModelForm):
    class Meta:
        model = ReportProject
        fields = ['reason']

class ReportCommentForm(forms.ModelForm):
    class Meta:
        model = ReportComment
        fields = ['reason']
