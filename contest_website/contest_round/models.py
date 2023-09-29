from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint

class SupportedLanguage(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=50)
    judge0_id = models.IntegerField(default=71)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_language = models.ForeignKey(
        SupportedLanguage, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username


class ContestRound(models.Model):
    round_label = models.CharField(max_length=250)
    round_duration = models.DurationField()
    has_started = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)

    def remaining_time(self):
        current_time = timezone.now()
        start_time = self.start_time
        duration = self.round_duration

        if self.has_started and start_time:
            remaining_seconds = max(
                0, (start_time + duration - current_time).total_seconds())
            return remaining_seconds
        else:
            return 0

    def __str__(self) -> str:
        return self.round_label


class Problem(models.Model):
    contest_round = models.ForeignKey(
        ContestRound, related_name="problems", on_delete=models.CASCADE)
    problem_name = models.CharField(max_length=600)
    content = RichTextUploadingField()

    def __str__(self):
        return self.problem_name


class UserResponse(models.Model):
    contest_round = models.ForeignKey(ContestRound, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    submission_time = models.TimeField(null=True)
    has_submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s response to '{self.problem.problem_name}'"
    class Meta:
        # Define a unique constraint to ensure one response per user per problem
        constraints = [
            UniqueConstraint(fields=['user', 'problem'], name='unique_user_response')
        ]


class UserResponsePoints(models.Model):
    user_response = models.ForeignKey(UserResponse, on_delete=models.CASCADE)
    marks = models.IntegerField()


class HomePageContent(models.Model):
    title = models.TextField(max_length=1000, default="Default Title")
    content = RichTextUploadingField()

    @classmethod
    def check_max_objects(cls):
        max_objects = 5  # Change this to your desired maximum limit
        if cls.objects.count() >= max_objects:
            raise ValidationError("Maximum number of objects reached.")

    def save(self, *args, **kwargs):
        self.check_max_objects()
        super().save(*args, **kwargs)
