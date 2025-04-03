import requests
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import os
import pytz
import glob
import shutil

def get_binance_data():
    """Binance'den BTC verilerini çeker"""
    try:
        # Binance API'si değişmeden çalışmaya devam ediyor
        response = requests.get('https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT', 
                               headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(f"Binance API yanıt kodu: {response.status_code}")
            return None
            
        data = response.json()
        return {
            'exchange': 'Binance',
            'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
            'bid': float(data['bidPrice']),
            'ask': float(data['askPrice']),
            'bid_qty': float(data['bidQty']),
            'ask_qty': float(data['askQty'])
        }
    except Exception as e:
        print(f"Binance veri çekme hatası: {e}")
        return None

def get_okx_data():
    """OKX'den BTC verilerini çeker"""
    try:
        # OKX API'sine istek atma
        response = requests.get('https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT',
                               headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(f"OKX API yanıt kodu: {response.status_code}")
            return None
            
        data = response.json()
        
        if data['code'] == '0' and len(data['data']) > 0:
            ticker = data['data'][0]
            return {
                'exchange': 'OKX',
                'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
                'bid': float(ticker['bidPx']),  # En iyi alış fiyatı
                'ask': float(ticker['askPx']),  # En iyi satış fiyatı
                'bid_qty': float(ticker['bidSz']),  # Alış miktarı
                'ask_qty': float(ticker['askSz'])   # Satış miktarı
            }
        else:
            print(f"OKX API veri hatası: {data}")
            return None
    except Exception as e:
        print(f"OKX veri çekme hatası: {e}")
        return None

def get_coinbase_data():
    """Coinbase'den BTC verilerini çeker"""
    try:
        # Coinbase Pro API kullanıyoruz (eski GDAX)
        response = requests.get('https://api.exchange.coinbase.com/products/BTC-USD/ticker',
                               headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(f"Coinbase API yanıt kodu: {response.status_code}")
            return None
            
        ticker_data = response.json()
        
        # Derinlik bilgisi alalım
        order_book = requests.get('https://api.exchange.coinbase.com/products/BTC-USD/book?level=1',
                                 headers={'User-Agent': 'Mozilla/5.0'})
        if order_book.status_code != 200:
            print(f"Coinbase order book API yanıt kodu: {order_book.status_code}")
            book_data = {'bids': [[0, 0]], 'asks': [[0, 0]]}
        else:
            book_data = order_book.json()
        
        return {
            'exchange': 'Coinbase',
            'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
            'bid': float(book_data['bids'][0][0]) if len(book_data['bids']) > 0 else float(ticker_data['price']),
            'ask': float(book_data['asks'][0][0]) if len(book_data['asks']) > 0 else float(ticker_data['price']),
            'bid_qty': float(book_data['bids'][0][1]) if len(book_data['bids']) > 0 else None,
            'ask_qty': float(book_data['asks'][0][1]) if len(book_data['asks']) > 0 else None
        }
    except Exception as e:
        print(f"Coinbase veri çekme hatası: {e}")
        return None
        
def get_kraken_data():
    """Kraken'den BTC verilerini çeker"""
    try:
        response = requests.get('https://api.kraken.com/0/public/Ticker?pair=XBTUSD',
                               headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(f"Kraken API yanıt kodu: {response.status_code}")
            return None
            
        data = response.json()
        
        if 'error' in data and len(data['error']) > 0:
            print(f"Kraken API hata döndürdü: {data['error']}")
            return None
            
        if 'result' in data and 'XXBTZUSD' in data['result']:
            result = data['result']['XXBTZUSD']
            
            return {
                'exchange': 'Kraken',
                'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
                'bid': float(result['b'][0]),
                'ask': float(result['a'][0]),
                'bid_qty': float(result['b'][2]),
                'ask_qty': float(result['a'][2])
            }
        else:
            print(f"Kraken API beklenmeyen yanıt formatı: {data}")
            return None
    except Exception as e:
        print(f"Kraken veri çekme hatası: {e}")
        return None

def get_bybit_data():
    """Bybit'den BTC verilerini çeker"""
    try:
        response = requests.get('https://api.bybit.com/v5/market/orderbook?category=spot&symbol=BTCUSDT&limit=1',
                               headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(f"Bybit API yanıt kodu: {response.status_code}")
            return None
            
        data = response.json()
        
        if data['retCode'] == 0 and 'result' in data:
            result = data['result']
            bid = float(result['b'][0][0]) if 'b' in result and len(result['b']) > 0 else 0
            ask = float(result['a'][0][0]) if 'a' in result and len(result['a']) > 0 else 0
            bid_qty = float(result['b'][0][1]) if 'b' in result and len(result['b']) > 0 else 0
            ask_qty = float(result['a'][0][1]) if 'a' in result and len(result['a']) > 0 else 0
            
            return {
                'exchange': 'Bybit',
                'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
                'bid': bid,
                'ask': ask,
                'bid_qty': bid_qty,
                'ask_qty': ask_qty
            }
        else:
            print(f"Bybit API hata döndürdü: {data}")
            return None
    except Exception as e:
        print(f"Bybit veri çekme hatası: {e}")
        return None

def get_gate_io_data():
    """Gate.io'dan BTC verilerini çeker"""
    try:
        response = requests.get('https://api.gateio.ws/api/v4/spot/order_book?currency_pair=BTC_USDT&limit=1',
                               headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(f"Gate.io API yanıt kodu: {response.status_code}")
            return None
            
        data = response.json()
        
        if 'bids' in data and 'asks' in data:
            bid = float(data['bids'][0][0]) if len(data['bids']) > 0 else 0
            ask = float(data['asks'][0][0]) if len(data['asks']) > 0 else 0
            bid_qty = float(data['bids'][0][1]) if len(data['bids']) > 0 else 0
            ask_qty = float(data['asks'][0][1]) if len(data['asks']) > 0 else 0
            
            return {
                'exchange': 'Gate.io',
                'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
                'bid': bid,
                'ask': ask,
                'bid_qty': bid_qty,
                'ask_qty': ask_qty
            }
        else:
            print(f"Gate.io API beklenmeyen yanıt formatı: {data}")
            return None
    except Exception as e:
        print(f"Gate.io veri çekme hatası: {e}")
        return None

def collect_all_exchange_data():
    """Tüm borsalardan veri toplar"""
    exchange_data = []
    
    # Her borsadan veri çekmeyi deneyin
    binance_data = get_binance_data()
    if binance_data:
        exchange_data.append(binance_data)
    
    okx_data = get_okx_data()
    if okx_data:
        exchange_data.append(okx_data)
    
    coinbase_data = get_coinbase_data()
    if coinbase_data:
        exchange_data.append(coinbase_data)
    
    kraken_data = get_kraken_data()
    if kraken_data:
        exchange_data.append(kraken_data)
    
    bybit_data = get_bybit_data()
    if bybit_data:
        exchange_data.append(bybit_data)
    
    gate_io_data = get_gate_io_data()
    if gate_io_data:
        exchange_data.append(gate_io_data)
    
    return exchange_data

def save_data_to_file(data):
    """Verileri dosyaya kaydeder"""
    current_date = datetime.now().strftime('%Y-%m-%d')
    filename = f'data/btc_prices_{current_date}.json'
    
    # data dizininin var olduğundan emin olun
    os.makedirs('data', exist_ok=True)
    
    # Dosya varsa, mevcut verileri yükleyin
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    
    # Yeni verileri ekleyin
    existing_data.extend(data)
    
    # Dosyaya yazın
    with open(filename, 'w') as file:
        json.dump(existing_data, file, indent=2)
    
    print(f"Veriler {filename} dosyasına kaydedildi")
    
    # Günlük özet dosyası oluşturun
    create_daily_summary(current_date)

def create_daily_summary(date):
    """Günlük özet dosyası oluşturur"""
    input_filename = f'data/btc_prices_{date}.json'
    output_filename = f'data/summary_{date}.json'
    
    if not os.path.exists(input_filename):
        print(f"Özet oluşturulamadı: {input_filename} dosyası bulunamadı")
        return
    
    with open(input_filename, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"Özet oluşturulamadı: {input_filename} dosyası geçersiz JSON formatı")
            return
    
    # Verileri DataFrame'e dönüştürün
    df = pd.DataFrame(data)
    
    # Hangi borsanın alışta, hangi borsanın satışta olduğunu belirleyin
    if not df.empty and len(df) > 0:
        # En düşük satış fiyatı (alış için en iyi)
        min_ask = df.loc[df['ask'] == df['ask'].min()]
        best_to_buy = min_ask['exchange'].values[0] if not min_ask.empty else None
        
        # En yüksek alış fiyatı (satış için en iyi)
        max_bid = df.loc[df['bid'] == df['bid'].max()]
        best_to_sell = max_bid['exchange'].values[0] if not max_bid.empty else None
        
        # Her borsa için son durumu alın
        latest_data = df.groupby('exchange').last().reset_index()
        
        summary = {
            'date': date,
            'latest_update': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
            'best_exchange_to_buy': best_to_buy,
            'best_exchange_to_sell': best_to_sell,
            'arbitrage_opportunity': float(max_bid['bid'].values[0] - min_ask['ask'].values[0]) if not min_ask.empty and not max_bid.empty else 0,
            'exchange_data': latest_data.to_dict('records')
        }
        
        with open(output_filename, 'w') as file:
            json.dump(summary, file, indent=2)
        
        print(f"Günlük özet {output_filename} dosyasına kaydedildi")

def cleanup_old_data(max_days=7, max_files=30):
    """
    Belirli bir günden daha eski verileri temizler
    
    Parameters:
    max_days (int): Saklanacak maksimum gün sayısı
    max_files (int): Saklanacak maksimum dosya sayısı
    """
    print(f"Eski veri temizleme başlatıldı: Maksimum {max_days} gün / {max_files} dosya saklanacak")
    
    # data klasörünün var olduğundan emin olun
    if not os.path.exists('data'):
        print("data klasörü bulunamadı, temizleme atlanıyor")
        return
    
    # Bugünden max_days gün öncesini hesaplayın
    cutoff_date = datetime.now() - timedelta(days=max_days)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
    
    # Tüm btc_prices ve summary dosyalarını bulun
    all_price_files = glob.glob('data/btc_prices_*.json')
    all_summary_files = glob.glob('data/summary_*.json')
    
    # Dosyaları tarihlerine göre sıralayın (en eskiler başta)
    all_price_files.sort()
    all_summary_files.sort()
    
    # Maksimum dosya sayısını kontrol edin
    if len(all_price_files) > max_files:
        files_to_delete = all_price_files[:-max_files]  # En eski dosyaları silin
        for file in files_to_delete:
            try:
                os.remove(file)
                print(f"Dosya silindi (kota aşımı): {file}")
            except Exception as e:
                print(f"Dosya silinirken hata oluştu: {file} - {e}")
    
    # Tarih kontrolüyle dosyaları silin
    for file in all_price_files:
        # Dosya adından tarihi çıkarın
        try:
            # Dosya adı formatı: data/btc_prices_YYYY-MM-DD.json
            file_date_str = file.split('_')[-1].split('.')[0]
            
            # Eğer dosya tarihi cutoff_date'den eskiyse, silin
            if file_date_str < cutoff_date_str:
                os.remove(file)
                print(f"Dosya silindi (tarih eskimesi): {file}")
        except Exception as e:
            print(f"Dosya işlenirken hata oluştu: {file} - {e}")
    
    # Summary dosyaları için de aynı işlemi yapın
    for file in all_summary_files:
        try:
            # Dosya adı formatı: data/summary_YYYY-MM-DD.json
            file_date_str = file.split('_')[-1].split('.')[0]
            
            # Eğer dosya tarihi cutoff_date'den eskiyse, silin
            if file_date_str < cutoff_date_str:
                os.remove(file)
                print(f"Özet dosyası silindi (tarih eskimesi): {file}")
        except Exception as e:
            print(f"Özet dosyası işlenirken hata oluştu: {file} - {e}")
    
    # data klasörünün boyutunu kontrol edin
    try:
        total_size = sum(os.path.getsize(f) for f in glob.glob('data/*') if os.path.isfile(f))
        print(f"Temizleme sonrası data klasörü boyutu: {total_size / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"Klasör boyutu hesaplanırken hata oluştu: {e}")

def main():
    """Ana fonksiyon"""
    print(f"Veri toplama başlatıldı: {datetime.now()}")
    
    # Eski verileri temizleyin (7 günden eski veriler ve maksimum 30 dosya)
    cleanup_old_data(max_days=7, max_files=30)
    
    # Tüm borsalardan verileri toplayın
    exchange_data = collect_all_exchange_data()
    
    if exchange_data:
        # Verileri kaydedin
        save_data_to_file(exchange_data)
        
        # Arbitraj fırsatlarını kontrol edin
        df = pd.DataFrame(exchange_data)
        min_ask = df['ask'].min()
        min_ask_exchange = df.loc[df['ask'] == min_ask, 'exchange'].values[0]
        
        max_bid = df['bid'].max()
        max_bid_exchange = df.loc[df['bid'] == max_bid, 'exchange'].values[0]
        
        # En iyi alış/satış fırsatlarını yazdırın
        print(f"En iyi alış borsası: {min_ask_exchange} ({min_ask} USDT)")
        print(f"En iyi satış borsası: {max_bid_exchange} ({max_bid} USDT)")
        
        # Arbitraj fırsatı varsa yazdırın
        if max_bid > min_ask and min_ask_exchange != max_bid_exchange:
            profit = max_bid - min_ask
            print(f"Arbitraj fırsatı: {min_ask_exchange}'dan alıp {max_bid_exchange}'a satarak {profit:.2f} USDT/BTC kar potansiyeli")
    else:
        print("Hiçbir borsadan veri toplanamadı")

if __name__ == "__main__":
    main()
