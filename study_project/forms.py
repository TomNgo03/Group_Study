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
        fields = ['title', 'description', 'reminder_option', 'reminder_day', 'reminder_date', 'reminder_month']

# class TaskForm(ModelForm):
#     class Meta:
#         model = Task
#         fields = '__all__'
#         exclude = ['created']

#     def clean(self):
#         cleaned_data = super().clean()
#         reminder_option = cleaned_data.get('reminder_option')

#         if reminder_option == 'weekly':
#             reminder_day = cleaned_data.get('reminder_day')
#             if reminder_day is None:
#                 self.add_error('reminder_day', 'Please select a day of the week.')

#         if reminder_option == 'monthly':
#             reminder_date = cleaned_data.get('reminder_date')
#             if reminder_date is None:
#                 self.add_error('reminder_date', 'Please enter a date of the month.')

#         if reminder_option == 'yearly':
#             reminder_month = cleaned_data.get('reminder_month')
#             reminder_date = cleaned_data.get('reminder_date')
#             if reminder_month is None:
#                 self.add_error('reminder_month', 'Please select a month.')
#             if reminder_date is None:
#                 self.add_error('reminder_date', 'Please enter a date.')

#         return cleaned_data