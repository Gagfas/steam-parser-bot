import requests
import json
import re

def normalize_qulity(item_name):
    patterns = {
        r'\bFactory New\b': '(Factory New)',
        r'\bMinimal Wear\b': '(Minimal Wear)',
        r'\bField-Tested\b': '(Field-Tested)',
        r'\bWell-Worn\b': '(Well-Worn)',
        r'\bBattle-Scarred\b': '(Battle-Scarred)',
        r'\bVanilla\b': '(Vanilla)'
    }
    for pattern, replacement in patterns.items():
        if re.search(pattern + r'\s*$', item_name):
            if not re.search(r'\([^)]+\)\s*$', item_name):
                return re.sub(pattern + r'\s*$', replacement, item_name)
    return item_name

def has_quality(item_name):
    qualities = ['(Factory New)', '(Minimal Wear)', '(Field-Tested)', 
                 '(Well-Worn)', '(Battle-Scarred)', '(Vanilla)']
    return any(quality in item_name for quality in qualities)

def is_no_data_error(result):
    return(isinstance(result, dict)) and result.get('error') == 'Нет данных о цене'

def retry_with_quality(default_quality = '(Field-Tested)'):
    def decorator(func):
        def wrapper(app_id, item_name, currency, *args, **kwargs):
            if '|' in item_name:
                parts = item_name.split('|')
                if len(parts) > 1:
                    after_pipe = parts[-1].strip()
                    quality_keywords = ['Factory', 'Minimal', 'Field-Tested', 
                                       'Well-Worn', 'Battle-Scarred', 'Vanilla']
                    for keyword in quality_keywords:
                        if keyword in after_pipe:
                            words = after_pipe.split()
                            for i, word in enumerate(words):
                                if keyword in word:
                                    if i < len(words) -2:
                                        return {
                                        'error': f'Неправильный формат. Укажите качество в конце.\n'
                                         f'Пример: "AK-47 | Safari Mesh ({keyword})"\n'
                                         f'Ваш ввод: "{item_name}"'}                               
                                    break 

            normalize_name = normalize_qulity(item_name)
            
            if normalize_name != item_name:
                result = func(app_id, normalize_name, currency, *args, **kwargs)
                if 'error' not in result:
                    result['_info'] = f'Исправлено качество'
                return result
            
            result = func(app_id, item_name, currency, *args, **kwargs)


            if is_no_data_error(result) and not has_quality(item_name):
                new_name = f'{item_name} {default_quality}'
                result = func(app_id, new_name, currency, *args, **kwargs)
                if 'error' not in result:
                    result['_info'] = f'Автоматически добавлено качество: {default_quality}'
                    return result
            return result
        return wrapper
    return decorator

@retry_with_quality()
def get_steam_price(app_id, item_name, currency):
    """ОСНОВНАЯ ФУНКЦИЯ: получает сырые данные от Steam API"""
    url = 'https://steamcommunity.com/market/priceoverview/'
    params = {
        'appid': app_id,
        'market_hash_name': item_name,
        'currency': currency
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            success = data.get('success')
            if success is True:
                if 'lowest_price' in data or 'median_price' in data:
                    return data
                else:
                    return {'error': 'Нет данных о цене'}
            else:
                return {'error': 'Неверный ответ от Steam'}
        else:
            return {'error': f'HTTP ошибка: {response.status_code}'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Ошибка соединения: {e}'}
    