from locust import HttpUser, between, task

class MyUser(HttpUser):
    wait_time = between(1, 2)
    
    @task
    def view_task_list(self):
        self.client.get("/task_list")
        
    def create_task(self):
        task_data = {
            'title': 'Test Task',
            'description': 'Test Task Description',
        }
        self.client.post('/create-task/', json=task_data)
        
class MyUser(HttpUser):
    wait_time = between(1, 2) 

    @task
    def view_room(self):
        self.client.get('/room/1/')
        
    @task
    def update_room(self):
        room_data = {
            'name': 'Updated Room',
            'description': 'Updated Room Description',
        }
        self.client.post('/update-room/1/', json=room_data)
    
    @task
    def delete_room(self):
        self.client.post('/delete-room/1/')
        
class MyUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def chat_page(self):
        chat_data = {
            'user_input': 'Hello',
        }
        self.client.post('/chat-page/', json=chat_data)
        

class MyUser(HttpUser):
    wait_time = between(1, 2) 

    @task
    def google_auth_callback(self):
        self.client.get('/google-auth-callback/')