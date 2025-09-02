from django import forms
from .models import Project, Comment, Donation, ReportProject, ReportComment

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'details', 'category', 'tags', 'total', 'start_time', 'end_time']

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
