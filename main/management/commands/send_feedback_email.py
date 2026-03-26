from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from main.models import Workshop, WorkshopVisitors, Feedback
from ...config import config

class Command(BaseCommand):
    help = "Send feedback link for a given workshop and visitor via email"

    def add_arguments(self, parser):
        parser.add_argument('workshop_id', type=int, help="ID of the workshop")
        parser.add_argument('visitor_uuid', type=str, help="UUID of the visitor")

    def handle(self, *args, **options):
        workshop_id = options['workshop_id']
        visitor_uuid = options['visitor_uuid']

        try:
            # Fetch workshop and visitor
            workshop = get_object_or_404(Workshop, id=workshop_id)
            visitor = get_object_or_404(WorkshopVisitors, WorkshopVisitors_uuid=visitor_uuid)

            # Check for existing feedback
            existing_feedback = Feedback.objects.filter(visitor=visitor, workshop=workshop).first()
            if existing_feedback:
                self.stdout.write(
                    self.style.WARNING(f"Feedback already exists for visitor {visitor_uuid} in workshop {workshop_id}.")
                )
                return

            # Construct the feedback link URL
            # feedback_url = f"http://127.0.0.1:8000/workshop/{workshop.id}/feedback/{visitor.WorkshopVisitors_uuid}/"
            feedback_url = f"{config.base_url}/workshop/{workshop.id}/feedback/{visitor.WorkshopVisitors_uuid}/"
            self.stdout.write(f"Feedback URL: {feedback_url}")

            # Send feedback link via email
            subject = f"Feedback Request for Workshop: {workshop.workshop_name}"
            message = f"Dear {visitor.name},\n\nWe would appreciate your feedback for the workshop '{workshop.workshop_name}'.\nPlease provide your feedback by clicking on the following link:\n\n{feedback_url}\n\nBest regards,\nWorkshop Team"

            # Send email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # From email address
                [visitor.email],  # Visitor's email address
                fail_silently=False,
            )

            self.stdout.write(self.style.SUCCESS(f"Feedback link sent to {visitor.email}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
