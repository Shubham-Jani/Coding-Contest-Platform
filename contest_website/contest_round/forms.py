from django import forms
from django_ace import AceWidget
from .models import SupportedLanguage
from .models import UserResponse


class LanguageSelectionForm(forms.Form):
    language = forms.ModelChoiceField(queryset=SupportedLanguage.objects.all())


class UserResponseForm(forms.Form):
    code = forms.CharField(widget=AceWidget(theme="twilight",
                                            width="100%",
                                            height="800px",
                                            fontsize="14pt",))
