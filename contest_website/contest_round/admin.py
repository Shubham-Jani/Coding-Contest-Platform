from django.contrib import admin
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Problem, ContestRound, UserResponse, UserProfile, UserResponsePoints
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    max_num = 1
    readonly_fields = ["default_language"]


class ResponsePointInline(admin.StackedInline):
    model = UserResponsePoints
    extra = 0


class UserResponseInline(admin.StackedInline):
    model = UserResponse
    extra = 0  # Set this to 0 to prevent the inline form from being added automatically
    inlines = [ResponsePointInline]
    readonly_fields = ["code", "submission_time",
                       "contest_round", "has_solved", "problem"]

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
# admin.site.register(ResponsePointsAdmin)
