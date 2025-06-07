# Webion

Webion, web sitelerindeki firma bilgilerini otomatik olarak çıkarıp Excel formatında kaydeden bir web scraping uygulamasıdır.

## Özellikler

- Çoklu sayfa tarama ve gezinme
- Firma detay sayfalarına otomatik erişim
- Verileri Excel dosyasına aktarma
- Windows ve Mac platformlarında çalışabilme
- Selenium ve Requests seçenekleri ile esnek scraping

## Kurulum

1. Python 3.8 veya üstü kurulu olmalıdır
2. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

3. Chrome tarayıcısı kurulu olmalıdır (Selenium kullanırken)

## Kullanım

```bash
python main.py
```

Program çalıştırıldığında, kullanıcıdan scraping yapılacak web sitesi URL'sini ve hangi bilgilerin çekilmek istendiğini soracaktır. Veriler toplandıktan sonra, program bunları otomatik olarak Excel dosyasına kaydeder.

## Ayarlar

`main.py` dosyasını düzenleyerek:

- Kaç sayfa taranacağını
- Hangi firma bilgilerinin çıkarılacağını
- Selenium veya Requests kullanımını seçebilirsiniz

## Geliştirici

Webion, Altaion Interactive tarafından geliştirilmiştir.
