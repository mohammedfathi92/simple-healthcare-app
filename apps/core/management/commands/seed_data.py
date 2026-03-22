import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.appointments.models import (
    MIN_GAP_BETWEEN_APPOINTMENTS,
    Appointment,
    AppointmentStatus,
)
from apps.patients.models import Patient

User = get_user_model()

SEED_MARKER = "seed_data"
NUM_PATIENTS = 5
NUM_APPOINTMENTS = 10


class Command(BaseCommand):
    help = "Seed a default provider, five patients, and ten appointments."

    def handle(self, *args, **options):
        fake = Faker()
        fake.seed_instance(random.randint(0, 999_999))

        user, created = User.objects.get_or_create(
            username="provider",
            defaults={
                "email": "provider@test.com",
                "is_active": True,
            },
        )
        user.email = "provider@test.com"
        user.is_active = True
        user.set_password("p@ssW0rd")
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"{'Created' if created else 'Updated'} provider user "
                f"(username=provider, password set)."
            )
        )

        Patient.objects.filter(provider=user, notes=SEED_MARKER).delete()
        Appointment.objects.filter(provider=user, notes=SEED_MARKER).delete()

        now = timezone.now()
        future_start = now + timedelta(days=1)

        patients = []
        for _ in range(NUM_PATIENTS):
            phone = fake.phone_number()[:32]
            # Generate US-format phone number: 10 digits, numbers only
            phone = fake.numerify(text="##########")
            patient = Patient.objects.create(
                provider=user,
                name=fake.name()[:255],
                phone=phone,
                email=email,
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=92),
                medical_history=fake.text(max_nb_chars=400).strip(),
                allergies=(
                    "NKDA"
                    if random.random() < 0.35
                    else fake.sentence(nb_words=6).rstrip(".")
                ),
                notes=SEED_MARKER,
            )
            patients.append(patient)

        fake.unique.clear()

        self.stdout.write(self.style.SUCCESS(f"Created {len(patients)} patients (Faker)."))

        # Sequential slots: no overlap and at least MIN_GAP_BETWEEN_APPOINTMENTS between visits.
        slot_start = future_start.replace(second=0, microsecond=0)
        status_choices = [s for s in AppointmentStatus.values]
        duration_choices = (15, 20, 30, 45, 60)

        for i in range(NUM_APPOINTMENTS):
            duration = random.choice(duration_choices)
            Appointment.objects.create(
                provider=user,
                patient=patients[i % len(patients)],
                scheduled_at=slot_start,
                duration=duration,
                status=random.choice(status_choices),
                reason=fake.sentence(nb_words=8).rstrip("."),
                notes=SEED_MARKER,
            )
            slot_start += timedelta(minutes=duration) + MIN_GAP_BETWEEN_APPOINTMENTS

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {NUM_APPOINTMENTS} appointments (sequential slots with 15+ min gaps)."
            )
        )
        self.stdout.write(self.style.NOTICE("Done."))
