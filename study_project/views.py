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
from google.auth.transport.requests import Request
# from google.oauth2.credentials import AccessTokenCredentials
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth import default
from google.auth.transport import requests
from google.auth.exceptions import RefreshError
from django.conf import settings
import json
import logging
load_dotenv()

logger = logging.getLogger(__name__)


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
def google_auth_callback(request):
    state = request.session.get('google_auth_state', None)

    flow = Flow.from_client_secrets_file(
        client_secrets_file=str(settings.BASE_DIR / 'secrets/client_secrets.json'),
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=request.build_absolute_uri('/google-auth-callback/')
    )

    flow.fetch_token(
        authorization_response=request.build_absolute_uri(),
        state=state
    )

    credentials = flow.credentials

    # Save the credentials in the database for the authenticated user
    user = request.user
    user.google_credentials = credentials.to_json()
    user.save()
    # print(user.google.credentials)
    logger.info(user.google.credentials)

    # Redirect the user to the desired page after authentication
    return redirect('home')  # Replace 'home' with the appropriate URL name

@login_required(login_url='login')
def google_auth(request):
    flow = Flow.from_client_secrets_file(
        client_secrets_file=str(settings.BASE_DIR / 'secrets/client_secrets.json'),
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=request.build_absolute_uri('/google-auth-callback/')
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    # Store the state in the session for later verification
    request.session['google_auth_state'] = state

    return redirect(authorization_url)

@login_required(login_url='login')
def sync_tasks_with_google_calendar(request):
    # Retrieve the tasks from the database
    tasks = Task.objects.filter(user=request.user)

    # Load the user's Google credentials
    google_credentials = Credentials.from_authorized_user_info(
        request.user.google_credentials,
        scopes=['https://www.googleapis.com/auth/calendar.events']
    )

    # Check if the credentials are expired and refresh if necessary
    if google_credentials.expired and google_credentials.refresh_token:
        google_credentials.refresh(Request())

    # Build the Google Calendar service
    service = build('calendar', 'v3', credentials=google_credentials)

    # Iterate over the tasks
    for task in tasks:
        # Extract task details
        title = task.title
        description = task.description
        reminder_option = task.reminder_option
        reminder_day = task.reminder_day
        reminder_date = task.reminder_date
        reminder_month = task.reminder_month
        reminder_yearly_date = task.reminder_yearly_date

        # Determine the reminder datetime based on the reminder_option
        reminder_datetime = None
        if reminder_option == 'daily':
            # Set the reminder to occur every day
            reminder_datetime = datetime.now()
        elif reminder_option == 'weekly':
            # Set the reminder to occur every week on the specified day
            reminder_datetime = datetime.now() + timedelta(days=reminder_day)
        elif reminder_option == 'monthly':
            # Set the reminder to occur every month on the specified date
            reminder_datetime = datetime.now().replace(day=reminder_date)
        elif reminder_option == 'yearly':
            # Set the reminder to occur every year on the specified month and date
            reminder_datetime = datetime.now().replace(month=reminder_month, day=reminder_yearly_date)

        # Create the event start and end datetime
        start_datetime = reminder_datetime
        end_datetime = start_datetime + timedelta(days=1)  # Assuming the event duration is 1 day

        # Create the event in Google Calendar
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
        }

        try:
            # Call the Google Calendar API to create the event
            service.events().insert(calendarId='primary', body=event).execute()
        except Exception as e:
            # Log the error or print the exception message for debugging
            print(f"An error occurred while creating the event: {str(e)}")

    # Redirect to a success page or return a response
    return HttpResponse("Tasks synchronized with Google Calendar successfully!")


@login_required(login_url='login')
def google_calendar_link(request):
    credentials_json = request.user.google_credentials

    if credentials_json is not None:
        try:
            credentials = Credentials.from_authorized_user_info(json.loads(credentials_json))
            credentials.refresh(Request())

            # email = credentials.id_token['email']
            email = request.user.email
            calendar_link = f"https://calendar.google.com/calendar/r?cid={email}"

            return redirect(calendar_link)
        except RefreshError:
            return redirect('google_auth')  # Replace with the correct URL name for the Google OAuth flow
    else:
        return redirect('google_auth')  # Replace with the correct URL name for the Google OAuth flow
