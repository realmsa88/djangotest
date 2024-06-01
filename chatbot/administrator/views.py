from django.core.exceptions import ObjectDoesNotExist 
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .decorators import admin_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CreateUserForm,  UserDetailsForm, StudentDetailsForm,  ModuleDetailsForm, ActivityDetailsForm, ModuleForm
from django.core.paginator import Paginator
from django.db import transaction 
from .models import auth_user_details, Student, Instrument, TeachingMode, BookInstrument, Book, Activity, ModuleDetails, Media # Import your model
from django.views.decorators.csrf import csrf_exempt
import json

@admin_required
def administrator(request):
    # Ensure that the user is authenticated
    if request.user.is_authenticated:
        # Access the first name and last name of the authenticated user
        first_name = request.user.first_name
        last_name = request.user.last_name
        
        # You can also access other user attributes if needed
        # username = request.user.username
        # email = request.user.email
        
        # Pass the user data to the template
        context = {
            'first_name': first_name,
            'last_name': last_name
        }
        
        # Load the template and render it with the context
        template = loader.get_template('master_admin.html')
        return HttpResponse(template.render(context, request))
    else:
        # Redirect or handle unauthenticated users as needed
        # For example, you might want to redirect them to the login page
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
        if user_form.is_valid() and details_form.is_valid():
            try:
                # Save the user instance
                user = user_form.save()

                # Save the user details instance
                details = details_form.save(commit=False)
                details.user = user
                details.save()

                # Get the selected group from the user form
                group = user_form.cleaned_data['group']
                
                # Add the user to the group
                user.groups.add(group)

                # Add a success message
                messages.success(request, 'User account created successfully!')

                # Redirect the user to the success page after successful registration
                return redirect('register')  # Assuming you have a named URL for success page
            except Exception as e:
                print("Error occurred during user registration:", e)
                messages.error(request, 'Error occurred during user registration')
    else:
        user_form = CreateUserForm()
        details_form = UserDetailsForm()
    
    return render(request, 'register.html', {'user_form': user_form, 'details_form': details_form})


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


@admin_required
def registerStudent(request):
    if request.method == 'POST':
        student_form = StudentDetailsForm(request.POST)
        if student_form.is_valid():
            try:
                with transaction.atomic():  # Start a database transaction
                    student = student_form.save(commit=False)  # Create student object but don't save to database yet

                    # Process the learning mode
                    learning_mode_id = student_form.cleaned_data['learningmode']
                    learning_mode = TeachingMode.objects.get(pk=learning_mode_id)
                    student.teaching_mode = learning_mode

                    # Now save the student instance with the learning mode included
                    student.save()
                    messages.success(request, 'Student registered successfully!')

                # Redirect the user to the success page after successful registration
                return redirect('register-student')
            except Exception as e:
                print("Error occurred during student registration:", e)
                messages.error(request, 'Error occurred during student registration')
    else:
        student_form = StudentDetailsForm()

    return render(request, 'register_student.html', {
        'student_form': student_form
    })



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
def delete_book_detail(request, module_id):
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
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_detail')  # Redirect to the appropriate page after successful submission
        else:
            error_message = "Failed to add module. Please check your inputs."
            # Pass the form and error message to the template
            return render(request, 'book_detail.html', {'form': form, 'error_message': error_message})
    else:
        form = ModuleForm()
        return render(request, 'book_detail.html', {'form': form})


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


def activity_details(request, id):
    activity = get_object_or_404(Activity, id=id)
    # media = get_object_or_404(Media, id=id)
    return render(request, 'activity_details.html', {'activity': activity})




def get_books(request, instrument_id):
    books = Book.objects.filter(bookinstrument__instrumentID=instrument_id)
    books_list = [{"id": book.id, "book": book.book} for book in books]
    return JsonResponse({"books": books_list})



def navbar(request):
    return render(request,'navbar_accounts.html')

def navbartest(request):
    return render(request,'navbartest.html')

@admin_required
def dashboard(request):

    return render(request, 'dashboard.html')
    