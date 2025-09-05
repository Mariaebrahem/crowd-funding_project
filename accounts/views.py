from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms
from .forms import ProfileUpdateForm

class ProfileDetailView(LoginRequiredMixin,DetailView):
    model = get_user_model()
    template_name = "account/profile_detail.html"
    context_object_name = "obj"
    
    def get_object(self):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUpdateForm
    template_name = "account/profile_update.html"
    success_url = reverse_lazy('profile')
    context_object_name = "obj"

    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Your profile has been updated successfully!')
        response = super().form_valid(form)
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_delete_button'] = True
        return context


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = get_user_model()
    template_name = "account/profile_delete.html"
    success_url = reverse_lazy('home')
    context_object_name = "obj"
    
    def get_object(self):
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        messages.success(request, 'Your account has been deleted successfully!')
        logout(request)
        user.delete()
        return HttpResponseRedirect(self.success_url)

    def post(self, request, *args, **kwargs):
        if 'confirm_delete' in request.POST:
            return self.delete(request, *args, **kwargs)
        else:
            messages.info(request, 'Account deletion cancelled.')
            return redirect('profile_update')