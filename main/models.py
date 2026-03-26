from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission, AbstractBaseUser, PermissionsMixin
import uuid


# Create your models here.
class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    account_made_at = models.DateTimeField(auto_now=True,null=True,blank=True) 
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=500)
    first_name = models.CharField(max_length=50,blank=True,null=True)
    last_name = models.CharField(max_length=50,blank=True,null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    phone_number = models.IntegerField(blank=True,null=True)
    designation = models.CharField(max_length=50,blank=True,null=True)

    roles = (("ADMIN", "ADMIN"), ("MANAGER", "MANAGER"))
    role = models.CharField(max_length=50,choices=roles, default="MANAGER")
    USERNAME_FIELD = 'email'
    objects = UserManager()


    def __str__(self):
        return self.email
    
class Workshop(models.Model):
    workshop_name = models.CharField(max_length=200)
    # workshop_date = models.DateTimeField(blank=True, null=True)
    #Start Data 
    workshop_start_date = models.DateTimeField(null=True,blank=True)  
    workshop_end_date = models.DateTimeField(null=True,blank=True) 
    workshop_description = models.TextField(null=True,blank=True)
    workshop_logo = models.ImageField(upload_to='logo/')
    workshop_location = models.CharField(max_length=500)
    company_logo  =models.ImageField(upload_to='company_logo/', null=True, blank=True)
    photos_link = models.CharField(null=True, blank=True,max_length=100)
    workshop_seats = models.IntegerField(null=True,blank=True)
    workshop_tables = models.IntegerField(null=True, blank=True)
    number_workshop_groups = models.IntegerField(null=True, blank=True)
    workshop_seats_per_table = models.IntegerField(null=True, blank=True)
    workshop_manager = models.ForeignKey(User, default=1, on_delete=models.SET_DEFAULT)
    
    workshop_uuid = models.UUIDField(default=uuid.uuid4)
    is_closed = models.BooleanField(default=False)
    
    presenter_tables = models.CharField(max_length=500, blank=True, null=True)
    is_designation_required = models.BooleanField(default=True)

    
    def __str__(self) -> str:
        return self.workshop_name
    

class Workshop_groups(models.Model):
    workshop_id = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=500)
    tables = models.CharField(max_length=1000)

# designations 
class Workshop_designations(models.Model):
    workshop_id = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name="designations",null=True, blank=True)
    designation_name = models.CharField(max_length=500)
    designation_tables = models.CharField(max_length=1000) 

    def __str__(self):
        return f"{self.designation_name}"



class WorkshopVisitors(models.Model):
    workshop_id = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255,null=True,blank=True)
    # designation = models.CharField(max_length=500,null=True,blank=True)
    designation = models.ForeignKey(Workshop_designations, on_delete=models.CASCADE,null=True, blank=True)
    designation_text = models.CharField(max_length=500, null=True, blank=True)
    department = models.CharField(max_length=255,null=True,blank=True)
    is_presenter = models.BooleanField(default=False)
    # participating_as = models.CharField(max_length=50,null=True,blank=True)
    email = models.CharField(max_length=500)
    mobile_number = models.IntegerField(null=True,blank=True)
    alloted_table = models.CharField(max_length=50, null=True,blank=True)
    alloted_group = models.CharField(max_length=100, null=True,blank=True)
    # attandance_qr = models.ImageField(upload_to='logo/')
    is_visited = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)  # New field
    WorkshopVisitors_uuid = models.UUIDField(default=uuid.uuid4,unique=True)
    # WorkshopVisitors_uuid=models.UUIDField(unique=True, default=uuid.uuid4)



class Feedback(models.Model):
    visitor = models.ForeignKey(WorkshopVisitors, on_delete=models.CASCADE)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    question_1_response = models.TextField(blank=True, null=True)
    question_2_response = models.CharField(max_length=20, blank=True, null=True)  # Emoji rating
    question_3_response = models.IntegerField(blank=True, null=True)  # Star rating
    question_4_response = models.TextField(blank=True, null=True)
    question_5_response = models.CharField(max_length=50, blank=True, null=True)  # Knowledge level
    question_6_response = models.TextField(blank=True, null=True)
    question_7_response = models.CharField(max_length=50, blank=True, null=True)  # Satisfaction level
    question_8_response = models.TextField(blank=True, null=True)
    question_9_response = models.TextField(blank=True, null=True)
    # New fields for AI sentiment analysis
    sentiment = models.CharField(max_length=20, blank=True, null=True) # Positive, Neutral, Negative
    sentiment_score = models.FloatField(blank=True, null=True)

class FeedbackQuestion(models.Model):
    question_1 = models.CharField(max_length=255)
    question_2 = models.CharField(max_length=255)
    question_3 = models.CharField(max_length=255)
    question_4 = models.CharField(max_length=255)
    question_5 = models.CharField(max_length=255)
    question_6 = models.CharField(max_length=255)
    question_7 = models.CharField(max_length=255)
    question_8 = models.CharField(max_length=255)
    question_9 = models.CharField(max_length=255)

class Poll(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=300)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return self.option_text

class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    visitor = models.ForeignKey(WorkshopVisitors, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('poll', 'visitor')

class VisitorPoints(models.Model):
    REASON_CHOICES = [
        ('attendance', 'Attendance'),
        ('feedback', 'Feedback'),
        ('poll', 'Poll Vote'),
    ]
    visitor = models.ForeignKey(WorkshopVisitors, on_delete=models.CASCADE)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('visitor', 'workshop', 'reason')
    


