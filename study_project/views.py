from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User, Task
from .forms import RoomForm, UserForm, MyUserCreationForm, TaskForm
import openai, os
from dotenv import load_dotenv
from datetime import date, timedelta, datetime
from django.shortcuts import get_object_or_404
from django.conf import settings
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.parse import urlencode
load_dotenv()


api_key = os.getenv('OPENAI_KEY', None)


# Create your views here.
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password is incorrect')
        
    context = {'page': page}
    return render(request, 'study_project/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred while registering')
    
    return render(request, 'study_project/login_register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    
    topics = Topic.objects.all()[0:10]
    room_count = rooms.count()
    rooms_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:5]
    
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'rooms_messages': rooms_messages}
    
    return render(request, 'study_project/home.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'study_project/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'study_project/activity.html', {'room_messages': room_messages})

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
       
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'study_project/room.html', context)
    
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    rooms_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'rooms_messages': rooms_messages, 'topics': topics}
    
    return render(request, 'study_project/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        return redirect('home')
    
    context = {'form': form, 'topics': topics}
    return render(request, 'study_project/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance = room)
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse('You are not allowed to update this room')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('home')
    
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'study_project/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id = pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed to delete this room')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'study_project/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id = pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed to delete this message')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render(request, 'study_project/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance = user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
        
    return render(request, 'study_project/update-user.html', {'form': form})

@login_required(login_url='login')
def chatPage(request):
    chatbot_response = None
    if api_key is not None and request.method == 'POST':
        openai.api_key = api_key
        user_input = request.POST.get('user_input')
        prompt = user_input
        
        response = openai.Completion.create(
            engine = 'text-davinci-003',
            prompt = prompt,
            max_tokens = 256,
            # stop = ".",
            temperature = 0.5,
        )
        print(response)
        chatbot_response = response['choices'][0]['text']
    return render(request, 'study_project/chat.html', {})

@login_required(login_url='login')
def taskList(request):
    tasks = Task.objects.filter(user=request.user)
    task_count = tasks.count()
    return render(request, 'study_project/task_list.html', {'tasks': tasks, 'task_count': task_count})

@login_required(login_url='login')
def taskDetail(request, pk):
    task = get_object_or_404(Task, id=pk, user = request.user)
    return render(request, 'study_project/task_detail.html', {'task': task})
    

@login_required(login_url='login')
def createTask(request):
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    return render(request, 'study_project/task_create.html', {'form': form})


@login_required(login_url='login')
def updateTask(request, pk):
    task = get_object_or_404(Task, id=pk, user = request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance = task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance = task)
    
    return render(request, 'study_project/task_update.html', {'form': form, 'task': task})
    
@login_required(login_url='login')
def deleteTask(request, pk):
    task = get_object_or_404(Task, id=pk, user = request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    
    return render(request, 'study_project/task_delete.html', {'obj': task})

@login_required(login_url='login')
def week_view(request):
    current_date = date.today()

    start_date = current_date - timedelta(days=current_date.weekday())
    end_date = start_date + timedelta(days=6)

    week_days = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        week_days.append(day)

    date_count = len(week_days)
    
    return render(request, 'study_project/week.html', {
        'week_days': week_days,
        'date_count': date_count
    })

@login_required(login_url='login')
def day_tasks_view(request, day):
    date = datetime.strptime(day, '%Y-%m-%d').date()

    tasks = Task.objects.filter(
        Q(reminder_option='daily') |
        Q(reminder_option='weekly', reminder_day=date.weekday()) |
        Q(reminder_option='monthly', reminder_date=date.day) |
        Q(reminder_option='yearly', reminder_month=date.month, reminder_yearly_date=date.day)
    ).filter(user=request.user)

    return render(request, 'study_project/day_tasks.html', {'tasks': tasks, 'day': date})

@login_required(login_url='login')
def google_calendar_tasks_view(request):
    # Get the user's access token from your authentication system
    access_token = request.user.google_access_token

    # Define the base URL for Google Calendar
    base_url = 'https://calendar.google.com/calendar'

    # Construct the query parameters for the URL
    params = {
        'cid': 'ngoquangtung281203@gmail.com',  # Replace with the user's calendar ID
        'authuser': '0',  # Replace with the user's authenticated Google account index (0 for the first account)
        'ctz': 'UTC',  # Replace with the user's timezone
        'pli': '1',
        'mode': 'day',
        'dates': '20230628/20230628',  # Replace with the desired date range
        'tf': 'true',
        'gsessionid': '',
        'sf': 'true',
        'output': 'xml',
    }

    # Encode the query parameters and append them to the base URL
    url = f'{base_url}?{urlencode(params)}'

    # Redirect the user to the generated URL
    return redirect(url)

