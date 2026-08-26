from django.core.management.base import BaseCommand
from academy.models import Track, Subject, Topic, Question, Tutor


TRACKS = [
    {"name": "WAEC / NECO", "slug": "waec-neco", "short_name": "WAEC", "color_hex": "#1F5C3F", "order": 1},
    {"name": "JAMB", "slug": "jamb", "short_name": "JAMB", "color_hex": "#7A1F2B", "order": 2},
    {"name": "Cambridge IGCSE", "slug": "cambridge-igcse", "short_name": "IGCSE", "color_hex": "#1D4E89", "order": 3},
    {"name": "Cambridge A-Levels", "slug": "cambridge-a-levels", "short_name": "A-Level", "color_hex": "#4B2E83", "order": 4},
    {"name": "IJMB", "slug": "ijmb", "short_name": "IJMB", "color_hex": "#8A5A19", "order": 5},
]

FULL_SUBJECTS = ["English Language", "Mathematics", "Physics", "Chemistry", "Biology"]
ALEVEL_SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Biology"]

SAMPLE_QUESTIONS = {
    "Chemistry": [
        {
            "topic": "Atomic Structure",
            "text": "What is the atomic number of an element equal to?",
            "options": {
                "a": "Number of neutrons",
                "b": "Number of protons",
                "c": "Number of protons plus neutrons",
                "d": "Number of electrons in the outer shell",
            },
            "correct": "b",
            "explanation": "The atomic number is defined as the number of protons in the nucleus of an atom.",
        },
        {
            "topic": "Periodic Table",
            "text": "Elements in the same group of the periodic table have the same number of:",
            "options": {"a": "Neutrons", "b": "Protons", "c": "Valence electrons", "d": "Isotopes"},
            "correct": "c",
            "explanation": "Elements in a group share the same number of electrons in their outermost shell, giving similar chemical properties.",
        },
        {
            "topic": "Chemical Bonding",
            "text": "Which type of bond involves the sharing of electron pairs between atoms?",
            "options": {"a": "Ionic bond", "b": "Covalent bond", "c": "Metallic bond", "d": "Hydrogen bond"},
            "correct": "b",
            "explanation": "A covalent bond forms when two atoms share one or more pairs of electrons.",
        },
    ],
    "Mathematics": [
        {
            "topic": "Algebra",
            "text": "Solve for x: 2x + 6 = 14",
            "options": {"a": "2", "b": "4", "c": "6", "d": "8"},
            "correct": "b",
            "explanation": "2x = 14 - 6 = 8, so x = 4.",
        },
        {
            "topic": "Geometry",
            "text": "What is the sum of interior angles of a triangle?",
            "options": {"a": "90°", "b": "180°", "c": "270°", "d": "360°"},
            "correct": "b",
            "explanation": "The interior angles of any triangle always sum to 180 degrees.",
        },
    ],
    "Physics": [
        {
            "topic": "Mechanics",
            "text": "What is the SI unit of force?",
            "options": {"a": "Joule", "b": "Watt", "c": "Newton", "d": "Pascal"},
            "correct": "c",
            "explanation": "Force is measured in Newtons (N), named after Sir Isaac Newton.",
        },
        {
            "topic": "Electricity",
            "text": "Ohm's law states that voltage equals current multiplied by:",
            "options": {"a": "Power", "b": "Resistance", "c": "Time", "d": "Charge"},
            "correct": "b",
            "explanation": "Ohm's Law: V = I × R, where R is resistance.",
        },
    ],
    "Biology": [
        {
            "topic": "Cell Biology",
            "text": "Which organelle is known as the powerhouse of the cell?",
            "options": {"a": "Nucleus", "b": "Ribosome", "c": "Mitochondrion", "d": "Golgi apparatus"},
            "correct": "c",
            "explanation": "Mitochondria produce ATP, the cell's main energy currency, through respiration.",
        },
        {
            "topic": "Genetics",
            "text": "DNA is found mainly in which part of a cell?",
            "options": {"a": "Cytoplasm", "b": "Nucleus", "c": "Cell wall", "d": "Vacuole"},
            "correct": "b",
            "explanation": "The nucleus houses the cell's chromosomal DNA.",
        },
    ],
    "English Language": [
        {
            "topic": "Comprehension",
            "text": "Choose the word nearest in meaning to 'abundant'.",
            "options": {"a": "Scarce", "b": "Plentiful", "c": "Fragile", "d": "Ancient"},
            "correct": "b",
            "explanation": "'Abundant' means existing in large quantities — synonymous with 'plentiful'.",
        },
        {
            "topic": "Grammar",
            "text": "Identify the correctly punctuated sentence.",
            "options": {
                "a": "Its a beautiful day.",
                "b": "It's a beautiful day.",
                "c": "Its' a beautiful day.",
                "d": "It's a beautiful, day.",
            },
            "correct": "b",
            "explanation": "\"It's\" is the contraction of \"it is\"; \"its\" (no apostrophe) is possessive.",
        },
    ],
}


class Command(BaseCommand):
    help = "Seed the database with iClass Online Academy tracks, subjects, sample questions and a demo tutor."

    def handle(self, *args, **options):
        tracks_by_slug = {}
        for t in TRACKS:
            track, _ = Track.objects.update_or_create(slug=t["slug"], defaults=t)
            tracks_by_slug[t["slug"]] = track
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(tracks_by_slug)} tracks"))

        subjects_by_name = {}
        for name in FULL_SUBJECTS:
            subject, _ = Subject.objects.get_or_create(name=name, defaults={"slug": name.lower().replace(" ", "-")})
            subjects_by_name[name] = subject

        for slug, track in tracks_by_slug.items():
            names = ALEVEL_SUBJECTS if slug == "cambridge-a-levels" else FULL_SUBJECTS
            for name in names:
                subjects_by_name[name].tracks.add(track)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(subjects_by_name)} subjects and linked them to tracks"))

        question_count = 0
        for subject_name, questions in SAMPLE_QUESTIONS.items():
            subject = subjects_by_name[subject_name]
            for track in subject.tracks.all():
                for q in questions:
                    topic, _ = Topic.objects.get_or_create(subject=subject, name=q["topic"])
                    _, created = Question.objects.get_or_create(
                        subject=subject, track=track, topic=topic, text=q["text"],
                        defaults={
                            "option_a": q["options"]["a"], "option_b": q["options"]["b"],
                            "option_c": q["options"]["c"], "option_d": q["options"]["d"],
                            "correct_option": q["correct"], "explanation": q["explanation"],
                        },
                    )
                    if created:
                        question_count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {question_count} sample questions across tracks"))

        tutor, _ = Tutor.objects.get_or_create(
            name="Mrs. Adaeze Okonkwo",
            defaults={"bio": "Chemistry & Biology tutor with 10+ years prepping WAEC and JAMB candidates."},
        )
        tutor.subjects.add(subjects_by_name["Chemistry"], subjects_by_name["Biology"])

        tutor2, _ = Tutor.objects.get_or_create(
            name="Mr. Tunde Bakare",
            defaults={"bio": "Mathematics & Physics tutor specialising in JAMB and A-Level exam technique."},
        )
        tutor2.subjects.add(subjects_by_name["Mathematics"], subjects_by_name["Physics"])

        self.stdout.write(self.style.SUCCESS("Seed complete. Run the server and log into /admin/ to add more content."))
