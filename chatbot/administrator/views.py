from django.core.exceptions import ObjectDoesNotExist 
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .decorators import admin_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CreateUserForm,  UserDetailsForm, StudentDetailsForm,  ModuleDetailsForm, ActivityDetailsForm, ModuleForm, RegisterInstrumentForm, TeacherInstrumentForm
from django.core.paginator import Paginator
from django.db import transaction 
from .models import auth_user_details, Student, Instrument, TeachingMode, BookInstrument, Book, Activity, ModuleDetails, Media, Teacher, ParentLogin, TeacherLogin # Import your model
from django.views.decorators.csrf import csrf_exempt
from teacher.models import Attendance, Teacher
import json
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models import Q
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.contrib.auth.decorators import user_passes_test
import logging


@admin_required
def administrator(request):
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name

        # Count totals
        total_teachers = User.objects.filter(groups__name="Teacher").count()
        total_students = Student.objects.count()
        total_instruments = Instrument.objects.count()

        # Fetch parent and teacher groups
        try:
            parent_group = Group.objects.get(name="Parent")
            teacher_group = Group.objects.get(name="Teacher")
        except Group.DoesNotExist:
            parent_group = None
            teacher_group = None

        # Query parent and teacher users
        parent_users = User.objects.filter(groups=parent_group) if parent_group else []
        teacher_users = User.objects.filter(groups=teacher_group) if teacher_group else []

        # Query parent logins by month
        parent_logins_by_month = (ParentLogin.objects
            .filter(parent__in=parent_users)
            .annotate(month=TruncMonth('login_time'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month'))

        # Query teacher logins by month
        teacher_logins_by_month = (TeacherLogin.objects
            .filter(teacher__in=teacher_users)
            .annotate(month=TruncMonth('login_time'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month'))

        # Combine months from both queries
        months_set = set([entry['month'] for entry in parent_logins_by_month] + [entry['month'] for entry in teacher_logins_by_month])
        months = sorted(list(months_set))

        # Initialize dictionaries for login counts
        parent_login_counts = {month: 0 for month in months}
        teacher_login_counts = {month: 0 for month in months}

        # Populate login counts dictionaries
        for entry in parent_logins_by_month:
            parent_login_counts[entry['month']] = entry['count']

        for entry in teacher_logins_by_month:
            teacher_login_counts[entry['month']] = entry['count']

        # Format months for display in the template
        months_str = [month.strftime('%B %Y') for month in months]

        # Prepare context dictionary for rendering the template
        context = {
            'total_teachers': total_teachers,
            'total_students': total_students,
            'total_instruments': total_instruments,
            'first_name': first_name,
            'last_name': last_name,
            'months': months_str,
            'parent_login_values': [parent_login_counts[month] for month in months],
            'teacher_login_values': [teacher_login_counts[month] for month in months],
        }

        # Render the template with the context
        return render(request, 'master_admin.html', context)
    
    else:
        return HttpResponse("")
    
@admin_required
def delete_account(request, username):
    if request.method == 'POST':
        print('Received POST request to delete account with username:', username)  # Add this line for debugging
        try:
            user = User.objects.get(username=username)
            user.delete()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

@admin_required
def accounts(request):
    # Get the authenticated user
    user = request.user

    # Get all accounts
    accounts_list = User.objects.all()

    # Get the number of entries per page from the request query parameters
    per_page = request.GET.get('per_page')
    default_per_page = 5
    
    if per_page == 'all':
        items_per_page = len(accounts_list)
        page_obj = accounts_list  # Display all accounts without pagination
    else:
        items_per_page = int(per_page) if per_page else default_per_page
        paginator = Paginator(accounts_list, items_per_page)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

    # Get all roles
    roles = Group.objects.all()
    
    # Retrieve phone numbers for each user
    user_phone_numbers = {}
    for account in accounts_list:
        try:
            # Retrieve the phone number associated with the user
            details = auth_user_details.objects.get(user=account)
            user_phone_numbers[account.id] = details.phone_number
        except auth_user_details.DoesNotExist:
            user_phone_numbers[account.id] = None
    
    user_address = {}
    for account in accounts_list:
        try:
            # Retrieve the phone number associated with the user
            details = auth_user_details.objects.get(user=account)
            user_address[account.id] = details.address
        except auth_user_details.DoesNotExist:
            user_address[account.id] = None
    # Pass the user data, pagination data, roles, and phone numbers to the template context
    context = {
        'user': user,
        'accounts': page_obj,
        'roles': roles,
        'user_phone_numbers': user_phone_numbers,
        'user_address' : user_address,
    }
    
    # Render the template with the context
    return render(request, 'accounts_list.html', context)


@admin_required
def register(request):
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        details_form = UserDetailsForm(request.POST)
        teacher_form = TeacherInstrumentForm(request.POST)
        
        if user_form.is_valid() and details_form.is_valid() and teacher_form.is_valid():
            try:
                # Save the user instance
                user = user_form.save()
                print("User created: ", user)
                
                # Save the user details instance
                details = details_form.save(commit=False)
                details.user = user
                details.save()
                print("User details saved: ", details)
                
                # Get the instruments from the teacher form
                instruments = teacher_form.cleaned_data['instruments']
                
                # Create a Teacher instance for each instrument
                for instrument in instruments:
                    Teacher.objects.create(teacher=details, instrument=instrument)
                
                # Get the selected group from the user form
                group = user_form.cleaned_data['group']
                print("Selected group: ", group)
                
                # Add the user to the group
                user.groups.add(group)
                print("User added to group: ", group)
                
                # Add a success message
                messages.success(request, 'User account created successfully!')
                
                # Redirect the user to the success page after successful registration
                return redirect('register')  # Assuming you have a named URL for success page
            except Exception as e:
                print("Error occurred during user registration:", e)
                messages.error(request, f'Error occurred during user registration: {e}')
        else:
            print("Form errors: ", user_form.errors, details_form.errors, teacher_form.errors)
            messages.error(request, 'Invalid form submission.')
    else:
        user_form = CreateUserForm()
        details_form = UserDetailsForm()
        teacher_form = TeacherInstrumentForm()
    
    return render(request, 'register.html', {'user_form': user_form, 'details_form': details_form, 'teacher_form': teacher_form})




@admin_required
def success(request):

 
    # Display a success message or perform other actions if needed
    return render(request, 'success.html')
    # Remove the 'success' query parameter from the URL
    # url = reverse('register')  # Assuming 'register' is the name of the URL pattern
    # url = url.split('?')[0]  # Remove query parameters
    # return HttpResponseRedirect(url)

@admin_required
def student(request) :

    students = Student.objects.all()

    context = {
        'students' : students
    }
    return render(request, 'student.html', context)

logger = logging.getLogger(__name__)

@csrf_exempt
def registerStudent(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_form = StudentDetailsForm(data)
            if student_form.is_valid():
                with transaction.atomic():
                    student = student_form.save()

                    selected_times = data.get('selectedTimes', '').split(',')
                    selected_date = data.get('selectedDate', '')
                    recurring_weeks = int(data.get('recurringWeeks', 1))  # Default to 1 week if not provided or invalid

                    # Retrieve teacher_id from JSON data
                    teacher_id = data.get('assigned_teacher', None)

                    if teacher_id is not None:
                        # Fetch the corresponding User object directly
                        try:
                            teacher_user = User.objects.get(id=teacher_id)
                        except User.DoesNotExist:
                            logger.error(f"User with id {teacher_id} does not exist")
                            return JsonResponse({'success': False, 'message': 'User does not exist'})

                        # Create Attendance instances for each selected time and recurring weeks
                        for time in selected_times:
                            try:
                                start_time = datetime.strptime(time.strip(), '%H:%M')
                                end_time = start_time + timedelta(minutes=30)

                                for week in range(recurring_weeks):
                                    new_attendance = Attendance.objects.create(
                                        student=student,
                                        teacher_email=teacher_user,
                                        title='Class',
                                        description='Regular Class',
                                        date=(datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(weeks=week)).date(),
                                        start_time=start_time.time(),
                                        end_time=end_time.time(),
                                        attendance='Attend',
                                        status='Pending Verification'
                                    )
                                    logger.info(f"Created Attendance: {new_attendance}")

                            except Exception as e:
                                logger.error(f"Error creating attendance: {str(e)}")
                                return JsonResponse({'success': False, 'message': 'Error creating attendance'})

                        return JsonResponse({'success': True, 'message': 'Student registered successfully!'})
                    else:
                        logger.error("assigned_teacher is missing in JSON data")
                        return JsonResponse({'success': False, 'message': 'assigned_teacher is missing in JSON data'})
            else:
                errors = dict(student_form.errors.items())
                logger.error(f"Invalid form data: {errors}")
                return JsonResponse({'success': False, 'message': 'Invalid form data', 'errors': errors})
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Invalid JSON data received'})
        except Exception as e:
            logger.error(f"Error registering student: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    elif request.method == 'GET':
        student_form = StudentDetailsForm()
        return render(request, 'register_student.html', {'student_form': student_form})
    else:
        logger.error("Method not allowed")
        return JsonResponse({'success': False, 'message': 'Method not allowed'})


from datetime import datetime
import logging

logger = logging.getLogger(__name__)
from django.db.models import Q

def get_teacher_classes(request, teacher_id):
    date = request.GET.get('date')
    
    if date is None:
        date = str(date.today())  # Set date to current date if None

    try:
        # Filter Attendance objects based on the provided teacher_id, date, attendance, and status
        classes = Attendance.objects.filter(
            teacher_email__id=teacher_id,
            date=date,
          
        ).select_related('student')

        print(f"Fetched classes for teacher_id={teacher_id}, date={date}: {classes}")

        classes_data = []
        for class_instance in classes:
            classes_data.append({
                'date': class_instance.date,
                'start_time': class_instance.start_time,
                'end_time': class_instance.end_time,
                'title': class_instance.title,
                'description': class_instance.description,
                'student_name': class_instance.student.studentName
            })

        return JsonResponse({'classes': classes_data})
    
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Teacher or classes not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    

@admin_required
def get_books(request, instrument_id):
    books = Book.objects.filter(bookinstrument__instrumentID=instrument_id)
    books_list = [{"id": book.id, "book": book.book} for book in books]
    return JsonResponse({"books": books_list})




@admin_required
def modules(request):
    instruments = Instrument.objects.all()
    instrument_names = Instrument.objects.all()
    book_instrument = BookInstrument.objects.all()

    instrumentID = request.GET.get('instrumentID')  # or however you get the instrument ID

    # Print instrumentID to debug
    print("Instrument ID:", instrumentID)

    # Filter BookInstrument objects based on the instrumentID
    book_instruments = BookInstrument.objects.filter(instrumentID=instrumentID)

    # Print the number of book_instruments for debugging
    print("Number of BookInstruments:", book_instruments.count())

     # Extract book IDs from the filtered queryset
    book_ids = list(book_instruments.values_list('bookID', flat=True))

    # Print book IDs for debugging
    print("Book IDs:", book_ids)

    # Filter BookInstrument objects based on the instrument ID
    book_instruments = BookInstrument.objects.filter(instrumentID=instrumentID)

    books_with_instruments = BookInstrument.objects.values_list('bookID', flat=True).distinct()

    # Filter Book objects based on the books_with_instruments queryset
    books = Book.objects.filter(id__in=books_with_instruments)

    print("Try find :" , books)

    instruments_with_books = []
    for instrument in instruments:
        books = Book.objects.filter(bookinstrument__instrumentID=instrument.id)
        instruments_with_books.append((instrument, books))

    # Extract unique major names
    unique_major_names = set()
    unique_instruments = []
    for instrument in instruments:
        if instrument.instrument_major_name not in unique_major_names:
            unique_instruments.append(instrument)
            unique_major_names.add(instrument.instrument_major_name)

    data = {
        'instruments': unique_instruments,
        'instrument_names': instrument_names,
        'book_instrument': book_instrument,
        'instruments_with_books': instruments_with_books,
        'book_ids': book_ids,
        'books': books,
    }
    return render(request, 'learning_modules.html', data)


@admin_required
def book_detail(request, book_id, instrument_major, instrument_minor):
    # Get the book object based on the book_id
    book = get_object_or_404(Book, id=book_id)
    
    # Get the instrument object based on the instrument_major and instrument_minor
    instrument = get_object_or_404(Instrument, instrument_major_name=instrument_major, instrument_minor_name=instrument_minor)
    
    # Get the BookInstrument object based on the book and instrument
    book_instrument = get_object_or_404(BookInstrument, bookID=book, instrumentID=instrument)
    
    # Filter ModuleDetails based on the BookInstrument
    modules = ModuleDetails.objects.filter(bookInstrument=book_instrument)

    return render(request, 'book_detail.html', {
        'book': book,
        'instrument_major': instrument_major,
        'instrument_minor': instrument_minor,
        'bookInstrument': book_instrument,
        'modules': modules
    })

@admin_required
@csrf_exempt
def delete_module(request, module_id):
    if request.method == "POST":
        try:
            module = ModuleDetails.objects.get(id=module_id)
            module.delete()
            messages.success(request, 'Module deleted successfully!')
            print("Module deleted successfully")
            return JsonResponse({"success": True})
        except ModuleDetails.DoesNotExist:
            return JsonResponse({"success": False, "error": "Module not found."})
    return JsonResponse({"success": False, "error": "Invalid request method."})

@csrf_exempt
@admin_required
def add_module(request):
    if request.method == "POST":
        data = json.loads(request.body)
        modules = data.get('modules', [])
        for module_data in modules:
            module_type = module_data.get('module_type')
            module_name = module_data.get('module_name')
            description = module_data.get('description')
            bookInstrument_id = module_data.get('bookInstrument')

            bookInstrument = BookInstrument.objects.get(id=bookInstrument_id)
            ModuleDetails.objects.create(
                module_type=module_type,
                module_name=module_name,
                description=description,
                bookInstrument=bookInstrument
            )
        
        # Return success response after creating modules
        return JsonResponse({'success': True, 'message': 'Modules created successfully'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@admin_required
def media (request) :
    activities = Activity.objects.all()

    context = {
        'activities' : activities
    }
    
    return render(request, 'media.html', context)

@admin_required
def activity(request):
    category = request.GET.get('category')
    if category:
        activities = Activity.objects.filter(activity_type=category)
    else:
        activities = Activity.objects.all()

    activity_types = Activity.objects.values_list('activity_type', flat=True).distinct()
    return render(request, 'activity.html', {
        'activities': activities,
        'activity_types': activity_types,
    })

@admin_required
def delete_activity(request, activity_id):
    if request.method == 'POST':
        activity = get_object_or_404(Activity, id=activity_id)
        activity.delete()
        messages.success(request, 'Activity deleted successfully.')
    return redirect('activity')

@admin_required
def registerActivity(request):
    if request.method == 'POST':
        activity_form = ActivityDetailsForm(request.POST)
        if activity_form.is_valid():
            activity_form.save()  # Save form data to the database
            messages.success(request, 'Activity registered successfully!')
            return redirect('register-activity')  # Redirect to the register-activity page
    else:
        activity_form = ActivityDetailsForm()
    return render(request, 'register_activity.html', {'activity_form': activity_form})

@admin_required
def activity_details(request, id):
    activity = get_object_or_404(Activity, id=id)
    # media = get_object_or_404(Media, id=id)
    return render(request, 'activity_details.html', {'activity': activity})




@admin_required
def register_modules(request):
    if request.method == 'POST':
        form = RegisterInstrumentForm(request.POST)
        if form.is_valid():
            primary_instrument = form.cleaned_data['primary_instrument']
            variation = form.cleaned_data['variation']
            books = form.cleaned_data['books']

            # Create the instrument with primary_instrument and variation
            instrument = Instrument.objects.create(
                instrument_major_name=primary_instrument,
                instrument_minor_name=variation
            )

            # Associate selected books with the instrument
            for book in books:
                BookInstrument.objects.create(bookID=book, instrumentID=instrument)

            messages.success(request, 'Instrument and associated books registered successfully.')
            return redirect('register-modules')
    else:
        form = RegisterInstrumentForm()

    return render(request, 'register_modules.html', {'form': form})


from django.views.decorators.http import require_http_methods
@require_http_methods(["DELETE"])
def delete_student(request, username):
    student = get_object_or_404(Student, studentName=username)
    student.delete()
    return JsonResponse({'message': 'Student deleted successfully.'})


def navbar(request):
    return render(request,'navbar_accounts.html')

def navbartest(request):
    return render(request,'navbartest.html')

@admin_required
def dashboard(request):

    return render(request, 'dashboard.html')
    