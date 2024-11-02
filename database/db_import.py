import psycopg2
from psycopg2.extras import RealDictCursor
import os
import shutil
from datetime import datetime
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

from db_config import DB_CONFIG
from db_config import get_db_connection

# Dosya klasörleri
AUDIO_FOLDER = 'audio_files'
IMAGE_FOLDER = 'images'

# Klasörleri oluştur
for folder in [AUDIO_FOLDER, IMAGE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def create_audio_waveform(audio_path, word):
    """
    Ses dosyasının dalga formunu görselleştirir ve kaydeder

    Args:
        audio_path: Ses dosyasının yolu
        word: Kelime (dosya adı için)
    Returns:
        str: Oluşturulan görsel dosyasının yolu
    """
    try:
        """
        # Ses dosyasını yükle
        y, sr = librosa.load(audio_path)

        # Matplotlib figure oluştur
        plt.figure(figsize=(10, 4))

        # Dalga formunu çiz
        plt.subplot(2, 1, 1)
        librosa.display.waveshow(y, sr=sr)
        plt.title('Waveform')

        # Spektrogramı çiz
        plt.subplot(2, 1, 2)
        spec = librosa.feature.melspectrogram(y=y, sr=sr)
        librosa.display.specshow(librosa.power_to_db(spec, ref=np.max),
                                 y_axis='mel', x_axis='time')
        plt.title('Mel Spectrogram')
        """
        # Dosya adı oluştur
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"{word}_waveform_{timestamp}.png"
        image_path = os.path.join(IMAGE_FOLDER, image_filename)

        # Görseli kaydet
        """
        plt.tight_layout()
        plt.savefig(image_path)
        plt.close()
        """

        return image_path

    except Exception as e:
        print(f"Görsel oluşturma hatası: {str(e)}")
        return None


def add_test_word(word, audio_path, image_path, difficulty_level, category):
    """
    Test kelimesi, ses dosyası ve görselini ekler

    Args:
        word: Kelime/Harf
        audio_path: Ses dosyasının orijinal yolu
        image_path: Görsel dosyasının yolu (None ise otomatik oluşturulur)
        difficulty_level: Zorluk seviyesi (1-5)
        category: Kategori
    """
    try:
        # Ses dosyası için yeni ad oluştur
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        audio_filename = f"{word}_{timestamp}.wav"
        new_audio_path = os.path.join(AUDIO_FOLDER, audio_filename)

        new_image_path = ""

        print("audio_filename = ", audio_filename, " :: new_audio_path = ", new_audio_path)

        # Ses dosyasını kopyala
        shutil.copy2(audio_path, new_audio_path)

        # Eğer görsel yolu verilmediyse otomatik oluştur
        if image_path is None:
            new_image_path = create_audio_waveform(new_audio_path, word)
            print("new image path: ", new_image_path)
        else:
            # Verilen görseli kopyala
            image_filename = f"{word}_waveform_{timestamp}.png"
            new_image_path = os.path.join(IMAGE_FOLDER, image_filename)
            print("image_filename = ", image_filename, " :: new_image_path = ", new_image_path)
            shutil.copy2(image_path, new_image_path)
        

        # Veritabanı bağlantısı
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Önce test_words tablosuna audio_path ve image_path sütunlarını ekle
        try:
            cur.execute("""
                ALTER TABLE turkish_alphabet 
                ADD COLUMN IF NOT EXISTS audio_path VARCHAR(255),
                ADD COLUMN IF NOT EXISTS image_path VARCHAR(255)
            """)
            conn.commit()
        except psycopg2.Error as e:
            print(f"Sütun ekleme hatası (zaten varsa normal): {e}")

        # Kelimeyi veritabanına ekle
        cur.execute("""
            INSERT INTO turkish_alphabet 
            (letter, difficulty_level, category, audio_path, image_path)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (word, difficulty_level, category, new_audio_path, new_image_path))

        new_word = cur.fetchone()
        conn.commit()

        print(f"Eklendi: {word}")
        print(f"Ses dosyası: {new_audio_path}")
        print(f"Görsel dosyası: {new_image_path}")

        return new_word

    except Exception as e:
        print(f"Hata: {word} eklenirken hata oluştu - {str(e)}")
        # Hata durumunda dosyaları temizle
        for path in [new_audio_path, new_image_path]:
            if path and os.path.exists(path):
                os.remove(path)
        raise e

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()



def test_word_import():
    """
    Ana fonksiyon - Test kelimelerini ekler
    """
    # Test kelimeleri
    test_words = [
        {
            'word': 'A',
            'audio_path': 'audio_files/a.wav',
            'image_path': 'images/a.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'B',
            'audio_path': 'audio_files/b.wav',
            'image_path': 'images/B.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'C',
            'audio_path': 'audio_files/c.wav',
            'image_path': 'images/C.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'CH',
            'audio_path': 'audio_files/ch.wav',
            'image_path': 'images/CH.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'D',
            'audio_path': 'audio_files/d.wav',
            'image_path': 'images/D.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'E',
            'audio_path': 'audio_files/e.wav',
            'image_path': 'images/E.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'F',
            'audio_path': 'audio_files/f.wav',
            'image_path': 'images/F.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'G',
            'audio_path': 'audio_files/g.wav',
            'image_path': 'images/G.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'GH',
            'audio_path': 'audio_files/gh.wav',
            'image_path': 'images/GH.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'H',
            'audio_path': 'audio_files/h.wav',
            'image_path': 'images/H.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'IH',
            'audio_path': 'audio_files/ih.wav',
            'image_path': 'images/IH.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'

        },
        {
            'word': 'I',
            'audio_path': 'audio_files/i.wav',
            'image_path': 'images/I.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'J',
            'audio_path': 'audio_files/j.wav',
            'image_path': 'images/J.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'K',
            'audio_path': 'audio_files/k.wav',
            'image_path': 'images/K.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'L',
            'audio_path': 'audio_files/L.wav',
            'image_path': 'images/L.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'M',
            'audio_path': 'audio_files/m.wav',
            'image_path': 'images/M.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'N',
            'audio_path': 'audio_files/n.wav',
            'image_path': 'images/N.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'O',
            'audio_path': 'audio_files/o.wav',
            'image_path': 'images/O.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'Ö',
            'audio_path': 'audio_files/oh.wav',
            'image_path': 'images/OH.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'P',
            'audio_path': 'audio_files/p.wav',
            'image_path': 'images/P.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'R',
            'audio_path': 'audio_files/r.wav',
            'image_path': 'images/R.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'S',
            'audio_path': 'audio_files/s.wav',
            'image_path': 'images/S.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'Ş',
            'audio_path': 'audio_files/sh.wav',
            'image_path': 'images/SH.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'T',
            'audio_path': 'audio_files/t.wav',
            'image_path': 'images/T.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'U',
            'audio_path': 'audio_files/u.wav',
            'image_path': 'images/U.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'Ü',
            'audio_path': 'audio_files/uh.wav',
            'image_path': 'images/UH.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'V',
            'audio_path': 'audio_files/v.wav',
            'image_path': 'images/V.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'Y',
            'audio_path': 'audio_files/y.wav',
            'image_path': 'images/Y.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        {
            'word': 'Z',
            'audio_path': 'audio_files/z.wav',
            'image_path': 'images/Z.png',
            'difficulty_level': 1,
            'category': 'UPPER_CASE'
        },
        # Daha fazla kelime ekleyebilirsiniz
    ]

    for word_data in test_words:
        try:
            add_test_word(
                word_data['word'],
                word_data['audio_path'],
                word_data['image_path'],
                word_data['difficulty_level'],
                word_data['category']
            )
        except Exception as e:
            print(f"Kelime eklenemedi: {word_data['word']} - {str(e)}")
            continue


if __name__ == "__main__":
    # Tüm kelimeleri eklemek için
    test_word_import()

    # Veya tek bir kelime eklemek için
    # add_single_word(
    #     word="example",
    #     audio_path="original_audio/example.wav",
    #     difficulty_level=2,
    #     category="basic",
    #     image_path=None  # Otomatik oluşturulacak
    # )

