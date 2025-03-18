# Prompt Arşiv Sistemi

Yapay zeka dönüşüm araçları (text2text, text2image, image2video vb.) için kapsamlı bir prompt arşivi ve test platformu.

## Özellikler

- **Prompt Arşivi:** Tüm promptlarınızı organize edin, kategorize edin ve kolayca erişin
- **Performans Takibi:** Promptların başarı puanlarını takip edin ve analiz edin
- **Prompt Önerileri:** Mevcut başarılı promptlardan ilham alın
- **Filtreleme ve Arama:** Dil, AI üreteci, dönüşüm türü ve etiketlere göre filtreleme yapın
- **Versiyon Takibi:** Promptların farklı versiyonlarını oluşturun ve karşılaştırın
- **İstatistikler:** Promptlarınız hakkında detaylı istatistikler görüntüleyin
- **API Desteği:** Harici uygulamalar için RESTful API 

## Desteklenen Dönüşüm Türleri

- Text2Text
- Text2Image
- Text2Video
- Text2Audio
- Image2Image
- Image2Text
- Image2Video
- Audio2Text
- Video2Text
- ve diğerleri...

## Kurulum

### Gereksinimler

- Python 3.8+
- pip (Python paket yöneticisi)
- SQLite (veya tercihe bağlı başka bir veritabanı)

### Adımlar

1. Repo'yu klonlayın:
   ```
   git clone https://github.com/kullanici/prompt-arsivi.git
   cd prompt-arsivi
   ```

2. Sanal ortam oluşturun (opsiyonel ama önerilir):
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac için
   venv\Scripts\activate     # Windows için
   ```

3. Bağımlılıkları yükleyin:
   ```
   pip install -r requirements.txt
   ```

4. Veritabanını başlatın:
   ```
   python init_db.py
   ```

5. Uygulamayı çalıştırın:
   ```
   python app.py
   ```

6. Tarayıcınızda şu adresi açın: `http://localhost:5023`

## Kullanım

1. **Yeni Prompt Ekleme:**
   - "Yeni Prompt Ekle" butonuna tıklayın
   - Form alanlarını doldurun
   - Etiketler ekleyin ve sonuç dosyasını yükleyin (isteğe bağlı)
   - "Kaydet" butonuna tıklayın

2. **Promptları Görüntüleme:**
   - Ana sayfadaki "Promptları Keşfet" butonuna tıklayın
   - Filtreleri kullanarak listeyi daraltın
   - Herhangi bir prompt kartına tıklayarak detayları görüntüleyin

3. **Versiyon Oluşturma:**
   - Bir prompt detay sayfasında "Versiyon Oluştur" butonuna tıklayın
   - Prompt içeriğini değiştirin ve diğer alanları güncelleyin
   - "Kaydet" butonuna tıklayın

4. **İstatistikleri Görüntüleme:**
   - Üst menüdeki "İstatistikler" linkine tıklayın
   - Çeşitli grafikler ve analizleri görüntüleyin

## API Kullanımı

API, `http://localhost:5023/api` adresinden erişilebilir.

### Endpointler

- `GET /api/prompts` - Tüm promptları listele (sayfalama ve filtreleme destekler)
- `GET /api/prompts/<id>` - Belirli bir promptu getir
- `GET /api/tags` - Tüm etiketleri listele
- `GET /api/stats` - İstatistikleri getir
- `POST /api/suggest-prompt` - Prompt önerisi oluştur

### Örnek İstek

```javascript
fetch('http://localhost:5023/api/prompts?language=Türkçe&generator_ai=DALL-E 3')
  .then(response => response.json())
  .then(data => console.log(data));
```

## Geliştirme

### Proje Yapısı

```
prompt_archive/
│
├── app.py              # Ana Flask uygulaması
├── config.py           # Konfigürasyon ayarları
├── models.py           # Veritabanı modelleri
├── routes/             # Route'lar
│   ├── __init__.py
│   ├── prompt_routes.py
│   └── api_routes.py
│
├── static/             # Statik dosyalar
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/        # Yüklenen dosyalar
│
├── templates/          # HTML şablonları
├── utils/              # Yardımcı fonksiyonlar
├── requirements.txt    # Bağımlılıklar
└── README.md           # Proje dokümantasyonu
```

### Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın.

## İletişim

Proje sorumlusu: [Ahmet Aksoy](mailto:ahmetax@gmail.com)

Proje bağlantısı: [https://github.com/ahmetax/prompt-archive](https://github.com/ahmetax/prompt-archive)
