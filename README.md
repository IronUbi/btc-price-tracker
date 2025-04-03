# Kripto Para Fiyat İzleyici

Bu proje, yüksek hacimli kripto para borsalarından BTC fiyat verilerini düzenli olarak çekip Github deposunda saklar. Veriler her dakika güncellenir ve en iyi alış/satış fırsatları belirlenir.

## Özellikler

- Her 1 dakikada bir çalışarak büyük borsalardan BTC fiyat verilerini çeker
- Binance, Coinbase, Kraken, Huobi gibi büyük borsalardan veri toplar
- Hangi borsanın alışta, hangi borsanın satışta avantajlı olduğunu belirler
- JSON formatında günlük veri dosyaları oluşturur
- Günlük özet dosyaları ile genel durumu takip etmeyi kolaylaştırır
- Olası arbitraj fırsatlarını tespit eder

## Veri Dosyaları

Veriler iki formatta saklanır:

1. `data/btc_prices_YYYY-MM-DD.json`: Tüm ham veriler
2. `data/summary_YYYY-MM-DD.json`: Günlük özet 

## API Kullanımı

Veriler doğrudan GitHub'dan API ile çekilebilir:

```
https://raw.githubusercontent.com/IronUbi/btc-price-tracker/main/data/summary_YYYY-MM-DD.json
```

## Kurulum

Bu projeyi kendi GitHub hesabınızda kullanmak için:

1. Repository'yi fork edin
2. GitHub Actions'ın çalışabilmesi için repository ayarlarından "Actions" izinlerini etkinleştirin
3. İlk çalıştırmayı manuel olarak tetikleyin: Actions -> BTC Price Tracker -> Run workflow

## Web Sitenize Entegre Etme

JSON verilerini web sitenize aşağıdaki gibi çekebilirsiniz:

```javascript
async function fetchBtcData() {
  const date = new Date().toISOString().slice(0, 10); // YYYY-MM-DD formatı
  const url = `https://raw.githubusercontent.com/[KULLANICI_ADI]/[REPO_ADI]/main/data/summary_${date}.json`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Veri çekme hatası:', error);
    return null;
  }
}
```

## Not

- GitHub Actions'ın çalışma sıklığı her 1 dakika olarak ayarlanmıştır
- API'ler sınırlamalar getirebilir, bu durumda bazı veriler eksik olabilir
- Bu veriyi ticari amaçla kullanmadan önce, her borsanın API kullanım koşullarını gözden geçirin
