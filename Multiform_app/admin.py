from django.contrib import admin
from .models.personal_info import PersonalInformation
from .models.educational_info import EducationalDetails
from .models.workexp_info import ExperienceDetails
from .models.achievement_info import AchievementDetails
from .models.banking_info import BankingDetails
from .models.reportingarea_info import ReportingAreaDetails
from .models.timeavailability_info import AvailabilityDetails
from .models.ratelist import RateList
from .models.CallbackForm import Callback

# Register your models here.
admin.site.register(PersonalInformation)
admin.site.register(EducationalDetails)
admin.site.register(ExperienceDetails)
admin.site.register(AchievementDetails)
admin.site.register(BankingDetails)
admin.site.register(ReportingAreaDetails)
admin.site.register(AvailabilityDetails)
admin.site.register(Callback)
admin.site.register(RateList)
