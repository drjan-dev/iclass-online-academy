from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Track(models.Model):
    """Exam body / track: WAEC/NECO, JAMB, Cambridge IGCSE, Cambridge A-Levels, IJMB."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    short_name = models.CharField(max_length=20, help_text="e.g. WAEC, JAMB, IGCSE")
    color_hex = models.CharField(max_length=7, default="#0B2545", help_text="Track accent color")
    crest = models.ImageField(upload_to="crests/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    tracks = models.ManyToManyField(Track, related_name="subjects")

    class Meta:
        unique_together = ("name",)
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    primary_track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True)
    streak_count = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Resource(models.Model):
    """A Lesson Slide, Lesson Video, Textbook, or Padlet item under a subject."""
    RESOURCE_TYPES = [
        ("slide", "Lesson Slides"),
        ("video", "Lesson Videos"),
        ("textbook", "Textbooks"),
        ("padlet", "Padlet"),
        ("past_question", "Past Questions"),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="resources")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="resources")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="resources/", blank=True, null=True)
    external_url = models.URLField(blank=True)
    is_free = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


class Tutor(models.Model):
    name = models.CharField(max_length=150)
    subjects = models.ManyToManyField(Subject, related_name="tutors")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="tutors/", blank=True, null=True)

    def __str__(self):
        return self.name


class LessonBooking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="bookings")
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name="bookings")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    scheduled_for = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.scheduled_for:%Y-%m-%d %H:%M}"


class Topic(models.Model):
    """A topic within a subject, used for topic-based tests."""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class Question(models.Model):
    LEVEL_CHOICES = [
        ("standard", "Standard"),
        ("teacher_competence", "Teacher Competence Test"),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="questions")
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="questions")
    level = models.CharField(max_length=30, choices=LEVEL_CHOICES, default="standard")
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")])
    explanation = models.TextField(blank=True, help_text="Shown on a wrong answer")

    def __str__(self):
        return self.text[:60]

    def options(self):
        return {"a": self.option_a, "b": self.option_b, "c": self.option_c, "d": self.option_d}


JAMB_COMBOS = {
    "medical": {
        "label": "Medical / Health Sciences",
        "subjects": ["English Language", "Physics", "Chemistry", "Biology"],
    },
    "science": {
        "label": "Science / Engineering",
        "subjects": ["English Language", "Physics", "Chemistry", "Mathematics"],
    },
}


class TestAttempt(models.Model):
    MODE_CHOICES = [
        ("subject", "Individual Subject Test"),
        ("topic", "Topic-Based Test"),
        ("jamb_combo", "Full JAMB Combo Test"),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attempts")
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="subject")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    combo_key = models.CharField(max_length=20, blank=True, help_text="medical / science, for JAMB combo tests")
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=0, help_text="0 = untimed")
    is_auto_submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.get_mode_display()} - {self.started_at:%Y-%m-%d}"

    @property
    def score(self):
        return self.answers.filter(is_correct=True).count()

    @property
    def total(self):
        return self.answers.count()


class Answer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("attempt", "question")

    def save(self, *args, **kwargs):
        if self.selected_option:
            self.is_correct = self.selected_option == self.question.correct_option
        super().save(*args, **kwargs)
