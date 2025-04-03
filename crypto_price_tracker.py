import requests
import pandas as pd
import time
import json
from datetime import datetime
import os
import pytz

def get_binance_data():
    """Binance'den BTC verilerini çeker"""
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT')
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

def get_coinbase_data():
    """Coinbase'den BTC verilerini çeker"""
    try:
        response = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/buy')
        buy_data = response.json()
        
        response = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/sell')
        sell_data = response.json()
        
        return {
            'exchange': 'Coinbase',
            'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
            'bid': float(sell_data['data']['amount']),
            'ask': float(buy_data['data']['amount']),
            'bid_qty': None,  # Coinbase API bu bilgiyi doğrudan sağlamıyor
            'ask_qty': None   # Coinbase API bu bilgiyi doğrudan sağlamıyor
        }
    except Exception as e:
        print(f"Coinbase veri çekme hatası: {e}")
        return None

def get_kraken_data():
    """Kraken'den BTC verilerini çeker"""
    try:
        response = requests.get('https://api.kraken.com/0/public/Ticker?pair=XBTUSD')
        data = response.json()
        result = data['result']['XXBTZUSD']
        
        return {
            'exchange': 'Kraken',
            'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
            'bid': float(result['b'][0]),
            'ask': float(result['a'][0]),
            'bid_qty': float(result['b'][2]),
            'ask_qty': float(result['a'][2])
        }
    except Exception as e:
        print(f"Kraken veri çekme hatası: {e}")
        return None

def get_ftx_data():
    """FTX'den BTC verilerini çeker"""
    try:
        response = requests.get('https://ftx.com/api/markets/BTC/USD')
        data = response.json()
        result = data['result']
        
        return {
            'exchange': 'FTX',
            'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
            'bid': float(result['bid']),
            'ask': float(result['ask']),
            'bid_qty': None,  # FTX API bu bilgiyi doğrudan sağlamıyor
            'ask_qty': None   # FTX API bu bilgiyi doğrudan sağlamıyor
        }
    except Exception as e:
        print(f"FTX veri çekme hatası: {e}")
        return None

def get_huobi_data():
    """Huobi'den BTC verilerini çeker"""
    try:
        response = requests.get('https://api.huobi.pro/market/depth?symbol=btcusdt&type=step0')
        data = response.json()
        
        return {
            'exchange': 'Huobi',
            'timestamp': datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'),
            'bid': float(data['tick']['bids'][0][0]),
            'ask': float(data['tick']['asks'][0][0]),
            'bid_qty': float(data['tick']['bids'][0][1]),
            'ask_qty': float(data['tick']['asks'][0][1])
        }
    except Exception as e:
        print(f"Huobi veri çekme hatası: {e}")
        return None

def collect_all_exchange_data():
    """Tüm borsalardan veri toplar"""
    exchange_data = []
    
    # Her borsadan veri çekmeyi deneyin
    binance_data = get_binance_data()
    if binance_data:
        exchange_data.append(binance_data)
    
    coinbase_data = get_coinbase_data()
    if coinbase_data:
        exchange_data.append(coinbase_data)
    
    kraken_data = get_kraken_data()
    if kraken_data:
        exchange_data.append(kraken_data)
    
    huobi_data = get_huobi_data()
    if huobi_data:
        exchange_data.append(huobi_data)
    
    # Notlar: FTX çalışmayabilir çünkü borsa kapandı, ama kodu dahil ediyorum
    ftx_data = get_ftx_data()
    if ftx_data:
        exchange_data.append(ftx_data)
    
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

def main():
    """Ana fonksiyon"""
    print(f"Veri toplama başlatıldı: {datetime.now()}")
    
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
