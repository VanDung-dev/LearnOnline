from django.contrib import admin
from .models import Category, Course, Section, Lesson, Enrollment, Progress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    prepopulated_fields = {'name': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'instructor', 'price', 'created_at', 'is_active']
    list_filter = ['category', 'instructor', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'lesson_type', 'order', 'is_published']
    list_filter = ['section__course', 'lesson_type', 'is_published']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'is_completed']
    list_filter = ['course', 'is_completed']


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed']
