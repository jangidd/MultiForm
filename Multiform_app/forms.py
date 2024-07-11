from django import forms
from .models.personal_info import PersonalInformation
from .models.educational_info import EducationalDetails
from .models.workexp_info import ExperienceDetails
from .models.achievement_info import AchievementDetails
from .models.banking_info import BankingDetails
from .models.reportingarea_info import ReportingAreaDetails
from .models.timeavailability_info import AvailabilityDetails
from .models.CallbackForm import Callback
from .models.choices import MRI_OPTIONS, CT_OPTIONS, TIME_OPTIONS



class CallbackForm(forms.ModelForm):
    class Meta:
        model = Callback
        fields = '__all__'

class PersonalInformationForm(forms.ModelForm):
    class Meta:
        model = PersonalInformation
        fields = '__all__'

class EducationalInfoForm(forms.ModelForm):
    class Meta:
        model = EducationalDetails
        fields = '__all__'

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = ExperienceDetails
        fields = '__all__'

class AchievementsInfoForm(forms.ModelForm):
    class Meta:
        model = AchievementDetails
        fields = '__all__'

class BankingDetailsForm(forms.ModelForm):
    class Meta:
        model = BankingDetails
        fields = '__all__'

class ReportingAreaForm(forms.ModelForm):
    mriopt = forms.MultipleChoiceField(choices=MRI_OPTIONS, widget=forms.CheckboxSelectMultiple)
    ctopt = forms.MultipleChoiceField(choices=CT_OPTIONS, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = ReportingAreaDetails
        fields = '__all__'

class TimeAvailabilityForm(forms.ModelForm):
    montime = forms.MultipleChoiceField(choices=TIME_OPTIONS, widget=forms.CheckboxSelectMultiple)
    tuetime = forms.MultipleChoiceField(choices=TIME_OPTIONS, widget=forms.CheckboxSelectMultiple)
    wedtime = forms.MultipleChoiceField(choices=TIME_OPTIONS, widget=forms.CheckboxSelectMultiple)
    thurstime = forms.MultipleChoiceField(choices=TIME_OPTIONS, widget=forms.CheckboxSelectMultiple)
    fritime = forms.MultipleChoiceField(choices=TIME_OPTIONS, widget=forms.CheckboxSelectMultiple)
    sattime = forms.MultipleChoiceField(choices=TIME_OPTIONS, widget=forms.CheckboxSelectMultiple)
    suntime = forms.MultipleChoiceField(choices=TIME_OPTIONS, widget=forms.CheckboxSelectMultiple)


    class Meta:
        model = AvailabilityDetails
        fields = '__all__'

