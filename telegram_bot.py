import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from django.contrib.auth.hashers import make_password, check_password
from asgiref.sync import sync_to_async
import django
import logging
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'form.settings')
django.setup()

from index.models import User, Form, Questions, Answer, Responses, Choices, UserMed, UserCity, RegionMedCenter, UserGender, DateOfBirth, UserDesc

API_TOKEN = '7240813949:AAEfydzNw59kBeaA5RFkeslhj7zYcu8VqX8'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

logged_in_users = {}
user_form_progress = {}

class FormState(StatesGroup):
    question = State()
    answer = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    password = State()
    region = State()
    med_center = State()
    optional_info = State()
    gender = State()
    birth_date = State()
    description = State()

async def get_user(username):
    try:
        return await sync_to_async(User.objects.get)(username=username)
    except User.DoesNotExist:
        return None

async def register_user(username, email, password, first_name='', last_name=''):
    try:
        hashed_password = make_password(password)
        user = await sync_to_async(User.objects.create)(
            username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            is_superuser=False,
            is_staff=False,
            is_active=True,
            date_joined=datetime.now()
        )
        return user
    except django.db.IntegrityError as e:
        print(f"IntegrityError: {e}")
        return None

async def get_single_form():
    try:
        return await sync_to_async(Form.objects.get)(is_single_form=True)
    except Form.DoesNotExist:
        return None

async def get_questions(form):
    return await sync_to_async(list)(form.questions.all())

async def get_choices(question):
    return await sync_to_async(list)(question.choices.all())

logger = logging.getLogger(__name__)

async def save_response(user, form, answers):
    try:
        response = await sync_to_async(Responses.objects.create)(
            response_code=''.join(random.choice(string.ascii_letters + string.digits) for x in range(20)),
            response_to=form,
            responder=user,
            responder_ip='unknown',
            responder_email=user.email if user else '',
            authenticated_responder=form.authenticated_responder
        )

        for answer in answers:
            await sync_to_async(response.response.add)(answer)
        return response
    except Exception as e:
        logger.error(f"Error saving response: {e}")
        return None

async def get_user_response(user, form):
    return await sync_to_async(list)(Responses.objects.filter(responder=user, response_to=form))

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Добро пожаловать в Form Bot!\n\n"
                       "Доступные команды:\n"
                       "/register - создать аккаунт\n"
                       "/login - войти\n"
                       "/logout - выйти\n"
                       "/forms - список доступных форм\n"
                       "/cancel - отменить заполнение формы")

@dp.message_handler(commands=['cancel'], state='*')
async def cancel_form(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id in user_form_progress:
        del user_form_progress[user_id]
        await state.finish()
        await message.reply("Заполнение формы отменено.")
    else:
        await message.reply("У вас нет активной формы для отмены.")

def get_region_buttons():
    buttons = [
        InlineKeyboardButton(text=city_name, callback_data=f"region_{city_key}")
        for city_key, city_name in UserCity.CITY_CHOICES
    ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(commands=['register'], state='*')
async def register(message: types.Message, state: FSMContext):
    try:
        username, email, password = message.text.split()[1:4]
        user = await get_user(username)
        if user:
            await message.reply("Пользователь уже существует!")
        else:
            await state.update_data(username=username, email=email, password=password)
            await message.answer("Выберите ваш регион:", reply_markup=get_region_buttons())
            await RegistrationState.region.set()
    except ValueError:
        await message.reply("Использование: /register <username> <email> <password>")

@dp.callback_query_handler(lambda c: c.data.startswith('region_'), state=RegistrationState.region)
async def process_region_choice(callback_query: types.CallbackQuery, state: FSMContext):
    region_key = callback_query.data[7:]
    await state.update_data(region=region_key)
    
    med_centers = await sync_to_async(list)(RegionMedCenter.objects.filter(region=region_key))
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    for med_center in med_centers:
        keyboard.add(InlineKeyboardButton(
            text=f"{med_center.get_med_center_display()} ({med_center.address})",
            callback_data=f"med_{med_center.med_center}"
        ))
    
    await callback_query.message.edit_text("Выберите медицинский центр:", reply_markup=keyboard)
    await RegistrationState.med_center.set()

@dp.callback_query_handler(lambda c: c.data.startswith('med_'), state=RegistrationState.med_center)
async def process_med_center_choice(callback_query: types.CallbackQuery, state: FSMContext):
    med_center_key = callback_query.data[4:]
    await state.update_data(med_center=med_center_key)
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Указать доп. информацию", callback_data="add_info"),
        InlineKeyboardButton("Пропустить", callback_data="skip_info")
    )
    
    await callback_query.message.edit_text(
        "Хотите указать дополнительную информацию (пол, дата рождения, описание)?",
        reply_markup=keyboard
    )
    await RegistrationState.optional_info.set()

@dp.callback_query_handler(lambda c: c.data in ['add_info', 'skip_info'], state=RegistrationState.optional_info)
async def process_optional_info_choice(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'skip_info':
        await complete_registration(callback_query.message, state)
    else:
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("Мужской", callback_data="gender_M"),
            InlineKeyboardButton("Женский", callback_data="gender_F"),
            InlineKeyboardButton("Не указывать", callback_data="gender_O")
        )
        await callback_query.message.edit_text("Укажите ваш пол:", reply_markup=keyboard)
        await RegistrationState.gender.set()

@dp.callback_query_handler(lambda c: c.data.startswith('gender_'), state=RegistrationState.gender)
async def process_gender_choice(callback_query: types.CallbackQuery, state: FSMContext):
    gender = callback_query.data[7:]
    await state.update_data(gender=gender)
    
    await callback_query.message.edit_text(
        "Укажите вашу дату рождения в формате ДД.ММ.ГГГГ или отправьте 'пропустить'"
    )
    await RegistrationState.birth_date.set()

@dp.message_handler(state=RegistrationState.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    if message.text.lower() == 'пропустить':
        await state.update_data(birth_date=None)
    else:
        try:
            birth_date = datetime.strptime(message.text, '%d.%m.%Y').date()
            await state.update_data(birth_date=birth_date)
        except ValueError:
            await message.reply("Неверный формат даты. Используйте ДД.ММ.ГГГГ или 'пропустить'")
            return

    await message.reply("Добавьте описание о себе или отправьте 'пропустить'")
    await RegistrationState.description.set()

@dp.message_handler(state=RegistrationState.description)
async def process_description(message: types.Message, state: FSMContext):
    if message.text.lower() != 'пропустить':
        await state.update_data(description=message.text)
    
    await complete_registration(message, state)

async def complete_registration(message, state: FSMContext):
    user_data = await state.get_data()
    
    user = await register_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password']
    )
    
    if user:
        await sync_to_async(UserCity.objects.create)(
            user=user,
            city=user_data['region']
        )
        
        await sync_to_async(UserMed.objects.create)(
            user=user,
            med_center=user_data['med_center']
        )
        
        if 'gender' in user_data:
            await sync_to_async(UserGender.objects.create)(
                user=user,
                gender=user_data['gender']
            )
        
        if 'birth_date' in user_data and user_data['birth_date']:
            await sync_to_async(DateOfBirth.objects.create)(
                user=user,
                date_of_birth=user_data['birth_date']
            )
        
        if 'description' in user_data and user_data['description']:
            await sync_to_async(UserDesc.objects.create)(
                user=user,
                desc=user_data['description']
            )
        
        await message.reply("Регистрация успешно завершена!")
    else:
        await message.reply("Произошла ошибка при регистрации.")
    
    await state.finish()

@dp.message_handler(commands=['login'])
async def login(message: types.Message):
    try:
        username, password = message.text.split()[1:3]
        user = await get_user(username)
        if user and check_password(password, user.password):
            logged_in_users[message.from_user.id] = username
            await message.reply("Вход выполнен успешно!")
        else:
            await message.reply("Неверное имя пользователя или пароль!")
    except ValueError:
        await message.reply("Использование: /login <username> <password>")

@dp.message_handler(commands=['logout'])
async def logout(message: types.Message):
    if message.from_user.id in logged_in_users:
        del logged_in_users[message.from_user.id]
        await message.reply("Выход выполнен успешно!")
    else:
        await message.reply("Вы не вошли в систему!")

@dp.message_handler(commands=['form'])
async def handle_form(message: types.Message, state: FSMContext):
    form = await get_single_form()
    if not form:
        await message.reply("В данный момент нет доступной формы для заполнения.")
        return

    if form.authenticated_responder and message.from_user.id not in logged_in_users:
        await message.reply("Вы должны войти в систему, чтобы заполнить форму.")
        return

    questions = await get_questions(form)
    user_form_progress[message.from_user.id] = {
        'form': form,
        'questions': questions,
        'current_question': 0,
        'responses': []
    }

    start_button = InlineKeyboardMarkup().add(InlineKeyboardButton("Начать", callback_data="start_form"))
    await message.reply(f"Форма: {form.title}\nОписание: {form.description}", reply_markup=start_button)

@dp.callback_query_handler(lambda c: c.data == 'start_form')
async def process_start_form(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await send_question(callback_query.from_user.id, state)

async def send_question(user_id, state: FSMContext):
    user_data = user_form_progress[user_id]
    questions = user_data['questions']
    current_question_index = user_data['current_question']

    question = questions[current_question_index]
    question_text = question.question
    question_type = question.question_type

    # Инициализируем базовую клавиатуру с кнопками навигации
    keyboard = InlineKeyboardMarkup()
    nav_buttons = []
    if current_question_index > 0:
        nav_buttons.append(InlineKeyboardButton("Предыдущий вопрос", callback_data="prev_question"))
    if current_question_index < len(questions) - 1:
        nav_buttons.append(InlineKeyboardButton("Следующий вопрос", callback_data="next_question"))
    else:
        nav_buttons.append(InlineKeyboardButton("Отправить", callback_data="submit_form"))

    if question_type == 'range slider':
        current_answer = next((r.answer for r in user_data['responses'] if r.answer_to == question), None)
        
        if question.max_value <= 10:
            keyboard = InlineKeyboardMarkup(row_width=5)
            buttons = []
            for i in range(question.max_value + 1):
                is_selected = current_answer == str(i)
                text = f"{'✅ ' if is_selected else ''}{i}"
                buttons.append(InlineKeyboardButton(text, callback_data=f"range_{i}"))
            keyboard.add(*buttons)
            keyboard.row(*nav_buttons)
        else:
            keyboard.add(InlineKeyboardButton("Ввести значение", callback_data="enter_value"))
            keyboard.row(*nav_buttons)

        await bot.send_message(
            user_id, 
            f"Вопрос: {question_text}\n" + 
            (f"Введите значение от 0 до {question.max_value}." if question.max_value > 10 else "Выберите значение:"), 
            reply_markup=keyboard
        )
        if question.max_value > 10:
            await state.set_state(FormState.answer)

    elif question_type in ['short', 'paragraph']:
        question_prompt = {
            'short': "Напишите краткий ответ.",
            'paragraph': "Напишите развернутый ответ."
        }
        keyboard.row(*nav_buttons)
        await bot.send_message(user_id, f"Вопрос: {question_text}\n{question_prompt[question_type]}", reply_markup=keyboard)
        await state.set_state(FormState.answer)

    elif question_type in ['multiple choice', 'checkbox']:
        choices = await get_choices(question)
        for choice in choices:
            is_selected = any(r.answer == str(choice.id) for r in user_data['responses'])
            text = f"{'✅ ' if is_selected else ''}{choice.choice}"
            keyboard.add(InlineKeyboardButton(text, callback_data=f"choice_{choice.id}"))
        keyboard.row(*nav_buttons)
        await bot.send_message(user_id, f"Вопрос: {question_text}", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('range_'))
async def process_range_choice(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    value = callback_query.data.split('_')[1]
    user_data = user_form_progress[user_id]
    question = user_data['questions'][user_data['current_question']]

    # Удаляем предыдущий ответ, если он существует
    existing_answer = next((r for r in user_data['responses'] if r.answer_to == question), None)
    if existing_answer:
        user_data['responses'].remove(existing_answer)
        await sync_to_async(existing_answer.delete)()

    # Создаем новый ответ
    answer = await sync_to_async(Answer.objects.create)(
        answer=value,
        answer_to=question
    )
    user_data['responses'].append(answer)

    await callback_query.message.delete()
    await send_question(user_id, state)

@dp.callback_query_handler(lambda c: c.data == 'enter_value', state='*')
async def process_enter_value(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_data = user_form_progress[user_id]
    question = user_data['questions'][user_data['current_question']]
    
    await callback_query.message.edit_text(
        f"Вопрос: {question.question}\n"
        f"Введите число от 0 до {question.max_value}:"
    )
    await state.set_state(FormState.answer)

@dp.message_handler(state=FormState.answer)
async def handle_answer(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = user_form_progress[user_id]
    current_question_index = user_data['current_question']
    question = user_data['questions'][current_question_index]
    answer_text = message.text.strip()

    if question.question_type == 'short' and len(answer_text) > 64:
        await bot.send_message(user_id, "Ответ слишком длинный. Максимальное количество символов: 64.")
        return
    elif question.question_type == 'paragraph' and len(answer_text) > 2000:
        await bot.send_message(user_id, "Ответ слишком длинный. Максимальное количество символов: 2000.")
        return

    if question.question_type == 'range slider':
        try:
            answer_value = int(answer_text)
            if answer_value > question.max_value:
                await bot.send_message(user_id, f"Значение превышает допустимый максимум. Введите значение от 0 до {question.max_value}.")
                return
        except ValueError:
            await bot.send_message(user_id, "Введите числовое значение.")
            return

    response = next((r for r in user_data['responses'] if r.answer_to == question), None)
    if response:
        await sync_to_async(response.delete)()
        user_data['responses'].remove(response)

    if not answer_text:
        answer = await sync_to_async(Answer.objects.create)(
            answer=None,
            answer_to=question
        )
    else:
        answer = await sync_to_async(Answer.objects.create)(
            answer=answer_text,
            answer_to=question
        )

    user_data['responses'].append(answer)

    await message.delete()
    user_data['current_question'] += 1

    await state.finish()

    if user_data['current_question'] < len(user_data['questions']):
        await send_question(user_id, state)

@dp.callback_query_handler(lambda c: c.data == 'prev_question' or c.data == 'next_question')
async def handle_navigation(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_data = user_form_progress[user_id]

    if callback_query.data == 'prev_question':
        if user_data['current_question'] > 0:
            user_data['current_question'] -= 1
    elif callback_query.data == 'next_question':
        if user_data['current_question'] < len(user_data['questions']) - 1:
            user_data['current_question'] += 1

    await state.finish()
    await callback_query.message.delete()
    await send_question(user_id, state)

@dp.callback_query_handler(lambda c: c.data.startswith('choice_'))
async def process_choice(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    choice_id = int(callback_query.data.split('_')[1])
    user_data = user_form_progress[user_id]
    question = user_data['questions'][user_data['current_question']]

    if question.question_type == 'multiple choice':
        existing_choice = next((r for r in user_data['responses'] if r.answer_to == question), None)
        if existing_choice:
            user_data['responses'].remove(existing_choice)
            await sync_to_async(existing_choice.delete)()

        selected_choice = next((r for r in user_data['responses'] if r.answer == str(choice_id)), None)
        if selected_choice:
            user_data['responses'].remove(selected_choice)
            await sync_to_async(selected_choice.delete)()
        else:
            answer = await sync_to_async(Answer.objects.create)(
                answer=str(choice_id),
                answer_to=question
            )
            user_data['responses'].append(answer)

    elif question.question_type == 'checkbox':
        selected_choice = next((r for r in user_data['responses'] if r.answer == str(choice_id)), None)
        if selected_choice:
            user_data['responses'].remove(selected_choice)
            await sync_to_async(selected_choice.delete)()
        else:
            answer = await sync_to_async(Answer.objects.create)(
                answer=str(choice_id),
                answer_to=question
            )
            user_data['responses'].append(answer)

    await callback_query.message.delete()
    await send_question(user_id, state)

@dp.callback_query_handler(lambda c: c.data == 'prev_question', state=FormState.answer)
async def process_prev_question(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_data = user_form_progress[user_id]

    if user_data['current_question'] > 0:
        user_data['current_question'] -= 1

    await state.finish()
    await callback_query.message.delete()
    await send_question(user_id, state)

@dp.callback_query_handler(lambda c: c.data == 'next_question', state=FormState.answer)
async def process_next_question(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_data = user_form_progress[user_id]

    if user_data['current_question'] < len(user_data['questions']) - 1:
        user_data['current_question'] += 1

    await state.finish()
    await callback_query.message.delete()
    await send_question(user_id, state)

@dp.callback_query_handler(lambda c: c.data == 'submit_form')
async def process_submit_form(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if user_id not in user_form_progress:
        await bot.send_message(user_id, "Произошла ошибка: форма не найдена.")
        return

    user_data = user_form_progress[user_id]
    form = user_data['form']
    responses = user_data['responses']

    for question in user_data['questions']:
        if question.required:
            if not any(r.answer_to == question for r in responses):
                edit_keyboard = InlineKeyboardMarkup()
                edit_keyboard.add(InlineKeyboardButton("Редактировать", callback_data="edit_form"))

                await bot.send_message(user_id, f"Вопрос '{question.question}' обязателен к ответу!", reply_markup=edit_keyboard)
                return

    confirmation_text = "Вы выбрали следующие ответы:\n\n"
    for question in user_data['questions']:
        response = next((r for r in responses if r.answer_to == question), None)
        if response:
            if question.question_type in ['multiple choice', 'checkbox']:
                choice = await sync_to_async(Choices.objects.get)(id=int(response.answer))
                confirmation_text += f"{question.question}: {choice.choice}\n"
            else:
                confirmation_text += f"{question.question}: {response.answer}\n"
        else:
            confirmation_text += f"{question.question}: (нет ответа)\n"

    confirmation_text += "\nВы уверены, что хотите отправить форму?"

    confirm_keyboard = InlineKeyboardMarkup()
    confirm_keyboard.add(InlineKeyboardButton("Подтвердить", callback_data="confirm_submission"))
    confirm_keyboard.add(InlineKeyboardButton("Редактировать", callback_data="edit_form"))

    await callback_query.message.edit_text(confirmation_text, reply_markup=confirm_keyboard)

@dp.callback_query_handler(lambda c: c.data == 'confirm_submission')
async def confirm_submission(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_data = user_form_progress[user_id]
    form = user_data['form']
    responses = user_data['responses']

    user = await get_user(logged_in_users.get(user_id))
    await save_response(user, form, responses)

    await callback_query.message.edit_text("Форма успешно отправлена!")
    del user_form_progress[user_id]

@dp.callback_query_handler(lambda c: c.data == 'edit_form')
async def edit_form(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_data = user_form_progress[user_id]

    user_data['current_question'] = 0
    await callback_query.message.delete()
    await send_question(user_id, state)

@dp.message_handler(commands=['forms'])
async def show_forms(message: types.Message):
    forms = await sync_to_async(list)(Form.objects.filter(is_single_form=True))
    
    if not forms:
        await message.reply("В данный момент нет доступных форм.")
        return
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    for form in forms:
        keyboard.add(
            InlineKeyboardButton(
                text=form.title,
                callback_data=f"select_form_{form.id}"
            )
        )
    
    await message.reply("Доступные формы:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('select_form_'))
async def select_form(callback_query: types.CallbackQuery, state: FSMContext):
    form_id = int(callback_query.data.split('_')[2])
    form = await sync_to_async(Form.objects.get)(id=form_id)
    
    if form.authenticated_responder and callback_query.from_user.id not in logged_in_users:
        await callback_query.message.reply("Вы должны войти в систему, чтобы заполнить эту форму.")
        return

    questions = await get_questions(form)
    user_form_progress[callback_query.from_user.id] = {
        'form': form,
        'questions': questions,
        'current_question': 0,
        'responses': []
    }

    start_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Начать", callback_data="start_form")
    )
    
    await callback_query.message.edit_text(
        f"Форма: {form.title}\nОписание: {form.description}",
        reply_markup=start_button
    )

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)