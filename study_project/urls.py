from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),

    path('update-user/', views.updateUser, name="update-user"),

    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),
    path('chat/', views.chatPage, name="chat"),
    
    # Task
    path('task_list/', views.taskList, name="task_list"),
    path('task/<int:pk>/', views.taskDetail, name="task"),
    path('task/create/', views.createTask, name="task_create"),
    path('task/update/<int:pk>/', views.updateTask, name="task_update"),
    path('task/delete/<int:pk>/', views.deleteTask, name="task_delete"),
    
    path('task_list/this_week', views.week_view, name="week_view"),
    path('day/<str:day>/', views.day_tasks_view, name='day_tasks'),
]