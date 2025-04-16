import os
import httpx
import random
import logging
import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta

# Настраиваем логирование
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Список разрешенных пользователей
ALLOWED_USERS = {1144374701, 6021385165, 2006843532, 538738275, 475554377, 343474939, 440445997}

# Список фраз после победы игрока
win_speech = [
    "Тебе просто повезло!",
    "Коровья лепёшка!",
    "Да коровья лепёшка!",
    "Щас дед отыграется!",
    "Ах ты сопляк!",
    "Вот дерьмо!",
    "Собачье дерьмо!",
    "Пошла чёрная полоса!",
    "Дерьмо!",
    "Чёрт!",
    "Чёрт подери!",
    "Собакино дерьмо!",
    "Да чёрт!",
    "Грёбаный Экибастуз!",
    "Ты случайно не на работе?",
    "Займи себя чем-нибудь!",
    "Тебе повезло, гупёшка!",
    "Везучий нубас!",
    "Какой везучий нубас!",
    "Наверное гордишься собой!",
    "Мне не повезло!",
    "Как так!",
    "Дерьмо собаки!",
    "Мне просто не повезло!",
    "Считай, что я поддался!",
    "Дерьмо собачье!",
    "Да как так!"
]

# Список фраз после поражения игрока 
lose_speech = [
    "Играешь как оладушек!",
    "Не, ну ты индеец!",
    "Я балдю, бом-бом!",
    "Ну ты оладушек!",
    "Ну ты нубас!",
    "Да ты нубас!",
    "Играешь как нубас!",
    "Дед давно в этом бизнесе!",
    "Как же дед хорош!",
    "Это было не сложно!",
    "Как я тебя!",
    "Ну ты гупёшка!",
    "Это было легко!",
    "Дед был создан ПОБЕЖДАТЬ!",
    "Дед мчится к победе!",
    "Учись у деда!",
    "Я просто читаю твои мысли!",
    "Дед всегда на шаг впереди!",
    "Просто не твой день!",
    "Просто не твой день, нубас!",
    "Я просто читаю эту игру!",
    "Это тебе не капчи решать!",
    "Я читаю эту игру!"
]

# Список фраз после ничьи 
draw_speech = [
    "У дураков мысли одинаковые.",
    "Ни тебе, ни мне.",
    "Щас разберёмся.",
    "Щас всё решится.",
    "Давай по новой.",
    "Ни мне, ни тебе.",
    "Потная катка.",
    "Ещё разок.",
    "Ещё.",
    "Какая потная катка.",
    "Неловко вышло.",
    "Неловко вышло, да?",
    "Давай ещё разок.",
    "Давай ещё."
]

# Города для погоды
CITIES = {
    "Бердск": "1510350",
    "НСК": "1496747",
    "Краснодар": "542420",
    "Москва": "524901",
    "Донецк": "565348",
    "Владивосток": "2013348",
    "Искитим": "1505429",
    "СПБ": "498817"
}

# Главное меню
MENU_KEYBOARD = ReplyKeyboardMarkup([
    ["☀️ Погода", "🔄 Курсы валют"],
    ["📰 Новости","✨✊✌️✋✨"]
], resize_keyboard=True)

# Меню Погода
WEATHER_KEYBOARD = ReplyKeyboardMarkup([
    ["НСК", "Бердск", "Краснодар"],
    ["СПБ", "Москва", "↩️"]
], resize_keyboard=True)

# Меню игры КАМЕНЬ-НОЖНИЦЫ-БУМАГА
IGRA_KEYBOARD = ReplyKeyboardMarkup([
    ["✌️ Ножницы", "✋ Бумага"],
    ["✊ Камень", "↩️"]
], resize_keyboard=True)

    # Добавим словарь для хранения счёта пользователей
user_scores = {}

# Варианты для игры КАМЕНЬ-НОЖНИЦЫ-БУМАГА
GAME_CHOICES = ["✊ Камень", "✌️ Ножницы", "✋ Бумага"]

# Правила игры КАМЕНЬ-НОЖНИЦЫ-БУМАГА (кто кого побеждает)
GAME_RULES = {
    "✊ Камень": {"✊ Камень": "ничья", "✌️ Ножницы": "победа", "✋ Бумага": "поражение"},
    "✌️ Ножницы": {"✊ Камень": "поражение", "✌️ Ножницы": "ничья", "✋ Бумага": "победа"},
    "✋ Бумага": {"✊ Камень": "победа", "✌️ Ножницы": "поражение", "✋ Бумага": "ничья"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"\n🤖💬  Дед Пердет активирован!\n\nЖми на кнопки,\nтолько не сломай ничё.",
        reply_markup=MENU_KEYBOARD
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "☀️ Погода":
        await update.message.reply_text("\n🤖💬  Выбери город.", reply_markup=WEATHER_KEYBOARD)

    elif text in CITIES:
        weather = await get_weather(text)
        await update.message.reply_text(weather)

    elif text == "↩️":
        await update.message.reply_text("\n🤖💬  Жми на кнопки,\n\nтолько не сломай ничё.", reply_markup=MENU_KEYBOARD)

    elif text == "🔄 Курсы валют":
        rates = await get_currency_rates()
        await update.message.reply_text(rates)

    elif text == "📰 Новости":
        news = await get_random_news()
        await update.message.reply_text(news)

    elif text == "✨✊✌️✋✨":
        await update.message.reply_text("\n🤖💬  Камень, ножницы, бумага.\n\nИгра до 9 побед. Проперди тебя дед!\n\n✊ Камень   ✌️ Ножницы   ✋ Бумага\n\n      жми, чтобы начать новую игру", reply_markup=IGRA_KEYBOARD)
    
    elif text in GAME_CHOICES:
        await play_game(update, text)
           
    else:
        await update.message.reply_text("🤖💬  Не понимаю.")

# ИГРА КАМЕНЬ-НОЖНИЦЫ-БУМАГА

async def play_game(update: Update, user_choice: str):
    user_id = update.message.from_user.id
    
    # Инициализируем счёт, если пользователь играет впервые
    if user_id not in user_scores:
        user_scores[user_id] = {'wins': 0, 'losses': 0, 'draws': 0}
    
    # Бот делает случайный выбор
    bot_choice = random.choice(GAME_CHOICES)
    
    # Определяем результат
    result = GAME_RULES[user_choice][bot_choice]

    # Обновляем счёт
    if result == "победа":
        user_scores[user_id]['wins'] += 1
        score_display = f"         ДЕД     {user_scores[user_id]['losses']} : {user_scores[user_id]['wins']} ▲ ТЫ"
    elif result == "поражение":
        user_scores[user_id]['losses'] += 1
        score_display = f"         ДЕД ▲ {user_scores[user_id]['losses']} : {user_scores[user_id]['wins']}     ТЫ"
    else:
        user_scores[user_id]['draws'] += 1
        score_display = f"         ДЕД     {user_scores[user_id]['losses']} • {user_scores[user_id]['wins']}     ТЫ"

    # Проверяем, достигнут ли выигрышный счёт
    game_over = False
    if user_scores[user_id]['wins'] >= 9 or user_scores[user_id]['losses'] >= 9:
        game_over = True
    
    # Формируем сообщение с результатом
    if game_over:
        message = f"🤖⚡  ✨ ✊ ✌️ ✋ ✨  {bot_choice}"
        
        # Добавляем окончательный счёт перед завершением матча
        if user_scores[user_id]['wins'] >= 9:
            message += f"\n\n         ДЕД   {user_scores[user_id]['losses']} : {user_scores[user_id]['wins']}  🏆  ТЫ ПОБИЛ ДЕДА"
        else:
            message += f"\n\n         ДЕД 🏆 {user_scores[user_id]['losses']} : {user_scores[user_id]['wins']}   ТЫ ОТБУЦКАН"
        
        message += "\n\n✊ Камень   ✌️ Ножницы   ✋ Бумага\n\n      жми, чтобы начать новую игру"
        # Сбрасываем счёт после завершения серии
        del user_scores[user_id]
    else:
        message = f"🤖⚡  ✨ ✊ ✌️ ✋ ✨  {bot_choice}"
        message += f"\n\n{score_display}"
        
        # Добавляем фразу бота с эмодзи
        if result == "победа":
            message += f"\n\n🤖💬  {random.choice(win_speech)}"
        elif result == "поражение":
            message += f"\n\n🤖💬  {random.choice(lose_speech)}"
        else:
            message += f"\n\n🤖💬  {random.choice(draw_speech)}"
    
    await update.message.reply_text(message, reply_markup=IGRA_KEYBOARD)
    
# ФУНКЦИЯ ПОГОДЫ
async def get_weather(city):
    city_id = CITIES.get(city)
    if not city_id:
        return "❌ Город не найден. Попробуйте снова."

    # Запрос текущей погоды
    current_url = f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    # Запрос прогноза на 5 дней с интервалом 3 часа (доступны данные на 6 и 12 часов)
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?id={city_id}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    try:
        # Получаем текущую погоду
        current_response = requests.get(current_url)
        current_response.raise_for_status()
        current_data = current_response.json()

        # Получаем прогноз
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # Получаем временную зону города (в секундах от UTC)
        timezone_offset = current_data.get('timezone', 0)  # по умолчанию UTC, если нет данных
        
        # Текущая погода
        temp_now = round(current_data["main"]["temp"])
        feels_like_now = round(current_data["main"]["feels_like"])
        description_now = current_data["weather"][0]["description"].capitalize()
        humidity_now = current_data["main"]["humidity"]
        pressure_hpa = current_data["main"]["pressure"]
        pressure_mmhg = round(pressure_hpa * 0.750064)  # Конвертация в мм рт. ст.
        wind_speed_now = round(current_data["wind"]["speed"])
        wind_deg_now = current_data["wind"].get("deg", 0)
        
        # Направление ветра
        directions = ['Св', 'СВ', 'Вс', 'ЮВ', 
                     'Юж', 'ЮЗ', 'Зп', 'СЗ']
        wind_dir_now = directions[round(wind_deg_now / 45) % 8] if "deg" in current_data["wind"] else "неизвестно"
        
        # Функция для преобразования времени с учетом временной зоны
        def get_local_time(utc_time, timezone_offset):
            return utc_time + timedelta(seconds=timezone_offset)
        
        # Текущее время в UTC
        current_utc_time = datetime.utcnow()
        # Локальное время города
        current_local_time = get_local_time(current_utc_time, timezone_offset)
        
        # Прогноз через 3 часа (берем 1-й элемент, т.к. прогноз каждые 3 часа)
        forecast_3h = forecast_data["list"][0]
        temp_3h = round(forecast_3h["main"]["temp"])
        description_3h = forecast_3h["weather"][0]["description"].capitalize()
        time_3h = datetime.strptime(forecast_3h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_3h_local = get_local_time(time_3h, timezone_offset)

        # Прогноз через 6 часов (берем 2-й элемент)
        forecast_6h = forecast_data["list"][1]
        temp_6h = round(forecast_6h["main"]["temp"])
        description_6h = forecast_6h["weather"][0]["description"].capitalize()
        time_6h = datetime.strptime(forecast_6h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_6h_local = get_local_time(time_6h, timezone_offset)

        # Прогноз через 9 часов (3-й элемент)
        forecast_9h = forecast_data["list"][2]
        temp_9h = round(forecast_9h["main"]["temp"])
        description_9h = forecast_9h["weather"][0]["description"].capitalize()
        time_9h = datetime.strptime(forecast_9h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_9h_local = get_local_time(time_9h, timezone_offset)

        # Прогноз через 12 часов (4-й элемент)
        forecast_12h = forecast_data["list"][3]
        temp_12h = round(forecast_12h["main"]["temp"])
        description_12h = forecast_12h["weather"][0]["description"].capitalize()
        time_12h = datetime.strptime(forecast_12h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_12h_local = get_local_time(time_12h, timezone_offset)
        
        # Прогноз через 15 часов (5-й элемент)
        forecast_15h = forecast_data["list"][4]
        temp_15h = round(forecast_15h["main"]["temp"])
        description_15h = forecast_15h["weather"][0]["description"].capitalize()
        time_15h = datetime.strptime(forecast_15h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_15h_local = get_local_time(time_15h, timezone_offset)
        
        # Прогноз через 18 часов (6-й элемент)
        forecast_18h = forecast_data["list"][5]
        temp_18h = round(forecast_18h["main"]["temp"])
        description_18h = forecast_18h["weather"][0]["description"].capitalize()
        time_18h = datetime.strptime(forecast_18h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_18h_local = get_local_time(time_18h, timezone_offset)
        
        # Прогноз через 24 часа (8-й элемент)
        forecast_24h = forecast_data["list"][7]
        temp_24h = round(forecast_24h["main"]["temp"])
        description_24h = forecast_24h["weather"][0]["description"].capitalize()
        time_24h = datetime.strptime(forecast_24h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_24h_local = get_local_time(time_24h, timezone_offset)
        
        # Прогноз через 30 часов (10-й элемент)
        forecast_30h = forecast_data["list"][9]
        temp_30h = round(forecast_30h["main"]["temp"])
        description_30h = forecast_30h["weather"][0]["description"].capitalize()
        time_30h = datetime.strptime(forecast_30h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_30h_local = get_local_time(time_30h, timezone_offset)
        
        # Прогноз через 36 часов (12-й элемент)
        forecast_36h = forecast_data["list"][11]
        temp_36h = round(forecast_36h["main"]["temp"])
        description_36h = forecast_36h["weather"][0]["description"].capitalize()
        time_36h = datetime.strptime(forecast_36h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_36h_local = get_local_time(time_36h, timezone_offset)
        
        # Прогноз через 42 часа (14-й элемент)
        forecast_42h = forecast_data["list"][13]
        temp_42h = round(forecast_42h["main"]["temp"])
        description_42h = forecast_42h["weather"][0]["description"].capitalize()
        time_42h = datetime.strptime(forecast_42h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_42h_local = get_local_time(time_42h, timezone_offset)
        
        # Прогноз через 48 часов (16-й элемент)
        forecast_48h = forecast_data["list"][15]
        temp_48h = round(forecast_48h["main"]["temp"])
        description_48h = forecast_48h["weather"][0]["description"].capitalize()
        time_48h = datetime.strptime(forecast_48h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_48h_local = get_local_time(time_48h, timezone_offset)
        
        # Прогноз через 60 часов (20-й элемент)
        forecast_60h = forecast_data["list"][19]
        temp_60h = round(forecast_60h["main"]["temp"])
        description_60h = forecast_60h["weather"][0]["description"].capitalize()
        time_60h = datetime.strptime(forecast_60h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_60h_local = get_local_time(time_60h, timezone_offset)
        
        # Прогноз через 72 часа (24-й элемент)
        forecast_72h = forecast_data["list"][23]
        temp_72h = round(forecast_72h["main"]["temp"])
        description_72h = forecast_72h["weather"][0]["description"].capitalize()
        time_72h = datetime.strptime(forecast_72h['dt_txt'], '%Y-%m-%d %H:%M:%S')
        time_72h_local = get_local_time(time_72h, timezone_offset)

        # Форматируем время для вывода
        current_time_str = current_local_time.strftime("%d.%m   %H:%M")
        time_3h_str = time_3h_local.strftime("%d.%m   %H:%M")
        time_6h_str = time_6h_local.strftime("%d.%m   %H:%M")
        time_9h_str = time_9h_local.strftime("%d.%m   %H:%M")
        time_12h_str = time_12h_local.strftime("%d.%m   %H:%M")
        time_15h_str = time_15h_local.strftime("%d.%m   %H:%M")
        time_18h_str = time_18h_local.strftime("%d.%m   %H:%M")
        time_24h_str = time_24h_local.strftime("%d.%m   %H:%M")
        time_30h_str = time_30h_local.strftime("%d.%m   %H:%M")
        time_36h_str = time_36h_local.strftime("%d.%m   %H:%M")
        time_42h_str = time_42h_local.strftime("%d.%m   %H:%M")
        time_48h_str = time_48h_local.strftime("%d.%m   %H:%M")
        time_60h_str = time_60h_local.strftime("%d.%m   %H:%M")
        time_72h_str = time_72h_local.strftime("%d.%m   %H:%M")

        # Формируем сообщение
        weather_message = (
            f"🤖💬  ☀️ Погода. {city}.\n\n"
            f"{current_time_str}   "
            f"{temp_now}°C   (ощ {feels_like_now}°C)\n"
            f"{description_now}\n"
            f"{humidity_now}%   "
            f"{wind_dir_now} {wind_speed_now}м/с   {pressure_mmhg}мм\n\n"

            f"{time_3h_str}   "
            f"{temp_3h}°C\n"
            f"{description_3h}\n"
            f"{time_6h_str}   "
            f"{temp_6h}°C\n"
            f"{description_6h}\n"
            f"{time_9h_str}   "
            f"{temp_9h}°C\n"
            f"{description_9h}\n"
            f"{time_12h_str}   "
            f"{temp_12h}°C\n"
            f"{description_12h}\n"
            
            f"{time_15h_str}   "
            f"{temp_15h}°C\n"
            f"{description_15h}\n"
            
            f"{time_18h_str}   {temp_18h}°C\n"
            f"{description_18h}\n"
            f"{time_24h_str}   {temp_24h}°C\n"
            f"{description_24h}\n\n"
            f"{time_30h_str}   {temp_30h}°C\n"
            f"{time_36h_str}   {temp_36h}°C\n"
            f"{time_42h_str}   {temp_42h}°C\n"
            f"{time_48h_str}   {temp_48h}°C"
        )

        return weather_message

    except Exception as e:
        logging.error(f"🤖💬  Ошибка при получении погоды: {e}")
        return f"🤖💬  ❌ Не удалось получить погоду для {city}"

# ФУНКЦИЯ КУРСОВ ВАЛЮТ
async def get_currency_rates():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    crypto_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,rub"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Основные валюты
        usd_rate = data["Valute"]["USD"]["Value"]
        eur_rate = data["Valute"]["EUR"]["Value"]
        gbp_rate = data["Valute"]["GBP"]["Value"]
        chf_rate = data["Valute"]["CHF"]["Value"]
        
        # Азиатские валюты
        cny_rate = data["Valute"]["CNY"]["Value"]
        jpy_rate = data["Valute"]["JPY"]["Value"] / 100  # Пересчёт за 1 иену
        sgd_rate = data["Valute"]["SGD"]["Value"]
        thb_rate = data["Valute"]["THB"]["Value"] / 10   # Пересчёт за 1 бат
        
        # Валюты СНГ и ближнего зарубежья
        byn_rate = data["Valute"]["BYN"]["Value"]
        uah_rate = data["Valute"]["UAH"]["Value"] / 10
        kzt_rate = data["Valute"]["KZT"]["Value"] / 100  # За 1 тенге
        
        # Ближневосточные валюты
        aed_rate = data["Valute"]["AED"]["Value"]
        
        # Другие популярные
        try_rate = data["Valute"]["TRY"]["Value"] / 10
        inr_rate = data["Valute"]["INR"]["Value"] / 100
        
        # Получаем данные о криптовалютах
        crypto_response = requests.get(crypto_url)
        crypto_response.raise_for_status()
        crypto_data = crypto_response.json()
        
        # Криптовалюты
        btc_usd = crypto_data["bitcoin"]["usd"]
        btc_rub = crypto_data["bitcoin"]["rub"]
        eth_usd = crypto_data["ethereum"]["usd"]
        eth_rub = crypto_data["ethereum"]["rub"]

        return (
            f"🤖💬  🔄 Почём BTC для народа?\n\n"
            f"USD 🇺🇸 {usd_rate:.2f} ₽ Доллар США\n"
            f"EUR 🇬🇧 {eur_rate:.2f} ₽ Евро\n"
            f"CNY 🇨🇳 {cny_rate:.2f} ₽ Китайский юань\n"
            f"GBP 🇬🇧 {gbp_rate:.2f} ₽ Фунт стерлингов\n\n"           
            f"BYN 🇧🇾 {byn_rate:.2f} ₽ Белорусский рубль\n"
            f"KZT 🇰🇿 {kzt_rate:.2f} ₽ Казахстанский тенге\n"
            f"UAH 🇺🇦 {uah_rate:.2f} ₽ Украинская гривна\n"
            f"AED 🇦🇪 {aed_rate:.2f} ₽ Дирхам ОАЭ\n"  
            f"TRY 🇹🇷 {try_rate:.2f} ₽ Турецкая лира\n"       
            f"CHF 🇨🇭 {chf_rate:.2f} ₽ Швейцарский франк\n"
            f"SGD 🇸🇬 {sgd_rate:.2f} ₽ Сингапурский доллар\n"        
            f"INR 🇮🇳 {inr_rate:.2f} ₽ Индийская рупия\n"
            f"JPY 🇯🇵 {jpy_rate:.2f} ₽ Японская йена\n" 
            f"THB 🇹🇭 {thb_rate:.2f} ₽ Тайский бат\n\n" 
            f"BTC ₿ {btc_usd:,.0f} $ ({btc_rub:,.0f} ₽) Bitcoin\n"
            f"ETH Ξ {eth_usd:,.0f} $ ({eth_rub:,.0f} ₽) Ethereum"
        )
        
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении курса валют: {e}")
        return "❌ Не удалось получить курс валют. Попробуйте позже."

async def get_random_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&language=ru&category=technology,science,business,food,entertainment"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                articles = data["results"]
                random_article = random.choice(articles)
                title = random_article.get("title", "Без заголовка")
                link = random_article.get("link", "#")
                return f"🤖💬  Вот те новость   {link}"
            else:
                return "🤖💬\n\nНовости чё-то барахлят.\n\nПопробуй позже."
    except httpx.HTTPStatusError as e:
        logging.error(f"Ошибка HTTP при получении новостей: {e}")
        return "❌ Не удалось получить новости. Попробуйте позже."
    except Exception as e:
        logging.error(f"Неожиданная ошибка при получении новостей: {e}")
        return "🤖💬\n\nНовости чё-то барахлят.\n\nПопробуй позже."

def main():
    if not TOKEN or not WEATHER_API_KEY or not NEWS_API_KEY:
        logging.error("Отсутствует токен или API-ключи! Укажите их в .env файле.")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    logging.info("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
