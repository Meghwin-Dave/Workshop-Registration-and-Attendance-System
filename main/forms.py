from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model
from django.forms import ModelForm
from django.forms.utils import ErrorList
from . import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Button, HTML
from crispy_forms.bootstrap import TabHolder, Tab
from datetime import date
from crispy_forms.layout import Layout, Div, Row, Column, HTML
from django.forms import modelformset_factory
from django import forms
from .models import Feedback
from django.forms import formset_factory
from .models import Workshop, WorkshopVisitors, Workshop_designations
from django import forms
from django import forms
from .models import FeedbackQuestion


# workshop ADD form
# class AddWorkshopForm(ModelForm):
#     helper = FormHelper()
#     helper.form_method = 'POST'
#     helper.form_tag = False
#     helper.form_show_labels = True
    
#     class Meta:
#         model = models.Workshop
#         fields = '__all__'
#         exclude = ('workshop_manager', 'workshop_uuid', 'is_closed')

#     def __init__(self, *args, **kwargs):
#         super(AddWorkshopForm, self).__init__(*args, **kwargs)
        
#         # Customizing labels
#         self.fields['number_workshop_groups'].label = 'Group Count'
        
#         required_fields = [
#             "workshop_location", 
#             "workshop_date", 
#             "workshop_name", 
#             "workshop_start_date", 
#             "workshop_end_date"
#         ]
        
#         for field in self.fields:
#             if field in required_fields:
#                 self.fields[field].widget.attrs.update({'class': "form-control form-control-user", 'required': True})
#             else:
#                 self.fields[field].widget.attrs.update({'class': "form-control form-control-user"})

#         # Configure date fields
#         self.fields['workshop_description'].widget.attrs.update({'rows': '1'})
#         self.fields['workshop_start_date'].widget.attrs.update({'id': 'datepicker1', 'autocomplete': 'on'})
#         self.fields['workshop_start_date'].input_formats = ['%Y-%m-%d']
#         self.fields['workshop_end_date'].widget.attrs.update({'id': 'datepicker2', 'autocomplete': 'on'})
#         self.fields['workshop_end_date'].input_formats = ['%Y-%m-%d']

#         sections = [
#             Div(
#                 # First row: Workshop name, Start date, End date
#                 Row(
#                     Column('workshop_name', css_class='form-group col-md-4 mb-0 my-4'),
#                     Column('workshop_start_date', css_class='form-group col-md-4 mb-0 my-4'),
#                     Column('workshop_end_date', css_class='form-group col-md-4 mb-0 my-4'),
#                 ),
#                 # Second row: Location and Logo
#                 Row(
#                     Column('workshop_location', css_class='form-group col-md-8 mb-0 my-4'),
#                     Column('workshop_logo', css_class='form-group col-md-4 mb-0 my-4'),
#                 ),
#                 # Third row: Description and Photos
#                 Row(
#                     Column('workshop_description', css_class='form-group col-md-8 mb-0 my-4'),
#                     Column('photos_link', css_class='form-group col-md-4 mb-0 my-4'),
#                 ),
#                 # Fourth row: Seats information
#                 Row(
#                     Column('company_logo', css_class='form-group col-md-4 mb-0 my-4'),
#                     Column('workshop_seats', css_class='form-group col-md-4 mb-0 my-4'),
#                     Column('workshop_tables', css_class='form-group col-md-4 mb-0 my-4'),
#                 ),
#                 # Fifth row: Workshop groups
#                 Row(
#                     Column('workshop_seats_per_table', css_class='form-group col-md-4 mb-0 my-4'),
#                     Column('number_workshop_groups', css_class='form-group col-md-4 mb-0 my-4'),
#                     Column('presenter_tables', css_class='form-group col-md-4 mb-0 my-4'),
#                 )
#             )
#         ]
        
#         layout_rows = []
#         field_names = [field_name for field_name in self.fields if field_name != 'done']
#         row_fields = 3 
#         for i in range(0, len(field_names), row_fields):
#             columns = [Column(field, css_class='form-group col-md-4 mb-0 my-4') for field in field_names[i:i + row_fields]]
#             layout_rows.append(Row(*columns))
            
#         self.helper.layout = Layout(*sections)
class AddWorkshopForm(ModelForm):
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_tag = False
    helper.form_show_labels = True

    class Meta:
        model = models.Workshop
        fields = '__all__'
        exclude = ('workshop_manager', 'workshop_uuid', 'is_closed')

    def __init__(self, *args, **kwargs):
        super(AddWorkshopForm, self).__init__(*args, **kwargs)
        
        # Customizing labels
        self.fields['number_workshop_groups'].label = 'Group Count'
        
        required_fields = [
            "workshop_location", 
            "workshop_name", 
            "workshop_start_date", 
            "workshop_end_date"
        ]
        
        for field in self.fields:
            if field in required_fields:
                self.fields[field].widget.attrs.update({'class': "form-control form-control-user", 'required': True})
            else:
                self.fields[field].widget.attrs.update({'class': "form-control form-control-user"})

        # Configure date fields
        self.fields['workshop_description'].widget.attrs.update({'rows': '1'})
        
        self.fields['workshop_start_date'].widget = forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
        self.fields['workshop_end_date'].widget = forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )

        # No additional classes for checkbox
        self.fields['is_designation_required'].widget.attrs.update({'class': ''})

        sections = [
            Div(
                # First row: Workshop name, Start date, End date
                Row(
                    Column('workshop_name', css_class='form-group col-md-4 mb-0 my-4'),
                    Column('workshop_start_date', css_class='form-group col-md-4 mb-0 my-4'),
                    Column('workshop_end_date', css_class='form-group col-md-4 mb-0 my-4'),
                ),
                # Second row: Location and Logo
                Row(
                    Column('workshop_location', css_class='form-group col-md-8 mb-0 my-4'),
                    Column('workshop_logo', css_class='form-group col-md-4 mb-0 my-4'),
                ),
                # Third row: Description and Photos
                Row(
                    Column('workshop_description', css_class='form-group col-md-8 mb-0 my-4'),
                    Column('photos_link', css_class='form-group col-md-4 mb-0 my-4'),
                ),
                # Fourth row: Seats information
                Row(
                    Column('company_logo', css_class='form-group col-md-4 mb-0 my-4'),
                    Column('workshop_seats', css_class='form-group col-md-4 mb-0 my-4'),
                    Column('workshop_tables', css_class='form-group col-md-4 mb-0 my-4'),
                ),
                # Fifth row: Workshop groups
                Row(
                    Column('workshop_seats_per_table', css_class='form-group col-md-4 mb-0 my-4'),
                    Column('number_workshop_groups', css_class='form-group col-md-4 mb-0 my-4'),
                    Column('presenter_tables', css_class='form-group col-md-4 mb-0 my-4'),
                ),
                # Normal checkbox for designation required
                Row(
                    Column('is_designation_required', css_class='form-group col-md-4 mb-0 my-4'),
                ),
            )
        ]
        
        self.helper.layout = Layout(*sections)



#Workshop visitor register 
class PrefixFirstNameWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        _attrs = attrs or {}
        widgets = [
            forms.Select(
                choices=[
                    ('Mr.', 'Mr.'),
                    ('Mrs.', 'Mrs.'),
                    ('Ms.', 'Ms.'),
                    ('Dr.','Dr.')
                ],
                attrs={
                    'class': 'form-select',
                    'style': 'width: 100px; display: inline-block;'
                }
            ),
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'First Name',
                    'style': 'width: calc(100% - 110px); display: inline-block; margin-left: 10px;'
                }
            )
        ]
        super().__init__(widgets, _attrs)

    def decompress(self, value):
        if value:
            return value.split(' ', 1)
        return ['Mr.', '']

    def render(self, name, value, attrs=None, renderer=None):
        # Override render method to wrap widgets in a div
        rendered_widgets = super().render(name, value, attrs, renderer)
        return f'<div style="display: block; width: 100%;">{rendered_widgets}</div>'

class PrefixFirstNameField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = [
            forms.ChoiceField(
                choices=[
                    ('Mr.', 'Mr.'),
                    ('Mrs.', 'Mrs.'),
                    ('Ms.', 'Ms.'),
                    ('Dr.','Dr.')
                ],
                required=True
            ),
            forms.CharField(required=True)
        ]
        super().__init__(fields, widget=PrefixFirstNameWidget(), *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return [data_list[0] , data_list[1]]
        return ''
class ParticipatingWidget(forms.Select):
    def __init__(self, attrs=None):
        _attrs = attrs or {}
        _attrs.update({
            'class': 'form-select',  # Use form-select like the prefix dropdown
            'style': 'width: 100%;'  # Make it full width
        })
        super().__init__(_attrs)
        

# class AddWorkshopVisitorForm(forms.ModelForm):
#     prefix_first_name = PrefixFirstNameField(
#         label="First Name",
#         required=True
#     )
#     last_name = forms.CharField(
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#         required=True
#     )
    
#     designation = forms.ModelChoiceField(
#         queryset=None,  # Will be set in __init__
#         empty_label="Select Designation",
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         required=True
#     )
        
#     department = forms.CharField(
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#         required=True
#     )
#     is_presenter = forms.ChoiceField(
#     choices=[
#         ('', 'Select'), 
#         (True, 'Yes'),
#         (False, 'No')
#     ],
#     widget=forms.Select(attrs={'class': 'form-control'}),
#     required=True,
#     label="Are you a Presenter?"
#     )
#     email = forms.EmailField(
#         widget=forms.EmailInput(attrs={'class': 'form-control'}),
#         required=True
#     )
#     mobile_number = forms.CharField(
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#         required=True
#     )

#     class Meta:
#         model = WorkshopVisitors
#         fields = ['prefix_first_name', 'last_name', 'designation', 'department', 
#                  'is_presenter', 'email', 'mobile_number']

#     def __init__(self, *args, **kwargs):
#         # Extract workshop_id if passed, otherwise set to None
#         workshop_id = kwargs.pop('workshop_id', None)
#         super().__init__(*args, **kwargs)

#         # Set the queryset for designation based on the workshop_id
#         if workshop_id:
#             self.fields['designation'].queryset = Workshop_designations.objects.filter(
#                 workshop_id=workshop_id
#             )
#         else:
#             # If no workshop_id is provided, show all designations
#             self.fields['designation'].queryset = Workshop_designations.objects.all()

#         # Crispy forms layout setup
#         self.helper = FormHelper()
#         self.helper.form_method = 'POST'
#         self.helper.form_tag = False
#         self.helper.form_show_labels = True
        
#         # Update form layout
#         self.helper.layout = Layout(
#             Row(Column('prefix_first_name', css_class='form-group col-md-12 mb-3')),
#             Row(Column('last_name', css_class='form-group col-md-12 mb-3')),
#             Row(Column('designation', css_class='form-group col-md-12 mb-3')),
#             Row(Column('department', css_class='form-group col-md-12 mb-3')),
#             Row(Column('is_presenter', css_class='form-group col-md-12 mb-3')),
#             Row(Column('email', css_class='form-group col-md-12 mb-3')),
#             Row(Column('mobile_number', css_class='form-group col-md-12 mb-3')),
#         )

#     def save(self, commit=True):
#         instance = super().save(commit=False)
        
#         # Combine prefix and first name
#         prefix, first_name = self.cleaned_data['prefix_first_name']
#         instance.first_name = f"{prefix} {first_name}"
        
#         instance.is_presenter = self.cleaned_data['is_presenter']
#         if commit:
#             instance.save()
#         return instance
class AddWorkshopVisitorForm(forms.ModelForm):
    prefix_first_name = PrefixFirstNameField(
        label="First Name",
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    department = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    is_presenter = forms.ChoiceField(
        choices=[('', 'Select'), ('True', 'Yes'), ('False', 'No')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Are you a Presenter?"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
    )
    mobile_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = WorkshopVisitors
        fields = ['prefix_first_name', 'last_name', 'department', 
                 'is_presenter', 'email', 'mobile_number']

    def __init__(self, *args, **kwargs):
        workshop_id = kwargs.pop('workshop_id', None)
        super().__init__(*args, **kwargs)
        
        if workshop_id:
            workshop = Workshop.objects.get(id=workshop_id)
            if not workshop.is_designation_required:
                self.fields['designation_text'] = forms.CharField(
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    required=True,
                    label="Designation"
                )
            else:
                self.fields['designation'] = forms.ModelChoiceField(
                    queryset=Workshop_designations.objects.filter(workshop_id=workshop_id),
                    empty_label="Select Designation",
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    required=True
                )

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_tag = False
        self.helper.form_show_labels = True
        
        # Dynamically add designation field to layout
        form_rows = [
            Row(Column('prefix_first_name', css_class='form-group col-md-12 mb-3')),
            Row(Column('last_name', css_class='form-group col-md-12 mb-3')),
            Row(Column('designation' if 'designation' in self.fields else 'designation_text', 
                      css_class='form-group col-md-12 mb-3')),
            Row(Column('department', css_class='form-group col-md-12 mb-3')),
            Row(Column('is_presenter', css_class='form-group col-md-12 mb-3')),
            Row(Column('email', css_class='form-group col-md-12 mb-3')),
            Row(Column('mobile_number', css_class='form-group col-md-12 mb-3'))
        ]
        self.helper.layout = Layout(*form_rows)

    def save(self, commit=True):
        instance = super().save(commit=False)
        prefix, first_name = self.cleaned_data['prefix_first_name']
        instance.first_name = f"{prefix} {first_name}"
        instance.is_presenter = (self.cleaned_data['is_presenter'] == 'True')
        if 'designation_text' in self.cleaned_data:
            instance.designation_text = self.cleaned_data['designation_text']
        elif 'designation' in self.cleaned_data:
            instance.designation = self.cleaned_data['designation']
        
        if commit:
            instance.save()
        return instance

#add user form
class AddUserForm(ModelForm):
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_tag = False
    helper.form_show_labels = True

    class Meta:
        model = models.User
        fields = '__all__'
        exclude = ('is_admin','is_active', 'is_staff', 'is_superuser', 'account_made_at')

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field != "role":
                self.fields[field].widget.attrs.update({'class':"form-control form-control-user", 'required':True})
            
        sections = [
            Div(
                Row(
                    Column('first_name', css_class='form-group col-md-6'),
                    Column('last_name', css_class='form-group col-md-6'),

                ),
                Row(
                    Column('email', css_class='form-group col-md-6'),
                    Column('password', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('phone_number', css_class='form-group col-md-6'),
                    Column('designation', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('role', css_class='col-md-12'),
                ),
            )
        ]
        layout_rows = []
        field_names = [field_name for field_name in self.fields if field_name != 'done']
        row_fields = 3 
        for i in range(0, len(field_names), row_fields):
            columns = [Column(field, css_class='form-group col-md-12') for field in field_names[i:i + row_fields]]
            layout_rows.append(Row(*columns))
        self.helper.layout = Layout(*sections)
    
    def save(self, commit=True):

        user = super(AddUserForm, self).save(commit=False)

        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user

#edit User form
class EditUserForm(ModelForm):
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_tag = False
    helper.form_show_labels = True

    class Meta:
        model = models.User
        fields = '__all__'
        exclude = ('is_admin','is_active', 'is_staff', 'is_superuser', 'account_made_at', 'password')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field != "role":
                self.fields[field].widget.attrs.update({'class':"form-control form-control-user", 'required':True})

        sections = [
            Div(
                Row(
                    Column('first_name', css_class='form-group col-md-6'),
                    Column('last_name', css_class='form-group col-md-6'),

                ),
                Row(
                    Column('email', css_class='form-group col-md-6'),
                    Column('phone_number', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('role', css_class='col-md-6'),
                    Column('designation', css_class='form-group col-md-6'),
                )
            )
        ]
        self.helper.layout = Layout(*sections)
     
     
        
#WorkshopGroupsForm setting form
class WorkshopGroupsForm(ModelForm):
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_tag = False
    helper.form_show_labels = True

    class Meta:
        model = models.Workshop_groups
        fields = [
            "group_name",
            "tables"
        ]
        exclude = ('workshop_manager',)

    sections = [
            Div(
                Row(
                    Column('group_name', css_class='form-group col-md-4 mb-0 my-4'),
                    Column('tables', css_class='form-group col-md-8 mb-0 my-4'),
                )
            )
        ]

WorkshopGroupsFormSet = modelformset_factory(models.Workshop_groups, form=WorkshopGroupsForm)

#FeedBack Form
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = [
            'question_1_response', 
            'question_2_response', 
            'question_3_response', 
            'question_4_response', 
            'question_5_response', 
            'question_6_response', 
            'question_7_response', 
            'question_8_response', 
            'question_9_response'
        ]
        widgets = {
            'question_2_response': forms.HiddenInput(),
            'question_3_response': forms.HiddenInput(),
            'question_5_response': forms.HiddenInput(),
            'question_7_response': forms.HiddenInput(),
        }


#feedback question from
class FeedbackQuestionForm(forms.ModelForm):
    class Meta:
        model = FeedbackQuestion 
        fields = ['question_1', 'question_2', 'question_3', 'question_4', 'question_5', 
                  'question_6', 'question_7', 'question_8', 'question_9']
        widgets = {
            'question_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'question 1'}),
            'question_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'question 2'}),
            'question_3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'question 3'}),
            'question_4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'question 4'}),
            'question_5': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'question 5'}),
            'question_6': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'question 6'}),
            'question_7': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'question 7'}),
            'question_8': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'question 8'}),
            'question_9': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'question 9'}),
        }
