from locust import HttpLocust, TaskSet, task

""""""

class UserUrlActions(TaskSet):

    def on_start(self):  # start load testing
        self.login()

    def login(self):
        self.client.post("/user_login/",
                             {"username": "admin101",
                              "password": "bridgeit123"})
    @task(1)
    def index(self):
        self.client.get('/')

    @task(1)
    def admin(self):
        self.client.get("/admin/")

class ApplicationUser(HttpLocust):
    task_set = UserUrlActions
    min_wait = 0
    max_wait = 0