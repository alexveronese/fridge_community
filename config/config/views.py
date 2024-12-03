from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from .forms import *


class UserCreateView(CreateView):
    form_class = CreateUserCustomer
    template_name = "user_create.html"
    success_url = reverse_lazy("login")

class OperatorCreateView(PermissionRequiredMixin, UserCreateView):
    permission_required = "is_staff"
    form_class = CreateUserOperator