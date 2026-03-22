"""
Tests for appointment creation and shared schedule validation (model layer).

Validation runs via Appointment.full_clean(), which invokes clean() and thus
get_appointment_schedule_errors (overlap + 15-minute gap rules).
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentStatus
from apps.patients.models import Patient

User = get_user_model()


class AppointmentScheduleValidationTests(TestCase):
    """Exercise schedule rules: valid slot, duplicate start time, minimum gap."""

    def setUp(self):
        self.provider = User.objects.create_user(
            username="provider_appts",
            password="unused-for-model-tests",
        )
        self.patient = Patient.objects.create(
            provider=self.provider,
            name="Test Patient",
            email="appt.patient@example.com",
        )
        # Fixed base time so assertions are deterministic.
        self.slot_start = (timezone.now() + timedelta(days=14)).replace(
            second=0,
            microsecond=0,
        )

    def test_valid_appointment_passes_full_clean_and_saves(self):
        """
        A new appointment with no conflicting bookings should pass full_clean()
        and persist: schedule validation allows the slot.
        """
        appt = Appointment(
            provider=self.provider,
            patient=self.patient,
            scheduled_at=self.slot_start,
            duration=30,
            status=AppointmentStatus.SCHEDULED,
            reason="Checkup",
        )
        appt.full_clean()
        appt.save()

        self.assertTrue(
            Appointment.objects.filter(
                pk=appt.pk,
                provider=self.provider,
                patient=self.patient,
            ).exists(),
        )

    def test_cannot_create_two_appointments_at_same_scheduled_start(self):
        """
        Same provider cannot have two active appointments starting at the same
        instant (same scheduled_at). This is the "duplicate slot" case—both
        overlap validation and the DB unique constraint apply; full_clean()
        catches the schedule conflict via clean().
        """
        first = Appointment(
            provider=self.provider,
            patient=self.patient,
            scheduled_at=self.slot_start,
            duration=30,
            status=AppointmentStatus.SCHEDULED,
        )
        first.full_clean()
        first.save()

        second = Appointment(
            provider=self.provider,
            patient=self.patient,
            scheduled_at=self.slot_start,
            duration=20,
            status=AppointmentStatus.SCHEDULED,
        )
        with self.assertRaises(ValidationError) as ctx:
            second.full_clean()
        self.assertIn("scheduled_at", ctx.exception.error_dict)

    def test_cannot_create_appointment_with_less_than_fifteen_minute_gap_after_prior(self):
        """
        Shared schedule validation: there must be at least 15 minutes between the
        end of one appointment and the start of the next. Here the second visit
        starts only 10 minutes after the first ends (30-minute duration).
        """
        first = Appointment(
            provider=self.provider,
            patient=self.patient,
            scheduled_at=self.slot_start,
            duration=30,
            status=AppointmentStatus.SCHEDULED,
        )
        first.full_clean()
        first.save()

        # First ends at slot_start + 30m; next starts at +40m → 10-minute gap.
        too_soon = self.slot_start + timedelta(minutes=40)
        second = Appointment(
            provider=self.provider,
            patient=self.patient,
            scheduled_at=too_soon,
            duration=30,
            status=AppointmentStatus.SCHEDULED,
        )
        with self.assertRaises(ValidationError) as ctx:
            second.full_clean()
        self.assertIn("scheduled_at", ctx.exception.error_dict)
