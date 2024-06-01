from django.shortcuts import render
from .decorators import teacher_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from administrator.models import Student, Teacher, Instrument, Book, BookInstrument, ModuleDetails
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from collections import defaultdict, Counter
from .models import ProgressBar
from django.contrib import messages
from django.db.models import Count, F, Q
# Create your views here.

@teacher_required
def teacher(request):
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
        template = loader.get_template('master_teacher.html')
        return HttpResponse(template.render(context, request))
    else:
        # Redirect or handle unauthenticated users as needed
        # For example, you might want to redirect them to the login page
        return HttpResponse("")
    

@teacher_required
def teaching_modules(request):
    # Get the logged-in user
    user = request.user

    # Get all teacher objects associated with the logged-in user
    teachers = Teacher.objects.filter(teacher__user=user)

    # Collect all instruments associated with these teachers
    instruments = Instrument.objects.filter(id__in=teachers.values_list('instrument_id', flat=True))

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

    students = Student.objects.filter(
        assigned_teacher=teacher,
        instrument__instrument_major_name=instrument_major,
        instrument__instrument_minor_name=instrument_minor,
        current_book_id=book_id
    ).annotate(
        pass_progress_count=Count('progressbar', filter=Q(progressbar__result__in=['3','4', '5']))
    )

    for student in students:
        total_progress = ModuleDetails.objects.filter(bookInstrument_id=book_id).count()
        pass_progress = student.pass_progress_count

        if total_progress > 0:
            student.progress_percentage = (pass_progress / total_progress) * 100
        else:
            student.progress_percentage = 0

        student.remaining_progress_percentage = 100 - student.progress_percentage

        # Additional debugging output
        print(f"Student: {student.studentName}, Total Progress: {total_progress}, Pass Progress: {pass_progress}")
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
    student_book = student.current_book

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
    student_book = student.current_book

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