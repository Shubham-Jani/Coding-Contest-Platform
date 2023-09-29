from django.contrib import admin
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Problem, ContestRound, UserResponse, UserProfile, UserResponsePoints, HomePageContent
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from django_ace import AceWidget
from ace_overlay.widgets import AceOverlayWidget

admin.site.site_header = "Algorithm Arena Admin"
admin.site.site_title = "Aglorithm Arena"
admin.site.index_title = "Algorithm Arena"


class HomePageAdmin(admin.ModelAdmin):
    model = HomePageContent
    max_num = 1


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    max_num = 1
    readonly_fields = ["default_language"]

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set all form fields to be disabled
        for field_name, field in self.fields.items():
            field.widget.attrs['disabled'] = 'disabled'
        # Access the currently edited user object through 'instance'
        user_response = kwargs.get('instance')
        if user_response:
            # Access the user related to this user response
            user = user_response.user
            # Access the user's profile
            try:
                user_profile = UserProfile.objects.get(user=user)
                # Determine the language mode from the user's profile
                default_language = user_profile.default_language.identifier if user_profile.default_language else 'python'
                # Set the mode parameter for the AceWidget based on the 'default_language'
                self.fields['code'].widget.mode = default_language
            except UserProfile.DoesNotExist:
                # Handle the case where the user doesn't have a profile or the profile is not set
                pass
class UserResponseInline(admin.StackedInline):
    model = UserResponse
    form = UserResponseForm 
    extra = 0  # Set this to 0 to prevent the inline form from being added automatically
    list_display = ['user', 'problem', 'submission_time']
    readonly_fields = ['user','contest_round','problem','submission_time','has_submitted']
# Create a custom admin class for the User model


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline, UserResponseInline]


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


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ContestRound, ContestRoundAdmin)
admin.site.register(HomePageContent, HomePageAdmin)
# admin.site.register(ResponsePointsAdmin)
