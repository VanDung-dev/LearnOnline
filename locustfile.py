"""
Base user behavior class for login handling
"""

from locust import HttpUser, task, between, SequentialTaskSet
import urllib3

# Disable SSL insecure warnings because of self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseUserBehavior(SequentialTaskSet):
    """Base behavior class for login handling"""
    
    def on_start(self):
        self.login()

    def login(self):
        # 1. GET Login page for CSRF
        response = self.client.get("/accounts/login/")
        csrftoken = response.cookies.get('csrftoken')
        
        if csrftoken is None:
            print("No CSRF token found!")
            return

        # 2. POST Login
        # Sharing 1 user admin for load testing
        # In fact, it is recommended to use a separate user to avoid locking the user row too much
        self.client.post(
            "/accounts/login/",
            {
                "username": "admin", 
                "password": "password123",
                "csrfmiddlewaretoken": csrftoken
            },
            headers={"X-CSRFToken": csrftoken}
        )


class StudentLearningBehavior(BaseUserBehavior):
    """Student behavior is learning"""

    @task
    def dashboard(self):
        self.client.get("/accounts/profile/")

    @task
    def view_course(self):
        # Khóa học trả phí (Phải enroll rồi)
        self.client.get("/courses/complete-python-bootcamp/")

    @task
    def learning_process(self):
        self.client.get("/courses/complete-python-bootcamp/learning-process/")


class NewStudentEnrollmentBehavior(SequentialTaskSet):
    """Behavior of new students looking for and enrolling in courses"""

    @task
    def browse_homepage(self):
        self.client.get("/")
    
    @task
    def browse_courses(self):
        self.client.get("/courses/")
    
    @task
    def search_course(self):
        self.client.get("/courses/search/autocomplete/?term=react")

    @task
    def view_course_detail(self):
        # Free Course (View More)
        self.client.get("/courses/react-for-beginners/")
    
    @task
    def click_enroll(self):
        # Simulation click the registration button
        # (need to login first, here test download the login page)
        self.client.get("/courses/react-for-beginners/enroll/")


class InstructorBehavior(BaseUserBehavior):
    """Instructor behavior managing courses"""

    @task
    def instructor_dashboard(self):
        self.client.get("/instructor/courses/")

    @task
    def create_course_page(self):
        self.client.get("/instructor/courses/create/")


class WebsiteUser(HttpUser):
    """User total (Visitor + Student + Instructor)"""
    # 5 seconds break between actions
    wait_time = between(2, 5)

    tasks = {
        NewStudentEnrollmentBehavior: 6,
        StudentLearningBehavior: 3,
        InstructorBehavior: 1,
    }
    
    users = [
        ("instructor_john", "password123"),
        ("instructor_jane", "password123"),
        ("student_alice", "password123"),
        ("student_bob", "password123"),
    ]

    def on_start(self):
        self.client.verify = False
        self.login()

    def login(self):
        import random
        # Pick a random user to avoid locking on a single account
        username, password = random.choice(self.users)
        
        response = self.client.get("/accounts/login/")
        csrftoken = response.cookies.get('csrftoken')
        
        if csrftoken:
            self.client.post(
                "/accounts/login/",
                {
                    "username": username,
                    "password": password,
                    "csrfmiddlewaretoken": csrftoken
                },
                headers={"X-CSRFToken": csrftoken}
            )