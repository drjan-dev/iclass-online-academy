from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .models import (
    Track, Subject, Resource, Question, Topic,
    TestAttempt, Answer, Student, LessonBooking, Tutor, JAMB_COMBOS,
)


def home(request):
    tracks = Track.objects.all()
    student = None
    recent_attempts = []
    if request.user.is_authenticated:
        student, _ = Student.objects.get_or_create(user=request.user)
        recent_attempts = student.attempts.order_by("-started_at")[:5]
    return render(request, "academy/home.html", {
        "tracks": tracks,
        "student": student,
        "recent_attempts": recent_attempts,
    })


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Student.objects.get_or_create(user=user)
            login(request, user)
            return redirect("academy:track_select")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def track_select(request):
    """Onboarding / track picker, also used as the entry point to Resources."""
    next_step = request.GET.get("next", "resources")
    tracks = Track.objects.all()
    return render(request, "academy/track_select.html", {"tracks": tracks, "next_step": next_step})


def subject_list(request, track_slug):
    track = get_object_or_404(Track, slug=track_slug)
    next_step = request.GET.get("next", "resources")
    subjects = track.subjects.all()
    return render(request, "academy/subject_list.html", {
        "track": track, "subjects": subjects, "next_step": next_step,
    })


def subject_detail(request, track_slug, subject_slug):
    track = get_object_or_404(Track, slug=track_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)
    tutors = subject.tutors.all()
    return render(request, "academy/subject_detail.html", {
        "track": track, "subject": subject, "tutors": tutors,
    })


def resource_list(request, track_slug, subject_slug, resource_type):
    track = get_object_or_404(Track, slug=track_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)
    resources = Resource.objects.filter(track=track, subject=subject, resource_type=resource_type)
    label = dict(Resource.RESOURCE_TYPES).get(resource_type, resource_type)
    return render(request, "academy/resource_list.html", {
        "track": track, "subject": subject, "resources": resources,
        "resource_type": resource_type, "label": label,
    })


@login_required
def book_tutor(request, track_slug, subject_slug):
    track = get_object_or_404(Track, slug=track_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)
    tutors = subject.tutors.all()
    if request.method == "POST":
        student, _ = Student.objects.get_or_create(user=request.user)
        tutor = get_object_or_404(Tutor, id=request.POST.get("tutor_id"))
        LessonBooking.objects.create(
            student=student, tutor=tutor, subject=subject,
            scheduled_for=request.POST.get("scheduled_for") or timezone.now(),
        )
        return render(request, "academy/booking_confirmed.html", {"track": track, "subject": subject, "tutor": tutor})
    return render(request, "academy/book_tutor.html", {"track": track, "subject": subject, "tutors": tutors})


# ---------------------------------------------------------------------------
# Test engine: readiness screen -> timed/untimed test -> results + feedback
# ---------------------------------------------------------------------------

def test_track_select(request):
    tracks = Track.objects.all()
    return render(request, "academy/test_track_select.html", {"tracks": tracks})


def test_subject_select(request, track_slug):
    track = get_object_or_404(Track, slug=track_slug)
    subjects = track.subjects.all()
    show_combo = track.short_name.upper() == "JAMB"
    return render(request, "academy/test_subject_select.html", {
        "track": track, "subjects": subjects, "show_combo": show_combo, "combos": JAMB_COMBOS,
    })


def test_topic_select(request, track_slug, subject_slug):
    track = get_object_or_404(Track, slug=track_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)
    topics = subject.topics.all()
    return render(request, "academy/test_topic_select.html", {"track": track, "subject": subject, "topics": topics})


def test_ready(request, track_slug):
    """The 'Are you ready?' screen before any test starts."""
    track = get_object_or_404(Track, slug=track_slug)
    mode = request.GET.get("mode", "subject")
    subject_slug = request.GET.get("subject")
    topic_id = request.GET.get("topic")
    combo_key = request.GET.get("combo")

    subject = get_object_or_404(Subject, slug=subject_slug) if subject_slug else None
    topic = get_object_or_404(Topic, id=topic_id) if topic_id else None
    combo = JAMB_COMBOS.get(combo_key) if combo_key else None

    question_count = 0
    time_limit = 0
    if mode == "jamb_combo" and combo:
        question_count = 180
        time_limit = 120
    elif mode == "topic" and topic:
        question_count = topic.questions.count()
    elif subject:
        question_count = Question.objects.filter(subject=subject, track=track, level="standard").count()

    return render(request, "academy/test_ready.html", {
        "track": track, "mode": mode, "subject": subject, "topic": topic,
        "combo_key": combo_key, "combo": combo,
        "question_count": question_count, "time_limit": time_limit,
    })


@login_required
def test_start(request, track_slug):
    """Creates the TestAttempt and redirects into the live test screen."""
    track = get_object_or_404(Track, slug=track_slug)
    mode = request.GET.get("mode", "subject")
    subject_slug = request.GET.get("subject")
    topic_id = request.GET.get("topic")
    combo_key = request.GET.get("combo")
    student, _ = Student.objects.get_or_create(user=request.user)

    subject = get_object_or_404(Subject, slug=subject_slug) if subject_slug else None
    topic = get_object_or_404(Topic, id=topic_id) if topic_id else None

    time_limit = 120 if mode == "jamb_combo" else 0
    attempt = TestAttempt.objects.create(
        student=student, track=track, mode=mode, subject=subject, topic=topic,
        combo_key=combo_key or "", time_limit_minutes=time_limit,
    )

    if mode == "jamb_combo":
        combo = JAMB_COMBOS[combo_key]
        questions = Question.objects.filter(track=track, subject__name__in=combo["subjects"], level="standard")
    elif mode == "topic":
        questions = Question.objects.filter(topic=topic, level="standard")
    else:
        questions = Question.objects.filter(track=track, subject=subject, level="standard")

    for q in questions:
        Answer.objects.get_or_create(attempt=attempt, question=q)

    return redirect("academy:test_take", attempt_id=attempt.id)


@login_required
def test_take(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student__user=request.user)
    if request.method == "POST":
        for answer in attempt.answers.all():
            selected = request.POST.get(f"q{answer.question_id}")
            if selected:
                answer.selected_option = selected
                answer.save()
        attempt.submitted_at = timezone.now()
        attempt.is_auto_submitted = request.POST.get("auto_submit") == "1"
        attempt.save()
        return redirect("academy:test_results", attempt_id=attempt.id)

    answers = attempt.answers.select_related("question").order_by("id")
    deadline_iso = ""
    if attempt.time_limit_minutes:
        deadline = attempt.started_at + timezone.timedelta(minutes=attempt.time_limit_minutes)
        deadline_iso = deadline.isoformat()
    return render(request, "academy/test_take.html", {
        "attempt": attempt, "answers": answers, "deadline_iso": deadline_iso,
    })


@login_required
def test_exit(request, attempt_id):
    """Confirmed exit without submitting — discards the in-progress attempt."""
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student__user=request.user)
    if request.method == "POST":
        attempt.delete()
        return redirect("academy:test_track_select")
    return render(request, "academy/test_exit_confirm.html", {"attempt": attempt})


@login_required
def test_results(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student__user=request.user)
    answers = attempt.answers.select_related("question", "question__subject").order_by("id")

    grouped = None
    if attempt.mode == "jamb_combo":
        by_subject = {}
        for a in answers:
            by_subject.setdefault(a.question.subject.name, []).append(a)
        grouped = [
            {"subject": name, "correct": sum(1 for x in lst if x.is_correct), "total": len(lst)}
            for name, lst in by_subject.items()
        ]

    wrong_answers = [a for a in answers if not a.is_correct]
    for a in wrong_answers:
        opts = a.question.options()
        a.selected_text = opts.get(a.selected_option, "No answer given")
        a.correct_text = opts.get(a.question.correct_option, "")
    percent = round((attempt.score / attempt.total) * 100) if attempt.total else 0

    return render(request, "academy/test_results.html", {
        "attempt": attempt, "answers": answers, "grouped": grouped,
        "wrong_answers": wrong_answers, "percent": percent,
    })
