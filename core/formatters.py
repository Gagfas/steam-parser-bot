from .steam_api import get_steam_price

def format_steam_price(data, item_name):
    """Форматирует данные о цене для красивого вывода"""
    
    result = {
        '🎯 Предмет': item_name,
        '✅ Статус': 'Найдено'
    }
    
    if 'lowest_price' in data:
        result['💰 Минимальная цена'] = data['lowest_price']
    
    if 'median_price' in data:
        result['📈 Средняя цена'] = data['median_price']
    
    if 'volume' in data:
        result['📦 Объём продаж (шт.)'] = data['volume']
    
    if '_info' in data:
        result['_info'] = data['_info']
        result['ℹ️ Примечание'] = data['_info'].replace('Автоматически добавлено качество: ', '')
    
    return result

def get_steam_price_formatted(app_id, item_name, currency):
    """Получает цену и сразу форматирует"""
    raw_result = get_steam_price(app_id, item_name, currency)
    # Если ошибка — возвращаем как есть
    if 'error' in raw_result:
        return raw_result
    formated = format_steam_price(raw_result, item_name)
    return formated

def print_result(result):
    """Красиво выводит результат запроса"""
    if not isinstance(result, dict):
        print(result)
        return
    
    if 'error' in result:
        # Выводим ошибку с правильными переносами
        print("❌ Ошибка:")
        error_msg = result['error']
        if '\\n' in error_msg:
            error_msg = error_msg.replace('\\', '\n')
        print(f'{error_msg}')
    elif '🎯 Предмет' in result: 
        print("✅ Успешно:")
        print('_' * 40)
        for key, value in result.items():
            if key not in ['_info']:
                print(f"  {key}: {value}")
            print('_' * 40)

    else:
        print("📊 Результат:")
        for key, value in result.items():
            print(f"  {key}: {value}")

