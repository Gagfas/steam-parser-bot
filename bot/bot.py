import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from core.simple_cache import SimpleSkinCache
from core.formatters import get_steam_price_formatted
from core.simple_monitor import SkinMonitor

load_dotenv()
user_monitors = {}

def get_user_monitor(user_id:int, cache: SimpleSkinCache, loop: asyncio.AbstractEventLoop) -> SkinMonitor:
    if user_id not in user_monitors:
        monitor = SkinMonitor(cache, update_interval=300)

        async def on_price_change(skin_name, old_price, new_price):
            await bot.send_message(
                user_id,
                f"⚡ **{skin_name}**\n"
                f"💰 {old_price} → {new_price}",
                parse_mode="Markdown"
            )
        def price_change_sync(skin_name, old_price, new_price):
            asyncio.run_coroutine_threadsafe(on_price_change(skin_name, old_price, new_price), loop)
        monitor.on_price_change = price_change_sync
        monitor.start()
        user_monitors[user_id] = monitor
    return user_monitors[user_id]

user_caches = {}

def get_user_cache(user_id: int) -> SimpleSkinCache:
    if user_id not in user_caches:
        
        data_dir = Path(__file__).parent.parent / 'data'
        
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Создана папка для кеша: {data_dir}")
        
        cache_file = data_dir / f'cache_{user_id}.json'
        
        user_caches[user_id] = SimpleSkinCache(
            max_size=50,
            cache_file=str(cache_file)
        )
        print(f"✅ Создан кеш для пользователя {user_id}")
    return user_caches[user_id]

TOKEN = os.getenv('BOT_TOKEN', '')

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: Message):
    get_user_cache(message.from_user.id)
    await message.answer(
        '**Steam Price Monitor**\n\n'
        'Я помогу отслеживать цены на скины CS2.\n'
        'Используй /help, чтобы узнать команды',
        parse_mode='Markdown'
    )
@dp.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        '**Доступные команды:**\n\n'
        '/start - Начать работу\n'
        '/help - Это сообщение\n'
        '/price <скин> - Показать цену сейчас\n'
        '/add <скин> - Добавить скин в отслеживание \n'
        '/list - Показать мои скины\n'
        '/remove <номер> - Удалить скин',
        parse_mode='Markdown'
    )
@dp.message(Command('price'))
async def cmd_price(message: Message):
    skin_name = message.text.replace('/price', '').strip()
    if not skin_name:
        await message.answer(
            'Укажите название скина\n' \
            'Пример: AK-47 | Safari Mesh (Field-Tested)',
            parse_mode='Markdown'
        )
        return
    await message.bot.send_chat_action(message.chat.id, 'typing')
    try:
        result = get_steam_price_formatted(730, skin_name, 5)
        
        if 'error' in result:
            await message.answer(f"❌ {result['error']}")
        else:
            text = (
                f"🎯 **{result.get('🎯 Предмет', skin_name)}**\n"
                f"💰 {result.get('💰 Минимальная цена', 'Нет данных')}\n"
                f"📈 {result.get('📈 Средняя цена', 'Нет данных')}\n"
                f"📦 {result.get('📦 Объём продаж', 'Нет данных')}"
            )
            if 'ℹ️ Примечание' in result:
                text += f"\nℹ️ {result['ℹ️ Примечание']}"
            
            await message.answer(text, parse_mode="Markdown")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(Command('add'))
async def cmd_add(message: Message):
    user_id = message.from_user.id
    skin_name = message.text.replace('/add', '').strip()
    if not skin_name:
        await message.answer(
            'Укажите название скина\n' \
            'Пример: AK-47 | Safari Mesh (Field-Tested)',
            parse_mode='Markdown'
        )
        return
    await message.bot.send_chat_action(message.chat.id, 'typing')
    result = get_steam_price_formatted(730, skin_name, 5)
    
    if 'error' in result:
        await message.answer(f"❌ {result['error']}")
        return
    cache = get_user_cache(user_id)
    cache.add(skin_name, result)
    loop = asyncio.get_running_loop()
    get_user_monitor(user_id, cache, loop)
    await message.answer(
        f"✅ **Скин добавлен!**\n\n"
        f"🎯 {result.get('🎯 Предмет')}\n"
        f"💰 {result.get('💰 Минимальная цена')}",
        parse_mode="Markdown"
    )
@dp.message(Command('list'))
async def cmd_list(message: Message):
    user_id = message.from_user.id
    cache = get_user_cache(user_id)
    skins = cache.get_all_with_data()
    if not skins:
        await message.answer('У вас нет отслеживаемых скинов')
        return
    
    text = '**Ваши скины:**\n\n'
    for i, (skin_name, data) in enumerate(skins, 1):
        price = data['price'].get('💰 Минимальная цена', 'Н/Д')
        updated = data['last_updated'][:16].replace('T', ' ')
        text += f"{i}. 🎯 {skin_name}\n   💰 {price} (обн: {updated})\n\n"

    if len(text) > 4000:
        text = text[:4000] + '...\n(слишком много скинов)'
    await message.answer(text, parse_mode='Markdown')

@dp.message(Command('remove'))
async def cmd_remove(message:Message):
    user_id = message.from_user.id
    cache = get_user_cache(user_id)
    parts = message.text.split()
    if len(parts) < 2:
        skins = cache.get_all_with_data()
        if not skins:
            await message.answer('У вас нет отслеживаемых скинов')
            return
        text = '**Ваши скины**\n\n'
        for i, (skin_name, data) in enumerate(skins, 1):
            price = data['price'].get('💰 Минимальная цена', 'Н/Д')
            text += f"{i}. 🎯 {skin_name}\n   💰 {price}\n\n"
        text += '❓ Чтобы удалить, введите:\n`/remove номер`'
        await message.answer(text, parse_mode='Markdown')
        return
    
    try:
        idx = int(parts[1]) - 1
    except ValueError:
        await message.answer('Номер должен быть числом')
        return
    skins = cache.get_all_with_data()
    if idx < 0 or idx >= len(skins):
        await message.answer(f'Невеный номер. Всего скинов {len(skins)}')
        return
    skin_name = skins[idx][0]
    cache.remove(skin_name)
    await message.answer(
        'Скин удален!**\n\n'
        f'{skin_name}',
        parse_mode='Markdown'
    )

async def main():
    print('Бот запускается...')
    print(f'Кеш будет сохраняться в папке data/')
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())