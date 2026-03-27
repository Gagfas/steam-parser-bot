Steam Price Monitor Bot

Telegram бот для отслеживания цен на скины CS2 в Steam Market.

## Возможности
- Поиск текущей цены скина
- Автоматическое исправление формата названий (Field-Tested → (Field-Tested)). Если формат указан некорректно, автоматом будет установлен (Field-Tested), кейсы отрабатыват без этого флага 
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
