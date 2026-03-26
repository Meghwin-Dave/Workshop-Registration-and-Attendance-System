import requests
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from main.models import Workshop, WorkshopVisitors, Feedback
from ...config import config

class Command(BaseCommand):
    help = "Send feedback links to all visitors of a specific workshop via email and SMS"

    def add_arguments(self, parser):
        parser.add_argument('workshop_id', type=int, help="The ID of the workshop to send feedback links for.")

    def handle(self, *args, **options):
        workshop_id = options['workshop_id']

        # SMS Gateway credentials
        # api_key = "qiFR5Ycg8EqKR1NnV96FGA"
        # sender_id = "ICRETG"

        try:
            workshop = get_object_or_404(Workshop, id=workshop_id)
            visitors = WorkshopVisitors.objects.filter(workshop_id=workshop_id)

            if not visitors.exists():
                self.stdout.write(self.style.WARNING(f"No visitors found for workshop ID {workshop_id}."))
                return

            for visitor in visitors:
                try:
                    # Check for existing feedback
                    if Feedback.objects.filter(visitor=visitor, workshop=workshop).exists():
                        self.stdout.write(
                            self.style.WARNING(f"Visitor {visitor.email} has already submitted feedback. Skipping.")
                        )
                        continue

                    # Generate feedback links
                    feedback_url = f"{config.base_url}/workshop/{workshop.id}/feedback/{visitor.WorkshopVisitors_uuid}/"
                    sms_feedback_url = f"{config.base_url}/workshop/feedback?visitor={visitor.WorkshopVisitors_uuid}-{workshop.id}"


                    print("sms_feedback_url", sms_feedback_url)

                    # Send email
                    subject = "Share Your Feedback – We Value Your Experience"
                    message = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: 'Quire Sans', sans-serif; line-height: 1.6; color: #000000; padding: 20px;">
    <p style="margin: 16px 0;color: #000000;">We hope you are having a great time and finding the workshop sessions engaging and insightful.</p>

    <p style="margin: 16px 0;color: #000000;">Your <span style="color: #FF0000; font-weight: bold;">feedback</span> plays a crucial role in helping us improve and create even better experiences for future events.</p>
    <p style="margin: 16px 0;color: #000000;">We kindly request you to take a moment to share your thoughts and suggestions with us. Please click the link below to access the feedback form:</p>
    <p style="margin: 16px 0;color: #000000;"><a href="{feedback_url}" style="color: #0066cc;">{feedback_url}</a></p>
    
    <p style="margin: 16px 0;color: #000000;">Your input is invaluable to us, and we truly appreciate your time and effort in sharing your experience</p>

    <p style="margin: 16px 0;color: #000000;">Thank you for being an integral part of this workshop. We look forward to reading your thoughts!</p>

    <p style="margin: 16px 0;color: #000000;">Best Regards,<br>iCretegy</p>
</body>
</html>"""

                    # send_mail(
                    #     subject,
                    #     message,
                    #     settings.DEFAULT_FROM_EMAIL,
                    #     [visitor.email],
                    #     fail_silently=False,
                    # )
                    send_mail(
                        subject,
                        '', 
                        settings.DEFAULT_FROM_EMAIL,
                        [visitor.email],
                        fail_silently=False,
                        html_message=message
                    )

                    self.stdout.write(self.style.SUCCESS(f"Feedback link sent to {visitor.email}"))

                    # Send SMS if mobile number exists
                    # if visitor.mobile_number:
                    #     phone = str(visitor.mobile_number).lstrip('0')  # Remove any leading zeros

                    #     # Send SMS using the template
                    #     sms_response = self.send_sms(
                    #         api_key,
                    #         sender_id,
                    #         phone,
                    #         sms_feedback_url
                    #     )

                    #     if isinstance(sms_response, dict):
                    #         if sms_response.get('ErrorMessage') == 'Success':
                    #             self.stdout.write(self.style.SUCCESS(f"SMS sent to {phone}"))
                    #         else:
                    #             error_msg = sms_response.get('ErrorMessage', str(sms_response))
                    #             self.stderr.write(
                    #                 self.style.ERROR(f"Failed to send SMS to {phone}: {error_msg}")
                    #             )
                    #     else:
                    #         self.stderr.write(
                    #             self.style.ERROR(f"Failed to send SMS to {phone}: {sms_response}")
                    #         )
                    # else:
                    #     self.stdout.write(
                    #         self.style.WARNING(f"No mobile number found for visitor {visitor.email}")
                    #     )

                except Exception as email_error:
                    self.stderr.write(
                        self.style.ERROR(f"Failed to process visitor {visitor.email}: {email_error}")
                    )

            self.stdout.write(self.style.SUCCESS('Feedback links sent successfully'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))

#     def send_sms(self, api_key, sender_id, phone_number, sms_feedback_url):
#         url = "https://www.smsgatewayhub.com/api/mt/SendSMS"

#         # Format the message text properly
#         message_text = (
#             f"Greetings from iCretegy! "
#             f"We hope you are enjoying the sessions. Your feedback is valuable to us, and we would love to hear about your experience so far. "
#             f"Please take a moment to share your thoughts by clicking the link below: {sms_feedback_url} "
#             f"Thank you for helping us improve!"
#         )

#         # Use proper XML escaping for the message text
#         from xml.sax.saxutils import escape
#         message_text_escaped = escape(message_text)

#         xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
# <SmsQueue>
#     <Account>
#         <APIKey>{escape(api_key)}</APIKey>
#         <SenderId>{escape(sender_id)}</SenderId>
#         <Channel>2</Channel>
#         <DCS>0</DCS>
#         <FlashSms>0</FlashSms>
#         <Route>1</Route>
#     </Account>
#     <Messages>
#         <Message>
#             <Number>{escape(phone_number)}</Number>
#             <Text>{message_text_escaped}</Text>
#         </Message>
#     </Messages>
# </SmsQueue>"""

#         headers = {
#             'Content-Type': 'application/xml; charset=UTF-8'  # Added charset specification
#         }

#         try:
#             response = requests.post(url, data=xml_template.encode('utf-8'), headers=headers)
#             print("Response status code:", response.status_code)
#             print("Response content:", response.text)  # Added for debugging

#             if response.status_code == 200:
#                 try:
#                     response_data = response.json()
#                     print("Response data:", response_data)
#                     return response_data
#                 except ValueError as e:
#                     print("JSON Parsing Error:", str(e))
#                     # Try to return the raw response if JSON parsing fails
#                     return {"ErrorMessage": f"Response: {response.text}"}
#             else:
#                 return {"ErrorMessage": f"HTTP {response.status_code}: {response.text}"}

#         except requests.exceptions.RequestException as e:
#             print("Request Exception:", str(e))
#             return {"ErrorMessage": str(e)}
