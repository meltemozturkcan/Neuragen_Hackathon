# Neuragen_Hackathon
program açıklaması

## Takım Üyeleri

- Üye 1: [Ezgi Cinan]([github_linki](https://github.com/ezgicinan))
- Üye 2: [Meltem Öztürkcan]([github_linki](https://github.com/meltemozturkcan))
- Üye 3: [Aylin Baykan](github_linki)
- 
## Teknolojiler

- Backend: Flask (Python)
- Veritabanı: PostgreSQL ,AWS
- Frontend: Flutter
- API: RESTful API
- Ses Tanıma: Google Cloud Gemini API

## Kurulum

1. Repository'yi klonlayın:
```bash
git clone https://github.com/kullanici_adi/repo_adi.git
cd repo_adi
```

2. Virtual environment oluşturun ve aktif edin:
```bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# Linux/Mac için:
source venv/bin/activate
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. PostgreSQL veritabanını kurun:
```bash
# PostgreSQL'i yükleyin ve çalıştırın
# database/db_setup.py dosyasını çalıştırın
python database/db_setup.py
```

5. .env dosyasını oluşturun:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

6. Uygulamayı çalıştırın:
```bash
python app.py
```

## Veritabanı Şeması

- users: Kullanıcı bilgileri
- test_results: Test sonuçları
- test_words: Test kelimeleri
- user_stats: Kullanıcı istatistikleri



## Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## Lisans

Bu proje [MIT](LICENSE) lisansı altında lisanslanmıştır.
