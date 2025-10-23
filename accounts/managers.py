from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    def students(self):
        return self.filter(profile__role='student')
    
    def instructors(self):
        return self.filter(profile__role='instructor')
    
    def admins(self):
        return self.filter(profile__role='admin')