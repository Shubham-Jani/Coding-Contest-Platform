"""
URL configuration for contest_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ckeditor_uploader import views as ckeditor_views
from contest_round.views import CustomLoginView, UserResponseSubmitView, LanguageSelectionView, check_round_started, SelectRound, ProblemSelectView, RunCodeView, RemainingTimeView, HomePageView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('ckeditor/upload/', ckeditor_views.upload, name='ckeditor_upload'),
    path('login/', CustomLoginView.as_view(), name='login'),

    # Add the URL pattern for the user response submission view
    path('submit_response/<int:contest_round_id>/<int:problem_id>/',
         UserResponseSubmitView.as_view(), name='submit_response'),
    path('language_selection/',
         LanguageSelectionView.as_view(), name='language_selection'),
    path('select_round/', SelectRound.as_view(), name='select_round'),
    path('<int:round_id>/problems/',
         ProblemSelectView.as_view(), name='problem_page'),
    path('check_round_started/', check_round_started,
         name='check_round_started'),
    path('run_code/', RunCodeView.as_view(), name='run_code'),
    path('_nested_admin/', include('nested_admin.urls')),
    path('remaining_time/<int:round_id>/',
         RemainingTimeView.as_view(), name='remaining_time'),
    path('', HomePageView.as_view(), name='home_page')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
