from django.contrib import admin
from .models import (
    Track, Subject, Student, Resource, Tutor, LessonBooking,
    Topic, Question, TestAttempt, Answer,
)


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "color_hex", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    filter_horizontal = ("tracks",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "primary_track", "streak_count")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "track", "resource_type", "is_free")
    list_filter = ("resource_type", "track", "subject")


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    filter_horizontal = ("subjects",)


@admin.register(LessonBooking)
class LessonBookingAdmin(admin.ModelAdmin):
    list_display = ("student", "tutor", "subject", "scheduled_for", "status")
    list_filter = ("status",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("subject", "name")
    list_filter = ("subject",)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_short", "subject", "topic", "track", "level", "correct_option")
    list_filter = ("subject", "track", "level")
    search_fields = ("text",)

    def text_short(self, obj):
        return obj.text[:60]
    text_short.short_description = "Question"


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "mode", "subject", "track", "started_at", "submitted_at", "score", "total")
    list_filter = ("mode", "track")
    inlines = [AnswerInline]
