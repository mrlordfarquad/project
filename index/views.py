from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .models import User, Choices, Questions, Answer, Form, Responses, DateOfBirth, UserGender, Image, UserCity
from django.core import serializers
from django.views.decorators.csrf import requires_csrf_token
import json
import random
import string
import csv
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.http import HttpResponseForbidden


def change_city(request):
    user_city, created = UserCity.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        selected_city = request.POST.get('City', '')
        user_city.city = selected_city
        user_city.save()
        # Now you can access the selected city directly through request.user.city
        return redirect('edit_profile')

    context = {}
    return render(request, 'index/edit-profile.html', context)


def change_date_of_birth(request):
    try:
        user_date_of_birth = request.user.dateofbirth
    except DateOfBirth.DoesNotExist:
        # Если профиля нет, создаем его с неопределенным полом
        user_date_of_birth = DateOfBirth(user=request.user, date_of_birth=None)
        user_date_of_birth.save()

    if request.method == 'POST':
        # Обработка формы
        new_date_of_birth = request.POST.get('date_of_birth', None)

        # Проверка, чтобы избежать изменения гендера другого пользователя
        if request.user.dateofbirth.id != user_date_of_birth.id:
            return HttpResponseForbidden("You do not have permission to perform this action.")

        user_date_of_birth.date_of_birth = new_date_of_birth
        user_date_of_birth.save()
        return redirect('edit_profile')

    context = {'user': request.user}
    return render(request, 'index/edit-profile.html', context)

def delete_date_of_birth(request):
    user = request.user
    try:
        user_date_of_birth = DateOfBirth.objects.get(user=user)
        user_date_of_birth.delete()
        return redirect('edit_profile')
    except DateOfBirth.DoesNotExist:
        return HttpResponse("Date of Birth not found", status=404)

@login_required
def change_gender(request):
    # Проверяем, имеет ли пользователь профиль с гендером
    try:
        user_gender = request.user.usergender
    except UserGender.DoesNotExist:
        # Если профиля нет, создаем его с неопределенным полом
        user_gender = UserGender(user=request.user, gender='O')
        user_gender.save()

    if request.method == 'POST':
        # Обработка формы
        new_gender = request.POST.get('gender', 'O')

        # Проверка, чтобы избежать изменения гендера другого пользователя
        if request.user.usergender.id != user_gender.id:
            return HttpResponseForbidden("You do not have permission to perform this action.")

        user_gender.gender = new_gender
        user_gender.save()
        return redirect('edit_profile')

    context = {'user': request.user}
    return render(request, 'index/edit-profile.html', context)

@login_required
def change_username(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        if new_username:
            request.user.username = new_username
            request.user.save()
            messages.success(request, 'Username успешно изменен.')
        else:
            messages.error(request, 'Пожалуйста, введите новый username.')

    return redirect('edit_profile')

@login_required
def change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Email успешно изменен.')
        else:
            messages.error(request, 'Пожалуйста, введите новый email.')

    return redirect('edit_profile')

def change_profile_image(request):
    if request.method == 'POST':
        image_url = request.POST.get('imageURL')

        # Проверяем, что пользователь авторизован, прежде чем изменять фотографию
        if request.user.is_authenticated:
            user = request.user
            # Создаем или обновляем запись Image для пользователя
            image_instance, created = Image.objects.get_or_create(user=user)
            image_instance.image_url = image_url
            image_instance.save()

    return redirect('edit_profile')

def delete_profile_image(request):
    if request.method == 'POST':
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Get the user's Image instance
            image_instance = request.user.image_info.first()

            # If the user has a profile image, delete it
            if image_instance:
                image_instance.delete()

    return redirect('edit_profile')


def delete_forms(request):
    if request.method == 'DELETE':
        form_ids = request.POST.getlist('forms[]')  # Ensure the correct parameter name
        # Perform the deletion logic based on the form_ids
        # Example: Form.objects.filter(id__in=form_ids).delete()
        return JsonResponse({'message': 'Forms deleted successfully'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    forms = Form.objects.filter(creator = request.user)
    return render(request, "index/index.html", {
        "forms": forms
    })

def login_view(request):
    #Check if the user is logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username = username, password = password)
        # if user authentication success
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "index/loginregister.html", {
                "message": "Invalid username and/or password"
            })
    return render(request, "index/loginregister.html")

def register(request):
    #Check if the user is logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        email = request.POST["email"]
        confirmation = request.POST["confirmation"]
        #check if the password is the same as confirmation
        if password != confirmation:
            return render(request, "index/loginregister.html", {
                "message": "Passwords must match."
            })
        #Checks if the username is already in use
        if User.objects.filter(email = email).count() == 1:
            return render(request, "index/loginregister.html", {
                "message": "Email already taken."
            })
        try:
            user = User.objects.create_user(username = username, password = password, email = email)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        except IntegrityError:
            return render(request, "index/loginregister.html", {
                "message": "Username already taken"
            })
    return render(request, "index/loginregister.html")


def logout_view(request):
    #Logout the user
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def create_form(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        data = json.loads(request.body)
        title = data["title"]
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        choices = Choices(choice = "Вариант 1")
        choices.save()
        question = Questions(question_type = "multiple choice", question= "Без названия", required= False)
        question.save()
        question.choices.add(choices)
        question.save()
        form = Form(code = code, title = title, creator=request.user)
        form.save()
        form.questions.add(question)
        form.save()
        return JsonResponse({"message": "Success", "code": code})
    else:
        return render(request, 'error/404.html');

def edit_form(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    return render(request, "index/form.html", {
        "code": code,
        "form": formInfo
    })

def edit_title(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        if len(data["title"]) > 0:
            formInfo.title = data["title"]
            formInfo.save()
        else:
            formInfo.title = formInfo.title[0]
            formInfo.save()
        return JsonResponse({"message": "Success", "title": formInfo.title})

def edit_description(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.description = data["description"]
        formInfo.save()
        return JsonResponse({"message": "Success", "description": formInfo.description})

def edit_bg_color(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.background_color = data["bgColor"]
        formInfo.save()
        return JsonResponse({"message": "Success", "bgColor": formInfo.background_color})

def edit_text_color(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.text_color = data["textColor"]
        formInfo.save()
        return JsonResponse({"message": "Success", "textColor": formInfo.text_color})

def edit_setting(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.collect_email = data["collect_email"]
        formInfo.is_quiz = data["is_quiz"]
        formInfo.authenticated_responder = data["authenticated_responder"]
        formInfo.confirmation_message = data["confirmation_message"]
        formInfo.edit_after_submit = data["edit_after_submit"]
        formInfo.allow_view_score = data["allow_view_score"]
        formInfo.save()
        return JsonResponse({'message': "Success"})

def delete_form(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        #Delete all questions and choices
        for i in formInfo.questions.all():
            for j in i.choices.all():
                j.delete()
            i.delete()
        for i in Responses.objects.filter(response_to = formInfo):
            for j in i.response.all():
                j.delete()
            i.delete()
        formInfo.delete()
        return JsonResponse({'message': "Success"})

def edit_question(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        question_id = data["id"]
        question = Questions.objects.filter(id = question_id)
        if question.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else: question = question[0]
        question.question = data["question"]
        question.question_type = data["question_type"]
        question.required = data["required"]
        if(data.get("score")): question.score = data["score"]
        if(data.get("answer_key")): question.answer_key = data["answer_key"]
        question.save()
        return JsonResponse({'message': "Success"})

def edit_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice_id = data["id"]
        choice = Choices.objects.filter(id = choice_id)
        if choice.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else: choice = choice[0]
        choice.choice = data["choice"]
        if(data.get('is_answer')): choice.is_answer = data["is_answer"]
        choice.save()
        return JsonResponse({'message': "Success"})


def add_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    form_info = Form.objects.filter(code=code)

    # Checking if form exists
    if form_info.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        form_info = form_info[0]

    # Checking if form creator is the current user
    if form_info.creator != request.user:
        return HttpResponseRedirect(reverse("403"))

    if request.method == "POST":
        data = json.loads(request.body)
        choice_number = form_info.questions.get(pk=data["question"]).choices.count() + 1
        choice_text = f"Вариант {choice_number}"

        # Create and save the choice
        choice = Choices(choice=choice_text)
        choice.save()

        # Add the choice to the form's question
        form_info.questions.get(pk=data["question"]).choices.add(choice)
        form_info.save()

        return JsonResponse({"message": "Success", "choice": choice.choice, "id": choice.id})

def remove_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice = Choices.objects.filter(pk = data["id"])
        if choice.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else: choice = choice[0]
        choice.delete()
        return JsonResponse({"message": "Success"})

def get_choice(request, code, question):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "GET":
        question = Questions.objects.filter(id = question)
        if question.count() == 0: return HttpResponseRedirect(reverse('404'))
        else: question = question[0]
        choices = question.choices.all()
        choices = [{"choice":i.choice, "is_answer":i.is_answer, "id": i.id} for i in choices]
        return JsonResponse({"choices": choices, "question": question.question, "question_type": question.question_type, "question_id": question.id})

def add_question(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        choices = Choices(choice = "Вариант 1")
        choices.save()
        question = Questions(question_type = "multiple choice", question= "Без названия", required= False)
        question.save()
        question.choices.add(choices)
        question.save()
        formInfo.questions.add(question)
        formInfo.save()
        return JsonResponse({'question': {'question': "Без названия", "question_type": "multiple choice", "required": False, "id": question.id},
        "choices": {"choice": "Вариант 1", "is_answer": False, 'id': choices.id}})

def delete_question(request, code, question):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        question = Questions.objects.filter(id = question)
        if question.count() == 0: return HttpResponseRedirect(reverse("404"))
        else: question = question[0]
        for i in question.choices.all():
            i.delete()
            question.delete()
        return JsonResponse({"message": "Success"})

def score(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args = [code]))
    else:
        return render(request, "index/score.html", {
            "form": formInfo
        })

def edit_score(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args = [code]))
    else:
        if request.method == "POST":
            data = json.loads(request.body)
            question_id = data["question_id"]
            question = formInfo.questions.filter(id = question_id)
            if question.count() == 0:
                return HttpResponseRedirect(reverse("edit_form", args = [code]))
            else: question = question[0]
            score = data["score"]
            if score == "": score = 0
            question.score = score
            question.save()
            return JsonResponse({"message": "Success"})

def answer_key(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args = [code]))
    else:
        if request.method == "POST":
            data = json.loads(request.body)
            question = Questions.objects.filter(id = data["question_id"])
            if question.count() == 0: return HttpResponseRedirect(reverse("edit_form", args = [code]))
            else: question = question[0]
            if question.question_type == "short" or question.question_type == "paragraph":
                question.answer_key = data["answer_key"]
                question.save()
            else:
                for i in question.choices.all():
                    i.is_answer = False
                    i.save()
                if question.question_type == "multiple choice":
                    choice = question.choices.get(pk = data["answer_key"])
                    choice.is_answer = True
                    choice.save()
                else:
                    for i in data["answer_key"]:
                        choice = question.choices.get(id = i)
                        choice.is_answer = True
                        choice.save()
                question.save()
            return JsonResponse({'message': "Success"})

def feedback(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args = [code]))
    else:
        if request.method == "POST":
            data = json.loads(request.body)
            question = formInfo.questions.get(id = data["question_id"])
            question.feedback = data["feedback"]
            question.save()
            return JsonResponse({'message': "Success"})

def view_form(request, code):
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    if formInfo.authenticated_responder:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
    return render(request, "index/view_form.html", {
        "form": formInfo
    })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def submit_form(request, code):
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    if formInfo.authenticated_responder:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(20))
        if formInfo.authenticated_responder:
            response = Responses(response_code = code, response_to = formInfo, responder_ip = get_client_ip(request), responder = request.user)
            response.save()
        else:
            if not formInfo.collect_email:
                response = Responses(response_code = code, response_to = formInfo, responder_ip = get_client_ip(request))
                response.save()
            else:
                response = Responses(response_code = code, response_to = formInfo, responder_ip = get_client_ip(request), responder_email=request.POST["email-address"])
                response.save()
        for i in request.POST:
            #Excluding csrf token
            if i == "csrfmiddlewaretoken" or i == "email-address":
                continue
            question = formInfo.questions.get(id = i)
            for j in request.POST.getlist(i):
                answer = Answer(answer=j, answer_to = question)
                answer.save()
                response.response.add(answer)
                response.save()
        return render(request, "index/form_response.html", {
            "form": formInfo,
            "code": code
        })

def responses(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]

    responsesSummary = []
    choiceAnswered = {}
    filteredResponsesSummary = {}
    for question in formInfo.questions.all():
        answers = Answer.objects.filter(answer_to = question.id)
        if question.question_type == "multiple choice" or question.question_type == "checkbox":
            choiceAnswered[question.question] = choiceAnswered.get(question.question, {})
            for answer in answers:
                choice = answer.answer_to.choices.get(id = answer.answer).choice
                choiceAnswered[question.question][choice] = choiceAnswered.get(question.question, {}).get(choice, 0) + 1
        responsesSummary.append({"question": question, "answers":answers })
    for answr in choiceAnswered:
        filteredResponsesSummary[answr] = {}
        keys = choiceAnswered[answr].values()
        for choice in choiceAnswered[answr]:
            filteredResponsesSummary[answr][choice] = choiceAnswered[answr][choice]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    return render(request, "index/responses.html", {
        "form": formInfo,
        "responses": Responses.objects.filter(response_to = formInfo),
        "responsesSummary": responsesSummary,
        "filteredResponsesSummary": filteredResponsesSummary
    })

def retrieve_checkbox_choices(response, question):
    checkbox_answers = []

    answers = Answer.objects.filter(answer_to=question, response=response)
    for answer in answers:
        selected_choice_ids = answer.answer.split(',')  # Split the string into individual choice IDs
        selected_choices = Choices.objects.filter(pk__in=selected_choice_ids)
        checkbox_answers.append([choice.choice for choice in selected_choices])

    return checkbox_answers



def exportcsv(request,code):
    formInfo = Form.objects.filter(code = code)
    formInfo = formInfo[0]
    responses=Responses.objects.filter(response_to = formInfo)
    questions = formInfo.questions.all()


    http_response = HttpResponse()
    http_response['Content-Type'] = 'text/csv'
    http_response['Content-Disposition'] = f'attachment; filename={formInfo.title}.csv'
    writer = csv.writer(http_response)
    header = ['Response Code', 'Responder', 'Responder Email','Responder_ip']

    for question in questions:
        header.append(question.question)

    writer.writerow(header)

    for response in responses:
        response_data = [
        response.response_code,
        response.responder.username if response.responder else 'Anonymous',
        response.responder_email if response.responder_email else '',
        response.responder_ip if response.responder_ip else ''
    ]
        for question in questions:
            answer = Answer.objects.filter(answer_to=question, response=response).first()


            if  question.question_type not in ['multiple choice','checkbox']:
                response_data.append(answer.answer if answer else '')
            elif question.question_type == "multiple choice":
                response_data.append(answer.answer_to.choices.get(id = answer.answer).choice if answer else '')
            elif question.question_type == "checkbox":
                if answer and question.question_type == 'checkbox':
                    checkbox_choices = retrieve_checkbox_choices(response,answer.answer_to)
                    response_data.append(checkbox_choices)

        print(response_data)
        writer.writerow(response_data)

    return http_response

def response(request, code, response_code):
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if not formInfo.allow_view_score:
        if formInfo.creator != request.user:
            return HttpResponseRedirect(reverse("403"))
    total_score = 0
    score = 0
    responseInfo = Responses.objects.filter(response_code = response_code)
    if responseInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: responseInfo = responseInfo[0]
    if formInfo.is_quiz:
        for i in formInfo.questions.all():
            total_score += i.score
        for i in responseInfo.response.all():
            if i.answer_to.question_type == "short" or i.answer_to.question_type == "paragraph":
                if i.answer == i.answer_to.answer_key: score += i.answer_to.score
            elif i.answer_to.question_type == "multiple choice":
                answerKey = None
                for j in i.answer_to.choices.all():
                    if j.is_answer: answerKey = j.id
                if answerKey is not None and int(answerKey) == int(i.answer):
                    score += i.answer_to.score
        _temp = []
        for i in responseInfo.response.all():
            if i.answer_to.question_type == "checkbox" and i.answer_to.pk not in _temp:
                answers = []
                answer_keys = []
                for j in responseInfo.response.filter(answer_to__pk = i.answer_to.pk):
                    answers.append(int(j.answer))
                    for k in j.answer_to.choices.all():
                        if k.is_answer and k.pk not in answer_keys: answer_keys.append(k.pk)
                    _temp.append(i.answer_to.pk)
                if answers == answer_keys: score += i.answer_to.score
    return render(request, "index/response.html", {
        "form": formInfo,
        "response": responseInfo,
        "score": score,
        "total_score": total_score
    })

def edit_response(request, code, response_code):
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    response = Responses.objects.filter(response_code = response_code, response_to = formInfo)
    if response.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: response = response[0]
    if formInfo.authenticated_responder:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        if response.responder != request.user:
            return HttpResponseRedirect(reverse('403'))
    if request.method == "POST":
        if formInfo.authenticated_responder and not response.responder:
            response.responder = request.user
            response.save()
        if formInfo.collect_email:
            response.responder_email = request.POST["email-address"]
            response.save()
        #Deleting all existing answers
        for i in response.response.all():
            i.delete()
        for i in request.POST:
            #Excluding csrf token and email address
            if i == "csrfmiddlewaretoken" or i == "email-address":
                continue
            question = formInfo.questions.get(id = i)
            for j in request.POST.getlist(i):
                answer = Answer(answer=j, answer_to = question)
                answer.save()
                response.response.add(answer)
                response.save()
        if formInfo.is_quiz:
            return HttpResponseRedirect(reverse("response", args = [formInfo.code, response.response_code]))
        else:
            return render(request, "index/form_response.html", {
                "form": formInfo,
                "code": response.response_code
            })
    return render(request, "index/edit_response.html", {
        "form": formInfo,
        "response": response
    })

def contact_form_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        name1 = Choices(choice="Вариант 1")
        name1.save()
        name = Questions(question_type = "short", question= "ФИО", required= True)
        name.save()
        name.choices.add(name1)
        name.save()
        email1 = Choices(choice="Вариант 2")
        email1.save()
        email = Questions(question_type="short", question = "Электронная почта", required = True)
        email.save()
        email.choices.add(email1)
        email.save()
        address1 = Choices(choice="Вариант 2")
        address1.save()
        address = Questions(question_type="paragraph", question="Адрес", required = True)
        address.save()
        address.choices.add(address1)
        address.save()
        phone1 = Choices(choice="Вариант 2")
        phone1.save()
        phone = Questions(question_type="short", question="Номер телефона", required = False)
        phone.save()
        phone.choices.add(phone1)
        phone.save()
        comments1 = Choices(choice="Вариант 2")
        comments1.save()
        comments = Questions(question_type = "paragraph", question = "Комментарии", required = False)
        comments.save()
        comments.choices.add(comments1)
        comments.save()
        form = Form(code = code, title = "Контактная информация", creator=request.user, background_color="#e2eee0", allow_view_score = False, edit_after_submit = True)
        form.save()
        form.questions.add(name)
        form.questions.add(email)
        form.questions.add(address)
        form.questions.add(phone)
        form.questions.add(comments)
        form.save()
        return JsonResponse({"message": "Успешно", "code": code})

def customer_feedback_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        comment = Choices(choice = "Комментарии")
        comment.save()
        question = Choices(choice = "Вопросы")
        question.save()
        bug = Choices(choice = "Баг-репорт")
        bug.save()
        feature = Choices(choice = "Запрос функции")
        feature.save()
        feedback_type = Questions(question = "Тип отзыва", question_type="multiple choice", required=False)
        feedback_type.save()
        feedback_type.choices.add(comment)
        feedback_type.choices.add(bug)
        feedback_type.choices.add(question)
        feedback_type.choices.add(feature)
        feedback_type.save()
        feedback1 = Choices(choice="Вариант 1")
        feedback1.save()
        feedback = Questions(question = "Отзыв", question_type="paragraph", required=True)
        feedback.save()
        feedback.choices.add(feedback1)
        feedback.save()
        suggestion1 = Choices(choice="Вариант 1")
        suggestion1.save()
        suggestion = Questions(question = "Предложения для улучшения", question_type="paragraph", required=False)
        suggestion.save()
        suggestion.choices.add(suggestion1)
        suggestion.save()
        name1 = Choices(choice="Вариант 1")
        name1.save()
        name = Questions(question = "ФИО", question_type="short", required=False)
        name.save()
        name.choices.add(name1)
        name.save()
        email1 = Choices(choice="Вариант 2")
        email1.save()
        email = Questions(question= "E-mail", question_type="short", required=False)
        email.save()
        email.choices.add(email1)
        email.save()
        form = Form(code = code, title = "Форма обратной связи", creator=request.user, background_color="#e2eee0", confirmation_message="Thanks so much for giving us feedback!",
        description = "Мы будем рады услышать ваши мысли или отзывы о том, как мы можем улучшить ваш опыт!", allow_view_score = False, edit_after_submit = True)
        form.save()
        form.questions.add(feedback_type)
        form.questions.add(feedback)
        form.questions.add(suggestion)
        form.questions.add(name)
        form.questions.add(email)
        return JsonResponse({"message": "Успешно", "code": code})

def event_registration_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        name1 = Choices(choice="Вариант 1")
        name1.save()
        name = Questions(question="ФИО", question_type= "short", required=True)
        name.save()
        name.choices.add(name1)
        name.save()
        email1 = Choices(choice="Вариант 2")
        email1.save()
        email = Questions(question = "E-mail", question_type="short", required=True)
        email.save()
        email.choices.add(email1)
        email.save()
        organization1 = Choices(choice="Вариант 3")
        organization1.save()
        organization = Questions(question = "Организация", question_type= "short", required=True)
        organization.save()
        organization.choices.add(organization1)
        organization.save()
        day1 = Choices(choice="Дня 1")
        day1.save()
        day2 = Choices(choice= "Дня 2")
        day2.save()
        day3 = Choices(choice= "Дня 3")
        day3.save()
        day = Questions(question="В какие дни вы будете присутствовать?", question_type="checkbox", required=True)
        day.save()
        day.choices.add(day1)
        day.choices.add(day2)
        day.choices.add(day3)
        day.save()
        dietary_none = Choices(choice="Нет")
        dietary_none.save()
        dietary_vegetarian = Choices(choice="Вегетарианское")
        dietary_vegetarian.save()
        dietary_kosher = Choices(choice="Кошерные")
        dietary_kosher.save()
        dietary_gluten = Choices(choice = "Без глютена")
        dietary_gluten.save()
        dietary = Questions(question = "Ограничения в питании", question_type="multiple choice", required = True)
        dietary.save()
        dietary.choices.add(dietary_none)
        dietary.choices.add(dietary_vegetarian)
        dietary.choices.add(dietary_gluten)
        dietary.choices.add(dietary_kosher)
        dietary.save()
        accept_agreement = Choices(choice = "Да")
        accept_agreement.save()
        agreement = Questions(question = "Я понимаю, что мне придется заплатить [ДЕНЬГИ] по прибытии", question_type="checkbox", required=True)
        agreement.save()
        agreement.choices.add(accept_agreement)
        agreement.save()
        form = Form(code = code, title = "Регистрация на мероприятие", creator=request.user, background_color="#fdefc3",
        confirmation_message="Мы приняли вашу регистрацию.\n\
Укажите здесь другую информацию.\n\
\n\
Сохраните ссылку ниже, по которой можно редактировать свою регистрацию вплоть до даты ее закрытия.",
        description = "Дата проведения: 4-6 января 2023 г.\n\
Адрес мероприятия: 123 'Ваша улица', 'Ваш город', Проспект 12345\n\
Свяжитесь с нами по телефону (123)-456-7890 и/или example@example.com", edit_after_submit=True, allow_view_score=False)
        form.save()
        form.questions.add(name)
        form.questions.add(email)
        form.questions.add(organization)
        form.questions.add(day)
        form.questions.add(dietary)
        form.questions.add(agreement)
        form.save()
        return JsonResponse({"message": "Успешно", "code": code})

def social_survey_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        gen1 = Choices(choice="Мужской")
        gen1.save()
        gen2 = Choices(choice= "Женский")
        gen2.save()
        gen = Questions(question="Какой у вас пол?", question_type="checkbox", required=True)
        gen.save()
        gen.choices.add(gen1)
        gen.choices.add(gen2)
        gen.save()
        age1 = Choices(choice="Вариант 1")
        age1.save()
        age = Questions(question="Ваш возраст", question_type= "short", required=True)
        age.save()
        age.choices.add(age1)
        age.save()
        que1 = Choices(choice="Работаю")
        que1.save()
        que2 = Choices(choice= "Учусь")
        que2.save()
        que = Questions(question="Вы работаете или учитесь?", question_type="checkbox", required=True)
        que.save()
        que.choices.add(que1)
        que.choices.add(que2)
        que.save()
        form = Form(code = code, title = "Социальный опрос", creator=request.user, background_color="#e2eee0", allow_view_score = False, edit_after_submit = True)
        form.save()
        form.questions.add(gen)
        form.questions.add(age)
        form.questions.add(que)
        form.save()
        return JsonResponse({"message": "Успешно", "code": code})

def delete_responses(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        responses = Responses.objects.filter(response_to = formInfo)
        for response in responses:
            for i in response.response.all():
                i.delete()
            response.delete()
        return JsonResponse({"message": "Успешно"})

# Error handler
def FourZeroThree(request, exception=None):
    return render(request, 'error/403.html', status=403)

def FourZeroFour(request, exception=None):
    return render(request, 'error/404.html', status=404)

def about_us(request):
    return render(request, 'index/aboutUs.html')

def contact_us(request):
    return render(request, 'index/contactUs.html')

def edit_profile(request):
    return render(request, 'index/edit-profile.html')

def view_profile(request):
    return render(request, 'index/view-profile.html')

def form_list_view(request):
    if request.method == 'POST':
        selected_forms = request.POST.getlist('selected_forms[]')

        # Проверяем, чтобы избежать ошибок, если selected_forms пуст
        if selected_forms:
            Form.objects.filter(id__in=selected_forms).delete()

    # Здесь вы можете добавить код для получения списка форм и передачи его в шаблон
    forms = Form.objects.all()

    return render(request, 'index/form_list.html', {'forms': forms})

