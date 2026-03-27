import json
import os
from datetime import datetime
from collections import OrderedDict

class SimpleSkinCache:

    #Простой LRU-кеш для одного пользователя
    #Структура:
    #{
    #    'AK-47 | Safari Mesh (Field-Tested)': {
    #        'price': {'💰 Минимальная цена': '7,54 руб.', ...},
    #        'last_updated': '2024-01-01T12:00:00',
    #        'last_accessed': '2024-01-01T12:00:00',
    #        'added_date': '2024-01-01T10:00:00'
    #    }
    #}
    def __init__(self, max_size = 50, cache_file='skin_cache.json'):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.cache_file = cache_file
        self.load()
    
    def add(self, skin_name, price_data):
        #Добавление скина
        now = datetime.now().isoformat()

        if skin_name in self.cache:
            #Обновляем существующий
            self.cache.move_to_end(skin_name)
            self.cache[skin_name].update({
                'price':price_data,
                'last_updated':now,
                'last_accessed':now
            })
        else:
            #Добавляем новый
            if len(self.cache) >= self.max_size:
                #Удаляем самый старый
                removed = self.cache.popitem(last=False)
                print(f"Кеш переполнен, удален: {removed[0]}")
            self.cache[skin_name] = {
                'price':price_data,
                'last_updated':now,
                'last_accessed':now,
                'added_date': now
            }
        self.save()
        return True
    
    def get(self, skin_name):
        #Получить данные о скине
        if skin_name in self.cache:
            self.cache.move_to_end(skin_name)
            self.cache[skin_name]['last_accessed'] = datetime.now().isoformat()
            self.save()
            return self.cache[skin_name]
        return None
    
    def get_all(self):
        #Получить информацию по всем скинам
        return list(self.cache.keys())
    
    def get_all_with_data(self):
        #Получить все скины с данными (для откладки)
        return [(name, data) for name, data in self.cache.items()]
    
    def remove(self, skin_name):
    #Удалить скин
        if skin_name in self.cache:
            del self.cache[skin_name]
            self.save()
            return True
        return False
    
    def update_price(self, skin_name, new_price):
        #Обновление цены скина, возвращает True если цена изменилась
        if skin_name not in self.cache:
            return False
        old_price = self.cache[skin_name]['price'].get('💰 Минимальная цена')
        new_price_str = new_price.get('💰 Минимальная цена')
        self.cache[skin_name]['price'] = new_price
        self.cache[skin_name]['last_updated'] = datetime.now().isoformat()
        changed = (old_price != new_price_str)
        if changed:
            self.cache[skin_name]['previous_price'] = old_price
        self.save()
        return changed
    
    def save(self):
        #Сохранить кеш в файл
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения кеша: {e}")
        
        
    def load(self):
            #Загрузить кеш из файла
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:                        self.cache = OrderedDict(json.load(f))
                print(f"✅ Загружено {len(self.cache)} скинов из кеша")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки кеша: {e}")

    def clear(self):
        self.cache.clear()
        self.save()
        print('Кеш очищен')
