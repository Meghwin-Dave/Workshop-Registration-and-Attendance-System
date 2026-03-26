from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from main.models import Workshop, WorkshopVisitors, Poll
from ...config import config

class Command(BaseCommand):
    help = "Send active poll link for a given workshop to all visitors via email"

    def add_arguments(self, parser):
        parser.add_argument('workshop_id', type=int, help="ID of the workshop")

    def handle(self, *args, **options):
        workshop_id = options['workshop_id']

        try:
            workshop = get_object_or_404(Workshop, id=workshop_id)
            active_poll = Poll.objects.filter(workshop=workshop, is_active=True).first()

            if not active_poll:
                self.stderr.write(self.style.WARNING(f"No active poll found for workshop {workshop_id}."))
                return

            visitors = WorkshopVisitors.objects.filter(workshop_id=workshop_id)
            if not visitors.exists():
                self.stderr.write(self.style.WARNING(f"No visitors found for workshop {workshop_id}."))
                return

            count = 0
            for visitor in visitors:
                try:
                    # Construct poll link
                    poll_url = f"{config.base_url}/poll/{visitor.WorkshopVisitors_uuid}/"
                    
                    subject = f"Live Poll: {active_poll.question}"
                    message = f"""Dear {visitor.name},

We have a live poll running for the workshop '{workshop.workshop_name}'.
Your opinion matters! Please vote by clicking the link below:

{poll_url}

Best regards,
Workshop Team"""

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [visitor.email],
                        fail_silently=False,
                    )
                    count += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed to send email to {visitor.email}: {e}"))

            self.stdout.write(self.style.SUCCESS(f"Poll invitations sent to {count} visitors for workshop {workshop_id}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
