from django.contrib import admin
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Problem, ContestRound, UserResponse, UserProfile, UserResponsePoints, HomePageContent
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from django_ace import AceWidget
from ace_overlay.widgets import AceOverlayWidget
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

admin.site.site_header = "Algorithm Arena Admin"
admin.site.site_title = "Aglorithm Arena"
admin.site.index_title = "Algorithm Arena"


class UserResponseResource(resources.ModelResource):
    user_username = fields.Field(
        column_name='username',
        attribute='user__username',
    )

    class Meta:
        model = UserResponse
        fields = ('user_username', 'contest_round__round_label','contest_round__start_time',
                  'contest_round__round_duration',
                   'problem__problem_name', 'code',
                    'submission_time', 'has_submitted')


class HomePageAdmin(admin.ModelAdmin):
    model = HomePageContent
    max_num = 1


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    max_num = 1
    readonly_fields = ["default_language","foul_count"]

class ResponsePointInline(admin.StackedInline):
    model = UserResponsePoints
    extra = 0
class UserResponseForm(forms.ModelForm):
    class Meta:
        model = UserResponse
        fields = '__all__'
        widgets = {
            'code': AceOverlayWidget(
                wordwrap=False,
                theme="terminal",
                width="full",
                height="85vh",
                attrs={'class': 'custom-ace-widget'},
            )
        }


class UserResponseInline(admin.StackedInline):
    model = UserResponse
    form = UserResponseForm
    extra = 0  # Set this to 0 to prevent the inline form from being added automatically

    # Define a custom method to format the time
    def get_form(self, request, obj=None, **kwargs):
        # Check if the user has view-only permissions (change this condition as needed)
        if not request.user.has_perm('auth.change_user'):
            return UserResponseForm
        return super().get_form(request, obj, **kwargs)
    
    def formatted_submission_time(self, obj):
        # Assuming obj.submission_time is a datetime field
        return obj.submission_time.strftime('%Y-%m-%d %H:%M:%S')

    formatted_submission_time.short_description = 'Formatted Submission Time'  # Customize the column header

    list_display = ['user', 'problem', 'formatted_submission_time']  # Include the formatted time in the list_display
    readonly_fields = ['user', 'contest_round', 'problem', 'formatted_submission_time', 'has_submitted']

# Create a custom admin class for the User model


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline, UserResponseInline]
    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     extra_context = extra_context or {}
    #     extra_context['show_save'] = False  # Disable the "Save" button
    #     extra_context['show_save_and_add_another'] = False  # Disable "Save and add another" button
    #     extra_context['show_save_and_continue'] = False  # Disable "Save and continue editing" button
    #     return super().change_view(request, object_id, form_url, extra_context=extra_context)



class ProblemAdminForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = '__all__'
        widgets = {
            'content': CKEditorUploadingWidget(),
        }


class ProblemStackedInline(admin.StackedInline):
    model = Problem
    form = ProblemAdminForm  # Use the custom form

    extra = 0  # Number of empty forms to display for adding problems


class ContestRoundAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Round Information', {
            'fields': ('round_label', 'round_duration', 'has_started', 'start_time'),
        }),
    )
    readonly_fields = ('has_started', 'start_time')
    list_display = ('round_label', 'round_duration')

    actions = ['start_event', 'stop_event']  # Define actions only once
    inlines = [ProblemStackedInline]

    def start_event(self, request, queryset):
        current_time = timezone.now()
        start_time = current_time
        # Your custom logic to start the event (e.g., set has_started to True)
        queryset.update(has_started=True, start_time=start_time)
        self.message_user(request, "Contest event started successfully.")

    def stop_event(self, request, queryset):
        # Your custom logic to stop the event (e.g., set has_started to False)
        queryset.update(has_started=False, start_time=None)
        self.message_user(request, "Contest event stopped successfully.")

    # Customize the labels for the actions
    start_event.short_description = "Start selected contest events"
    stop_event.short_description = "Stop selected contest events"


class ResponsePointsAdmin(admin.ModelAdmin):
    class Meta:
        model = UserResponse
    inlines = [ResponsePointInline]

class UserResponseAdmin(ImportExportModelAdmin):
    resource_classes = [UserResponseResource]
    list_display = ['user', 'problem', 'formatted_submission_time']
    readonly_fields = ['user', 'contest_round', 'problem', 'formatted_submission_time', 'has_submitted']
    form = UserResponseForm
    model = UserResponse
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False  # Disable the "Save" button
        extra_context['show_save_and_add_another'] = False  # Disable "Save and add another" button
        extra_context['show_save_and_continue'] = False  # Disable "Save and continue editing" button
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def formatted_submission_time(self, obj):
        # Assuming obj.submission_time is a datetime field
        return obj.submission_time.strftime('%H:%M:%S')

    formatted_submission_time.short_description = 'Submission Time'  # Customize the column header

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ContestRound, ContestRoundAdmin)
admin.site.register(HomePageContent, HomePageAdmin)
admin.site.register(UserResponse, UserResponseAdmin)
# admin.site.register(ResponsePointsAdmin)
