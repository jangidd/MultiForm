import io
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponse
from django.contrib.auth import login as contrib_login, authenticate
from django.contrib.auth.models import Group
from django.db import transaction
from datetime import datetime
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .forms import CallbackForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models.choices import MRI_OPTIONS, CT_OPTIONS, TIME_OPTIONS
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.template.loader import render_to_string, get_template
from django.conf import settings
from datetime import date
# from .views import generate_pdf as generate_pdf_view

 

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import blue, black
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph
from .models.ratelist import RateList

from .models import PersonalInformation, EducationalDetails, ExperienceDetails, AchievementDetails, BankingDetails, ReportingAreaDetails, AvailabilityDetails

# logging.basicConfig(
#     level=logging.DEBUG,  # Set the logging level to DEBUG or INFO
#     format='%(asctime)s - %(levelname)s - %(message)s',
# )

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            contrib_login(request, user)
            groups = user.groups.values_list('name', flat=True)
            if 'radiologist' in groups:
                return redirect('work')
            elif 'supercoordinator' in groups:
                return redirect('coordinator')
            elif 'coordinator' in groups:
                return redirect('coordinator')
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        else:
            try:
                personal_info = PersonalInformation.objects.get(email=email)
                if personal_info.stage2status == 'under_progress':
                    return render(request, 'pending.html')
                elif personal_info.stage2status == 'applied':
                    return render(request, 'pending.html')
                elif personal_info.stage2status == 'verification_failed':
                    return render(request, 'pending.html')
                elif personal_info.stage2status == 'verified_by_supercoordinator':
                    # Redirect to a different page, e.g., home page
                    return redirect('work')
                else:
                    return render(request, 'login.html', {'error': 'Invalid credentials'})
            except PersonalInformation.DoesNotExist:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

# Some extra view functions to handle different redirections.

def registration_pending(request, pk):
    personal_info = get_object_or_404(PersonalInformation, pk=pk)
    context = {
        'personal_info': personal_info,
    }
    return render(request, 'pending.html', context)

@login_required
def dashboard(request):
    user = request.user
    groups = user.groups.values_list('name', flat=True)
    context = {
        'user': user,
        'groups': groups,
    }
    return render(request, 'dashboard.html', context)

@login_required
def coordinator_dashboard(request):
    # Logic specific to coordinator dashboard
    return render(request, 'coordinator_dashboard.html')

@login_required
def supercoordinator_dashboard(request):
    # Logic specific to supercoordinator dashboard
    return render(request, 'supercoordinator_dashboard.html')

@login_required
def coordinator_dashboard(request):
    # Logic specific to coordinator dashboard
    return render(request, 'coordinator.html')

# End of extra view functions.

# This below view is for handling the logic of the callback page and redirecting it to a submission page.
def callback_form_view(request):
    if request.method == 'POST':
        form = CallbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('callback_complete')
    else:
        form = CallbackForm()
    return render(request, 'callback_form.html', {'form': form})

def callback_complete_view(request):
    return render(request, 'callback_complete.html')

def work(request):
    return render(request, 'work.html')

def index(request):
    return render(request, 'multiform.html')

# The below view is form showing the callback form on the coordinator's dashboard.
# (Don't get confused in the above and below view.)

def view_callback_form(request):
    user_id = request.GET.get('user_id')
    try:
        callback_form = CallbackForm.objects.get(user_id=user_id)
        return render(request, 'callback_form_details.html', {'callback_form': callback_form})
    except CallbackForm.DoesNotExist:
        return JsonResponse({'message': "User didn't fill any callback form"}, status=404)

# The logic to handle the coordinator page.

@login_required
def coordinator(request):
    personal_info = PersonalInformation.objects.all().order_by('first_name')
    
    # Check if the user belongs to the 'supercoordinator' group
    is_supercoordinator = request.user.groups.filter(name='supercoordinator').exists()
    
    context = {
        'personal_info': personal_info,
        'is_supercoordinator': is_supercoordinator
    }
    return render(request, 'coordinator.html', context)     

# End of the coordinator logic.

@csrf_exempt
def check_email_existence(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print('Email received:', email)  # Debugging log
        if email:
            exists_in_personal_info = PersonalInformation.objects.filter(email=email).exists()
            exists_in_users = User.objects.filter(email=email).exists()
            exists = exists_in_personal_info or exists_in_users
            return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})

def step1(request):
    if request.method == 'POST':
        request.session['first_name'] = request.POST.get('first_name', '')
        request.session['last_name'] = request.POST.get('last_name', '')
        request.session['email'] = request.POST.get('email', '')
        request.session['password'] = request.POST.get('password', '')
        request.session['cnfpassword'] = request.POST.get('cnfpassword', '')
        request.session['address'] = request.POST.get('address', '')
        request.session['contact_no'] = request.POST.get('contact_no', '')
        request.session['experience_years'] = request.POST.get('experience_years', '')
        request.session['resume'] = request.FILES.get('resume', '')
        request.session['photo'] = request.FILES.get('photo', '')
        return redirect('step2')
    return render(request, 'step1.html')

def step2(request):
    if request.method == 'POST':
        request.session['tenthname'] = request.POST.get('tenthname', '')
        request.session['tenthgrade'] = request.POST.get('tenthgrade', '')
        request.session['tenthpsyr'] = request.POST.get('tenthpsyr', '')
        request.session['tenthcertificate'] = request.FILES.get('tenthcertificate', '')
        request.session['twelthname'] = request.POST.get('twelthname', '')
        request.session['twelthgrade'] = request.POST.get('twelthgrade', '')
        request.session['twelthpsyr'] = request.POST.get('twelthpsyr', '')
        request.session['twelthcertificate'] = request.FILES.get('twelthcertificate', '')
        request.session['mbbsinstitution'] = request.POST.get('mbbsinstitution', '')
        request.session['mbbsgrade'] = request.POST.get('mbbsgrade', '')
        request.session['mbbspsyr'] = request.POST.get('mbbspsyr', '')
        request.session['mbbsmarksheet'] = request.FILES.get('mbbsmarksheet', '')
        request.session['mbbsdegree'] = request.FILES.get('mbbsdegree', '')
        request.session['mdinstitution'] = request.POST.get('mdinstitution', '')
        request.session['mdgrade'] = request.POST.get('mdgrade', '')
        request.session['mdpsyr'] = request.POST.get('mdpsyr', '')
        request.session['mdmarksheet'] = request.FILES.get('mdmarksheet', '')
        request.session['mddegree'] = request.FILES.get('mddegree', '')
        request.session['videofile'] = request.FILES.get('videofile', '')
        return redirect('step3')
    return render(request, 'step2.html')

def step3(request):
    if request.method == 'POST':
        request.session['exinstitution1'] = request.POST.get('exinstitution1', '')
        request.session['exstdate1'] = request.POST.get('exstdate1', '')
        request.session['exenddate1'] = request.POST.get('exenddate1', '')
        request.session['exinstitution2'] = request.POST.get('exinstitution2', '')
        request.session['exstdate2'] = request.POST.get('exstdate2', '')
        request.session['exenddate2'] = request.POST.get('exenddate2', '')
        request.session['exinstitution3'] = request.POST.get('exinstitution3', '')
        request.session['exstdate3'] = request.POST.get('exstdate3', '')
        request.session['exenddate3'] = request.POST.get('exenddate3', '')
        return redirect('step4')
    return render(request, 'step3.html')

def step4(request):
    if request.method == 'POST':
        request.session['award1'] = request.POST.get('award1', '')
        request.session['awarddate1'] = request.POST.get('awarddate1', '')
        request.session['award2'] = request.POST.get('award2', '')
        request.session['awarddate2'] = request.POST.get('awarddate2', '')
        request.session['publishlink'] = request.POST.get('publishlink', '')
        return redirect('step5')
    return render(request, 'step4.html')

def step5(request):
    if request.method == 'POST':
        request.session['accholdername'] = request.POST.get('accholdername', '')
        request.session['bankname'] = request.POST.get('bankname', '')
        request.session['branchname'] = request.POST.get('branchname', '')
        request.session['acnumber'] = request.POST.get('acnumber', '')
        request.session['ifsc'] = request.POST.get('ifsc', '')
        request.session['pancardno'] = request.POST.get('pancardno', '')
        request.session['aadharcardno'] = request.POST.get('aadharcardno', '')
        request.session['pancard'] = request.FILES.get('pancard', '')
        request.session['aadharcard'] = request.FILES.get('aadharcard', '')
        request.session['cheque'] = request.FILES.get('cheque', '')
        return redirect('step6')
    return render(request, 'step5.html')

def step6(request):
    if request.method == 'POST':
        request.session['mriopt'] = request.POST.get('mriopt', '')
        request.session['mriothers'] = request.POST.get('mriothers', '')
        request.session['ctopt'] = request.POST.get('ctopt', '')
        request.session['ctothers'] = request.POST.get('ctothers', '')
        request.session['xray'] = request.POST.get('xray', '')
        request.session['others'] = request.POST.get('others', '')
        return redirect('step7')
    return render(request, 'step6.html')

def step7(request):
    if request.method == 'POST':
        request.session['monday'] = request.POST.get('monday', '')
        request.session['tuesday'] = request.POST.get('tuesday', '')
        request.session['wednesday'] = request.POST.get('wednesday', '')
        request.session['thursday'] = request.POST.get('thursday', '')
        request.session['friday'] = request.POST.get('friday', '')
        request.session['saturday'] = request.POST.get('saturday', '')
        request.session['sunday'] = request.POST.get('sunday', '')
        request.session['starttime1'] = request.POST.get('starttime1', '')
        request.session['endtime1'] = request.POST.get('endtime1', '')
        request.session['starttime2'] = request.POST.get('starttime2', '')
        request.session['endtime2'] = request.POST.get('endtime2', '')
        request.session['starttime3'] = request.POST.get('starttime3', '')
        request.session['endtime3'] = request.POST.get('endtime3', '')
        request.session['starttime4'] = request.POST.get('starttime4', '')
        request.session['endtime4'] = request.POST.get('endtime4', '')
        return redirect('submit')
    return render(request, 'step7.html')

def submit(request):
    if request.method == 'POST':
        try:
            # Extract and format date fields
            tenthpsyr = parse_date(request.POST.get('tenthpsyr', ''))
            twelthpsyr = parse_date(request.POST.get('twelthpsyr', ''))
            mbbspsyr = parse_date(request.POST.get('mbbspsyr', ''))
            mdpsyr = parse_date(request.POST.get('mdpsyr', ''))
            awarddate1 = parsing_date(request.POST.get('awarddate1', ''))
            awarddate2 = parsing_date(request.POST.get('awarddate2', ''))

           # Helper function to get a list of selected options' names
            def get_selected_options_names(field_name):
                options = request.POST.getlist(field_name)
                return options




             # Create or update PersonalInformation instance
            email = request.POST.get('email', '')
            if 'update_existing' in request.POST:
                user = User.objects.get(email=email)
                personal_info = user.personalinformation
                # Update personal_info fields here if needed
            else:
                personal_info = PersonalInformation.objects.create(
                    first_name=request.POST.get('first_name', ''),
                    last_name=request.POST.get('last_name', ''),
                    email=email,
                    password=request.POST.get('password', ''),
                    cnfpassword=request.POST.get('cnfpassword', ''),
                    address=request.POST.get('address', ''),
                    contact_no=request.POST.get('contact_no', ''),
                    experience_years=int(request.POST.get('experience_years', 0)),
                    resume=request.FILES.get('resume', ''),
                    photo=request.FILES.get('photo', '')
                )

            # Create EducationalDetails instance
            educational_info = EducationalDetails.objects.create(
                tenthname=request.POST.get('tenthname', ''),
                tenthgrade=request.POST.get('tenthgrade', ''),
                tenthpsyr=tenthpsyr,
                tenthcertificate=request.FILES.get('tenthcertificate', ''),
                twelthname=request.POST.get('twelthname', ''),
                twelthgrade=request.POST.get('twelthgrade', ''),
                twelthpsyr=twelthpsyr,
                twelthcertificate=request.FILES.get('twelthcertificate', ''),
                mbbsinstitution=request.POST.get('mbbsinstitution', ''),
                mbbsgrade=request.POST.get('mbbsgrade', ''),
                mbbspsyr=mbbspsyr,
                mbbsmarksheet=request.FILES.get('mbbsmarksheet', ''),
                mbbsdegree=request.FILES.get('mbbsdegree', ''),
                mdinstitution=request.POST.get('mdinstitution', ''),
                mdgrade=request.POST.get('mdgrade', ''),
                mdpsyr=mdpsyr,
                mdmarksheet=request.FILES.get('mdmarksheet', ''),
                mddegree=request.FILES.get('mddegree', ''),
                videofile=request.FILES.get('videofile', ''),
                personal_information=personal_info
            )

            # Create ExperienceDetails instance
            experience_info = ExperienceDetails.objects.create(
                exinstitution1=request.POST.get('exinstitution1', ''),
                exstdate1=parse_date(request.POST.get('exstdate1', '')),
                exenddate1=parse_date(request.POST.get('exenddate1', '')),
                exinstitution2=request.POST.get('exinstitution2', ''),
                exstdate2=parse_date(request.POST.get('exstdate2', '')),
                exenddate2=parse_date(request.POST.get('exenddate2', '')),
                exinstitution3=request.POST.get('exinstitution3', ''),
                exstdate3=parse_date(request.POST.get('exstdate3', '')),
                exenddate3=parse_date(request.POST.get('exenddate3', '')),
                personal_information=personal_info
            )

            # Create AchievementDetails instance
            achievement_info = AchievementDetails.objects.create(
                award1=request.POST.get('award1', ''),
                awarddate1=awarddate1,
                award2=request.POST.get('award2', ''),
                awarddate2=awarddate2,
                publishlink=request.POST.get('publishlink', ''),
                personal_information=personal_info
            )

            # Create BankingDetails instance
            banking_info = BankingDetails.objects.create(
                accholdername=request.POST.get('accholdername', ''),
                bankname=request.POST.get('bankname', ''),
                branchname=request.POST.get('branchname', ''),
                acnumber=request.POST.get('acnumber', ''),
                ifsc=request.POST.get('ifsc', ''),
                pancardno=request.POST.get('pancardno', ''),
                aadharcardno=request.POST.get('aadharcardno', ''),
                pancard=request.FILES.get('pancard', ''),
                aadharcard=request.FILES.get('aadharcard', ''),
                cheque=request.FILES.get('cheque', ''),
                personal_information=personal_info
            )

            # Create AvailabilityDetails instance
            availability_info = AvailabilityDetails.objects.create(
                monday=bool(request.POST.get('monday', False)),
                tuesday=bool(request.POST.get('tuesday', False)),
                wednesday=bool(request.POST.get('wednesday', False)),
                thursday=bool(request.POST.get('thursday', False)),
                friday=bool(request.POST.get('friday', False)),
                saturday=bool(request.POST.get('saturday', False)),
                sunday=bool(request.POST.get('sunday', False)),
                starttime1=request.POST.get('starttime1', ''),
                endtime1=request.POST.get('endtime1', ''),
                starttime2=request.POST.get('starttime2', ''),
                endtime2=request.POST.get('endtime2', ''),
                starttime3=request.POST.get('starttime3', ''),
                endtime3=request.POST.get('endtime3', ''),
                starttime4=request.POST.get('starttime4', ''),
                endtime4=request.POST.get('endtime4', ''),
                personal_information=personal_info
            )

            # Create ReportingAreaDetails instance
            reporting_area_info = ReportingAreaDetails.objects.create(
                mriopt=', '.join(get_selected_options_names('mriopt')),
                mriothers=request.POST.get('mriothers', ''),
                ctopt=', '.join(get_selected_options_names('ctopt')),
                ctothers=request.POST.get('ctothers', ''),
                xray=bool(request.POST.get('xray', False)),
                others=bool(request.POST.get('others', False)),
                otherText=request.POST.get('otherText', ''),
                personal_information=personal_info
            )

            # Create Rate List Instance 
            rate_list = RateList.objects.create(
                mri1=int(request.POST.get('mri1', 200)),
                mri2=int(request.POST.get('mri2', 100)),
                mri3=int(request.POST.get('mri3', 250)),
                mri4=int(request.POST.get('mri4', 250)),
                mri5=int(request.POST.get('mri5', 300)),
                mri6=int(request.POST.get('mri6', 300)),
                ct1=int(request.POST.get('ct1', 150)),
                ct2=int(request.POST.get('ct2', 150)),
                ct3=int(request.POST.get('ct3', 150)),
                ct4=int(request.POST.get('ct4', 200)),
                ct5=int(request.POST.get('ct5', 225)),
                ct6=int(request.POST.get('ct6', 200)),
                ct7=int(request.POST.get('ct7', 500)),
                xray1=int(request.POST.get('xray1', 20)),
                xray2=int(request.POST.get('xray2', 75)),
                radiologist=personal_info
            )

            # Continue creating other model instances as needed

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")

        # Clear session data after successful submission
        request.session.flush()

        # return HttpResponse("Data saved successfully.")
        return redirect('success', pk=personal_info.pk)

    return render(request, 'submit.html')

# View function to redirect to the success page.
def success(request, pk):
    personal_info = get_object_or_404(PersonalInformation, pk=pk)
    
    context = {
        'first_name': personal_info.first_name,
        'last_name': personal_info.last_name,
        'personal_info': personal_info,
        'personal_info_pk': personal_info.pk,  # Pass the personal_info pk for linking back
    }
    return render(request, 'success.html', context)

# This is the view for the rate list .
def rate_list(request, radiologist_id):
    radiologist = get_object_or_404(PersonalInformation, pk=radiologist_id)
    rate_list = get_object_or_404(RateList, radiologist=radiologist)
    return render(request, 'rate_list.html', {'rate_list': rate_list, 'radiologist': radiologist})

def update_status_rate_list(request):
    if request.method == 'POST':
        rate_list_id = request.POST.get('rate_list_id')
        status = request.POST.get('status')
        rate_list = get_object_or_404(RateList, id=rate_list_id)
        rate_list.status = status
        rate_list.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

# View function to render the view response on the success page.
def view_response(request, pk):
    # Replace 1 with the appropriate ID of the saved form data
    personal_info = get_object_or_404(PersonalInformation, pk=pk)
    educational_info = get_object_or_404(EducationalDetails, personal_information=personal_info)
    experience_info = get_object_or_404(ExperienceDetails, personal_information=personal_info)
    achievement_info = get_object_or_404(AchievementDetails, personal_information=personal_info)
    banking_info = get_object_or_404(BankingDetails, personal_information=personal_info)
    availability_info = get_object_or_404(AvailabilityDetails, personal_information=personal_info)
    reporting_area_info = get_object_or_404(ReportingAreaDetails, personal_information=personal_info)

    context = {
        'personal_info': personal_info,
        'educational_info': educational_info,
        'experience_info': experience_info,
        'achievement_info': achievement_info,
        'banking_info': banking_info,
        'availability_info': availability_info,
        'reporting_area_info': reporting_area_info
    }

    return render(request, 'view_response.html', context)

def parse_date(date_string):
    if date_string:
        try:
            return datetime.strptime(date_string + '-01', '%Y-%m-%d')
        except ValueError:
            # Handle invalid date format here
            return None
    return None

def parsing_date(date_string):
    if date_string:
        try:
            return datetime.strptime(date_string , '%Y-%m-%d')
        except ValueError:
            # Handle invalid date format here
            return None
    return None

@require_POST
@csrf_exempt
def update_stage1status(request, pk):
    try:
        data = PersonalInformation.objects.get(pk=pk)
        stage1status = request.POST.get('stage1status')
        data.stage1status = stage1status
        data.save()
        return JsonResponse({'status': 'success'})
    except PersonalInformation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Data not found'}, status=404)

@require_POST
@csrf_exempt
def update_stage2status(request, pk):
    try:
        data = PersonalInformation.objects.get(pk=pk)
        stage2status = request.POST.get('stage2status')
        data.stage2status = stage2status
        data.save()
        return JsonResponse({'status': 'success'})
    except PersonalInformation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Data not found'}, status=404)
# def register_user(request):
#     if request.method == 'POST':
#         # Process form data to create a new user
#         # Example: Assuming form data is POSTed to this view
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         # Fetch other necessary fields

#         # Check if user already exists based on email or other unique identifier
#         # Example: Check if user with email already exists
#         if PersonalInformation.objects.filter(email=email).exists():
#             return redirect('/registration_error/')  # Redirect to error page if user already exists

#         # Assuming status is 'under_progress' by default for new registrations
#         new_user = PersonalInformation.objects.create(
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#             # Populate other fields as needed
#             status='under_progress'  # Default status for new registrations
#         )

#         # Redirect logic based on status
#         if new_user.status == 'under_progress':
#             return redirect('/registration_pending/')  # Redirect to pending registration page

#         return redirect('/registration_success/')  # Redirect to success page after registration

#     return render(request, 'registration_form.html')
@login_required
def view_complete_form(request, pk):
    try:
        # Fetch all related model instances using the primary key
        personal_information = get_object_or_404(PersonalInformation, pk=pk)
        educational_info = get_object_or_404(EducationalDetails, personal_information=personal_information)
        experience_info = get_object_or_404(ExperienceDetails, personal_information=personal_information)
        achievement_info = get_object_or_404(AchievementDetails, personal_information=personal_information)
        banking_info = get_object_or_404(BankingDetails, personal_information=personal_information)
        reporting_area_info = get_object_or_404(ReportingAreaDetails, personal_information=personal_information)
        availability_info = get_object_or_404(AvailabilityDetails, personal_information=personal_information)

        # pdf_url = generate_pdf(personal_information, educational_info, experience_info, achievement_info, banking_info, reporting_area_info, availability_info)

        # Constructing the response data as JSON
        response = {
            'personal_information': {
                'first_name': personal_information.first_name,
                'last_name': personal_information.last_name,
                'email': personal_information.email,
                'password': personal_information.password,
                'address': personal_information.address,
                'contact_no': personal_information.contact_no,
                'resume': request.build_absolute_uri(personal_information.resume.url) if personal_information.resume else None,
                'photo': request.build_absolute_uri(personal_information.photo.url) if personal_information.photo else None,
                'experience_years': personal_information.experience_years,
                # Add more fields as needed
            },
            'educational_info': {
                'tenthname': educational_info.tenthname,
                'tenthgrade': educational_info.tenthgrade,
                'tenthpsyr': educational_info.tenthpsyr,
                'tenthcertificate': request.build_absolute_uri(educational_info.tenthcertificate.url) if educational_info.tenthcertificate else None,
                'twelthname': educational_info.twelthname,
                'twelthgrade': educational_info.twelthgrade,
                'twelthpsyr': educational_info.twelthpsyr,
                'twelthcertificate': request.build_absolute_uri(educational_info.twelthcertificate.url) if educational_info.twelthcertificate else None,
                'mbbsinstitution': educational_info.mbbsinstitution,
                'mbbsgrade': educational_info.mbbsgrade,
                'mbbspsyr': educational_info.mbbspsyr,
                'mbbsmarksheet': request.build_absolute_uri(educational_info.mbbsmarksheet.url) if educational_info.mbbsmarksheet else None,
                'mbbsdegree': request.build_absolute_uri(educational_info.mbbsdegree.url) if educational_info.mbbsdegree else None,
                'mdinstitution': educational_info.mdinstitution,
                'mdgrade': educational_info.mdgrade,
                'mdpsyr': educational_info.mdpsyr,
                'mdmarksheet': request.build_absolute_uri(educational_info.mdmarksheet.url) if educational_info.mdmarksheet else None,
                'mddegree': request.build_absolute_uri(educational_info.mddegree.url) if educational_info.mddegree else None,
                'videofile': request.build_absolute_uri(educational_info.videofile.url) if educational_info.videofile else None,
                # Add more fields as needed
            },
            'experience_info': {
                'exinstitution1': experience_info.exinstitution1,
                'exstdate1': experience_info.exstdate1,
                'exenddate1': experience_info.exenddate1,
                'exinstitution2': experience_info.exinstitution2,
                'exstdate2': experience_info.exstdate2,
                'exenddate2': experience_info.exenddate2,
                'exinstitution3': experience_info.exinstitution3,
                'exstdate3': experience_info.exstdate3,
                'exenddate3': experience_info.exenddate3,
                # Add more fields as needed
            },
            'achievement_info': {
                'award1': achievement_info.award1,
                'awarddate1': achievement_info.awarddate1,
                'award2': achievement_info.award2,
                'awarddate2': achievement_info.awarddate2,
                'publishlink': achievement_info.publishlink,
                # Add more fields as needed
            },
            'banking_info': {
                'accholdername': banking_info.accholdername,
                'bankname': banking_info.bankname,
                'branchname': banking_info.branchname,
                'acnumber': banking_info.acnumber,
                'ifsc': banking_info.ifsc,
                'pancardno': banking_info.pancardno,
                'aadharcardno': banking_info.aadharcardno,
                'pancard': request.build_absolute_uri(banking_info.pancard.url) if banking_info.pancard else None,
                'aadharcard': request.build_absolute_uri(banking_info.aadharcard.url) if banking_info.aadharcard else None,
                'cheque': request.build_absolute_uri(banking_info.cheque.url) if banking_info.cheque else None,
                # Add more fields as needed
            },
            'reporting_area_info': {
                'mriopt': reporting_area_info.mriopt,
                'mriothers': reporting_area_info.mriothers,
                'ctopt': reporting_area_info.ctopt,
                'ctothers': reporting_area_info.ctothers,
                'xray': reporting_area_info.xray,
                'others': reporting_area_info.others,
                'otherText': reporting_area_info.otherText,
                # Add more fields as needed
            },
            'availability_info': {
                'monday': availability_info.monday,
                'tuesday': availability_info.tuesday,
                'wednesday': availability_info.wednesday,
                'thursday': availability_info.thursday,
                'friday': availability_info.friday,
                'saturday': availability_info.saturday,
                'sunday': availability_info.sunday,
                'starttime1': availability_info.starttime1,
                'endtime1': availability_info.endtime1,
                'starttime2': availability_info.starttime2,
                'endtime2': availability_info.endtime2,
                'starttime3': availability_info.starttime3,
                'endtime3': availability_info.endtime3,
                'starttime4': availability_info.starttime4,
                'endtime4': availability_info.endtime4,
                # Add more fields as needed
            },
            # "pdf_url": pdf_url,  # Add the PDF URL to the response
        }

        logging.info(f"Successfully fetched complete form data for PK={pk}")
        return JsonResponse(response)

    except ObjectDoesNotExist as e:
        error_message = f"Object does not exist: {str(e)}"
        logging.error(error_message)
        return JsonResponse({'error': error_message}, status=404)

    except Exception as e:
        error_message = f"Error fetching complete form data: {str(e)}"
        logging.error(error_message)
        return JsonResponse({'error': error_message}, status=500)

@csrf_exempt
def update_messages(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        coordinator_message = request.POST.get('coordinator_message')
        supercoordinator_message = request.POST.get('supercoordinator_message')
        stage1status = request.POST.get('stage1status')
        stage2status = request.POST.get('stage2status')

        try:
            data = PersonalInformation.objects.get(pk=pk)
            if coordinator_message is not None:
                data.coordinator_message = coordinator_message
            if supercoordinator_message is not None:
                data.supercoordinator_message = supercoordinator_message
            if stage1status is not None:
                data.stage1status = stage1status
            if stage2status is not None:
                data.stage2status = stage2status
            data.save()
            return JsonResponse({'status': 'success'})
        except PersonalInformation.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Data not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# This is the view to generate the pdf of the responses.

# def generate_response_pdf(request, pk):
#     personal_info = PersonalInformation.objects.get(pk=pk)
#     educational_info = EducationalDetails.objects.get(pk=pk)
#     experience_info = ExperienceDetails.objects.get(pk=pk)
#     achievement_info = AchievementDetails.objects.get(pk=pk)
#     banking_info = BankingDetails.objects.get(pk=pk)
#     reporting_info = ReportingAreaDetails.objects.get(pk=pk)
#     availability_info = AvailabilityDetails.objects.get(pk=pk)

#     html_string = render_to_string('response_pdf.html', {
#         'personal_information': personal_info,
#         'educational_info': educational_info,
#         'experience_info': experience_info,
#         'achievement_info': achievement_info,
#         'banking_info': banking_info,
#         'reporting_info': reporting_info,
#         'availability_info': availability_info,
#     })

#     html = weasyprint.HTML(string=html_string)
#     pdf = html.write_pdf()

#     response = HttpResponse(pdf, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="response.pdf"'
#     return response

# def generate_pdf(request, pk):
#     if request.method == 'POST':
#         try:
#             personal_information = get_object_or_404(PersonalInformation, pk=pk)
#             educational_info = EducationalDetails.objects.filter(personal_information=personal_information).first()
#             experience_info = ExperienceDetails.objects.filter(personal_information=personal_information).first()
#             achievement_info = AchievementDetails.objects.filter(personal_information=personal_information).first()
#             banking_info = BankingDetails.objects.filter(personal_information=personal_information).first()
#             reporting_area_info = ReportingAreaDetails.objects.filter(personal_information=personal_information).first()
#             availability_info = AvailabilityDetails.objects.filter(personal_information=personal_information).first()

#             response = HttpResponse(content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="form_data_{pk}.pdf"'
            
#             doc = SimpleDocTemplate(response, pagesize=letter)
#             styles = getSampleStyleSheet()
#             elements = []

#             def add_paragraph(elements, text, style=styles['Normal']):
#                 elements.append(Paragraph(text, style))

#             # Personal Information
#             add_paragraph(elements, "Personal Information:", styles['Heading1'])
#             add_paragraph(elements, f"First Name: {personal_information.first_name or 'N/A'}")
#             add_paragraph(elements, f"Last Name: {personal_information.last_name or 'N/A'}")
#             add_paragraph(elements, f"Email: {personal_information.email or 'N/A'}")
#             add_paragraph(elements, f"Password: {personal_information.password or 'N/A'}")
#             add_paragraph(elements, f"Address: {personal_information.address or 'N/A'}")
#             add_paragraph(elements, f"Contact No.: {personal_information.contact_no or 'N/A'}")
#             add_paragraph(elements, f"Resume: {personal_information.resume.url if personal_information.resume else 'No Resume Uploaded'}")
#             add_paragraph(elements, f"Photo: {personal_information.photo.url if personal_information.photo else 'No Photo Uploaded'}")
#             add_paragraph(elements, f"Experience Years: {personal_information.experience_years or 'N/A'}")

#             # Educational Details
#             if educational_info:
#                 add_paragraph(elements, "Educational Details:", styles['Heading1'])
#                 add_paragraph(elements, f"10th School Name: {educational_info.tenthname or 'N/A'}")
#                 add_paragraph(elements, f"10th Grade: {educational_info.tenthgrade or 'N/A'}")
#                 add_paragraph(elements, f"10th Passing Year: {educational_info.tenthpsyr or 'N/A'}")
#                 add_paragraph(elements, f"10th Certificate: {educational_info.tenthcertificate.url if educational_info.tenthcertificate else 'No Certificate Uploaded'}")
#                 add_paragraph(elements, f"12th School Name: {educational_info.twelthname or 'N/A'}")
#                 add_paragraph(elements, f"12th Grade: {educational_info.twelthgrade or 'N/A'}")
#                 add_paragraph(elements, f"12th Passing Year: {educational_info.twelthpsyr or 'N/A'}")
#                 add_paragraph(elements, f"12th Certificate: {educational_info.twelthcertificate.url if educational_info.twelthcertificate else 'No Certificate Uploaded'}")
#                 add_paragraph(elements, f"MBBS Institution: {educational_info.mbbsinstitution or 'N/A'}")
#                 add_paragraph(elements, f"MBBS Grade: {educational_info.mbbsgrade or 'N/A'}")
#                 add_paragraph(elements, f"MBBS Passing Year: {educational_info.mbbspsyr or 'N/A'}")
#                 add_paragraph(elements, f"MBBS Marksheet: {educational_info.mbbsmarksheet.url if educational_info.mbbsmarksheet else 'No Marksheet Uploaded'}")
#                 add_paragraph(elements, f"MBBS Degree: {educational_info.mbbsdegree.url if educational_info.mbbsdegree else 'No Degree Uploaded'}")
#                 add_paragraph(elements, f"MD Institution: {educational_info.mdinstitution or 'N/A'}")
#                 add_paragraph(elements, f"MD Grade: {educational_info.mdgrade or 'N/A'}")
#                 add_paragraph(elements, f"MD Passing Year: {educational_info.mdpsyr or 'N/A'}")
#                 add_paragraph(elements, f"MD Marksheet: {educational_info.mdmarksheet.url if educational_info.mdmarksheet else 'No Marksheet Uploaded'}")
#                 add_paragraph(elements, f"MD Degree: {educational_info.mddegree.url if educational_info.mddegree else 'No Degree Uploaded'}")
#                 add_paragraph(elements, f"Video File: {educational_info.videofile.url if educational_info.videofile else 'No Video Uploaded'}")
#             else:
#                 add_paragraph(elements, "Educational Details: No educational details available.", styles['Heading1'])

#             # Experience Details
#             if experience_info:
#                 add_paragraph(elements, "Experience Details:", styles['Heading1'])
#                 add_paragraph(elements, f"Experience 1 Institution: {experience_info.exinstitution1 or 'N/A'}")
#                 add_paragraph(elements, f"Experience 1 Starting Date: {experience_info.exstdate1 or 'N/A'}")
#                 add_paragraph(elements, f"Experience 1 Ending Date: {experience_info.exenddate1 or 'N/A'}")
#                 add_paragraph(elements, f"Experience 2 Institution: {experience_info.exinstitution2 or 'N/A'}")
#                 add_paragraph(elements, f"Experience 2 Starting Date: {experience_info.exstdate2 or 'N/A'}")
#                 add_paragraph(elements, f"Experience 2 Ending Date: {experience_info.exenddate2 or 'N/A'}")
#                 add_paragraph(elements, f"Experience 3 Institution: {experience_info.exinstitution3 or 'N/A'}")
#                 add_paragraph(elements, f"Experience 3 Starting Date: {experience_info.exstdate3 or 'N/A'}")
#                 add_paragraph(elements, f"Experience 3 Ending Date: {experience_info.exenddate3 or 'N/A'}")
#             else:
#                 add_paragraph(elements, "Experience Details: No experience details available.", styles['Heading1'])

#             # Achievement Details
#             if achievement_info:
#                 add_paragraph(elements, "Achievement Details:", styles['Heading1'])
#                 add_paragraph(elements, f"Award 1: {achievement_info.award1 or 'N/A'}")
#                 add_paragraph(elements, f"Award Date 1: {achievement_info.awarddate1 or 'N/A'}")
#                 add_paragraph(elements, f"Award 2: {achievement_info.award2 or 'N/A'}")
#                 add_paragraph(elements, f"Award Date 2: {achievement_info.awarddate2 or 'N/A'}")
#                 add_paragraph(elements, f"Publish Link: {achievement_info.publishlink or 'N/A'}")
#             else:
#                 add_paragraph(elements, "Achievement Details: No achievement details available.", styles['Heading1'])

#             # Banking Details
#             if banking_info:
#                 add_paragraph(elements, "Banking Details:", styles['Heading1'])
#                 add_paragraph(elements, f"Account Holder Name: {banking_info.accholdername or 'N/A'}")
#                 add_paragraph(elements, f"Bank Name: {banking_info.bankname or 'N/A'}")
#                 add_paragraph(elements, f"Branch Name: {banking_info.branchname or 'N/A'}")
#                 add_paragraph(elements, f"Account Number: {banking_info.acnumber or 'N/A'}")
#                 add_paragraph(elements, f"IFSC Code: {banking_info.ifsc or 'N/A'}")
#                 add_paragraph(elements, f"Pan Card Number: {banking_info.pancardno or 'N/A'}")
#                 add_paragraph(elements, f"Aadhar Card Number: {banking_info.aadharcardno or 'N/A'}")
#                 add_paragraph(elements, f"Pan Card: {banking_info.pancard or 'No Pan Card Uploaded'}")
#                 add_paragraph(elements, f"Aadhar Card: {banking_info.aadharcard or 'No Aadhar Card Uploaded'}")
#                 add_paragraph(elements, f"Cheque: {banking_info.cheque or 'No Cheque Uploaded'}")
#             else:
#                 add_paragraph(elements, "Banking Details: No banking details available.", styles['Heading1'])

#             # Reporting Area Details
#             if reporting_area_info:
#                 add_paragraph(elements, "Reporting Area Details:", styles['Heading1'])
#                 add_paragraph(elements, f"MRI Option: {reporting_area_info.mriopt or 'N/A'}")
#                 add_paragraph(elements, f"MRI Others: {reporting_area_info.mriothers or 'N/A'}")
#                 add_paragraph(elements, f"CT Options: {reporting_area_info.ctopt or 'N/A'}")
#                 add_paragraph(elements, f"CT Others: {reporting_area_info.ctothers or 'N/A'}")
#                 add_paragraph(elements, f"Xray: {reporting_area_info.xray or 'N/A'}")
#                 add_paragraph(elements, f"Others: {reporting_area_info.others or 'N/A'}")
#                 add_paragraph(elements, f"Others Description: {reporting_area_info.otherText or 'N/A'}")
#             else:
#                 add_paragraph(elements, "Reporting Area Details: No reporting area details available.", styles['Heading1'])

#             # Availability Details
#             if availability_info:
#                 add_paragraph(elements, "Availability Details:", styles['Heading1'])
#                 add_paragraph(elements, f"Monday: {availability_info.monday or 'N/A'}")
#                 add_paragraph(elements, f"Tuesday: {availability_info.tuesday or 'N/A'}")
#                 add_paragraph(elements, f"Wednesday: {availability_info.wednesday or 'N/A'}")
#                 add_paragraph(elements, f"Thursday: {availability_info.thursday or 'N/A'}")
#                 add_paragraph(elements, f"Friday: {availability_info.friday or 'N/A'}")
#                 add_paragraph(elements, f"Saturday: {availability_info.saturday or 'N/A'}")
#                 add_paragraph(elements, f"Sunday: {availability_info.sunday or 'N/A'}")
#                 add_paragraph(elements, f"Time Slot 1 (start): {availability_info.starttime1 or 'N/A'}")
#                 add_paragraph(elements, f"Time Slot 1 (end): {availability_info.endtime1 or 'N/A'}")
#                 add_paragraph(elements, f"Time Slot 2 (start): {availability_info.starttime2 or 'N/A'}")
#                 add_paragraph(elements, f"Time Slot 2 (end): {availability_info.endtime2 or 'N/A'}")
#                 add_paragraph(elements, f"Time Slot 3 (start): {availability_info.starttime3 or 'N/A'}")
#                 add_paragraph(elements, f"Time Slot 3 (end): {availability_info.endtime3 or 'N/A'}")
#                 add_paragraph(elements, f"Time Slot 4 (start): {availability_info.starttime4 or 'N/A'}")
#                 add_paragraph(elements, f"Time Slot 4 (end): {availability_info.endtime4 or 'N/A'}")
#             else:
#                 add_paragraph(elements, "Availability Details: No availability details available.", styles['Heading1'])

#             doc.build(elements)
#             return response

#         except ObjectDoesNotExist as e:
#             error_message = f"Object does not exist: {str(e)}"
#             return JsonResponse({'error': error_message}, status=404)

#         except Exception as e:
#             error_message = f"Error generating PDF: {str(e)}"
#             return JsonResponse({'error': error_message}, status=500)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=400)

def generate_pdf(request, pk):
    personal_info = get_object_or_404(PersonalInformation, pk=pk)
    educational_info = get_object_or_404(EducationalDetails, personal_information=personal_info)
    experience_info = get_object_or_404(ExperienceDetails, personal_information=personal_info)
    achievement_info = get_object_or_404(AchievementDetails, personal_information=personal_info)
    banking_info = get_object_or_404(BankingDetails, personal_information=personal_info)
    reporting_area_info = get_object_or_404(ReportingAreaDetails, personal_information=personal_info)
    availability_info = get_object_or_404(AvailabilityDetails, personal_information=personal_info)

    response = HttpResponse(content_type='application/pdf')
    filename = f"{personal_info.first_name}_{personal_info.last_name}_form_data_{personal_info.pk}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    def add_new_page(p, y):
        p.showPage()
        y = height - 40
        return y

    def draw_text(text, data, y, p, indent=100):
        if y < 40:
            y = add_new_page(p, y)
        data_str = str(data) if not isinstance(data, date) else data.strftime('%Y-%m-%d')  # Convert date to string if necessary
        p.drawString(indent, y, text)
        p.drawString(indent + 150, y, ":")
        p.drawString(indent + 170, y, data_str)
        return y - 15
    
    def draw_last_text(text, data, y, p, indent=100):
        if y < 40:
            y = add_new_page(p, y)
        data_str = str(data) if not isinstance(data, date) else data.strftime('%Y-%m-%d')  # Convert date to string if necessary
        p.drawString(indent, y, text)
        p.drawString(indent + 150, y, ":")
        p.drawString(indent + 170, y, data_str)
        return y - 25
    
    def draw_text_heading(text, data, y, p, indent=100):
        if y < 40:
            y = add_new_page(p, y)
        data_str = str(data) if not isinstance(data, date) else data.strftime('%Y-%m-%d')  # Convert date to string if necessary
        p.drawString(indent, y, text)
        p.drawString(indent, y - 7, "------------------------------------------")
        
        return y - 25

    def draw_link(text, url, link_text, y, p, indent=100):
        if y < 40:
            y = add_new_page(p, y)
        text_width = stringWidth(link_text, fontName="Helvetica", fontSize=12)
        p.drawString(indent, y, text)
        p.drawString(indent + 150, y, ":")
        # Debugging print statement to ensure URL is correctly passed
        print(f"Drawing link: {text}, URL: {url}")
        if url:
            p.setFillColor(blue)
            p.drawString(indent + 170, y, link_text)
            p.linkURL(f'{url}#target=_blank', (indent + 170, y, indent + 170 + text_width, y + 10), relative=1, thickness=1, color=blue)
            p.setFillColor(black)  # Reset color to black for other texts
        else:
            p.drawString(indent + 170, y, "N/A")
        return y - 15

    def draw_last_link(text, url, link_text, y, p, indent=100):
        if y < 40:
            y = add_new_page(p, y)
        text_width = stringWidth(link_text, fontName="Helvetica", fontSize=12)
        p.drawString(indent, y, text)
        p.drawString(indent + 150, y, ":")
        # Debugging print statement to ensure URL is correctly passed
        print(f"Drawing link: {text}, URL: {url}")
        if url:
            p.setFillColor(blue)
            p.drawString(indent + 170, y, link_text)
            p.linkURL(f'{url}#target=_blank', (indent + 170, y, indent + 170 + text_width, y + 10), relative=1, thickness=1, color=blue)
            p.setFillColor(black)  # Reset color to black for other texts
        else:
            p.drawString(indent + 170, y, "N/A")
        return y - 25


    # Draw the title at the top of the page
    title = f"Form Details of {personal_info.first_name} {personal_info.last_name}"
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, title)
    y -= 30  # Adjust the space after the title

    p.setFont("Helvetica", 12)  # Reset font size to normal

    # Draw Personal Information section
    y = draw_text_heading("Personal Information","", y, p)
    y = draw_text("First Name", personal_info.first_name or 'N/A', y, p)
    y = draw_text("Last Name", personal_info.last_name or 'N/A', y, p)
    y = draw_text("Email", personal_info.email or 'N/A', y, p)
    y = draw_text("Password", personal_info.password or 'N/A', y, p)
    y = draw_text("Confirm Password", personal_info.cnfpassword or 'N/A', y, p)
    y = draw_text("Address", personal_info.address or 'N/A', y, p)
    y = draw_text("Contact Number", personal_info.contact_no or 'N/A', y, p)
    y = draw_text("Years of Experience", str(personal_info.experience_years or 'N/A'), y, p)
    if personal_info.resume:
        resume_url = request.build_absolute_uri(personal_info.resume.url) if personal_info.resume else None
        y = draw_link("Resume", resume_url, "View Resume", y, p)
    if personal_info.photo:
        photo_url = request.build_absolute_uri(personal_info.photo.url) if personal_info.photo else None
        y = draw_last_link("Photo", photo_url, "View Photo", y, p)

    # Draw Educational Details section
    y = draw_text_heading("Educational Details","", y, p)
    y = draw_text("Tenth Name", educational_info.tenthname or 'N/A', y, p)
    y = draw_text("Tenth Grade", educational_info.tenthgrade or 'N/A', y, p)
    y = draw_text("Tenth Passing Year", educational_info.tenthpsyr or 'N/A', y, p)
    if educational_info.tenthcertificate:
        tenth_cert_url = request.build_absolute_uri(educational_info.tenthcertificate.url) if educational_info.tenthcertificate else None
        y = draw_link("Tenth Certificate", tenth_cert_url, "View Tenth Certificate", y, p)
    y = draw_text("Twelfth Name", educational_info.twelthname or 'N/A', y, p)
    y = draw_text("Twelfth Grade", educational_info.twelthgrade or 'N/A', y, p)
    y = draw_text("Twelfth Passing Year", educational_info.twelthpsyr or 'N/A', y, p)
    if educational_info.twelthcertificate:
        twelfth_cert_url = request.build_absolute_uri(educational_info.twelthcertificate.url) if educational_info.twelthcertificate else None
        y = draw_link("Twelfth Certificate", twelfth_cert_url, "View Twelfth Certificate", y, p)
    y = draw_text("MBBS Institution", educational_info.mbbsinstitution or 'N/A', y, p)
    y = draw_text("MBBS Grade", educational_info.mbbsgrade or 'N/A', y, p)
    y = draw_text("MBBS Passing Year", educational_info.mbbspsyr or 'N/A', y, p)
    if educational_info.mbbsmarksheet:
        mbbs_marksheet_url = request.build_absolute_uri(educational_info.mbbsmarksheet.url) if educational_info.mbbsmarksheet else None
        y = draw_link("MBBS Marksheets", mbbs_marksheet_url, "View MBBS Marksheets", y, p)
    if educational_info.mbbsdegree:
        mbbs_degree_url = request.build_absolute_uri(educational_info.mbbsdegree.url) if educational_info.mbbsdegree else None
        y = draw_link("MBBS Degree", mbbs_degree_url, "View MBBS Degree", y, p)
    y = draw_text("MD Institution", educational_info.mdinstitution or 'N/A', y, p)
    y = draw_text("MD Grade", educational_info.mdgrade or 'N/A', y, p)
    y = draw_text("MD Passing Year", educational_info.mdpsyr or 'N/A', y, p)
    if educational_info.mdmarksheet:
        md_marksheet_url = request.build_absolute_uri(educational_info.mdmarksheet.url) if educational_info.mdmarksheet else None
        y = draw_link("MD Marksheets", md_marksheet_url, "View MD Marksheets", y, p)
    if educational_info.mddegree:
        md_degree_url = request.build_absolute_uri(educational_info.mddegree.url) if educational_info.mddegree else None
        y = draw_link("MD Degree", md_degree_url, "View MD Degree", y, p)
    if educational_info.videofile:
        video_url = request.build_absolute_uri(educational_info.videofile.url) if educational_info.videofile else None
        y = draw_last_link("Video File", video_url, "View Video", y, p)

    # Draw Experience Details section
    y = draw_text_heading("Experience Details","", y, p)
    y = draw_text("Experience 1 Institution", experience_info.exinstitution1 or 'N/A', y, p)
    y = draw_text("Experience 1 Starting Date", experience_info.exstdate1 or 'N/A', y, p)
    y = draw_text("Experience 1 Ending Date", experience_info.exenddate1 or 'N/A', y, p)
    y = draw_text("Experience 2 Institution", experience_info.exinstitution2 or 'N/A', y, p)
    y = draw_text("Experience 2 Starting Date", experience_info.exstdate2 or 'N/A', y, p)
    y = draw_text("Experience 2 Ending Date", experience_info.exenddate2 or 'N/A', y, p)
    y = draw_text("Experience 3 Institution", experience_info.exinstitution3 or 'N/A', y, p)
    y = draw_text("Experience 3 Starting Date", experience_info.exstdate3 or 'N/A', y, p)
    y = draw_last_text("Experience 3 Ending Date", experience_info.exenddate3 or 'N/A', y, p)
    

    # Draw Achievement Details section
    y = draw_text_heading("Achievement Details","", y-39, p)
    y = draw_text("Award 1", achievement_info.award1 or 'N/A', y, p)
    y = draw_text("Award Date 1", achievement_info.awarddate1 or 'N/A', y, p)
    y = draw_text("Award 2", achievement_info.award2 or 'N/A', y, p)
    y = draw_text("Award Date 2", achievement_info.awarddate2 or 'N/A', y, p)
    y = draw_last_text("Publish Link", achievement_info.publishlink or 'N/A', y, p)
    

    # Draw Banking Details section
    y = draw_text_heading("Banking Details","", y, p)
    y = draw_text(f"Account Holder Name:", banking_info.accholdername or 'N/A', y, p)
    y = draw_text(f"Bank Name:" , banking_info.bankname or 'N/A', y, p)
    y = draw_text(f"Branch Name:", banking_info.branchname or 'N/A', y, p)
    y = draw_text(f"IFSC Code:",banking_info.ifsc or 'N/A', y, p)
    y = draw_text(f"Account Number:",banking_info.acnumber or 'N/A', y, p)
    y = draw_text(f"Pan Card Number:",banking_info.pancardno or 'N/A', y, p)
    y = draw_text(f"Aadhar Card Number:",banking_info.aadharcardno or 'N/A', y, p)
    if banking_info.pancard:
        pancard_url = request.build_absolute_uri(banking_info.pancard.url) if banking_info.pancard else None
        y = draw_link("Pan Card", pancard_url, "View Pan Card", y, p)
    if banking_info.aadharcard:
        aadharcard_url = request.build_absolute_uri(banking_info.aadharcard.url) if banking_info.aadharcard else None
        y = draw_link("Aadhar Card", aadharcard_url, "View Aadhar Card", y, p)
    if banking_info.cheque:
        cheque_url = request.build_absolute_uri(banking_info.cheque.url) if banking_info.cheque else None
        y = draw_last_link("Cheque", cheque_url, "View Cheque", y, p)

    # Draw Reporting Area Details section
    y = draw_text_heading("Reporting Area Details","", y, p)
    y = draw_text(f"MRI Option:",reporting_area_info.mriopt or 'N/A', y, p)
    y = draw_text(f"MRI Others:",reporting_area_info.mriothers or 'N/A', y, p)
    y = draw_text(f"CT Option:",reporting_area_info.ctopt or 'N/A', y, p)
    y = draw_text(f"CT Others:",reporting_area_info.ctothers or 'N/A', y, p)
    y = draw_text(f"Xray:",reporting_area_info.xray or 'N/A', y, p)
    y = draw_text(f"Others:",reporting_area_info.others or 'N/A', y, p)
    y = draw_last_text(f"Others Description:",reporting_area_info.otherText or 'N/A', y, p)

    # Draw Availability Details section
    y = draw_text_heading("Availability Details","", y, p)
    y = draw_text(f"Monday:",availability_info.monday or 'N/A', y, p)
    y = draw_text(f"Tuesday:",availability_info.tuesday or 'N/A', y, p)
    y = draw_text(f"Wednesday:",availability_info.wednesday or 'N/A', y, p)
    y = draw_text(f"Thursday:",availability_info.thursday or 'N/A', y, p)
    y = draw_text(f"Friday:",availability_info.friday or 'N/A', y, p)
    y = draw_text(f"Saturday:",availability_info.saturday or 'N/A', y, p)
    y = draw_text(f"Sunday:",availability_info.sunday or 'N/A', y, p)
    y = draw_text(f"Time Slot 1 (start):",availability_info.starttime1 or 'N/A', y, p)
    y = draw_text(f"Time Slot 1 (end):",availability_info.endtime1 or 'N/A', y, p)
    y = draw_text(f"Time Slot 2 (start):",availability_info.starttime2 or 'N/A', y, p)
    y = draw_text(f"Time Slot 2 (end):",availability_info.endtime2 or 'N/A', y, p)
    y = draw_text(f"Time Slot 3 (start):",availability_info.starttime3 or 'N/A', y, p)
    y = draw_text(f"Time Slot 3 (end)",availability_info.endtime3 or 'N/A', y, p)
    y = draw_text(f"Time Slot 4 (start):",availability_info.starttime4 or 'N/A', y, p)
    y = draw_text(f"Time Slot 4 (end):",availability_info.endtime4 or 'N/A', y, p)

    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=f"{personal_info.first_name}_{personal_info.last_name}_form_data_{personal_info.pk}.pdf")
