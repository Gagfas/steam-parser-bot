import time
import threading
from datetime import datetime
from .simple_cache import SimpleSkinCache
from .formatters import get_steam_price_formatted

class SkinMonitor:
    #Мониторинг цен скинов из кеша с заданным интервалом
    def __init__(self, cache, update_interval=300):
        self.cache = cache
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        self.on_price_change = None #обратная связь при изменении цены
        self.on_every_check = None
    
    def start(self):
        if self.running:
            print('Мониторинг уже запущен')
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f'Мониторинг запущен (интервал {self.update_interval} сек)')

    def stop(self):
        #Остановить мониторинг
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print('Мониторинг остановлен')
    
    def _monitor_loop(self):
        #Основной цикл мониторинга
        while self.running:
            try:
                self._check_all_prices()
                #Ожидание с проверкой флага остановки
                for _ in range(self.update_interval):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f'Ошибка в цикле мониторинга: {e}')
                time.sleep(60)
    
    def _check_all_prices(self):
        #Проверить цены всех скинов в кеше
        skins = self.cache.get_all()
        if not skins:
            return
        
        print(f'\n{"="*50}')
        print(f' Проверка цен | {datetime.now().strftime("%H:%M:%S")}')
        print(f'{"="*50}')

        for skin_name in skins:
            result = get_steam_price_formatted(730, skin_name, 5)
      
            if 'error' not in result:
                changed = self.cache.update_price(skin_name, result)
                price = result.get('💰 Минимальная цена')

                if self.on_every_check:
                    data = self.cache.get(skin_name)
                    old_price = data.get('previous_price') if changed else price
                    self.on_every_check(skin_name, old_price, price, changed)

                if changed and self.on_price_change:
                    #Цена изменилась, callback
                    data = self.cache.get(skin_name)
                    old_price = data.get('previous_price')
                    self.on_price_change(skin_name, old_price, price)
            else:
                print(f"Ошибка: {result['error']}")

                #Пауза между запросами, чтобы не нагружать апи
            time.sleep(2)
    print(f"{'='*50}\n")
    print()


    def check_now(self):
        #Принудительно проверить все цены
        print('Принудительная проверка...')
        self._check_all_prices()

    def check_now_with_results(self):
    #Принудительная проверка с возвратом результатов
    #Возвращает список (skin_name, result, changed)

        results = []
        skins = self.cache.get_all()
    
        if not skins:
            print("📭 Кеш пуст")
            return results
    
        print(f"\n🔄 Проверка цен | {datetime.now().strftime('%H:%M:%S')}")
    
        for skin_name in skins:
            print(f"  🔍 {skin_name}")
            result = get_steam_price_formatted(730, skin_name, 5)
        
            if 'error' not in result:
                changed = self.cache.update_price(skin_name, result)
                results.append((skin_name, result, changed))
            
                if changed and self.on_price_change:
                    data = self.cache.get(skin_name)
                    old_price = data.get('previous_price')
                    new_price = result.get('💰 Минимальная цена')
                    self.on_price_change(skin_name, old_price, new_price)
            else:
                results.append((skin_name, result, False))
        
            time.sleep(2)
    
        return results