# Steam Price Monitor Bot

Telegram бот для отслеживания цен на скины CS2 в Steam Market.

## Возможности
- Поиск текущей цены скина
- Автоматическое исправление формата названий (Field-Tested → (Field-Tested)). Если формат указан некорректно, автоматом будет установлен (Field-Tested), кейсы отрабатывают без этого флага
- Мониторинг изменения цен с уведомлениями
- Поддержка нескольких пользователей (кеш в JSON)
- Команды: `/add`, `/list`, `/remove`, `/price`, `/start`, `/help`

## Установка и запуск

### Локально
```bash
git clone https://github.com/Gagfas/steam-parser-bot.git
cd steam-parser-bot
cp .env.example .env
# Вставьте токен в .env
pip install -r requirements.txt
python bot/bot.py
```

### Запуск через Docker
```bash
git clone https://github.com/Gagfas/steam-parser-bot.git
cd steam-parser-bot
echo "BOT_TOKEN=ваш_токен_здесь" > .env
docker build -t steam-bot .
docker run -d --name steam-bot --restart always --env-file .env steam-bot
```

### Переменные окружения
Создайте файл `.env` с содержанием:
```
BOT_TOKEN=ваш_токен_здесь
```
Токен можно получить у [@BotFather](https://t.me/botfather).

## Важно
Токен бота не хранится в репозитории. Используйте `.env` файл.
