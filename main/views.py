from email.mime.image import MIMEImage
from django.shortcuts import render
from django.contrib.auth.models import User, auth
from django.shortcuts import redirect, render, reverse
from django.contrib.auth.decorators import login_required
from . import models, forms
from django.http import JsonResponse
import json
import random
import qrcode
from django.http import Http404
import io
import base64
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
import uuid
from django.core.exceptions import MultipleObjectsReturned
from django.contrib import messages
from django.urls import path
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from io import BytesIO
from django.core.files import File
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
import subprocess
from django.shortcuts import render, get_object_or_404
from .models import Workshop, WorkshopVisitors, Feedback
from .forms import FeedbackForm
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from . import models
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.core.management import call_command
from . import models
import subprocess
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Workshop, WorkshopVisitors, Feedback, FeedbackQuestion, Poll, PollOption, PollVote, VisitorPoints
from .forms import FeedbackForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from . import models
from django.shortcuts import render, redirect
from .forms import FeedbackQuestionForm  # Corrected import
from .models import FeedbackQuestion
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json
import calendar
import requests
import base64
from io import BytesIO
from django.http import HttpResponse
from bs4 import BeautifulSoup
from .config import config
from .services import award_points, analyze_and_save_sentiment, get_top_keywords

@login_required(login_url="../login/")
def home(request):
    return render(request, "home.html", {"dashboard_key":True})

def login(request):
    if request.method == 'GET':
        # Capture the next parameter if provided
        next_url = request.GET.get('next', '/')
        return render(request, 'login.html', {'next': next_url})

    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        next_url = request.POST.get('next', '/')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect(next_url)  # Redirect to the next URL or default to home
        else:
            messages.error(request, 'Invalid Credential')
            return render(request, 'login.html', {'message': 'Invalid Credential', 'next': next_url})

def logout(request):
	auth.logout(request)
	return redirect(reverse('login'))

# Home View
@login_required(login_url="../login/")
def home(request):
    total_workshops = Workshop.objects.count()
    total_visitors = WorkshopVisitors.objects.count()
    
    # Get the current year
    current_year = timezone.now().year
    
    # Generate all 12 months for the current year
    all_months = [timezone.datetime(current_year, month, 1) for month in range(1, 13)]
    
    # Get monthly workshop data
    monthly_workshops = Workshop.objects.filter(
        workshop_start_date__year=current_year
    ).annotate(
        month=TruncMonth('workshop_start_date')
    ).values('month').annotate(
        workshop_count=Count('id')
    ).order_by('month')
    
    # Create a dictionary of workshop counts for easy lookup
    workshop_dict = {entry['month'].month: entry['workshop_count'] for entry in monthly_workshops}
    
    # Prepare chart data for monthly workshops
    months = [month.strftime('%B') for month in all_months]
    workshop_counts = [workshop_dict.get(month.month, 0) for month in all_months]
    
    # Workshop Positive Feedbacks Pie Chart
    # Filter feedbacks with 4 or 5 star ratings
    workshops_positive_feedback = Feedback.objects.filter(
        question_3_response__in=[4, 5]
    ).values('workshop__workshop_name').annotate(
        positive_feedback_count=Count('id')
    ).order_by('-positive_feedback_count')
    
    # Prepare data for pie chart
    workshop_names = []
    positive_feedback_counts = []
    
    for item in workshops_positive_feedback:
        workshop_names.append(item['workshop__workshop_name'])
        positive_feedback_counts.append(item['positive_feedback_count'])
    
    # JSON serialize the lists
    months_json = json.dumps(months)
    workshop_counts_json = json.dumps(workshop_counts)
    workshop_names_json = json.dumps(workshop_names)
    positive_feedback_counts_json = json.dumps(positive_feedback_counts)
    
    context = {
        'total_workshops': total_workshops,
        'total_visitors': total_visitors,
        'months': months_json,  
        'workshop_counts': workshop_counts_json,
        'workshop_names': workshop_names_json,
        'positive_feedback_counts': positive_feedback_counts_json,
    }
    return render(request, "home.html", context)


# Workshop Views
@login_required(login_url="../login/")
def show_workshop(request):
    data = models.Workshop.objects.all().order_by("-id")
    return render(request, "workshop/show_workshop.html", context={
        "data": data, 
        "show_flag": True, 
        "heading": "Workshop List", 
        "columns": ["Sr No.", "Name", "Date", "Total Seats"], 
        "add_url": "/add_workshop", 
        "edit_url": "/edit_workshop", 
        "delete_url": "/delete_workshop", 
        "workshop_key": True
    })

#add workshop

@login_required(login_url="../login/")
def add_workshop(request):
    if request.method == "POST":
        form = forms.AddWorkshopForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a new workshop but don't save yet
            workshop_form = form.save(commit=False)
            # Set the current user as the workshop manager
            workshop_form.workshop_manager = request.user
            # Save the workshop to the database
            workshop_form.save()
            return redirect("../show_workshop")
        
        return render(request, "workshop/add_workshop.html", context={
            "form": form, 
            "show_flag": True, 
            "heading": "Add Workshop", 
            "workshop_key": True
        })
    else:
        # Empty form for new workshop
        form = forms.AddWorkshopForm()
        return render(request, "workshop/add_workshop.html", context={
            "form": form, 
            "show_flag": True, 
            "heading": "Add Workshop", 
            "workshop_key": True
        })
@login_required(login_url="../login/")
def edit_workshop(request, pk):
    # Get the workshop to edit
    workshop = models.Workshop.objects.get(id=pk)
    visitors = models.WorkshopVisitors.objects.filter(workshop_id=pk)

    if request.method == "POST":
        form = forms.AddWorkshopForm(request.POST, request.FILES, instance=workshop)
        if form.is_valid():
            # Save the form data but don't commit it yet
            workshop_form = form.save(commit=False)
            # Assign the current user as the workshop manager
            workshop_form.workshop_manager = request.user
            # Save the edited workshop
            workshop_form.save()
            return redirect("../show_workshop")
        
        return render(request, "workshop/add_workshop.html", context={
            'workshop_id': workshop.id,
            "form": form, 
            "show_flag": True, 
            "heading": "Edit Workshop", 
            "workshop_key": True, 
            "is_edit": True, 
            "workshop_id": pk,
            "visitors": visitors,
            "group_details": json.dumps(list(models.Workshop_groups.objects.filter(workshop_id=pk).values('group_name', 'tables'))), 
            "is_closed": workshop.is_closed,
            "is_designation_required": workshop.is_designation_required
        })
    else:
        # Pre-fill the form with the existing workshop data
        form = forms.AddWorkshopForm(instance=workshop)
        return render(request, "workshop/add_workshop.html", context={
            "form": form, 
            "show_flag": True, 
            "heading": "Edit Workshop", 
            "workshop_key": True, 
            "is_edit": True, 
            "workshop_id": pk, 
            "visitors": visitors,
            "group_details": json.dumps(list(models.Workshop_groups.objects.filter(workshop_id=pk).values('group_name', 'tables'))), 
            "is_closed": workshop.is_closed,
            "is_designation_required": workshop.is_designation_required
        })

# delete workshop
@login_required(login_url="../login/")
def delete_workshop(request, pk):
    workshop_entry = models.Workshop.objects.get(id=pk)
    workshop_entry.delete()
    return redirect("../show_workshop")

# save group details 
@login_required(login_url="../login/")
def save_group_details(request, pk):
    if request.method == 'POST':
        # Get the workshop instance
        workshop = models.Workshop.objects.get(id=pk)

        # Delete existing group details for this workshop
        models.Workshop_groups.objects.filter(workshop_id=pk).delete()
        
        # Initialize an empty list to store the new group records
        new_groups = []
        
        # Iterate through the form data and process each group
        group_count = 0
        while True:
            group_name_key = f'group_name_{group_count + 1}'
            tables_key = f'tables_{group_count + 1}'
            
            # Check if the form has values for the current group
            if group_name_key in request.POST and tables_key in request.POST:
                group_name = request.POST[group_name_key]
                tables = request.POST[tables_key]

                # Create a new Workshop_groups object
                new_group = models.Workshop_groups(
                    workshop_id=workshop,
                    group_name=group_name,
                    tables=tables
                )
                new_groups.append(new_group)
                
                group_count += 1  # Move to the next group
            else:
                # Break the loop when there are no more groups
                break

        # Bulk create all new groups at once
        if new_groups:
            models.Workshop_groups.objects.bulk_create(new_groups)

        # Send a success response
        return JsonResponse({'status': 'success', 'message': 'Group details saved successfully'})
    else:
        # Retrieve and return existing group details
        workshop = models.Workshop.objects.get(id=pk)
        updated_groups = models.Workshop_groups.objects.filter(workshop_id=pk).values('group_name', 'tables')
        return JsonResponse(list(updated_groups), safe=False)

#edit Group details
@login_required(login_url="../login/")
def edit_number_of_groups(request, pk):
    if request.method == "POST":
        workshop = models.Workshop.objects.get(id=pk)
        workshop.number_workshop_groups = request.POST["number_of_groups"]
        workshop.save()
        return JsonResponse({'status': 'success', 'message': 'Edited group number successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Not valid request method'}, status=401)



#close workshop 
@login_required(login_url="../login/")
def close_workshop(request, pk):
    try:
        workshop = models.Workshop.objects.get(id=pk)
        if workshop.is_closed:
            messages.error(request, 'Workshop is already closed!')
            return redirect('home')
        
        # Use Django's subprocess module safely
        # command = ["/home/ubuntu/icretegy-wsra/wenv/bin/python3", "manage.py", "close_workshop", str(workshop.pk)]
        # command = ["/home/enviroer/virtualenv/icretegy-wsra/3.8/bin/python", "manage.py", "close_workshop", str(workshop.pk)]
        command = ["python", "manage.py", "close_workshop", str(workshop.pk)]
        subprocess.Popen(command)
        
        messages.success(request, 'Workshop closing process has started.')
        return redirect('home')
    
    except models.Workshop.DoesNotExist:
        messages.error(request, 'Workshop not found.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error closing workshop: {str(e)}')
        return redirect('home')


# show workshop visitors
@login_required(login_url="../login/")
def show_visitors(request, pk):
    # Fetch the specific workshop by primary key
    workshop = models.Workshop.objects.get(id=pk)
    
    # Get visitors for the specific workshop
    if workshop.is_closed:
        # If the workshop is closed, sort visitors by 'alloted_group' in ascending order
        data = models.WorkshopVisitors.objects.filter(workshop_id=workshop).order_by('alloted_group')
    else:
        # If the workshop is not closed, you can use other ordering logic
        data = models.WorkshopVisitors.objects.filter(workshop_id=workshop).order_by("-id")
    
    is_closed = workshop.is_closed
    are_emails_sent = request.session.get('emails_sent_{}'.format(pk), False)
    is_feedback_sent = request.session.get('feedback_sent_{}'.format(pk), False)  # Check if feedback was sent
    
    return render(request, "workshop/show_visitors.html", 
                  context={
                      "data": data,
                      "show_flag": True,
                      "heading": "Workshop Visitors List",
                      "columns": ["Sr No.", "Full Name", "Mobile Number", "Email Details", "Designation"," Is Presenter", "Alloted Table", "Alloted Group", "Attandance"],
                      "workshop_key": True,
                      "workshop_id": pk,
                      "is_closed": is_closed,
                      "is_feedback_sent": is_feedback_sent,
                      "are_emails_sent": are_emails_sent
                  })



#visitor_registration_form
def visitor_registration_form(request, workshop_uuid):
    workshop = get_object_or_404(models.Workshop, workshop_uuid=workshop_uuid)
    
    # Generate list of dates in "d M Y" format (e.g., "21 Dec 2024")
    date_list = [
        (workshop.workshop_start_date + timedelta(days=i)).strftime("%d %B %Y")
        for i in range((workshop.workshop_end_date - workshop.workshop_start_date).days + 1)
    ]

    if request.method == "GET":
        # Pass workshop_id to the form to filter the designations
        form = forms.AddWorkshopVisitorForm(workshop_id=workshop.id)
        return render(request, "register.html", context={
            "form": form,
            "closed": workshop.is_closed,
            "workshop_name": workshop.workshop_name,
            "workshop_logo": workshop.workshop_logo,
            "workshop_location": workshop.workshop_location,
            "workshop_start_date": workshop.workshop_start_date,
            "workshop_end_date": workshop.workshop_end_date,
            "workshop_description": workshop.workshop_description,
            "date_list": date_list  # Pass the list of dates to the template
        })
    else:
        form = forms.AddWorkshopVisitorForm(request.POST, workshop_id=workshop.id)
        if form.is_valid():
            workshop_form = form.save(commit=False)
            workshop_form.workshop_id = workshop
            workshop_form.visitor_uuid = uuid.uuid4()
            workshop_form.save()

            workshop_form.qr_code = generate_qr_code(workshop_form.id).replace("/media/", "")
            workshop_form.save()

            return render(request, "register.html", context={
                "form": forms.AddWorkshopVisitorForm(workshop_id=workshop.id),
                "completed": True,
                "closed": workshop.is_closed,
                "workshop_name": workshop.workshop_name,
                "workshop_logo": workshop.workshop_logo,
                "workshop_location": workshop.workshop_location,
                "workshop_start_date": workshop.workshop_start_date,
                "workshop_end_date": workshop.workshop_end_date,
                "workshop_description": workshop.workshop_description,
                "date_list": date_list 
            })
        else:
            print("Form is not valid. Errors:", form.errors)
            return render(request, "register.html", context={
                "form": form,
                "form_errors": form.errors,
                "closed": workshop.is_closed,
                "workshop_name": workshop.workshop_name,
                "workshop_logo": workshop.workshop_logo,
                "workshop_location": workshop.workshop_location,
                "workshop_start_date": workshop.workshop_start_date,
                "workshop_end_date": workshop.workshop_end_date,
                "workshop_description": workshop.workshop_description,
                "date_list": date_list 
            })


#show user 
@login_required(login_url="../login/")
def show_users(request):
	data = models.User.objects.all().order_by("-id")
	return render(request, "User/show_users.html", context={"data":data, "show_flag":True, "heading":"User List", "columns":["Sr No.", "Name", "Role", "Email"], "add_url":"/add_user", "edit_url":"/edit_user", "delete_url":"/delete_user", "user_key":True})

#add user
@login_required(login_url="../login/")
def add_user(request):
	form = forms.AddUserForm()
	if request.method == "POST":
		form = forms.AddUserForm(request.POST)
		if form.is_valid():
			# models.User.objects.create_user(**request.POST)
			form.save()
			return redirect("../show_users")
		return render(request, "User/add_user.html", context={"form":form, "show_flag":True, "heading":"Add User", "user_key":True})
	else:
		form = forms.AddUserForm()
		return render(request, "User/add_user.html", context={"form":form, "show_flag":True, "heading":"Add User", "user_key":True})

#edit user
@login_required(login_url="../login/")
def edit_user(request, pk):
	user_object = models.User.objects.get(id=pk)
	form = forms.EditUserForm(instance=user_object)
	if request.method == "POST":
		form = forms.EditUserForm(request.POST, instance=user_object)
		if form.is_valid():
			# models.User.objects.create_user(**request.POST)
			form.save()
			return redirect("../show_users")
		return render(request, "User/add_user.html", context={"form":form, "show_flag":True, "heading":"Add User", "user_key":True, "user_id":pk})
	else:
		return render(request, "User/add_user.html", context={"form":form, "show_flag":True, "heading":"Add User", "user_key":True, "user_id":pk})

# delete user
@login_required(login_url="../login/")
def delete_user(request, pk):
	user_object = models.User.objects.get(id=pk)

	user_object.delete()

	return redirect("../show_users")

@login_required(login_url="../login/")
def change_password(request, pk):
	user_object = models.User.objects.get(id=pk)

	user_object.set_password(request.POST["password"])

	user_object.save()

	return JsonResponse({'status': 'success', 'message': 'Edited group number successfully'})


#qr scanner
def qr_scanner(request):
    context = {
        'heading': 'QR Code Scanner',
        'show_flag': True,
        'success_msg': 0,
        'name1': '12345'
    }
    return render(request, 'scanner/qr_scanner.html', context)

#workshop_scanner
def workshop_scanner(request, workshop_id):
    try:
        # Get the specific workshop using ID
        workshop = get_object_or_404(models.Workshop, id=workshop_id)
        context = {
            'heading': f'QR Code Scanner for Workshop: {workshop.workshop_name}',
            'show_flag': True,
            'workshop_id': workshop_id,
            'workshop_name': workshop.workshop_name
        }
        return render(request, 'scanner/qr_scanner.html', context)
    except models.Workshop.DoesNotExist:
        messages.error(request, "Workshop not found")
        return redirect('home')


#generate_qr_code
def generate_qr_code(visitor_id):
    try:
        print(visitor_id)
        visitor = get_object_or_404(models.WorkshopVisitors, id=visitor_id)
        # base_url = "https://icretegy-wsra.enviroerp.com"
        base_url = f"{config.base_url}"
        verification_url = f"{base_url}/verify_visitor/{visitor.WorkshopVisitors_uuid}"
        
        # Create a QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Create the QR code image in memory
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image_io = BytesIO()
        qr_image.save(qr_image_io, format='PNG')
        qr_image_io.seek(0)  # Ensure the pointer is at the beginning of the file
        
        # Save the image to the visitor model
        visitor.qr_code.save(f"{visitor.id}_qr.png", File(qr_image_io), save=True)
        
        return visitor.qr_code.url  # Return URL or any info as needed

    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None


# verify_visitor
def verify_visitor(request, uuid, workshop_id):
    try:
        # Verify if the workshop exists
        workshop = get_object_or_404(models.Workshop, id=workshop_id)
        
        # Try to get the visitor by UUID
        try:
            workshop_visitor = models.WorkshopVisitors.objects.get(WorkshopVisitors_uuid=uuid)
        except models.WorkshopVisitors.DoesNotExist:
            messages.error(request, "Invalid QR code. Visitor not found.")
            return redirect('workshop_scanner', workshop_id=workshop_id)
        
        # Check if the visitor's registered workshop matches
        if workshop_visitor.workshop_id.id != workshop.id:
            print("workshop id, return workshop id ======>",workshop_id,workshop.id)
            messages.error(request, 
                f"Access Denied: This visitor is registered for workshop '{workshop_visitor.workshop_id.workshop_name}'"
            )
            # print("in the if ------------------")
            return render(request, 'workshop/visitor_verification.html',{"flag":True})
        
        # If the visitor is valid for this workshop
        
        context = {
            'visitor_name': workshop_visitor.first_name,
            'mobile_number': workshop_visitor.mobile_number,
            'email': workshop_visitor.email,
            'designation': workshop_visitor.designation,
            'alloted_table': workshop_visitor.alloted_table,
            'alloted_group': workshop_visitor.alloted_group,
            'is_visited': workshop_visitor.is_visited,
            'workshop_name': workshop.workshop_name,
            'workshop_id': str(workshop_id),
            'visitor_uuid': str(uuid),  # Add this line
            'is_designation_required': workshop.is_designation_required, 
            'designation_text': workshop_visitor.designation_text, 
        }
        # print("Context",context)
        return render(request,"workshop/visitor_verification.html",context)

    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        print("Error===>",str(e))
        return render(request, 'workshop/visitor_verification.html')

# Make attendance
@require_POST
def mark_attendance(request, workshop_id, uuid):
    try:
        # Get the workshop visitor
        workshop_visitor = get_object_or_404(
            models.WorkshopVisitors, 
            WorkshopVisitors_uuid=uuid,
            workshop_id_id=workshop_id
        )
        
        # Check if attendance is already marked
        if workshop_visitor.is_visited:
            return JsonResponse({
                'success': False,
                'message': f"Attendance for {workshop_visitor.first_name} was already marked."
            })
        
        # Mark attendance
        workshop_visitor.is_visited = True
        workshop_visitor.save()
        
        # Award 10 points for attendance
        award_points(workshop_visitor, workshop_visitor.workshop_id, 'attendance', 10)
        
        return JsonResponse({
            'success': True,
            'message': f"Successfully marked attendance for {workshop_visitor.first_name}"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Error marking attendance: {str(e)}"
        })
      

#generate workshop ticket
def generate_ticket(request, visitor_id):
    try:
        visitor = get_object_or_404(models.WorkshopVisitors, id=visitor_id)
        workshop = visitor.workshop_id  

        start_date = workshop.workshop_start_date
        end_date = workshop.workshop_end_date

        if not start_date or not end_date:
            raise ValueError("Start date or End date is missing")

        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)

        base_url = request.build_absolute_uri('/')[:-1] 

        qr_code_url = (
            f"{base_url}{visitor.qr_code.url}" 
            if visitor.qr_code else f"{base_url}/static/default_qr.png"
        )
        
        context = {
            'visitor': visitor,
            'workshop': workshop,
            'qr_code_url': qr_code_url, # Use in the template
            'visitor_uuid': visitor.WorkshopVisitors_uuid,
            'full_name': f"{visitor.first_name} {visitor.last_name}" if visitor.first_name and visitor.last_name else " ",
            'alloted_table': f"{visitor.alloted_table}" if visitor.alloted_table else "Not Assigned",
            'alloted_group': visitor.alloted_group if visitor.alloted_group else "Not Assigned",
            'date_list': date_list,
        }
        return render(request, 'workshop/ticket.html', context)
    
    except models.WorkshopVisitors.DoesNotExist:
        messages.error(request, "Visitor not found")
        return redirect('home')
    
    except AttributeError as ae:
        messages.error(request, f"Attribute error: {str(ae)}")
        return redirect('home')
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')
    

def sms_ticket(request):
    try:
        visitor_id = request.GET.get('ticket')
        if not visitor_id:
            messages.error(request, "No ticket ID provided")
            return redirect('home')
        
        try:
            visitor_id = int(visitor_id)
        except ValueError:
            messages.error(request, "Invalid ticket ID format")
            return redirect('home')

        visitor = get_object_or_404(models.WorkshopVisitors, id=visitor_id)
        workshop = visitor.workshop_id

        start_date = workshop.workshop_start_date
        end_date = workshop.workshop_end_date

        if not start_date or not end_date:
            raise ValueError("Start date or End date is missing")

        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)

        base_url = request.build_absolute_uri('/')[:-1]

        qr_code_url = (
            f"{base_url}{visitor.qr_code.url}"
            if visitor.qr_code else f"{base_url}/static/default_qr.png"
        )

        context = {
            'visitor': visitor,
            'workshop': workshop,
            'qr_code_url': qr_code_url,
            'visitor_uuid': visitor.WorkshopVisitors_uuid,
            'full_name': f"{visitor.first_name} {visitor.last_name}" if visitor.first_name and visitor.last_name else " ",
            'alloted_table': f"{visitor.alloted_table}" if visitor.alloted_table else "Not Assigned",
            'alloted_group': visitor.alloted_group if visitor.alloted_group else "Not Assigned",
            'date_list': date_list,
        }
        return render(request, 'workshop/ticket.html', context)

    except models.WorkshopVisitors.DoesNotExist:
        messages.error(request, "Visitor not found")
        return redirect('home')

    except AttributeError as ae:
        messages.error(request, f"Attribute error: {str(ae)}")
        return redirect('home')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

    
def sms_feedback(request):
    try:
        # Extract visitor and workshop info from the 'visitor' GET parameter
        visitor_workshop_info = request.GET.get('visitor')

        visitor_uuid = "-".join(request.GET.get('visitor').split("-")[:-1])
        workshop_id = request.GET.get('visitor').split("-")[-1]
    
        # Fetch workshop and visitor objects using the extracted information
        workshop = get_object_or_404(Workshop, id=workshop_id)
        visitor = get_object_or_404(WorkshopVisitors, WorkshopVisitors_uuid=visitor_uuid)

        # Check if feedback already exists
        existing_feedback = Feedback.objects.filter(visitor=visitor, workshop=workshop).exists()

        # Fetch the feedback question
        feedback_question = FeedbackQuestion.objects.first()

        if request.method == 'POST':
            form = FeedbackForm(request.POST)
            if form.is_valid():
                feedback = form.save(commit=False)
                feedback.visitor = visitor
                feedback.workshop = workshop
                feedback.save()

                # Analyze sentiment and award 5 points for feedback
                analyze_and_save_sentiment(feedback)
                award_points(visitor, workshop, 'feedback', 5)

                return render(request, 'workshop/feedback.html', {
                    'feedback_submitted': True,
                    'feedback_question': feedback_question,
                    'workshop': workshop,
                    'visitor': visitor,
                })
        else:
            form = FeedbackForm()

        return render(request, 'workshop/feedback.html', {
            'form': form,
            'feedback_question': feedback_question,
            'feedback_submitted': existing_feedback,
            'workshop': workshop,
            'visitor': visitor,
        })

    except Workshop.DoesNotExist:
        messages.error(request, "Workshop not found")
        return redirect('home')

    except WorkshopVisitors.DoesNotExist:
        messages.error(request, "Visitor not found")
        return redirect('home')

    except AttributeError as ae:
        messages.error(request, f"Attribute error: {str(ae)}")
        return redirect('home')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

# def download_ticket(request, id):
#     # base_url = "https://icretegy-wsra.enviroerp.com/ticket/"
#     base_url = f"{config.base_url}/ticket/"
#     target_url = f"{base_url}{id}/"
    
#     try:
#         # Fetch the HTML content
#         response = requests.get(target_url)
#         response.raise_for_status()  # Raise error for bad responses
#         html_content = response.text
        
#         # Parse the HTML using BeautifulSoup
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # Find all image tags
#         for img_tag in soup.find_all('img'):
#             img_url = img_tag.get('src')

#             if img_url:
#                 # If the image URL is relative, adjust it to be absolute
#                 if not img_url.startswith('http'):
#                     img_url = f"{config.base_url}{img_url}"
                
#                 # Download the image
#                 img_response = requests.get(img_url)
#                 img_response.raise_for_status()  # Raise error for bad responses

#                 # Convert image to base64
#                 img_base64 = base64.b64encode(img_response.content).decode('utf-8')

#                 # Replace the image URL in the HTML with a base64-encoded string
#                 img_tag['src'] = f"data:image/png;base64,{img_base64}"

#         # Get the modified HTML
#         modified_html = str(soup)

#         # Prepare the response as an HTML file download
#         download_response = HttpResponse(modified_html, content_type='application/pdf')
#         download_response['Content-Disposition'] = f'attachment; filename="page_{id}.pdf"'
        
#         return download_response
    
#     except requests.exceptions.RequestException as e:
#         return HttpResponse(f"Error fetching the URL: {e}", status=500)
    
from io import BytesIO
from django.http import HttpResponse
from xhtml2pdf import pisa
import requests
from bs4 import BeautifulSoup

# def download_ticket(request, id):
#     # base_url = "https://icretegy-wsra.enviroerp.com/ticket/"
#     # img_base_url = f"{config.base_url}"
#     img_base_url = "http://127.0.0.1:8000/"
#     print(img_base_url)
#     base_url = f"{img_base_url}/ticket/"
#     target_url = f"{base_url}{id}/"

#     try:
#         # Fetch the HTML content
#         response = requests.get(target_url)
#         response.raise_for_status()
#         html_content = response.text

#         # Parse the HTML using BeautifulSoup
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # Replace image URLs with absolute URLs
#         for img_tag in soup.find_all('img'):
#             img_url = img_tag.get('src')
#             if img_url and not img_url.startswith('http'):
#                 img_url = f"{img_base_url}{img_url}"
#                 img_tag['src'] = img_url

#         # Convert the updated HTML to a string
#         modified_html = str(soup)

#         # Convert HTML to PDF using xhtml2pdf
#         pdf_buffer = BytesIO()
#         pisa_status = pisa.CreatePDF(BytesIO(modified_html.encode('utf-8')), dest=pdf_buffer)

#         # Check for errors in PDF generation
#         if pisa_status.err:
#             return HttpResponse("Error generating PDF", status=500)

#         # Return the PDF as an HTTP response
#         pdf_buffer.seek(0)
#         response = HttpResponse(pdf_buffer, content_type='text/html')
#         response['Content-Disposition'] = f'attachment; filename="ticket_{id}.html"'
#         return response

#     except requests.exceptions.RequestException as e:
#         return HttpResponse(f"Error fetching the URL: {e}", status=500)
#     except Exception as e:
#         return HttpResponse(f"Error generating PDF: {e}", status=500)

def download_ticket(request, id):
        # img_base_url = f"{config.base_url}"
    img_base_url = f"{config.base_url}"
    base_url = f"{img_base_url}/ticket/"
    target_url = f"{base_url}{id}/"
    
    try:
        # Fetch the HTML content
        response = requests.get(target_url)
        response.raise_for_status()  # Raise error for bad responses
        html_content = response.text
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find all image tags
        for img_tag in soup.find_all('img'):
            img_url = img_tag.get('src')
            if img_url:
                # If the image URL is relative, adjust it to be absolute
                if not img_url.startswith('http'):
                    img_url = f"{config.base_url}{img_url}"
                
                # Download the image
                img_response = requests.get(img_url)
                img_response.raise_for_status()  # Raise error for bad responses
                # Convert image to base64
                img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                # Replace the image URL in the HTML with a base64-encoded string
                img_tag['src'] = f"data:image/png;base64,{img_base64}"
        # Get the modified HTML
        modified_html = str(soup)
        # Prepare the response as an HTML file download
        download_response = HttpResponse(modified_html, content_type='text/html')
        download_response['Content-Disposition'] = f'attachment; filename="page_{id}.html"'
        
        return download_response
    
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error fetching the URL: {e}", status=500)


# visitor feedback 
def feedback_view(request, workshop_id, visitor_uuid):
    # Fetch the workshop and visitor
    workshop = get_object_or_404(Workshop, id=workshop_id)
    visitor = get_object_or_404(WorkshopVisitors, WorkshopVisitors_uuid=visitor_uuid)
    
    # Check if feedback already exists
    existing_feedback = Feedback.objects.filter(visitor=visitor, workshop=workshop).exists()
    if existing_feedback:
        return render(request, 'workshop/feedback.html', {
            'feedback_submitted': True,
            'feedback_question': FeedbackQuestion.objects.first(),
            'workshop': workshop,
            'visitor': visitor,
        })
    
    # Get the feedback question
    feedback_question = FeedbackQuestion.objects.first()
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Save the new feedback
            feedback = form.save(commit=False)
            feedback.visitor = visitor
            feedback.workshop = workshop
            feedback.save()
            
            # Analyze sentiment and award 5 points for feedback
            analyze_and_save_sentiment(feedback)
            award_points(visitor, workshop, 'feedback', 5)
            
            return render(request, 'workshop/feedback.html', {
                'feedback_submitted': True,
                'feedback_question': feedback_question,
                'workshop': workshop,
                'visitor': visitor,
            })
    else:
        # Handle GET request to show the feedback form
        form = FeedbackForm()
    
    return render(request, 'workshop/feedback.html', {
        'form': form,
        'feedback_question': feedback_question,
        'feedback_submitted': False,
        'workshop': workshop,
        'visitor': visitor,
    })


# send feedback link (email)
@login_required(login_url="../login/")
def send_feedback_emails(request, workshop_id):
    try:
        # Get the workshop instance
        workshop = models.Workshop.objects.get(id=workshop_id)
        
        # Trigger the feedback email sending process
        # command = ["/home/enviroer/virtualenv/icretegy-wsra/3.8/bin/python", "manage.py", "feedback", str(workshop_id)]
        # command = ["/home/ubuntu/icretegy-wsra/wenv/bin/python3", "manage.py", "feedback", str(workshop_id)]
        command = ["python", "manage.py", "feedback", str(workshop_id)]
        
        subprocess.Popen(command)
        
        # Mark the feedback email process as started in the session
        request.session['feedback_sent_{}'.format(workshop_id)] = True
        
        messages.success(request, 'Feedback Link Send process has started.')
        return redirect('home')  # Redirect as needed
    except Exception as e:
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)


# show user feedback
def show_feedback(request, visitor_uuid):
    try:
        visitor = get_object_or_404(WorkshopVisitors, WorkshopVisitors_uuid=visitor_uuid)
        feedback = Feedback.objects.filter(visitor=visitor).values(
            'question_1_response',
            'question_2_response',
            'question_3_response',
            'question_4_response',
            'question_5_response',
            'question_6_response',
            'question_7_response',
            'question_8_response',
            'question_9_response',
        )

        if feedback.exists():
            return JsonResponse({
                "success": True,
                "feedback": list(feedback),
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "No feedback has been added yet.",
            }, status=404)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)


from django.http import JsonResponse

from django.http import JsonResponse

def get_designations_and_groups(request, workshop_id):
    designations = models.Workshop_designations.objects.filter(workshop_id=workshop_id)
    groups = models.Workshop_groups.objects.filter(workshop_id=workshop_id)

    return JsonResponse({
        'designations': [
            {
                'id': d.id, 
                'designation_name': d.designation_name
            } for d in designations
        ],
        'groups': [
            {
                'id': g.id, 
                'group_name': g.group_name
            } for g in groups
        ]
    })
# edit visitor_details
@csrf_protect
@require_POST
def edit_visitor_details(request):
    try:
        # Get form data
        visitor_uuid = request.POST.get('visitor_uuid')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name', '')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        designation_id = request.POST.get('designation', '')
        alloted_table = request.POST.get('alloted_table', '')
        alloted_group_id = request.POST.get('alloted_group', '')

        # Find the visitor by UUID
        visitor = get_object_or_404(models.WorkshopVisitors, WorkshopVisitors_uuid=visitor_uuid)

        # If designation ID is provided, get the corresponding Workshop_designations instance
        if designation_id:
            # Retrieve the designation instance using the ID
            designation_instance = get_object_or_404(models.Workshop_designations, id=designation_id)
            visitor.designation = designation_instance

        # Update other fields
        visitor.first_name = first_name
        visitor.last_name = last_name
        visitor.mobile_number = mobile_number
        visitor.email = email
        visitor.alloted_table = alloted_table
        
        # Handle group - retrieve the group name if an ID is provided
        if alloted_group_id:
            group_instance = get_object_or_404(models.Workshop_groups, id=alloted_group_id)
            visitor.alloted_group = group_instance.group_name

        # Save the changes
        visitor.save()

        return JsonResponse({
            'success': True, 
            'message': 'Visitor details updated successfully',
            'visitor_id': visitor.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': str(e)
        }, status=400)

#seat mail send
@login_required(login_url="../login/")
def send_emails(request, workshop_id):
    try:
        # Trigger email sending
        # command = ["/home/ubuntu/icretegy-wsra/wenv/bin/python3", "manage.py", "send_emails", str(workshop_id)]
        # command = ["/home/enviroer/virtualenv/icretegy-wsra/3.8/bin/python", "manage.py", "send_emails", str(workshop_id)]
        command = ["python", "manage.py", "close_workshop", str(workshop_id)]
        subprocess.Popen(command)

        # Set session flag to indicate emails are being sent
        request.session['emails_sent_{}'.format(workshop_id)] = True
        
        messages.success(request, 'Emails are being sent. The process has started.')
        return redirect('show_visitors', pk=workshop_id)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

    

#save designation details
@login_required(login_url="../login/")
def save_designation_details(request, pk):
    if request.method == 'POST':
        try:
            workshop = models.Workshop.objects.get(id=pk)
        except models.Workshop.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Workshop not found'}, status=404)

        # Track existing designations to identify which ones to remove
        existing_designations = list(
            models.Workshop_designations.objects
            .filter(workshop_id=pk)
            .values('designation_name', 'designation_tables')
        )

        # Initialize lists to track new and removal designations
        new_designations = []
        current_designations = []

        # Collect new designations
        designation_count = 0
        while True:
            designation_name_key = f'designation_name_{designation_count + 1}'
            designation_tables_key = f'designation_tables_{designation_count + 1}'

            # Check if the form has values for the current designation
            if designation_name_key in request.POST and designation_tables_key in request.POST:
                designation_name = request.POST[designation_name_key]
                designation_tables = request.POST[designation_tables_key]

                # Skip empty designations
                if designation_name.strip() and designation_tables.strip():
                    current_designations.append({
                        'designation_name': designation_name, 
                        'designation_tables': designation_tables
                    })

                    # Check if this is a new designation
                    is_new = True
                    for existing in existing_designations:
                        if (existing['designation_name'] == designation_name and 
                            existing['designation_tables'] == designation_tables):
                            is_new = False
                            break

                    if is_new:
                        new_designation = models.Workshop_designations(
                            workshop_id=workshop,
                            designation_name=designation_name,
                            designation_tables=designation_tables
                        )
                        new_designations.append(new_designation)

                designation_count += 1
            else:
                # Break the loop when there are no more designations
                break

        # Remove designations that are no longer in the current list
        designations_to_remove = [
            existing for existing in existing_designations 
            if existing not in current_designations
        ]

        if designations_to_remove:
            models.Workshop_designations.objects.filter(
                workshop_id=pk,
                designation_name__in=[d['designation_name'] for d in designations_to_remove],
                designation_tables__in=[d['designation_tables'] for d in designations_to_remove]
            ).delete()

        # Bulk create all new designations at once
        if new_designations:
            models.Workshop_designations.objects.bulk_create(new_designations)

        # Send a success response
        return JsonResponse({
            'status': 'success', 
            'message': 'Designation details saved successfully'
        })
    else:
        # Retrieve and return existing designation details
        try:
            workshop = models.Workshop.objects.get(id=pk)
        except models.Workshop.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Workshop not found'}, status=404)

        updated_designations = models.Workshop_designations.objects.filter(workshop_id=pk).values('designation_name', 'designation_tables')
        return JsonResponse(list(updated_designations), safe=False)

# feedback add
def add_feedback(request):
    if request.method == 'POST':
        form = FeedbackQuestionForm(request.POST)
        if form.is_valid():
            # Case 1: If there is an existing feedback entry, update it; otherwise, create a new one
            feedback = FeedbackQuestion.objects.first()  # Get the first feedback entry (if exists)
            if feedback:
                # Update existing feedback
                feedback.question_1 = form.cleaned_data['question_1']
                feedback.question_2 = form.cleaned_data['question_2']
                feedback.question_3 = form.cleaned_data['question_3']
                feedback.question_4 = form.cleaned_data['question_4']
                feedback.question_5 = form.cleaned_data['question_5']
                feedback.question_6 = form.cleaned_data['question_6']
                feedback.question_7 = form.cleaned_data['question_7']
                feedback.question_8 = form.cleaned_data['question_8']
                feedback.question_9 = form.cleaned_data['question_9']
                feedback.save()
            else:
                # If no feedback exists, create a new one
                feedback = form.save()

            messages.success(request, 'Feedback submitted successfully!')
            return redirect('add_feedback')  # Redirect to the same page

    else:
        # Fetch the first feedback entry, or create a new one if it doesn't exist
        feedback = FeedbackQuestion.objects.first()
        
        if feedback:
            form = FeedbackQuestionForm(instance=feedback)
        else:
            form = FeedbackQuestionForm()

    return render(request, 'add_feedback.html', {'form': form})

# --- Advanced Features API Endpoints ---

@login_required(login_url="../login/")
def api_workshop_stats(request, workshop_uuid):
    workshop = get_object_or_404(Workshop, workshop_uuid=workshop_uuid)
    visitors = WorkshopVisitors.objects.filter(workshop_id=workshop)
    
    total_registered = visitors.count()
    total_checked_in = visitors.filter(is_visited=True).count()
    
    total_seats = workshop.workshop_seats or 0
    remaining_seats = max(0, total_seats - total_checked_in)
    
    feedback_count = Feedback.objects.filter(workshop=workshop).count()
    active_poll = Poll.objects.filter(workshop=workshop, is_active=True).first()
    poll_participation = 0
    if active_poll:
        poll_participation = PollVote.objects.filter(poll=active_poll).count()
        
    return JsonResponse({
        'registered': total_registered,
        'checked_in': total_checked_in,
        'remaining': remaining_seats,
        'feedback_count': feedback_count,
        'poll_participation': poll_participation
    })

@login_required(login_url="../login/")
def api_table_occupancy(request, workshop_uuid):
    workshop = get_object_or_404(Workshop, workshop_uuid=workshop_uuid)
    visitors = WorkshopVisitors.objects.filter(workshop_id=workshop).exclude(alloted_table__isnull=True).exclude(alloted_table='')
    
    table_stats = {}
    if workshop.workshop_tables:
        for i in range(1, workshop.workshop_tables + 1):
            table_stats[str(i)] = 0
            
    for visitor in visitors:
        if visitor.is_visited:
            table_num = visitor.alloted_table
            table_stats[table_num] = table_stats.get(table_num, 0) + 1
            
    seats_per_table = workshop.workshop_seats_per_table or 1
    
    data = []
    for table_id, occupied in table_stats.items():
        data.append({
            'table': table_id,
            'occupied': occupied,
            'total': seats_per_table,
            'status': 'red' if occupied >= seats_per_table else ('yellow' if occupied > 0 else 'green')
        })
        
    return JsonResponse({'tables': data})

def api_live_poll(request, workshop_uuid):
    workshop = get_object_or_404(Workshop, workshop_uuid=workshop_uuid)
    poll = Poll.objects.filter(workshop=workshop, is_active=True).order_by('-created_at').first()
    
    if not poll:
        return JsonResponse({'active': False})
        
    options = poll.options.all().values('id', 'option_text', 'vote_count')
    visitor_uuid = request.GET.get('visitor_uuid')
    has_voted = False
    if visitor_uuid:
        has_voted = PollVote.objects.filter(poll=poll, visitor__WorkshopVisitors_uuid=visitor_uuid).exists()
        
    return JsonResponse({
        'active': True,
        'poll_id': poll.id,
        'question': poll.question,
        'options': list(options),
        'has_voted': has_voted
    })

def api_poll_vote(request, poll_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
        
    poll = get_object_or_404(Poll, id=poll_id)
    if not poll.is_active:
        return JsonResponse({'error': 'Poll is not active'}, status=400)
        
    data = json.loads(request.body)
    visitor_uuid = data.get('visitor_uuid')
    option_id = data.get('option_id')
    
    visitor = get_object_or_404(WorkshopVisitors, WorkshopVisitors_uuid=visitor_uuid)
    option = get_object_or_404(PollOption, id=option_id, poll=poll)
    
    if PollVote.objects.filter(poll=poll, visitor=visitor).exists():
        return JsonResponse({'error': 'Already voted'}, status=400)
        
    PollVote.objects.create(poll=poll, visitor=visitor, selected_option=option)
    option.vote_count += 1
    option.save()
    award_points(visitor, poll.workshop, 'poll', 3)
    
    return JsonResponse({'success': True, 'vote_count': option.vote_count})

def api_leaderboard(request, workshop_uuid):
    workshop = get_object_or_404(Workshop, workshop_uuid=workshop_uuid)
    from django.db.models import Sum
    top_participants = VisitorPoints.objects.filter(workshop=workshop)\
        .values('visitor__first_name', 'visitor__last_name')\
        .annotate(total_points=Sum('points'))\
        .order_by('-total_points')[:10]
        
    data = []
    for i, p in enumerate(top_participants):
        data.append({
            'rank': i + 1,
            'name': f"{p['visitor__first_name']} {p['visitor__last_name']}",
            'points': p['total_points']
        })
        
    return JsonResponse({'leaderboard': data})

@login_required(login_url="../login/")
def api_feedback_sentiment(request, workshop_uuid):
    workshop = get_object_or_404(Workshop, workshop_uuid=workshop_uuid)
    feedbacks = Feedback.objects.filter(workshop=workshop)
    sentiment_counts = feedbacks.values('sentiment').annotate(count=Count('id'))
    
    summary = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
    for entry in sentiment_counts:
        label = entry['sentiment'] or 'Neutral'
        summary[label] = entry['count']
        
    keywords = get_top_keywords(workshop.id)
    return JsonResponse({'sentiment': summary, 'keywords': keywords})

# --- Manager Views ---

@login_required(login_url="../login/")
def live_dashboard(request, pk):
    workshop = get_object_or_404(Workshop, id=pk)
    return render(request, 'workshop/live_dashboard.html', {'workshop': workshop, 'workshop_key': True})

@login_required(login_url="../login/")
def poll_management(request, pk):
    workshop = get_object_or_404(Workshop, id=pk)
    polls = Poll.objects.filter(workshop=workshop).order_by('-created_at')
    return render(request, 'workshop/poll_management.html', {'workshop': workshop, 'polls': polls, 'workshop_key': True})

@require_POST
@login_required(login_url="../login/")
def create_poll(request, pk):
    workshop = get_object_or_404(Workshop, id=pk)
    question = request.POST.get('question')
    options_text = request.POST.getlist('options')
    poll = Poll.objects.create(workshop=workshop, question=question)
    for opt in options_text:
        if opt.strip():
            PollOption.objects.create(poll=poll, option_text=opt.strip())
    messages.success(request, 'Poll created successfully.')
    return redirect('poll_management', pk=pk)

@require_POST
@login_required(login_url="../login/")
def toggle_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if not poll.is_active:
        Poll.objects.filter(workshop=poll.workshop).update(is_active=False)
        poll.is_active = True
    else:
        poll.is_active = False
    poll.save()
    return JsonResponse({'success': True, 'is_active': poll.is_active})

@login_required(login_url="../login/")
def leaderboard_view(request, pk):
    workshop = get_object_or_404(Workshop, id=pk)
    return render(request, 'workshop/leaderboard.html', {'workshop': workshop, 'workshop_key': True})

@login_required(login_url="../login/")
def feedback_analytics_view(request, pk):
    workshop = get_object_or_404(Workshop, id=pk)
    return render(request, 'workshop/feedback_analytics.html', {'workshop': workshop, 'workshop_key': True})

# --- Visitor Views ---

def visitor_poll(request, visitor_uuid):
    visitor = get_object_or_404(WorkshopVisitors, WorkshopVisitors_uuid=visitor_uuid)
    workshop = visitor.workshop_id
    return render(request, 'workshop/visitor_poll.html', {'visitor': visitor, 'workshop': workshop})

def visitor_leaderboard(request, workshop_uuid):
    workshop = get_object_or_404(Workshop, workshop_uuid=workshop_uuid)
    return render(request, 'workshop/visitor_leaderboard.html', {'workshop': workshop})


@login_required
def send_poll_emails(request, workshop_id):
    """
    Trigger sending poll invitations to all visitors of a workshop.
    """
    workshop = get_object_or_404(Workshop, id=workshop_id)
    active_poll = Poll.objects.filter(workshop=workshop, is_active=True).first()

    if not active_poll:
        return JsonResponse({'success': False, 'error': 'No active poll found to send.'})

    visitors = WorkshopVisitors.objects.filter(workshop_id=workshop_id)
    if not visitors.exists():
        return JsonResponse({'success': False, 'error': 'No visitors found for this workshop.'})

    count = 0
    from .config import config
    
    errors = []
    sent_to = []

    for visitor in visitors:
        try:
            # Construct poll link
            if 'http' not in config.base_url:
                domain = f"{request.scheme}://{request.get_host()}"
                poll_url = f"{domain}/poll/{visitor.WorkshopVisitors_uuid}/"
            else:
                poll_url = f"{config.base_url}/poll/{visitor.WorkshopVisitors_uuid}/"

            subject = f"Live Poll: {active_poll.question}"
            message = f"Dear {visitor.name},\n\nWe have a live poll running for '{workshop.workshop_name}'. Please vote here:\n\n{poll_url}\n\nRegards,\nTeam"

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [visitor.email],
                fail_silently=False,
            )
            count += 1
            sent_to.append(visitor.email)
        except Exception as e:
            err_msg = str(e)
            print(f"Error sending to {visitor.email}: {err_msg}")
            if err_msg not in errors:
                errors.append(err_msg)

    if count == 0 and errors:
        return JsonResponse({'success': False, 'error': f'Failed to send emails. Error: {", ".join(errors)}'})

    return JsonResponse({
        'success': True, 
        'message': f'Invitations sent to {count} visitors.',
        'sent_to': sent_to,
        'errors': errors
    })



