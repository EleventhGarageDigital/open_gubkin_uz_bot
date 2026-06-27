import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота, который выдаёт @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Название Google-таблицы (должно совпадать с реальным названием файла в Google Sheets)
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "open_day_gubkin_2024")

# Путь к JSON-файлу с ключом сервисного аккаунта Google
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# Список направлений: ключ -> (отображаемое название, категория)
DIRECTIONS = {
    "geology": {"title": "Геология и разведка месторождений", "category": "Технические"},
    "drilling": {"title": "Бурение нефтяных и газовых скважин", "category": "Технические"},
    "oil_gas": {"title": "Разработка нефтяных и газовых месторождений", "category": "Технические"},
    "pipeline_transport": {"title": "Трубопроводный транспорт нефти и газа", "category": "Технические"},
    "chemical_tech": {"title": "Химическая технология (нефтепереработка)", "category": "Технические"},
    "mechanical_eng": {"title": "Машины и оборудование нефтегазовой отрасли", "category": "Технические"},
    "economics": {"title": "Экономика", "category": "Экономика и менеджмент"},
    "management": {"title": "Менеджмент", "category": "Экономика и менеджмент"},
    "logistics": {"title": "Логистика и управление цепями поставок", "category": "Экономика и менеджмент"},
    "state_municipal": {"title": "Государственное и муниципальное управление", "category": "Экономика и менеджмент"},
}

# Доступные даты Дня открытых дверей (формат: "YYYY-MM-DD")
AVAILABLE_DATES = [
    "2024-11-23",
    "2024-11-30",
    "2024-12-07",
]

# Доступное время записи на каждую дату
AVAILABLE_TIMES = [
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
]

# ID администратора(ов) — получат уведомление о новой записи (можно оставить пустым)
ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]
