from django.views.generic import DetailView
from django.contrib.auth import get_user_model

class ProfileDetailView(DetailView):
    model = get_user_model()
    template_name = "account/profile_detail.html"
    context_object_name = "obj"
    
    def get_object(self):
        return self.request.user