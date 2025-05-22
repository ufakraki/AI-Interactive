# API'den hava ve astronomi verisi çekme fonksiyonları

import requests
import os
import ephem  # Ay evresi için eklendi
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY", "")

# Şehir adı ile hava durumu verisi al
# Dönüş: sıcaklık, basınç, bulut, rüzgar hızı, rüzgar yönü

def get_weather_data(city):
    print(f"[DEBUG] get_weather_data çağrıldı: {city}")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},TR&appid={OPENWEATHER_KEY}&units=metric"
    print(f"[DEBUG] OpenWeatherMap URL: {url}")
    try:
        res = requests.get(url).json()
        print(f"[DEBUG] OpenWeatherMap yanıtı: {res}")
    except Exception as e:
        print(f"[ERROR] OpenWeatherMap bağlantı hatası: {e}")
        return None
    if "main" not in res:
        print(f"[ERROR] OpenWeatherMap yanıtı beklenmiyor: {res}")
        return None
    return {
        "temp": res["main"]["temp"],
        "pressure": res["main"]["pressure"],
        "clouds": res["clouds"]["all"],
        "wind_speed": res["wind"]["speed"] * 3.6,  # m/s -> km/s
        "wind_deg": res["wind"]["deg"],
        "sunrise": res["sys"]["sunrise"],
        "sunset": res["sys"]["sunset"]
    }

# Koordinat ile ay evresi al

def get_moon_phase(lat, lon):
    print(f"[DEBUG] get_moon_phase çağrıldı: lat={lat}, lon={lon}")
    # ephem kütüphanesi ile ay evresi hesaplanıyor
    try:
        # Şu anki UTC zamanı al
        now = datetime.utcnow()
        # Gözlemci oluştur (enlem ve boylam ile)
        obs = ephem.Observer()
        obs.lat = str(lat)
        obs.lon = str(lon)
        obs.date = now
        # Ay evresi (0: Yeni Ay, 0.25: İlk Dördün, 0.5: Dolunay, 0.75: Son Dördün)
        moon = ephem.Moon(obs)
        phase = moon.phase  # 0-100 arası, 0: Yeni Ay, 50: Dolunay, 100: Yeni Ay
        print(f"[DEBUG] ephem ay evresi (yüzde): {phase}")
        # Açıklama olarak sadeleştir
        if phase < 5:
            return "Yeni Ay"
        elif 5 <= phase < 45:
            return "Hilal"
        elif 45 <= phase < 55:
            return "Dolunay"
        elif 55 <= phase < 95:
            return "Şişkin Ay"
        else:
            return "Yeni Ay"
    except Exception as e:
        print(f"[ERROR] Ay evresi hesaplanamadı: {e}")
        return "Bilinmiyor"
