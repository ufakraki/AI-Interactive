# 2 saatte bir otomatik veri güncelleme scripti

import schedule
import time
import json
from redis import Redis
from api_entegrasyon import get_weather_data, get_moon_phase
import smtplib
from email.mime.text import MIMEText
# Hata oluştuğunda e-posta gönderen fonksiyon
def send_error_email(subject, message):
    # GMAIL SMTP ayarları
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "kutkun@gmail.com"  # Gönderen (kendi adresiniz)
    receiver_email = "kutkun@gmail.com"  # Alıcı (kendi adresiniz)
    password = "cphi ochz zuph ttnf"  # Gmail uygulama şifresi kullanın

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"[INFO] Hata bildirimi e-posta ile gönderildi.")
    except Exception as e:
        print(f"[ERROR] E-posta gönderilemedi: {e}")

print("[DEBUG] scheduler.py başladı")
from balik_tahmin import score_fishing_conditions

# Redis bağlantısı (Docker'da servis adı redis olmalı)
r = Redis(host="redis", port=6379)

# Şehirler ve koordinatları
CITIES = {
    "canakkale": {"lat": 40.1, "lon": 26.4, "name": "canakkale"},
    "edremit": {"lat": 39.6, "lon": 26.9, "name": "edremit"},
    "ayvalik": {"lat": 39.3, "lon": 26.7, "name": "ayvalik"}
}

def update_data():
    for city, coords in CITIES.items():
        try:
            print(f"[INFO] {city} için veri çekiliyor...")
            print(f"[DEBUG] get_weather_data öncesi: {coords['name']}")
            w = get_weather_data(coords["name"])
            print(f"[DEBUG] get_weather_data sonrası: {w}")
            if not w:
                print(f"[ERROR] {city} için hava verisi alınamadı, atlanıyor.")
                # Hata durumunda e-posta gönder
                send_error_email(
                    subject=f"balikavi.com Hata: {city} için hava verisi alınamadı",
                    message=f"{city} için hava verisi alınamadı. Saat: {time.ctime()}"
                )
                # Redis'e hata kaydı
                r.set(f"data_{city}", json.dumps({"error": True, "message": "Hava verisi alınamadı"}))
                continue
            print(f"[INFO] Hava verisi: {w}")
            print(f"[DEBUG] get_moon_phase öncesi: lat={coords['lat']}, lon={coords['lon']}")
            m = get_moon_phase(coords["lat"], coords["lon"])
            print(f"[DEBUG] get_moon_phase sonrası: {m}")
            if not m:
                print(f"[ERROR] {city} için ay evresi alınamadı, atlanıyor.")
                send_error_email(
                    subject=f"balikavi.com Hata: {city} için ay evresi alınamadı",
                    message=f"{city} için ay evresi alınamadı. Saat: {time.ctime()}"
                )
                r.set(f"data_{city}", json.dumps({"error": True, "message": "Ay evresi alınamadı"}))
                continue
            print(f"[INFO] Ay evresi: {m}")
            sun = "gün batımı"  # Basit örnek, geliştirilebilir
            season = "ilkbahar"  # Geliştirilebilir
            wind_dir = "güneybatı"  # Geliştirilebilir

            score = score_fishing_conditions(
                water_temp=w["temp"],
                cloud_cover=w["clouds"],
                wind_speed=w["wind_speed"],
                wind_dir=wind_dir,
                pressure=w["pressure"],
                sun_phase=sun,
                moon_phase=m,
                season=season
            )
            print(f"[INFO] Skor: {score}")
            # Sonuçları Redis'e kaydet
            r.set(f"data_{city}", json.dumps({"score": score, "details": {**w, "moon": m}}))
            print(f"[INFO] {city} için veri kaydedildi.")
        except Exception as e:
            print(f"[ERROR] {city} için veri güncellenemedi: {e}")
            send_error_email(
                subject=f"balikavi.com Hata: {city} için genel hata",
                message=f"{city} için veri güncellenemedi: {e}\nSaat: {time.ctime()}"
            )
            r.set(f"data_{city}", json.dumps({"error": True, "message": str(e)}))

# 2 saatte bir güncelle
schedule.every(2).hours.do(update_data)

if __name__ == "__main__":
    update_data()  # Başlangıçta hemen çalıştır
    while True:
        schedule.run_pending()
        time.sleep(60)
