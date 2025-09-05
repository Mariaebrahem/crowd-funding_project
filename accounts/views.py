from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.forms import ProfileUpdateForm, ProfileDeleteForm
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = "account/profile_detail.html"
    context_object_name = "obj"

    def get_object(self):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUpdateForm
    template_name = "account/profile_update.html"
    success_url = reverse_lazy("profile")
    context_object_name = "obj"

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your profile has been updated successfully!")
        response = super().form_valid(form)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_delete_button"] = True
        return context


class ProfileDeleteView(LoginRequiredMixin, CreateView):
    form_class = ProfileDeleteForm
    template_name = None
    success_url = reverse_lazy("landing")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = self.request.user
        if form.is_valid():
            user.is_active = False
            user.save()

            logout(self.request)

            messages.success(
                self.request, "Your account has been deleted successfully!"
            )

        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Incorrect password.")
        return HttpResponseRedirect(reverse_lazy("profile_update"))
