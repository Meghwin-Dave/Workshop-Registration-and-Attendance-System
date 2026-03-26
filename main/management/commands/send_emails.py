import requests
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from main.models import Workshop, WorkshopVisitors
from ...config import config

class Command(BaseCommand):
    help = "Seating Arrangement for Upcoming Workshop – Important Details Inside"

    def add_arguments(self, parser):
        parser.add_argument('workshop_id', type=int, help="ID of the workshop")

    def handle(self, *args, **options):
        workshop_id = options['workshop_id']
        # api_key = "qiFR5Ycg8EqKR1NnV96FGA"
        # sender_id = "ICRETG"
        # dlt_template_id = "1007866561255343974" 
        # telemarketer_id = "1302157243747322354"

        try:
            workshop = get_object_or_404(Workshop, id=workshop_id)
            visitors = WorkshopVisitors.objects.filter(workshop_id=workshop_id)

            if not visitors.exists():
                self.stderr.write(self.style.WARNING(f"No visitors found for workshop ID {workshop_id}"))
                return

            for visitor in visitors:
                try:
                    ticket_url = f"{config.base_url}/ticket/{visitor.id}/"
                    sms_ticket_url = f"{config.base_url}/ticket?ticket={visitor.id}"

                    subject = "Seating Arrangement for Upcoming Workshop – Important Details Inside"
                    message = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: 'Quire Sans', sans-serif; line-height: 1.6; color: #000000; padding: 20px;">
    <p style="margin: 16px 0;color: #000000;">Thank you for registering for our upcoming workshop. We are thrilled to have you with us and look forward to an engaging and informative session.</p>

    <p style="margin: 16px 0;color: #000000;">Please click the link below to get your ticket and find <span style="color: #FF0000; font-weight: bold;">your seating arrangement</span> and <span style="color: #FF0000; font-weight: bold;">assigned group name</span> for the event:</p>

    <p style="margin: 16px 0;color: #000000;"><a href="{ticket_url}" style="color: #0066cc;">{ticket_url}</a></p>

    <p style="margin: 16px 0;color: #006400;">This <span style="color: #006400; font-weight: bold;">barcode will be required for entry</span> to the workshop, so please ensure you bring it with you, either digitally or printed.</p>

    <div style="margin: 24px 0;color: #000000;">
        <p style="color: #000080; font-weight: bold; margin-bottom: 16px;">Important Notes:</p>
        <p style="margin: 10px 0; padding-left: 20px;color: #000000;">› <strong>Punctuality:</strong> Kindly be on time to ensure the event starts promptly.</p>
        <p style="margin: 10px 0; padding-left: 20px;color: #000000;">› <strong>Dress Code:</strong> Please wear professional attire for the event.</p>
        <p style="margin: 10px 0; padding-left: 20px;color: #000000;">› <strong>Group Assignment:</strong> Please remember your assigned group name for easier flow.</p>
    </div>

    <p style="margin: 16px 0;color: #000000;">We look forward to a productive and insightful session.</p>

    <p style="margin: 16px 0;color: #000000;">Best Regards,<br>iCretegy</p>
</body>
</html>"""

                    send_mail(
                        subject,
                        '', 
                        settings.DEFAULT_FROM_EMAIL,
                        [visitor.email],
                        fail_silently=False,
                        html_message=message
                    )

                    self.stdout.write(self.style.SUCCESS(f"Email sent to {visitor.email}"))

#                     if visitor.mobile_number:
#                         phone = self.format_phone_number(visitor.mobile_number)
#                         sms_response = self.send_sms(
#                             api_key,
#                             sender_id,
#                             phone,
#                             telemarketer_id,
#                             dlt_template_id,
#                             sms_ticket_url
#                         )

#                         if isinstance(sms_response, dict):
#                             if sms_response.get('ErrorMessage') == 'Success':
#                                 self.stdout.write(self.style.SUCCESS(f"SMS sent to {phone}"))
#                             else:
#                                 self.stderr.write(self.style.ERROR(f"SMS failed for {phone}: {sms_response.get('ErrorMessage')}"))
#                         else:
#                             self.stderr.write(self.style.ERROR(f"SMS failed for {phone}: {sms_response}"))
#                     else:
#                         self.stdout.write(self.style.WARNING(f"No mobile number for {visitor.email}"))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error processing {visitor.email}: {str(e)}"))
                    continue

#         except Exception as e:
#             self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))

#     def send_sms(self, api_key, sender_id, phone_number, telemarketer_id, template_id, sms_ticket_url):
#         url = "https://www.smsgatewayhub.com/api/mt/SendSMS"
        
#         # XML template for the SMS message
#         xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
# <SmsQueue>
#     <Account>
#         <APIKey>{api_key}</APIKey>
#         <SenderId>{sender_id}</SenderId>
#         <Channel>2</Channel>
#         <DCS>0</DCS>
#         <FlashSms>0</FlashSms>
#         <Route>1</Route>
#     </Account>
#     <Messages>
#         <Message>
#             <Number>{phone_number}</Number>
#             <Text>Greetings from iCretegy! Thank you for your participation in the upcoming workshop. We are excited to have you join us! Please find the link below to check your seating arrangement:This {sms_ticket_url} You need to bring this barcode on the day of workshop for the entry. Looking forward to seeing you soon!</Text>
#         </Message>
#     </Messages>
# </SmsQueue>"""

#         # Prepare headers and payload
#         headers = {
#             'Content-Type': 'application/xml'
#         }

#         try:
#             # print("Sending SMS with XML:", xml_template)
#             response = requests.post(url, data=xml_template, headers=headers)
#             print("Response status code:", response.status_code)

#             # Only try to parse JSON if we have a successful response
#             if response.status_code == 200:
#                 try:
#                     response_data = response.json()
#                     print("Response data:", response_data)
#                     return response_data
#                 except ValueError as e:
#                     print("JSON Parsing Error:", str(e))
#                     return {"ErrorMessage": f"Invalid JSON response: {str(e)}"}
#             else:
#                 return {"ErrorMessage": f"HTTP {response.status_code}: {response.text}"}

        except requests.exceptions.RequestException as e:
            print("Request Exception:", str(e))
            return {"ErrorMessage": str(e)}

#     def format_phone_number(self, phone):
#         """Format phone number to ensure it includes country code."""
#         phone = str(phone).strip().lstrip('0')
#         if not phone.startswith('91'):
#             phone = '91' + phone
#         return phone
