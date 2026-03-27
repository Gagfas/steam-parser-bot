import time
from core.simple_cache import SimpleSkinCache
from core.simple_monitor import SkinMonitor
from core.formatters import print_result, get_steam_price_formatted


def add_skin_interactive(cache):
    #Интерактивное добавление скина
    print('\n Добавление нового скина')
    skin_name = input('Введите название скина: ').strip()

    if not skin_name:
        print('Название не может быть пустым')
        return False
    print(f'Проверяю: {skin_name}...')
    result = get_steam_price_formatted(730, skin_name, 5)

    if 'error' in result:
        print(f"Ошибка: {result['error']}")
        return False
    
    cache.add(skin_name, result)
    print(f'Скин добавлен')
    print_result(result)
    return True
    
def remove_skin_interactive(cache):
    #Интерактивное удаление скина
    skins = cache.get_all()
    if not skins:
        print('Кеш пуст, нечего удалять')
        return False
    print('\n Удаление скина')
    print('Доступные скины:')
    for i, skin in enumerate(skins, 1):
        print(f' {i}. {skin}')
    try:
        choice = input('\nВведите номер скина для удаления (или 0 для отмены): '.strip())
        if choice == '0':
            return False
        idx = int(choice) - 1
        if 0 <= idx < len(skins):
            skin_name = skins[idx]
            cache.remove(skin_name)
            print(f'Скин "{skin_name}" удален')
            return True
        else:
            print('Неверный номер')
            return False
    except ValueError:
        print('Введите число')
        return False

def list_skins_interactive(cache):
    #Показать все скины в кеше
    skins = cache.get_all_with_data()
    if not skins:
        print("Кеш пуст")
        return
    print('\n Скины в кеше:')
    print('-'*50)
    for skin_name, data in skins:
        price = data['price'].get('💰 Минимальная цена', 'Н/Д')
        updated = data['last_updated'][:19]
        print(f"🎯 {skin_name}")
        print(f"   💰 {price}")
        print(f"   🕒 {updated}")
    print('-'*50)

def show_menu():
    #Показать главное меню
    print("\n" + "="*50)
    print("🎮 STEAM PRICE MONITOR")
    print("="*50)
    print("1. ➕ Добавить скин")
    print("2. 🗑 Удалить скин")
    print("3. 📋 Показать все скины")
    print("4. 🚀 Запустить мониторинг")
    print("5. 🛑 Остановить мониторинг")
    print("6. 🔄 Проверить цены сейчас")
    print("0. ❌ Выход")
    print("="*50)


def main():
    print("🎮 Steam Price Monitor (Интерактивный режим)")
    print("=" * 50)

    #Создаем кеш(Макс 50 скинов)
    cache = SimpleSkinCache(max_size=50)
    #Создаем монитор ( проверка каждые 5 минут)
    monitor = SkinMonitor(cache, update_interval=300)
    def on_every_check(skin_name, old_price, new_price, changed):
        """Вызывается при каждой проверке"""
        if changed:
            print(f"\n⚡ {skin_name}: {old_price} → {new_price}")
        else:
            print(f"\n💤 {skin_name}: {new_price}")
    monitor.on_every_check= on_every_check

    running = True
    while running:
        show_menu()
        choice = input('Выберите действие: ').strip()
        if choice == '1':
            add_skin_interactive(cache)
        elif choice == '2':
            remove_skin_interactive(cache)
        elif choice == '3':
            list_skins_interactive(cache)
        elif choice == '4':
            if not monitor.running:
                monitor.start()
            else:
                print('Монитор уже запущен')
        elif choice == '5':
            if monitor.running:
                monitor.stop()
            else:
                print("Мониторинг не запущен")
        elif choice == '6':
            print("🔄 Принудительная проверка...")
            results = monitor.check_now_with_results()
    
            if results:
                print("\n📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
                print("-" * 40)
                for skin_name, result, changed in results:
                    if 'error' in result:
                        print(f"❌ {skin_name}: {result['error']}")
                    else:
                        price = result.get('💰 Минимальная цена')
                        changed_mark = "⚡" if changed else " "
                        print(f"{changed_mark} {skin_name}: {price}")
                print("-" * 40)
            else:
                print("📭 Нет скинов для проверки")
    
            input("\nНажмите Enter для продолжения...")

        elif choice == '0':
            if monitor.running:
                monitor.stop()
            print('До свидания!')
            running = False
        else:
            print('Неверный выбор. Попробуйте снова')
        if running and choice not in ['4', '5', '6']: #Не паузить после команд мониторинга
            input('\nНажмите Enter для продолжения...')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n Программа прервана пользователем')
    