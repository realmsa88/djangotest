from django.shortcuts import render
from .decorators import teacher_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from administrator.models import Student, Teacher, Instrument, Book, BookInstrument, ModuleDetails, auth_user_details,Activity, StudentActivity, Media, Album
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from collections import defaultdict, Counter
from .models import ProgressBar, Attendance
from django.contrib import messages
from django.db.models import Count, F, Q, Avg
from django.views.decorators.http import require_POST
import json, logging
from pytz import timezone as pytz_timezone
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models.functions import ExtractWeek, ExtractYear
from django.core.exceptions import MultipleObjectsReturned
# Create your views here.
@login_required
def teacher(request):
    if request.user.is_authenticated:
        try:
            user_details = request.user.auth_user_details
        except auth_user_details.DoesNotExist:
            return HttpResponse("User details do not exist.")

        # Retrieve all teachers associated with the current user
        teachers = Teacher.objects.filter(teacher=user_details)

        if teachers.exists():
            # Initialize lists to store data
            instrument_data = []
            student_progress = []
            attendance_data = []

            # Fetch only the instruments taught by the teacher
            instruments_taught = Instrument.objects.filter(teacher__in=teachers)

            # Prepare instruments for dropdown
            instruments_choices = instruments_taught.values('instrument_minor_name', 'instrument_major_name')

            for instrument in instruments_taught:
                students_under_instrument = Student.objects.filter(assigned_teacher=user_details.user, instrument=instrument)
                student_progress_query = ProgressBar.objects.filter(student__in=students_under_instrument)

                # Calculate average progress
                if student_progress_query.exists():
                    average_progress = student_progress_query.aggregate(avg_progress=Avg('result'))['avg_progress']
                else:
                    average_progress = 0

                instrument_data.append({
                    'instrument_name': instrument.instrument_minor_name,
                    'instrument_minor_name': instrument.instrument_minor_name,
                    'average_progress': average_progress,
                    'students_count': students_under_instrument.count()
                })

            # Retrieve student progress for all students taught by this teacher
            students = Student.objects.filter(assigned_teacher=user_details.user).annotate(
                pass_progress_count=Count('progressbar', filter=Q(progressbar__result__in=['3', '4', '5']))
            )

            for student in students:
                total_modules = ModuleDetails.objects.filter(
                    bookInstrument__bookID_id=student.book_id,
                    bookInstrument__instrumentID_id=student.instrument_id
                ).count()

                pass_modules = ProgressBar.objects.filter(student=student, result__in=['3', '4', '5']).count()

                if total_modules > 0:
                    progress_percentage = (pass_modules / total_modules) * 100
                else:
                    progress_percentage = 0

                student_progress.append({
                    'studentName': student.studentName,
                    'progress_percentage': progress_percentage,
                    'total_modules': total_modules,
                    'student_id': student.id
                })

            # Retrieve attendance data for all students taught by this teacher
            attendance_data_query = Attendance.objects.filter(
                teacher_email=user_details.user,
                status='Approved'
            ).annotate(
                week=ExtractWeek('date'),
                year=ExtractYear('date')
            ).values('student__id', 'student__studentName', 'week', 'year').annotate(
                attendance_count=Count('id', filter=Q(attendance='Attend')),
                absence_count=Count('id', filter=Q(attendance='Absent'))
            )

            attendance_data.extend(attendance_data_query)

            # Prepare context for rendering the template
            context = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'students_count': Student.objects.filter(assigned_teacher=user_details.user).count(),
                'total_instruments_taught': instruments_taught.count(),
                'instrument_data': instrument_data,
                'instruments_choices': instruments_choices,
                'student_progress': json.dumps(student_progress),
                'attendance_data': json.dumps(list(attendance_data))
            }

            return render(request, 'master_teacher.html', context)
        
        else:
            return HttpResponse("Teacher record does not exist for the logged-in user.")

    else:
        return HttpResponse("You are not logged in.")




@teacher_required
def teaching_modules(request):
    try:
        # Get the logged-in user's auth_user_details instance
        user_details = auth_user_details.objects.get(user=request.user)
    except auth_user_details.DoesNotExist:
        # Handle case where auth_user_details doesn't exist for the logged-in user
        return render(request, 'error.html', {'message': 'User details not found.'})

    # Get all Teacher objects associated with the user's auth_user_details instance
    teachers = Teacher.objects.filter(teacher=user_details)

    # Collect all instruments associated with these teachers
    instruments = Instrument.objects.filter(id__in=teachers.values_list('instrument', flat=True))

    # Get all unique major names
    instrument_majors = instruments.values_list('instrument_major_name', flat=True).distinct()

    # Get all book IDs associated with these instruments
    book_ids = BookInstrument.objects.filter(instrumentID__in=instruments).values_list('bookID', flat=True)

    # Get all books corresponding to the retrieved book IDs
    books = Book.objects.filter(id__in=book_ids)

    # Pass the instruments, books, and instrument majors to the template
    context = {
        'instruments': instruments,
        'books': books,
        'instrument_majors': instrument_majors,
    }

    return render(request, 'teaching_modules.html', context)


@teacher_required
def student_progress(request, instrument_minor, instrument_major, book_id):
    teacher = request.user

    # Fetch students assigned to the teacher with the specified instrument and book
    students = Student.objects.filter(
        assigned_teacher=teacher,
        instrument__instrument_major_name=instrument_major,
        instrument__instrument_minor_name=instrument_minor,
        book_id=book_id
    ).annotate(
        pass_progress_count=Count('progressbar', filter=Q(progressbar__result__in=['3', '4', '5']))
    )

    for student in students:
        # Calculate total modules for the specific book and instrument
        total_modules = ModuleDetails.objects.filter(bookInstrument__bookID_id=book_id,
                                                     bookInstrument__instrumentID_id=student.instrument_id).count()
        # Calculate passed modules for the student
        pass_modules = ProgressBar.objects.filter(student=student, result__in=['3', '4', '5']).count()

        if total_modules > 0:
            student.progress_percentage = (pass_modules / total_modules) * 100
        else:
            student.progress_percentage = 0

        student.remaining_progress_percentage = 100 - student.progress_percentage

        # Additional debugging output
        print(f"Student: {student.studentName}, Total Modules: {total_modules}, Passed Modules: {pass_modules}")
        print(f"Progress Percentage: {student.progress_percentage}")
        print(f"Remaining Progress Percentage: {student.remaining_progress_percentage}")

    context = {
        'students': students,
        'instrument_major': instrument_major,
        'instrument_minor': instrument_minor,
        'book_id': book_id,
    }

    return render(request, 'student_progress.html', context)

@teacher_required
def student_results(request, student_name):
    student = get_object_or_404(Student, studentName=student_name)
    student_instrument = student.instrument
    student_book = student.book

    # Get the related BookInstrument entries for the student's book and instrument
    book_instruments = BookInstrument.objects.filter(bookID=student_book, instrumentID=student_instrument)

    if not book_instruments.exists():
        return HttpResponse("No matching BookInstrument found for the student's book.")
    
    # Get ModuleDetails entries that relate to the BookInstrument entries
    module_details = ModuleDetails.objects.filter(bookInstrument__in=book_instruments)

    module_types = set(module.module_type for module in module_details)
    results_by_module = {module: [] for module in module_details}

    # Get ProgressBar entries for the student and the modules found
    progress_bar_objects = ProgressBar.objects.filter(student=student, module__in=module_details)

    for progress_bar in progress_bar_objects:
        results_by_module[progress_bar.module].append(progress_bar.result)
    
    # Calculate progress for Practice modules
    practice_modules = module_details.filter(module_type='Practice')
    total_practice_modules = practice_modules.count()
    passed_practice_modules = progress_bar_objects.filter(module__in=practice_modules, result__in=['3','4', '5']).count()
    practice_completion_percentage = (passed_practice_modules / total_practice_modules) * 100 if total_practice_modules > 0 else 0

    # Calculate progress for Repertoire modules
    repertoire_modules = module_details.filter(module_type='Repertoire')
    total_repertoire_modules = repertoire_modules.count()
    passed_repertoire_modules = progress_bar_objects.filter(module__in=repertoire_modules, result__in=['3','4', '5']).count()
    repertoire_completion_percentage = (passed_repertoire_modules / total_repertoire_modules) * 100 if total_repertoire_modules > 0 else 0

    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        result = request.POST.get('result')
        
        module = get_object_or_404(ModuleDetails, id=module_id)
        progress_bar, created = ProgressBar.objects.get_or_create(student=student, module=module)
        progress_bar.result = result
        progress_bar.save()
        
        messages.success(request, f'Result for {module.module_name} updated successfully.')
        return redirect('student_results', student_name=student_name)

    context = {
        'student': student,
        'book_id': student_book.id,
        'instrument_major_name': student_instrument.instrument_major_name,
        'instrument_minor_name': student_instrument.instrument_minor_name,
        'module_types': module_types,
        'results_by_module': results_by_module,
        'practice_completion_percentage': practice_completion_percentage,
        'repertoire_completion_percentage': repertoire_completion_percentage,
    }

    return render(request, 'student_results.html', context)





@teacher_required
def update_student_result(request, student_name):
    student = get_object_or_404(Student, studentName=student_name)
    student_instrument = student.instrument
    student_book = student.book

    # Get the related BookInstrument entries for the student's book and instrument
    book_instruments = BookInstrument.objects.filter(bookID=student_book, instrumentID=student_instrument)

    if not book_instruments.exists():
        return HttpResponse("No matching BookInstrument found for the student's book.")
    
    # Get ModuleDetails entries that relate to the BookInstrument entries
    module_details = ModuleDetails.objects.filter(bookInstrument__in=book_instruments)

    module_types = set(module.module_type for module in module_details)
    results_by_module = {module: [] for module in module_details}

    # Get ProgressBar entries for the student and the modules found
    progress_bar_objects = ProgressBar.objects.filter(student=student, module__in=module_details)

    for progress_bar in progress_bar_objects:
        results_by_module[progress_bar.module].append(progress_bar.result)
    
    # Calculate progress for Practice modules
    practice_modules = module_details.filter(module_type='Practice')
    total_practice_modules = practice_modules.count()
    passed_practice_modules = progress_bar_objects.filter(module__in=practice_modules, result__in=['3','4', '5']).count()
    practice_completion_percentage = (passed_practice_modules / total_practice_modules) * 100 if total_practice_modules > 0 else 0

    # Calculate progress for Repertoire modules
    repertoire_modules = module_details.filter(module_type='Repertoire')
    total_repertoire_modules = repertoire_modules.count()
    passed_repertoire_modules = progress_bar_objects.filter(module__in=repertoire_modules, result__in=['3','4', '5']).count()
    repertoire_completion_percentage = (passed_repertoire_modules / total_repertoire_modules) * 100 if total_repertoire_modules > 0 else 0

    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        result = request.POST.get('result')
        
        module = get_object_or_404(ModuleDetails, id=module_id)
        progress_bar, created = ProgressBar.objects.get_or_create(student=student, module=module)
        progress_bar.result = result
        progress_bar.save()
        
        messages.success(request, f'Result for {module.module_name} updated successfully.')
        return redirect('student_results', student_name=student_name)

    context = {
        'student': student,
        'book_id': student_book.id,
        'instrument_major_name': student_instrument.instrument_major_name,
        'instrument_minor_name': student_instrument.instrument_minor_name,
        'module_types': module_types,
        'results_by_module': results_by_module,
        'practice_completion_percentage': practice_completion_percentage,
        'repertoire_completion_percentage': repertoire_completion_percentage,
    }

    return render(request, 'student_results.html', context)


def pass_values(request):
    # Retrieve 'PASS' values from your data source
    pass_values = [...]  # Retrieve pass values from your database or any other source
    return JsonResponse({'pass_values': pass_values})


from .models import Teacher
from django.template.loader import render_to_string
from django.http import JsonResponse

def get_attendance(request, student_id):
    # Retrieve attendance details for the given student
    attendance_details = Attendance.objects.filter(student_id=student_id).values('date', 'status', 'title', 'description', 'end_time', 'start_time')

    # Return the attendance details as JSON response
    return JsonResponse({'attendance_details': list(attendance_details)})



@login_required
def student_list_by_book(request, instrument_minor, instrument_major, book_id):
    user = request.user
    try:
        # Assuming auth_user_details is the related model to User that Teacher uses
        auth_user = auth_user_details.objects.get(user=user)
        teachers = Teacher.objects.filter(teacher=auth_user)  # Get the Teacher instances using auth_user_details
    except auth_user_details.DoesNotExist:
        return redirect('student-attendance')

    if not teachers.exists():
        return redirect('student-attendance')

    # Get the book
    book = get_object_or_404(Book, pk=book_id)

    # Filter students by the user (not the Teacher instance)
    students = Student.objects.filter(
        assigned_teacher=user,
        instrument__instrument_major_name=instrument_major,
        instrument__instrument_minor_name=instrument_minor,
        book_id=book_id
    ).annotate(
        pass_progress_count=Count('progressbar', filter=Q(progressbar__result__in=['3', '4', '5']))
    )

    # Fetch attendance records for each student
    for student in students:
        student.attendance = Attendance.objects.filter(student=student).values('title', 'date','description', 'status', 'end_time', 'start_time', 'attendance')

    context = {
        'book': book,
        'students': students,
        'instrument_minor': instrument_minor,
        'instrument_major': instrument_major
    }
    return render(request, 'students_by_book.html', context)


logger = logging.getLogger(__name__)

@csrf_exempt
def attend_student(request):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            # Get current local time
            current_time = datetime.now().time()
            print(f"Current time: {current_time}")
            print(f"User: {user.username}")

            ongoing_class = Attendance.objects.filter(
                teacher_email=user,
                start_time__lte=current_time,
                end_time__gte=current_time
            ).first()

            if ongoing_class:
                # Get the attendance ID of the ongoing class
                attendance_id = ongoing_class.id

                # Update the status of the ongoing class
                ongoing_class.status = 'Approved'
                ongoing_class.save()

                # return JsonResponse({
                #     'success': True,
                #     'status': 'Approved',
                #     'student_name': ongoing_class.student.studentName,
                #     'start_time': ongoing_class.start_time.strftime("%I:%M %p"),
                #     'end_time': ongoing_class.end_time.strftime("%I:%M %p"),
                #     'attendance_id': attendance_id
                # })
                messages.success(request, "Attendance verified and approved successfully!")
                return redirect('student-attendance') 
            
            
            else:
                print("No ongoing class found")
                return JsonResponse({'success': False, 'error': 'No ongoing class found at the current time for the current teacher.'})
        else:
            print("User not authenticated")
            return JsonResponse({'success': False, 'error': 'User not authenticated.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def attendance(request):
    try:
        teacher_instances = Teacher.objects.filter(teacher=request.user.auth_user_details)
        
        if teacher_instances.exists():
            teacher_instance = teacher_instances.first()  # Assuming we only take the first instance
        else:
            return render(request, 'student_attendance.html', {'error': 'Teacher does not exist for the logged-in user'})
        
    except MultipleObjectsReturned:
        return render(request, 'student_attendance.html', {'error': 'Multiple Teacher instances found for the logged-in user'})
    
    instruments = Instrument.objects.filter(teacher=teacher_instance)
    instrument_majors = instruments.values_list('instrument_major_name', flat=True).distinct()
    book_ids = BookInstrument.objects.filter(instrumentID__in=instruments).values_list('bookID', flat=True)
    books = Book.objects.filter(id__in=book_ids)
    
    context = {
        'instruments': instruments,
        'books': books,
        'instrument_majors': instrument_majors,
    }
    return render(request, 'student_attendance.html', context)


@login_required
def students_for_date(request, date):
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)
    
    current_time = datetime.now().time()
    
    # Retrieve the logged-in user
    user = request.user
    
    # Ensure the user is a teacher (if using groups or another method)
    # Example: Check if user belongs to a specific group named 'teachers'
    if not user.groups.filter(name='teacher').exists():
        return JsonResponse({'error': 'User is not authorized as a teacher'}, status=403)
    
    # Fetch attendance records for the selected date and teacher (logged-in user)
    students = Attendance.objects.filter(date=selected_date, teacher_email=user).select_related('student')
    
    student_data = []
    for attendance in students:
        start_time = attendance.start_time
        end_time = attendance.end_time
        is_ongoing = start_time <= current_time <= end_time
        
        student_data.append({
            'name': attendance.student.studentName,
            'start_time': start_time.strftime("%H:%M:%S"),
            'end_time': end_time.strftime("%H:%M:%S"),
            'is_ongoing': is_ongoing
        })
    
    return JsonResponse({'students': student_data})





from datetime import datetime, time


@login_required
def student_attendance_view(request):
    current_time = datetime.now().time()
    current_date = datetime.now().date()
    
    try:
        teacher_instance = auth_user_details.objects.get(user=request.user).teacher
    except auth_user_details.DoesNotExist:
        return render(request, 'student_attendance.html', {'error': 'Teacher does not exist for the logged-in user'})
    
    ongoing_classes = Attendance.objects.filter(date=current_date, start_time__lte=current_time, end_time__gte=current_time, teacher=teacher_instance)
    
    context = {
        'ongoing_classes': ongoing_classes,
        'current_date': current_date,
    }
    return render(request, 'student_attendance.html', context)


@login_required
def attendance_list(request):
    # Get the current user details
    current_user = request.user

    # Retrieve the corresponding auth_user_details instance
    try:
        user_details = auth_user_details.objects.get(user=current_user)
    except auth_user_details.DoesNotExist:
        # Handle the case where no auth_user_details instance is found
        user_details = None

    # Retrieve all attendance records associated with the current user
    if user_details:
        all_attendance = Attendance.objects.filter(teacher_email=user_details.user)
        for attendance in all_attendance:
            attendance.instrument_major_name = attendance.student.instrument
            attendance.picture_url = attendance.student.picture.url if attendance.student.picture else 'http://bootdey.com/img/Content/avatar/avatar1.png'
    else:
        all_attendance = []

    # Debug prints for verification
    print("Current User:", current_user)
    print("All Attendance:", all_attendance)

    # Initialize counters
    total_attend_approved = 0
    total_attend_pending = 0
    total_absent_approved = 0
    total_absent_pending = 0

    # Calculate totals
    for attendance in all_attendance:
        if attendance.attendance == 'Attend':
            if attendance.status == 'Approved':
                total_attend_approved += 1
            elif attendance.status == 'Pending Verification':
                total_attend_pending += 1
        elif attendance.attendance == 'Absent':
            if attendance.status == 'Approved':
                total_absent_approved += 1
            elif attendance.status == 'Pending Verification':
                total_absent_pending += 1

    # Render the template with context data
    return render(request, 'attendance_list.html', {
        'attendance_list': all_attendance,
        'total_attend_approved': total_attend_approved,
        'total_attend_pending': total_attend_pending,
        'total_absent_approved': total_absent_approved,
        'total_absent_pending': total_absent_pending,
    })




@require_POST
def verify_attendance(request):
    # Get attendance_id from POST data
    attendance_id = request.POST.get('attendance_id')

    # Ensure attendance_id is valid and not empty
    if attendance_id:
        try:
            # Attempt to retrieve Attendance object by id
            attendance = Attendance.objects.get(id=int(attendance_id))
            attendance.status = 'Approved'
            attendance.save()
            messages.success(request, "Attendance verified and approved successfully!")
            return redirect('attendance-list')
        except ObjectDoesNotExist:
            # Handle case where Attendance record does not exist
            messages.error(request, "Attendance record not found or could not be verified.")
            return redirect('attendance-list')
        except ValueError as e:
            # Handle case where attendance_id conversion to int fails
            messages.error(request, f"Invalid attendance ID format: {e}")
            return redirect('attendance-list')
    else:
        # Handle case where attendance_id is empty
        messages.error(request, "Attendance ID is empty or invalid.")
        return redirect('attendance-list')



def activity_list_teacher(request):
    category = request.GET.get('category')
    if category:
        activities = Activity.objects.filter(activity_type=category)
    else:
        activities = Activity.objects.all()

    activity_types = Activity.objects.values_list('activity_type', flat=True).distinct()
    return render(request, 'activity_list_teacher.html', {
        'activities': activities,
        'activity_types': activity_types,
    })








@teacher_required
def media (request) :
    activities = Activity.objects.all()

    context = {
        'activities' : activities
    }
    
    return render(request, 'media_teacher.html', context)


def upload_media(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        # Create a new instance of Media associated with the activity
        media = Media(activity=activity, media_name=file)
        media.save()
        
        return JsonResponse({'message': 'File uploaded successfully.'})
    
    return JsonResponse({'error': 'File upload failed.'}, status=400)

@csrf_exempt
def activity_details(request, id):
    try:
        # Retrieve the Activity instance
        activity = get_object_or_404(Activity, pk=id)
        
        # Process file upload logic
        if request.method == 'POST' and request.FILES:
            files = request.FILES.getlist('media_files')
            logger.debug(f"Files received: {files}")
            
            # Retrieve the related Album instance (assuming one album per activity for simplicity)
            album = Album.objects.filter(activityID=activity).first()
            
            if not album:
                logger.error("No album found for this activity.")
                return JsonResponse({'success': False, 'message': 'No album found for this activity.'})
            
            for file in files:
                media_type = 'image' if file.content_type.startswith('image') else 'video'
                try:
                    Media.objects.create(
                        albumID=album,
                        media_type=media_type,
                        media_name=file,
                    )
                    logger.info(f"File {file.name} uploaded successfully and stored as media.")
                except Exception as e:
                    logger.error(f"Failed to upload file {file.name}: {str(e)}")
                    return JsonResponse({'success': False, 'message': f'Failed to upload file {file.name}: {str(e)}'})
            
            # Return JSON response indicating success
            return JsonResponse({'success': True, 'message': 'File(s) uploaded successfully.'})

        # Handle GET requests to render the template
        albums = Album.objects.filter(activityID=activity).order_by('-id')
        media_items = Media.objects.filter(albumID__in=albums).order_by('-id')
        return render(request, 'activity_details_teacher.html', {'activity': activity, 'albums': albums, 'media_items': media_items})
    
    except Exception as e:
        logger.error(f"Error in activity_details view: {str(e)}")
        return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})
    




def delete_media(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    media.delete()
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))







@login_required
def view_report(request, student_id):
    # Retrieve parent associated with the logged-in user
    teacher = request.user  # Assuming parent is directly related to User model

    student = get_object_or_404(Student, id=student_id)
    
    # Fetch related data for the student
    book_instruments = BookInstrument.objects.filter(bookID=student.book, instrumentID=student.instrument)
    module_details = ModuleDetails.objects.filter(bookInstrument__in=book_instruments)
    
    # Fetch progress bar objects for the student and modules found
    progress_bar_objects = ProgressBar.objects.filter(student=student, module__in=module_details)

    print(f"Logged-in parent: {teacher}")

    # Get students related to this parent
    students = Student.objects.filter(assigned_teacher=teacher)

    # Print debug information
    print(f"Related students: {students}")

    # Retrieve all attendance records associated with the parent user
    all_attendance = Attendance.objects.filter(student=student, student__assigned_teacher=teacher)

    
    # Prepare results by module
    results_by_module = {}
    for progress_bar in progress_bar_objects:
        results_by_module[progress_bar.module_id] = progress_bar.result
        print(f"Module ID: {progress_bar.module_id}, Result: {progress_bar.result}")
    
    
    # Calculate progress for Practice modules
    practice_modules = module_details.filter(module_type='Practice')
    total_practice_modules = practice_modules.count()
    passed_practice_modules = progress_bar_objects.filter(module__in=practice_modules, result__in=['3', '4', '5']).count()
    practice_completion_percentage = (passed_practice_modules / total_practice_modules) * 100 if total_practice_modules > 0 else 0
    
    # Calculate progress for Repertoire modules
    repertoire_modules = module_details.filter(module_type='Repertoire')
    total_repertoire_modules = repertoire_modules.count()
    passed_repertoire_modules = progress_bar_objects.filter(module__in=repertoire_modules, result__in=['3', '4', '5']).count()
    repertoire_completion_percentage = (passed_repertoire_modules / total_repertoire_modules) * 100 if total_repertoire_modules > 0 else 0
    
    # Prepare data to be passed to the template
    context = {
        'student': student,
        'practice_completion_percentage': practice_completion_percentage,
        'repertoire_completion_percentage': repertoire_completion_percentage,
        'results_by_module': results_by_module,
        'module_details': module_details,
        'all_attendance': all_attendance  # Include attendance data
    }
    
    return render(request, 'report_template_teacher.html', context)

def activity_students_list_teacher(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    student_activities = StudentActivity.objects.filter(activity=activity)

    students_list = []
    for student_activity in student_activities:
        student = student_activity.student
        students_list.append({
            'studentName': student.studentName,
            'instrument_major_name': student.instrument.instrument_major_name,
            'instrument_minor_name': student.instrument.instrument_minor_name,
            'book' : student.book,
            'gender' : student.gender,
            'teacher_first_name' : student.assigned_teacher.first_name,
            'teacher_last_name' : student.assigned_teacher.last_name,
            'age' : student.age  # Adjust as per your Instrument model
        })

    context = {
        'activity': activity,
        'students_list': students_list,
    }

    return render(request, 'activity_info_teacher.html', context)
