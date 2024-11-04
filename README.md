# Neuragen_Hackathon

**Aina : Konuşma Gelişimi İçin Yapay Zekâ Destekli Eğitim Asistanı**

**Genel Bakış** 

Aina, 4 - 8 yaş arası çocuklarda sesbilgisel gelişim gecikmesi ve konuşma bozukluklarının erken teşhisini kolaylaştırmak, eğitimsel içerik ve aktivitelerle konuşma becerilerini geliştirmek amacıyla tasarlanmış Türkiye'deki ilk Türkçe yapay zekâ destekli mobil uygulamadır. 

Gelişmiş Gemini-1.5 Flash modeli gibi modelleri kullanarak, kullanıcıların konuşma kalıplarını değerlendirir ve geliştirme alanlarında yönlendirme sağlar. Program süresince Aina, istatistiksel analiz ile gelişimi izleyerek kullanıcıların ilerlemelerini takip etmelerine olanak tanır. 

Aina'nın öne çıkan özelliklerinden biri veri gizliliğine gösterdiği özen. Hiçbir ses verisi kaydedilmez ve kişisel bilgilere erişim sağlanmaz, bu da kullanıcılar için tamamen anonim bir deneyim sunar. Bu yaklaşım, gizlilikten ödün vermeden konuşma terapisi alanında en yeni yapay zeka özelliklerini sunmaktadır.

 - **Demo Linki** : Uygulama demosu için [tıklayınız](https://neuragen-hackathon.onrender.com).
 -   **Uygulama Tanıtım Videosu:** Uygulama tanıtım videosu için [tıklayınız](https://drive.google.com/file/d/1hiMxHpw8UDJVv2dcfuZAHQjI5kJ-B3Vi/view?usp=drive_link).

## Hakkımızda 
 [Ezgi Cinan]([github_linki](https://github.com/ezgicinan))
 [Meltem Öztürkcan]([github_linki](https://github.com/meltemozturkcan))
 [Aylin Baykan]([github_linki](https://github.com/Aylinbaykan/neuragen_hackathon))
 
[Ford Otosan](https://www.linkedin.com/company/ford-otosan/),[Vehbi Koç Vakfı / Vehbi Koç Foundation](https://www.linkedin.com/company/vehbi-koc-vakfi/)  ve  [Mikado Sustainable Development Consulting](https://www.linkedin.com/company/mikado-sustainable-development-consulting/)  iş birliği ile hayata geçirilen  [#GelecekHayalim](https://www.linkedin.com/feed/hashtag/?keywords=gelecekhayalim&highlightedUpdateUrns=urn%3Ali%3Aactivity%3A7226210373039738881)  projesi kapsamında UP School AI Eğitimlerinde bir araya gelerek,  [BTK Akademi](https://www.linkedin.com/company/btk-akademi/) Hackathon 2024 yarışması için Aina uygulamasını geliştirmeye başlayan üç kadın yazılımcıyız. 


## Sistem Mimarisi

## Teknik Özellikler

-   **Backend**: Flask (Python)
-   **Veritabanı**: PostgreSQL, AWS RDS Cloud
-   **Frontend**: Flutter (çapraz platform)
-   **API**: RESTful API
-   **Ses Tanıma**: Google Cloud Gemini API (Gemini-1.5 Flash Model)

### Backend

-   **Teknoloji**: Flask (Python)
-   **Görev**: Aina'nın backend kısmı, kullanıcı etkileşimleri ve ses işleme görevlerini yöneten ana merkez olarak hizmet verir. Gerçek zamanlı ses tanıma ve analiz sağlamak için Google Cloud Gemini API ile entegre edilmiştir.
### Veritabanı

-   **Tür**: PostgreSQL
-   **Dağıtım**: AWS RDS Cloud
-   **Veri Yönetimi**: Veritabanı yapısı, kullanıcı oturum yönetimi ve istatistiksel takip için verimli bir yapı sunar. Aina'nın gizlilik ilkesi doğrultusunda kişisel bilgi veya ses verisi saklanmamaktadır.

### API

-   **Tür**: RESTful API
-   **İşlev**: Frontend, backend ve üçüncü taraf hizmetler arasında iletişimi sağlar. RESTful API, ölçeklenebilirliği sağlamak için hem GET hem de POST isteklerini verimli bir şekilde işleyerek sağlam ve güvenilir veri işleme sunar.

### Ses Tanıma ve Analiz

-   **Servis**: Google Cloud Gemini API (Gemini-1.5 Flash Model)
-   **Görev**: Bu API, kullanıcıların konuşmalarını gerçek zamanlı olarak tanıyarak analiz eder ve kişiselleştirilmiş terapi yolculuğunda AI destekli geri bildirim sağlar.

## Eğitim Modülü
Bu modülde, farklı seviyelere uygun eğitim içerikleri, aktiviteler ve pratik testler bulunur. Eğitim modülü, çocukların bireysel gelişim hızlarına göre uyarlanabilir ve onların konuşma becerilerini güçlendirecek adım adım bir ilerleme sağlar. Modülde ayrıca, görsel destekler ve sesli yönlendirmeler ile çocuğun aktif katılımı teşvik edilir. Dil terapistlerinin ve ebeveynlerin yönlendirmeleriyle birlikte kullanılabilecek bu modül, çocuğun dil gelişiminde kalıcı iyileşmeler elde etmesini hedefler.

## Anonimlik ve Veri Gizliliği

Aina, kullanıcı anonimliği odaklı bir yaklaşımla tasarlanmıştır. Hiçbir ses verisi kaydedilmez ve kullanıcıların kişisel veya tanımlayıcı bilgilerine erişim sağlanmaz. Anonim veri yapıları kullanılarak Aina, veri işleme konusundaki etik standartlarla uyumlu olarak güvenli bir platform sunmaktadır.



## Konuşma Terapisi Standartlarıyla Uyumluluk

Aina'nın yapay zeka destekli yaklaşımı, CAPE-V, SSI, HAPP ve GFTA gibi tanınmış konuşma terapisi değerlendirmeleriyle uyumludur. Bu uyumluluk, konuşma terapistlerine konuşma problemlerinin türü ve şiddeti hakkında standartlaştırılmış ve güvenilir analizler sunarak tanısal içgörüler ve kişiselleştirilmiş geri bildirim sağlamaktadır.


Uygulama Sequence Tasarımı : Sequence Diagramını görmek için [tıklayınız](https://drive.google.com/file/d/1oL6tqO-6lbVSKqBN6TjNNI3ClmsUcDBa/view?usp=drive_link)
