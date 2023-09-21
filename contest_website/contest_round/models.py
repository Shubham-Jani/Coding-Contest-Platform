from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
import datetime
from django.utils import timezone


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
    has_solved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s response to '{self.problem.problem_name}'"


class UserResponsePoints(models.Model):
    user_response = models.ForeignKey(UserResponse, on_delete=models.CASCADE)
    marks = models.IntegerField()
