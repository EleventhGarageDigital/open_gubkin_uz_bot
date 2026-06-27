# Бот регистрации абитуриентов — День открытых дверей РГУ нефти и газа (Губкина) 2024

Telegram-бот: `@open_day_gubkin_2024_bot`

Бот собирает у абитуриента:
1. ФИО (текстовый ввод)
2. Направление (Технические / Экономика и менеджмент → конкретная специальность)
3. Дату визита
4. Время визита

...и записывает всё в Google Sheets.

---

## 📁 Структура проекта

```
gubkin_bot/
├── bot.py                  # точка входа
├── config.py               # настройки, список направлений, дат, времени
├── requirements.txt
├── .env.example             # шаблон переменных окружения
├── handlers/
│   ├── states.py            # FSM-состояния
│   ├── keyboards.py         # инлайн-клавиатуры
│   └── registration.py      # вся логика диалога
└── utils/
    └── sheets.py             # запись данных в Google Sheets
```

---

## 1. Создание Telegram-бота

1. Откройте Telegram, найдите **@BotFather**.
2. Отправьте `/newbot`.
3. Укажите имя бота (например, "Регистрация ДОД Губкина 2024").
4. Укажите username — раз вы упомянули `open_day_gubkin_2024_bot`, можно попробовать его (если он свободен).
5. BotFather выдаст **токен** вида `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` — сохраните его, он пойдёт в `.env`.

---

## 2. Настройка Google Sheets API с нуля (сервисный аккаунт)

Это самый важный и нетривиальный шаг, разберём его подробно.

### Шаг 2.1 — Создайте проект в Google Cloud

1. Перейдите на [console.cloud.google.com](https://console.cloud.google.com/).
2. Войдите под своим Google-аккаунтом (тем же, где будет таблица).
3. В верхней панели нажмите на выпадающий список проектов → **"Новый проект"**.
4. Назовите проект, например `gubkin-open-day-bot`, и нажмите **"Создать"**.

### Шаг 2.2 — Включите нужные API

1. В меню слева: **"APIs & Services" → "Library"** (Библиотека API).
2. Найдите и включите ("Enable"):
   - **Google Sheets API**
   - **Google Drive API**

### Шаг 2.3 — Создайте сервисный аккаунт

1. В меню слева: **"APIs & Services" → "Credentials"** (Учётные данные).
2. Нажмите **"+ Create Credentials" → "Service account"**.
3. Укажите имя, например `sheets-bot-writer`, нажмите **"Create and Continue"**.
4. Роль можно не назначать (или выбрать "Editor") → **"Continue" → "Done"**.

### Шаг 2.4 — Создайте JSON-ключ

1. На странице **Credentials** найдите созданный сервисный аккаунт и кликните на него.
2. Перейдите на вкладку **"Keys"**.
3. **"Add Key" → "Create new key" → формат JSON** → "Create".
4. Файл автоматически скачается — это и есть `credentials.json`.
5. Поместите этот файл в папку проекта `gubkin_bot/` (рядом с `bot.py`).

⚠️ **Никогда не публикуйте этот файл и не коммитьте его в открытый Git-репозиторий** — он даёт полный доступ к таблице.

### Шаг 2.5 — Откройте JSON-файл и найдите email сервисного аккаунта

Внутри `credentials.json` есть поле:
```json
"client_email": "sheets-bot-writer@gubkin-open-day-bot.iam.gserviceaccount.com"
```
Скопируйте это значение.

### Шаг 2.6 — Создайте Google-таблицу и дайте доступ сервисному аккаунту

1. Зайдите на [sheets.google.com](https://sheets.google.com), создайте новую таблицу.
2. Назовите её **точно так же**, как указано в `config.py` → `GOOGLE_SHEET_NAME` (по умолчанию `open_day_gubkin_2024`).
3. Нажмите **"Поделиться" (Share)** в правом верхнем углу.
4. Вставьте email сервисного аккаунта (из шага 2.5) и выдайте роль **"Редактор" (Editor)**.
5. Снимите галочку "уведомить" (необязательно) и нажмите **"Отправить/Поделиться"**.

Готово — теперь бот сможет писать в эту таблицу через сервисный аккаунт. Заголовки таблицы создадутся автоматически при первом запуске.

---

## 3. Установка и запуск бота

### Шаг 3.1 — Установите Python 3.10+ и зависимости

```bash
cd gubkin_bot
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Шаг 3.2 — Настройте переменные окружения

```bash
cp .env.example .env
```

Откройте `.env` и заполните:
```
BOT_TOKEN=ваш_токен_от_BotFather
GOOGLE_SHEET_NAME=open_day_gubkin_2024
GOOGLE_CREDENTIALS_FILE=credentials.json
ADMIN_IDS=123456789
```

Чтобы узнать свой Telegram ID для `ADMIN_IDS`, напишите боту **@userinfobot**.

### Шаг 3.3 — Проверьте структуру файлов

Убедитесь, что `credentials.json` лежит рядом с `bot.py`:
```
gubkin_bot/
├── bot.py
├── credentials.json   ← добавили вручную
├── .env                ← создали из .env.example
└── ...
```

### Шаг 3.4 — Запустите бота

```bash
python3 bot.py
```

Если всё настроено верно, увидите в консоли:
```
INFO - Бот запускается...
```

Теперь откройте бота в Telegram и отправьте `/start`.

---

## 4. Как редактировать списки направлений / дат / времени

Всё хранится в `config.py`:

- **Направления** — словарь `DIRECTIONS`. Добавьте новую запись:
  ```python
  "new_key": {"title": "Название направления", "category": "Технические"},
  ```
  Категория должна совпадать с одной из существующих ("Технические" или "Экономика и менеджмент"), либо можете завести новую — кнопки подстроятся автоматически.

- **Даты** — список `AVAILABLE_DATES`, формат `"YYYY-MM-DD"`.

- **Время** — список `AVAILABLE_TIMES`, формат `"HH:MM"`.

После изменения `config.py` просто перезапустите бота.

---

## 5. Структура итоговой таблицы

| Дата записи в системе | ФИО | Направление | Категория | Дата визита | Время визита | Telegram ID | Telegram username |
|---|---|---|---|---|---|---|---|

Строка добавляется автоматически при подтверждении записи абитуриентом.

---

## 6. Деплой (чтобы бот работал 24/7)

Локальный `python3 bot.py` работает, только пока открыт терминал/компьютер. Для постоянной работы — варианты:

- **VPS** (например, простой сервер за 3-5$/мес) + `systemd`-сервис или `screen`/`tmux`.
- **PythonAnywhere**, **Railway.app**, **Render.com** — простой деплой бесплатного/дешёвого тира под aiogram-бота с polling.

Пример простого `systemd`-юнита на Linux-сервере (`/etc/systemd/system/gubkin-bot.service`):
```ini
[Unit]
Description=Gubkin Open Day Bot
After=network.target

[Service]
WorkingDirectory=/home/youruser/gubkin_bot
ExecStart=/home/youruser/gubkin_bot/venv/bin/python3 bot.py
Restart=always
EnvironmentFile=/home/youruser/gubkin_bot/.env

[Install]
WantedBy=multi-user.target
```
Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gubkin-bot
sudo systemctl start gubkin-bot
```

---

## 7. Частые проблемы

| Проблема | Решение |
|---|---|
| `SpreadsheetNotFound` | Название таблицы в Google Sheets должно **точно** совпадать с `GOOGLE_SHEET_NAME` в `.env` |
| `PermissionError` / `APIError 403` | Не выдан доступ сервисному аккаунту на таблицу — повторите шаг 2.6 |
| `FileNotFoundError: credentials.json` | Файл не лежит в корне проекта или указан неверный путь в `.env` |
| Бот не отвечает | Проверьте `BOT_TOKEN`, убедитесь что процесс `bot.py` запущен и нет ошибок в консоли |
| `Unauthorized` от Telegram | Токен неверный — пересоздайте через BotFather командой `/token` |
