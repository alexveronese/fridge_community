from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm

class CreateUserCustomer(UserCreationForm):

    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name="Customers")
        g.user_set.add(user)
        return user

class CreateUserOperator(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name="Operators")
        g.user_set.add(user)
        return user