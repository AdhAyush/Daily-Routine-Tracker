from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import login, authenticate, logout
from datetime import time
import json
from datetime import date , datetime, timedelta
from django.contrib import messages
from django.http import JsonResponse
from .tasks import your_midnight_task

def add_times(time1, time2):
    """
    Add two `datetime.time` objects and return the resulting `datetime.time`.
    Handles overflow of minutes into hours correctly.
    """
    total_seconds = (time1.hour * 3600 + time1.minute * 60) + (time2.hour * 3600 + time2.minute * 60)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return time(hour=hours, minute=minutes)


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    
    user = request.user
    today = date.today()

    tasks = []


    progress = 0
    try:
        info = Info.objects.get(user = user)
    except Info.DoesNotExist:
        info = Info(user = user)
        info.save()
        
    
    print(info.streak)
    streak = info.streak 
    score = 0

    if DayPlan.objects.filter(user=user, date=today).exists():

        plan = DayPlan.objects.get(user=user, date=today)
        tasks = Task.objects.filter(DayPlan=plan)
        
        score = plan.score

        completed_time = (0, 0)
        total_time = (0, 0)
        
        for task in tasks:
            
            total_time= (total_time[0]+ task.estimated_time.hour, total_time[1] + task.estimated_time.minute) 
            if task.is_completed:
                completed_time = (completed_time[0]+ task.estimated_time.hour, completed_time[1]+task.estimated_time.minute)
        progress = (completed_time[0]*60 +completed_time[1])/(total_time[0]*60 + total_time[1])*100
        
    
    return render(request, 'index.html', {'tasks': tasks, 
                                          'progress': int(progress) , 
                                          'streak': streak , 
                                          'score': score})

def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not CustomUser.objects.filter(email=email).exists():
            return render(request, 'login.html', {'error': 'User does not exist'})

        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        profession = request.POST.get('profession')
        password = request.POST.get('password')

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'User with this email already exists'})

        # Save the user to the database
        user = CustomUser(name=name, email=email, profession=profession)
        user.set_password(password)  # Use set_password to hash the password
        user.save()

        # Create an Info object for the user
        info = Info(user=user)
        info.save()


        login(request, user)
        response = render(request, 'index.html')
        response.set_cookie('user', user.email)
        return response

def logout_view(request):
    logout(request)
    return redirect('home')


def plans(request):
    return render(request, 'plan.html', {'editable': True})

def analytics(request):
    return redirect('home')

def completed(request):
    if request.method == 'GET':
        user = request.user
        day = request.GET.get('date')
        
        if not day:
            day = date.today().strftime('%Y-%m-%d')

        tasks = []
        if DayPlan.objects.filter(user=user, date=day).exists():
            plan = DayPlan.objects.get(user=user, date=day)
            tasks = Task.objects.filter(DayPlan=plan)

            if day == str(date.today().strftime('%Y-%m-%d')):
                return render(request, 'completed.html', {'tasks': tasks, 'editable': True, 'date': day})
            else:
                return render(request, 'completed.html', {'tasks': tasks, 'editable': False , 'date': day})

        return render(request, 'completed.html', {'tasks': tasks, 'editable': False, 'date': day})

    return redirect('home')

def get_completed_by_date(request):
    if request.method == "GET":
        user = request.user
        date = request.GET.get('date')

        tasks = []
        if not date:
            return JsonResponse({'error': 'Date is required'}, status=400)
        if DayPlan.objects.filter(user=user, date=date).exists():
            plan = DayPlan.objects.get(user=user, date=date)
            tasks = Task.objects.filter(DayPlan=plan, is_completed=True)

            if date == str(date.today()):
                return render(request, 'completed.html', {'tasks': tasks, 'editable': True})
            else:
                return JsonResponse({'tasks': tasks, 'editable': False})
        
        return JsonResponse({'tasks': tasks, 'editable': False})



def add_plan(request):
    if request.method =="POST":

        task_data = json.loads(request.POST.get('taskData'))
            
            # Extract data from the received JSON
        date = task_data.get('date')
        task = task_data.get('tasks', [])
        hour = task_data.get('hrs', [])
        minute = task_data.get('mins', [])
        category = task_data.get('categories', [])

        print(date, task, hour, minute, category)

        
        is_completed = False
        user = request.user

        if not date or not task or not category or not hour or not minute:
            return render(request, 'plan.html', {'error': 'All fields are required', 'editable': True})

        if not (len(task) == len(category) == len(hour) == len(minute)):
            return render(request, 'plan.html', {'error': 'Mismatched data in tasks, categories, or times.', 'editable': True})
    
        plan, created = DayPlan.objects.get_or_create(user=user, date=date)    
    
        Task.objects.filter(DayPlan=plan).delete()
        
       
        # Example usage in your existing code
        total_compulsary_time = time(hour=0, minute=0)
        total_optional_time = time(hour=0, minute=0)

        for tsk, ctgory, hr, mins in zip(task, category, hour, minute):
            estimated_time = time(hour=int(hr), minute=int(mins))
            task = Task(DayPlan=plan, task=tsk, category=ctgory, estimated_time=estimated_time)
            task.save()

            if ctgory == 'Compulsory':
                total_compulsary_time = add_times(total_compulsary_time, estimated_time)
            else:
                total_optional_time = add_times(total_optional_time, estimated_time)

        plan.total_compulsary_time = total_compulsary_time
        plan.total_optional_time = total_optional_time
        plan.save()

        print("task added")



        return render(request, 'plan.html', {'success': 'Plan added successfully', 'editable': True})

        
def get_plans(request):
    if request.method == 'GET':
        user = request.user
        day = request.GET.get('date')
        
       
        if not day:  # Check if day parameter is provided
            return JsonResponse({'error': 'Date is required', 'editable': True}, status=400)

       
        try:
            # Parse the date string into a date object
            date_from_request = datetime.strptime(day, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD.', 'editable': True}, status=400)     
        
        print(date_from_request)

        today = date.today()
        if date_from_request<today:
            editable = False
        else:
            editable = True 
        
        if DayPlan.objects.filter(user=user, date=day).exists():
            plan = DayPlan.objects.get(user=user, date=day)
            tasks = Task.objects.filter(DayPlan=plan)

            task_data = []
            for task in tasks:
                task_data.append({
                    'name': task.task,
                    'hours': task.estimated_time.hour,
                    'minutes': task.estimated_time.minute,
                    'category': task.category,
                })
            
            
            return JsonResponse({'tasks': task_data, 'editable': editable})
        
        # Return an empty tasks list if no DayPlan exists for the date
        return JsonResponse({'tasks': [], 'editable': editable})
    
    # If the request method is not GET, return a 405 Method Not Allowed error
    return JsonResponse({'error': 'Invalid request method', 'editable':editable}, status=405)
        
def update_completed(request):
    if request.method == 'POST':
        try:
            streak = True
            # Iterate over POST data to update tasks
            for key, value in request.POST.items():
                if key.startswith('is_completed_'):
                    # Extract task ID
                    task_id = key.split('_')[2]
                    is_completed = value == 'true'


                    # Get remarks for this task
                    remarks_key = f'remarks_{task_id}'
                    remarks = request.POST.get(remarks_key, '').strip()


                    # Update the task in the database
                    Task.objects.filter(id=task_id).update(
                        is_completed=is_completed,
                        remarks=remarks
                    )
                    

            messages.success(request, "Tasks updated successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        check_and_update_streak(request.user)
        check_and_update_score(request.user)
        # Redirect back to the completed tasks page
        return redirect('/completed/')

    # If not a POST request, redirect to the tasks page
    return redirect('/completed/')


def check_and_update_streak(CustomUser):
    today = date.today()
    
    if DayPlan.objects.filter(user = CustomUser, date = today):
        dayPlan = DayPlan.objects.get(user = CustomUser, date = today)
        if dayPlan.completed:
            return True
        else:
            tasks = Task.objects.filter(DayPlan = dayPlan)
            
            flag = True
            for task in tasks:
                if not task.is_completed and task.category == 'Compulsory':
                    flag = False
                    return False

            if flag:
                dayPlan.completed = True
                info = Info.objects.get(user = CustomUser)
                info.streak += 1
                info.save()
                dayPlan.save()
                return True
    else:
        return False


def check_and_update_score(CustomUser):
    user = CustomUser
    today = date.today()
    if DayPlan.objects.filter(user = user, date = today).exists():
        plan = DayPlan.objects.get(user = user, date = today)
        tasks = Task.objects.filter(DayPlan = plan)
        
        completed_compulsary_time = (0, 0)
        completed_optional_time = (0, 0)

        

        for task in tasks:
            if task.is_completed and task.category == 'Compulsory':
                completed_compulsary_time = (completed_compulsary_time[0]+ task.estimated_time.hour, completed_compulsary_time[1]+task.estimated_time.minute)
            elif task.is_completed and task.category == 'Optional':
                completed_optional_time = (completed_optional_time[0]+ task.estimated_time.hour, completed_optional_time[1]+task.estimated_time.minute)
            else:
                continue
        try:
            compulsary_score = (completed_compulsary_time[0]*60 + completed_compulsary_time[1])/ (plan.total_compulsary_time.hour*60 + plan.total_compulsary_time.minute) * 9.5
        except ZeroDivisionError:
            compulsary_score = 0
        
        try:
            optional_score = (completed_optional_time[0]*60 + completed_optional_time[1])/ (plan.total_optional_time.hour*60 + plan.total_optional_time.minute) * 0.5
        except ZeroDivisionError:
            optional_score = 0

        plan.score = compulsary_score + optional_score
        plan.save()

        

def get_progress(request):
    if request.method == 'GET':
        user = request.user
        today = date.today()

        if DayPlan.object.filter(user = user, date = today).exist():
            plan = DayPlan.objects.get(user = user, date = today)
            tasks = Task.objects.filter(DayPlan = plan)

            completed_time = (0, 0)
            total_time = (0, 0)
            

            for task in tasks:
                
                total_time= (total_time[0]+ task.estimated_time.hour, total_time[1] + task.estimated_time.minute) 

                if task.is_completed:
                    completed_time = (completed_time[0]+ task.estimated_time.hour, completed_time[1]+task.estimated_time.minute)

            progress = (completed_time[0]*60 +completed_time[1])/(total_time[0]*60 + total_time[1])*100

            response = JsonResponse({'progress': progress})
        else:
            response = JsonResponse({'prog total_compulsary_scoreress': 0})

        return response
    

from django.http import HttpResponse

def celery_test(request):
    your_midnight_task.delay()
    return HttpResponse("Task added to the queue")