import os
import sys
import django
from django.utils import timezone

# Setup path to import apps
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from apps.courses.models import Category, Course, Section, Subsection, Lesson, Quiz, Question, Answer, Enrollment
from apps.accounts.models import Profile

def seed():
    print("=" * 50)
    print("Seeding Complete Demo Course...")
    print("=" * 50)
    
    # 1. Get or create Instructor and Student
    instructor_user, _ = User.objects.get_or_create(
        username='instructor_john',
        defaults={'email': 'john@example.com', 'is_staff': True}
    )
    instructor_user.set_password('password123')
    instructor_user.save()
    
    # Update profile role
    instructor_user.profile.role = Profile.INSTRUCTOR
    instructor_user.profile.save()
    
    student_user, _ = User.objects.get_or_create(
        username='student_alice',
        defaults={'email': 'alice@example.com'}
    )
    student_user.set_password('password123')
    student_user.save()
    student_user.profile.role = Profile.STUDENT
    student_user.profile.save()
    
    # 2. Get or create Category
    category, _ = Category.objects.get_or_create(
        name="Blockchain Technology",
        defaults={"description": "Learn about distributed ledgers and enterprise blockchains."}
    )
    
    # 3. Create Course
    course, created = Course.objects.get_or_create(
        title="Introduction to HieraChain Ledger",
        defaults={
            "slug": "intro-hierachain-ledger",
            "short_description": "Learn how to use HieraChain in enterprise applications.",
            "description": "This course covers HieraChain ledger structure, P2P networking, and integration steps with Django.",
            "category": category,
            "instructor": instructor_user,
            "price": 0.00,
            "certificate_price": 0.00,
            "is_active": True
        }
    )
    if created:
        print(f"Created Course: {course.title}")
    else:
        print(f"Course already exists: {course.title}")
        
    # 4. Create Section
    section, created = Section.objects.get_or_create(
        course=course,
        title="Chapter 1: Ledger Basics",
        defaults={
            "description": "Basic concepts of HieraChain decentralized ledger.",
            "order": 1
        }
    )
    
    # 5. Create Subsection
    subsection, created = Subsection.objects.get_or_create(
        section=section,
        title="1.1 Overview & Architecture",
        defaults={
            "description": "High-level understanding of Main-Chain and Sub-Chains.",
            "order": 1
        }
    )
    
    # 6. Create Lesson (Text)
    lesson_text, created = Lesson.objects.get_or_create(
        subsection=subsection,
        title="What is HieraChain?",
        defaults={
            "slug": "what-is-hierachain",
            "lesson_type": "text",
            "content": "<h2>Overview</h2><p>HieraChain is a hierarchical blockchain ledger framework designed for enterprise application verification.</p><h3>Key features:</h3><ul><li>Main-Chain & Sub-Chain hierarchy</li><li>RESILIENCE via circuit breakers and retry mechanisms</li><li>Privacy collections and channel division</li></ul>",
            "order": 1,
            "is_published": True
        }
    )
    if created:
        print(f"  Created Lesson: {lesson_text.title}")
        
    # 7. Create Lesson (Quiz)
    lesson_quiz, created = Lesson.objects.get_or_create(
        subsection=subsection,
        title="HieraChain Knowledge Check",
        defaults={
            "slug": "hierachain-knowledge-check",
            "lesson_type": "quiz",
            "content": "Take this quiz to test your understanding of HieraChain.",
            "order": 2,
            "is_published": True,
            "max_check": 3
        }
    )
    if created:
        print(f"  Created Quiz Lesson: {lesson_quiz.title}")
        
    # 8. Create Quiz questions and answers
    quiz, created = Quiz.objects.get_or_create(
        lesson=lesson_quiz,
        defaults={
            "title": "HieraChain Basics Quiz",
            "description": "Test your core knowledge."
        }
    )
    
    # Question 1
    q1, created = Question.objects.get_or_create(
        quiz=quiz,
        text="Which version of HieraChain did we install?",
        defaults={
            "question_type": "single",
            "order": 1,
            "points": 5
        }
    )
    if created:
        Answer.objects.create(question=q1, text="0.0.1", is_correct=False, order=1)
        Answer.objects.create(question=q1, text="0.0.4", is_correct=True, order=2)
        Answer.objects.create(question=q1, text="0.1.0", is_correct=False, order=3)
        print("    Added Q1 & Answers")
        
    # Question 2
    q2, created = Question.objects.get_or_create(
        quiz=quiz,
        text="Is HieraChain designed for cryptocurrency/tokens?",
        defaults={
            "question_type": "single",
            "order": 2,
            "points": 5
        }
    )
    if created:
        Answer.objects.create(question=q2, text="Yes", is_correct=False, order=1)
        Answer.objects.create(question=q2, text="No (It focuses on business data integrity)", is_correct=True, order=2)
        print("    Added Q2 & Answers")
        
    # 9. Enroll Student Alice
    enrollment, created = Enrollment.objects.get_or_create(
        user=student_user,
        course=course
    )
    if created:
        print(f"Enrolled student {student_user.username} in {course.title}")
        
    print("\n" + "=" * 50)
    print("Database seeding completed successfully!")
    print("=" * 50)

if __name__ == '__main__':
    seed()
