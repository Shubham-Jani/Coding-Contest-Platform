from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django_ace import AceWidget
from .forms import UserResponseForm, LanguageSelectionForm
from .models import (UserResponse, Problem, ContestRound, SupportedLanguage, UserProfile,
                      HomePageContent)
from django.urls import reverse
from django.http import HttpResponseNotAllowed,HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import requests
import time
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.contrib.auth import logout
import base64
import urllib.parse

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
            if user_response.problem_id in unsolved_problems and  user_response.has_submitted:
                unsolved_problems.discard(user_response.problem_id)
        return render(request, self.template_name, {"contest_round": selected_round, "round_problems": round_problems, "round_id": round_id,
                                                     "unsolved_problems": unsolved_problems, "has_round_started": has_round_started})

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

def logout_view(request):
    logout(request)
    return redirect("login")


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
        ace_mode = default_language
        if ace_mode == 'c' or ace_mode == 'cpp':
            ace_mode = 'c_cpp'
        form.fields['code'].widget.mode = ace_mode
        existing_response = UserResponse.objects.filter(
            contest_round=contest_round, problem=problem, user=request.user
            ).first()
        if existing_response and existing_response.has_submitted == False:
            form.initial['code'] = existing_response.code

        return render(request, self.template_name, {'contest_round': contest_round, 'problem': problem, 'form': form,
                                                    'selected_language': user_profile.default_language,
                                                    'selected_language_id': user_profile.default_language.judge0_id,
                                                    "has_round_started": has_round_started})

    def post(self, request, contest_round_id, problem_id):
        contest_round = get_object_or_404(ContestRound, pk=contest_round_id)
        problem = get_object_or_404(Problem, pk=problem_id)

        # Create a form instance with AceWidget for code input
        form = UserResponseForm(request.POST)

        if form.is_valid():
            existing_response = UserResponse.objects.filter(
            contest_round=contest_round, problem=problem, user=request.user
            ).first()
            if existing_response and existing_response.has_submitted:
                # If a response already exists, return an error message or redirect
                return HttpResponseBadRequest("<h1 style='color:red'>You have already submitted a response for this problem.</h1>")

            code = form.cleaned_data['code']
            current_time = time.strftime("%H:%M:%S")
            action = request.POST.get('action')
            # Try to get an existing UserResponse object
            existing_response, created = UserResponse.objects.get_or_create(
                contest_round=contest_round, problem=problem, user=request.user,
                defaults={'code': code, 'has_submitted': False if action == "save" else True, 'submission_time': current_time}
            )

            if not created:
                # If the object already exists, update its attributes
                existing_response.code = code
                existing_response.submission_time = current_time
                existing_response.has_submitted = False if action == "save" else True
                existing_response.save()
            return redirect('problem_page', contest_round_id)
        else:
            return render(request, self.template_name, {'contest_round': contest_round, 'problem': problem, 'form': form})
        
@method_decorator(login_required, name='dispatch')
def save_code_and_redirect(request,contest_round_id,problem_id):
    if request.method == 'POST':
        code = request.POST.get('user-code')
        print(code + "hello")
    return redirect('problem_page', contest_round_id)


def check_round_started(request):
    if request.is_ajax() and request.method == 'GET':
        round_id = request.GET.get('round_id')
        round = get_object_or_404(ContestRound, pk=round_id)
        return JsonResponse({'has_started': round.has_started})
    else:
        # Handle other cases as needed
        return JsonResponse({'has_started': False})
    
def decode(encoded_data):
    decoded_data = urllib.parse.unquote(encoded_data)
    decoded_bytes = base64.b64decode(decoded_data)
    return decoded_bytes.decode('utf-8')
@method_decorator(login_required, name='dispatch')
class RunCodeView(View):
    template_name = 'code_result.html'

    def post(self, request, *args, **kwargs):
        user_code = request.POST.get('code')
        user_profile = get_object_or_404(UserProfile, user=request.user)
        language_id = user_profile.default_language.judge0_id
        # Replace with the actual Judge0 API URL
        judge0_api_url = settings.JUDGE0_API_URL
        # Prepare the data to send to the Judge0 API
        # encoding code
        data = {
            'source_code': user_code,
            'language_id': language_id,
            'base64_encoded': True
        }
        # Make a POST request to the Judge0 API to submit the code
        response = requests.post(judge0_api_url, json=data)
        submission_token = response.json().get('token')
        print(f"submission token: {submission_token}")
        # Sleep for 5 seconds (adjust the duration as needed)
        while (True):
            code_output_url = f"{judge0_api_url}/{submission_token}?base64_encoded=true"
            time.sleep(2)
            code_output = requests.get(code_output_url)
            result = code_output.json()
            if result["status"]["description"] not in ["Processing", "In Queue"]:
                for key, value in result.items():
                    if isinstance(value, str):
                        try:
                            decoded_value = decode(value)
                            result[key] = decoded_value
                        except (TypeError, UnicodeDecodeError):
                            pass  # Skip decoding if it's not a valid Base64-encoded string
                break

        print(result)
        # Render the HTML template with the response data and return it
        return render(request, self.template_name, {'result': result})


class RemainingTimeView(View):
    template_name = 'remaining_time.html'

    def get(self, request, contest_round_id, *args, **kwargs):
        round = get_object_or_404(ContestRound, contest_round_id)
        return render(request, self.template_name, {'round': round})
@method_decorator(login_required, name='dispatch')
class GetFoulView(View):
    def get(self,request):
        current_foul_object = UserProfile.objects.get(user=request.user)
        return JsonResponse({"foul_count":current_foul_object.count})
@method_decorator(login_required, name='dispatch')
class IncrementFoulView(View):
    def post(self, request):
        try:
            current_foul_object = UserProfile.objects.get(user=request.user)
            current_foul_object.foul_count += 1
            current_foul_object.save()
            response_data = {
                'message': current_foul_object.foul_count,
            }
            return JsonResponse(response_data, status=200)
        except UserProfile.DoesNotExist:
            response_data = {
                'message': 'User profile not found.',
            }
            return JsonResponse(response_data, status=404)