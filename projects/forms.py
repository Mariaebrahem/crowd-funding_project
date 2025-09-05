from django import forms
from .models import (
    Project,
    Comment,
    Donation,
    ReportProject,
    ReportComment,
    ProjectImage,
)
from django.forms import inlineformset_factory


class StyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class ProjectForm(StyledForm):
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


class ProjectImageForm(StyledForm):
    class Meta:
        model = ProjectImage
        fields = ["image"]


ProjectImageFormSet = inlineformset_factory(
    Project,
    ProjectImage,
    form=ProjectImageForm,
    can_order=True,
    min_num=1,
    extra=0,
    max_num=5,
    can_delete=True,
)


class CommentForm(StyledForm):
    class Meta:
        model = Comment
        fields = ["comment", "parent"]


class DonationForm(StyledForm):
    class Meta:
        model = Donation
        fields = ["amount"]

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.project.total_donations >= self.project.cap:
            raise forms.ValidationError("This project has already reached its funding goal.")
        
        if self.project.end_time and self.project.end_time < forms.fields.datetime.date.today():
            raise forms.ValidationError("This project has already ended.")

        amount = self.cleaned_data.get("amount", None)
        
        if amount and amount > (self.project.cap - self.project.total_donations):
            raise forms.ValidationError(
                f"The maximum amount you can donate is {self.project.cap - self.project.total_donations}."
            )
        
        return super().clean()


class ReportProjectForm(StyledForm):
    class Meta:
        model = ReportProject
        fields = ["reason"]


class ReportCommentForm(StyledForm):
    class Meta:
        model = ReportComment
        fields = ["reason"]
