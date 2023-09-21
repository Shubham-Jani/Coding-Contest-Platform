from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django_ace import AceWidget
from .forms import UserResponseForm, LanguageSelectionForm
from .models import UserResponse, Problem, ContestRound, SupportedLanguage, UserProfile, HomePageContent
from django.urls import reverse
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import requests
import time
from django.conf import settings


class HomePageView(View):
    template_name = "home_page.html"

    def get(self, request):
        content = HomePageContent.objects.first()
        return render(request, self.template_name, {"homepage": content})


@method_decorator(login_required, name='dispatch')
class ProblemSelectView(View):
    template_name = "problem_selection.html"

    def get(self, request, round_id):
        selected_round = get_object_or_404(ContestRound, pk=round_id)
        round_problems = Problem.objects.filter(contest_round=selected_round)
        has_round_started = selected_round.has_started
        user_responses = UserResponse.objects.filter(
            contest_round=selected_round, user=request.user)

        # Create a dictionary to store whether each problem is solved by the user
        unsolved_problems = {problem.id for problem in round_problems}

        # Check if the user has submitted responses for each problem
        for user_response in user_responses:
            if user_response.problem_id in unsolved_problems:
                unsolved_problems.discard(user_response.problem_id)
        print(type(unsolved_problems))
        return render(request, self.template_name, {"contest_round": selected_round, "round_problems": round_problems, "round_id": round_id, "unsolved_problems": unsolved_problems, "has_round_started": has_round_started})

    def post(self, request):
        # If a POST request is not allowed for this view, respond with a 405 Method Not Allowed error
        return HttpResponseNotAllowed(['GET'])


@method_decorator(login_required, name="dispatch")
class SelectRound(View):
    template_name = "round_selection.html"

    def get(self, request):
        rounds = ContestRound.objects.all().order_by('pk')
        return render(request, self.template_name, {'rounds': rounds})

    def post(self, request):
        # If a POST request is not allowed for this view, respond with a 405 Method Not Allowed error
        return HttpResponseNotAllowed(['GET'])


class CustomLoginView(LoginView):
    template_name = 'login.html'  # Replace 'login.html' with your login template
    success_url = "language_selection"


@method_decorator(login_required, name="dispatch")
class LanguageSelectionView(View):
    template_name = 'language_selection.html'

    def get(self, request):
        form = LanguageSelectionForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LanguageSelectionForm(request.POST)

        if form.is_valid():
            # Store the selected language in the user's profile
            user_profile, created = UserProfile.objects.get_or_create(
                user=request.user)
            user_profile.default_language = form.cleaned_data['language']
            user_profile.save()

            # Redirect to the start of the coding round
            return redirect('select_round')

        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class UserResponseSubmitView(View):
    template_name = 'submit_response.html'

    def get(self, request, contest_round_id, problem_id):
        user_profile = UserProfile.objects.get(user=request.user)
        default_language = user_profile.default_language.identifier if user_profile.default_language else 'python'

        contest_round = get_object_or_404(ContestRound, pk=contest_round_id)
        has_round_started = contest_round.has_started
        problem = get_object_or_404(Problem, pk=problem_id)

        # Create a form instance with AceWidget for code input
        form = UserResponseForm()

        # Set the mode parameter for the AceWidget based on the user's default language
        form.fields['code'].widget.mode = default_language

        return render(request, self.template_name, {'contest_round': contest_round, 'problem': problem, 'form': form, 'selected_language': user_profile.default_language, 'selected_language_id': user_profile.default_language.judge0_id, "has_round_started": has_round_started})

    def post(self, request, contest_round_id, problem_id):
        contest_round = get_object_or_404(ContestRound, pk=contest_round_id)
        problem = get_object_or_404(Problem, pk=problem_id)

        # Create a form instance with AceWidget for code input
        form = UserResponseForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']
            current_time = time.strftime("%H:%M:%S")
            UserResponse.objects.create(
                contest_round=contest_round, problem=problem, user=request.user, code=code, has_solved=True, submission_time=current_time)
            # Add additional logic here, e.g., checking the submission

            return redirect('problem_page', contest_round_id)
        else:
            return render(request, self.template_name, {'contest_round': contest_round, 'problem': problem, 'form': form})


def check_round_started(request):
    if request.is_ajax() and request.method == 'GET':
        round_id = request.GET.get('round_id')
        round = get_object_or_404(ContestRound, pk=round_id)
        return JsonResponse({'has_started': round.has_started})
    else:
        # Handle other cases as needed
        return JsonResponse({'has_started': False})

# running code (experimental)


class RunCodeView(View):
    template_name = 'code_result.html'

    def post(self, request, *args, **kwargs):
        user_code = request.POST.get('code')
        user_profile = get_object_or_404(UserProfile, user=request.user)
        language_id = user_profile.default_language.judge0_id
        # Replace with the actual Judge0 API URL
        judge0_api_url = settings.JUDGE0_API_URL
        print(user_code)
        # Prepare the data to send to the Judge0 API
        data = {
            'source_code': user_code,
            'language_id': language_id
        }
        # Make a POST request to the Judge0 API to submit the code
        response = requests.post(judge0_api_url, json=data)
        submission_token = response.json().get('token')
        # Sleep for 5 seconds (adjust the duration as needed)
        while (True):
            code_output_url = f"{judge0_api_url}/{submission_token}"
            time.sleep(2)
            code_output = requests.get(code_output_url)
            result = code_output.json()
            if (result["status"]["description"] != "Processing" != "In Queue"):
                break
        # Render the HTML template with the response data and return it
        return render(request, self.template_name, {'result': result})


class RemainingTimeView(View):
    template_name = 'remaining_time.html'

    def get(self, request, contest_round_id, *args, **kwargs):
        round = get_object_or_404(ContestRound, contest_round_id)
        return render(request, self.template_name, {'round': round})
