from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

class DateOfBirth(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)

    def age(self):
        today = datetime.now().date()
        birthdate = self.date_of_birth
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age

    def __str__(self):
        return f"{self.user.username}'s Date of Birth"

class UserGender(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices)

    def __str__(self):
        return f"{self.user.username}'s Gender"

class Image(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='image_info')
    image_url = models.URLField(blank=True, null=True)

class UserCity(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name='city_info')
    ALMATY = 'Алматы'
    NUR_SULTAN = 'Нур-Султан'
    KARAGANDA = 'Караганда'
    SHYMKENT = 'Шымкент'
    AKTOBE = 'Актобе'
    SEMEY = 'Семей'
    ATYRAU = 'Атырау'
    PAVLODAR = 'Павлодар'
    URALSK = 'Уральск'
    UST_KAMENOGORSK = 'Усть-Каменогорск'
    KOKSHETAU = 'Кокшетау'
    KOSTANAY = 'Костанай'
    PETROPAVLOVSK = 'Петропавлск'
    ORAL = 'Орал'
    TALDYKORGAN = 'Талдыкорган'

    CITY_CHOICES = [
        ('', 'Выбрать страну'),
        (ALMATY, 'Алматы'),
        (NUR_SULTAN, 'Нур-Султан'),
        (KARAGANDA, 'Караганда'),
        (SHYMKENT, 'Шымкент'),
        (AKTOBE, 'Актобе'),
        (SEMEY, 'Семей'),
        (ATYRAU, 'Атырау'),
        (PAVLODAR, 'Павлодар'),
        (URALSK, 'Уральск'),
        (UST_KAMENOGORSK, 'Усть-Каменогорск'),
        (KOKSHETAU, 'Кокшетау'),
        (KOSTANAY, 'Костанай'),
        (PETROPAVLOVSK, 'Петропавловск'),
        (ORAL, 'Орал'),
        (TALDYKORGAN, 'Талдыкорган'),
    ]

    city = models.CharField(max_length=50, blank=True, null=True, choices=CITY_CHOICES)

class User(AbstractUser):
    date_of_birth = models.ForeignKey(DateOfBirth, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')
    gender = models.ForeignKey(UserGender, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')
    city = models.ForeignKey(UserCity, on_delete=models.CASCADE, null=True, blank=True, related_name='user_info')

class Choices(models.Model):
    choice = models.CharField(max_length=5000)
    is_answer = models.BooleanField(default=False)

class Questions(models.Model):
    question = models.CharField(max_length= 10000)
    question_type = models.CharField(max_length=20)
    required = models.BooleanField(default= False)
    answer_key = models.CharField(max_length = 5000, blank = True)
    score = models.IntegerField(blank = True, default=0)
    feedback = models.CharField(max_length = 5000, null = True)
    choices = models.ManyToManyField(Choices, related_name = "choices")

class Answer(models.Model):
    answer = models.CharField(max_length=5000)
    answer_to = models.ForeignKey(Questions, on_delete = models.CASCADE ,related_name = "answer_to")

class Form(models.Model):
    code = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=10000, blank = True)
    creator = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "creator")
    background_color = models.CharField(max_length=20, default = "#202124")
    text_color = models.CharField(max_length=20, default="#272124")
    collect_email = models.BooleanField(default=False)
    authenticated_responder = models.BooleanField(default = False)
    edit_after_submit = models.BooleanField(default=False)
    confirmation_message = models.CharField(max_length = 10000, default = "Ваш ответ был отправлен.")
    is_quiz = models.BooleanField(default=False)
    allow_view_score = models.BooleanField(default= True)
    createdAt = models.DateTimeField(auto_now_add = True)
    updatedAt = models.DateTimeField(auto_now = True)
    questions = models.ManyToManyField(Questions, related_name = "questions")

class Responses(models.Model):
    response_code = models.CharField(max_length=20)
    response_to = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="response_to")
    responder_ip = models.CharField(max_length=30)
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responder", blank=True, null=True)
    responder_email = models.EmailField(blank=True)
    response = models.ManyToManyField(Answer, related_name="response")

    def save(self, *args, **kwargs):
        # Assuming you want to link the responder_email to User.email
        if self.responder and not self.responder_email:
            self.responder_email = self.responder.email
        super().save(*args, **kwargs)

