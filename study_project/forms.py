from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User, Task

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']
    
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']
        
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'reminder_option', 'reminder_day', 'reminder_date', 'reminder_month', 'reminder_yearly_date']
