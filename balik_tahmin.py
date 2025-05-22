# Balık avı verim tahmin fonksiyonu
# Kodlar yeni başlayanlar için bol açıklamalı ve sade tutulmuştur.
def score_fishing_conditions(
    water_temp, cloud_cover, wind_speed, wind_dir,
    pressure, sun_phase, moon_phase, season
):
    # Su sıcaklığına göre puan
    def score_temp(t):
        if 14 <= t <= 24:
            return 10
        elif 10 <= t < 14 or 24 < t <= 27:
            return 7
        else:
            return 5

    # Bulutluluğa göre puan
    def score_cloud(c):
        if 30 <= c <= 60:
            return 9
        elif c < 30 or c > 60:
            return 7
        else:
            return 5

    # Rüzgar hızına göre puan
    def score_wind_speed(w):
        if 5 <= w <= 14:
            return 10
        elif 15 <= w <= 20:
            return 7
        else:
            return 5

    # Rüzgar yönüne göre puan
    def score_wind_dir(d):
        direction_map = {
            "kuzey": 6, "kuzeydoğu": 7, "doğu": 6,
            "güneydoğu": 8, "güney": 9, "güneybatı": 7,
            "batı": 7, "kuzeybatı": 6
        }
        return direction_map.get(d.lower(), 6)

    # Basınca göre puan
    def score_pressure(p):
        if 1007 <= p <= 1012:
            return 10
        else:
            return 7

    # Güneş evresine göre puan
    def score_sun(s):
        if s in ["sunrise", "sunset", "gün doğumu", "gün batımı"]:
            return 10
        else:
            return 6

    # Ay evresine göre puan
    def score_moon(m):
        if m.lower() in ["dolunay", "yeni ay"]:
            return 10
        else:
            return 7

    # Mevsime göre puan
    def score_season(s):
        return {"ilkbahar": 9, "yaz": 7, "sonbahar": 8, "kış": 6}.get(s.lower(), 7)

    # Faktörlerin ağırlıkları
    weights = {
        "temp": 0.25,
        "moon": 0.15,
        "cloud": 0.10,
        "wind_speed": 0.10,
        "wind_dir": 0.05,
        "pressure": 0.10,
        "sun": 0.10,
        "season": 0.05
    }

    # Toplam skor hesaplama
    total_score = (
        score_temp(water_temp) * weights["temp"] +
        score_moon(moon_phase) * weights["moon"] +
        score_cloud(cloud_cover) * weights["cloud"] +
        score_wind_speed(wind_speed) * weights["wind_speed"] +
        score_wind_dir(wind_dir) * weights["wind_dir"] +
        score_pressure(pressure) * weights["pressure"] +
        score_sun(sun_phase) * weights["sun"] +
        score_season(season) * weights["season"]
    )

    # Skoru yüzdeye çevirip döndür
    return round(total_score * 10, 1)
