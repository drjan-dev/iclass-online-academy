from django.urls import path
from . import views

app_name = "academy"

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),

    path("resources/", views.track_select, name="track_select"),
    path("resources/<slug:track_slug>/", views.subject_list, name="subject_list"),
    path("resources/<slug:track_slug>/<slug:subject_slug>/", views.subject_detail, name="subject_detail"),
    path("resources/<slug:track_slug>/<slug:subject_slug>/<str:resource_type>/", views.resource_list, name="resource_list"),
    path("resources/<slug:track_slug>/<slug:subject_slug>/book-tutor/", views.book_tutor, name="book_tutor"),

    path("tests/", views.test_track_select, name="test_track_select"),
    path("tests/<slug:track_slug>/", views.test_subject_select, name="test_subject_select"),
    path("tests/<slug:track_slug>/<slug:subject_slug>/topics/", views.test_topic_select, name="test_topic_select"),
    path("tests/<slug:track_slug>/ready/", views.test_ready, name="test_ready"),
    path("tests/<slug:track_slug>/start/", views.test_start, name="test_start"),
    path("tests/attempt/<int:attempt_id>/", views.test_take, name="test_take"),
    path("tests/attempt/<int:attempt_id>/exit/", views.test_exit, name="test_exit"),
    path("tests/attempt/<int:attempt_id>/results/", views.test_results, name="test_results"),
]
