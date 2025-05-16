# Temel imaj olarak Python 3.11'in resmi slim sürümünü kullan
FROM python:3.11-slim-bullseye

# Netcat ve gerekli sistem araçlarını kur
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-traditional \
    gcc \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python ortam ayarları
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=core.settings

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını kopyala
COPY . .
# Statik klasörü ayrıca kopyala (varsa)
RUN mkdir -p /app/static
COPY static /app/static

# Komutları çalıştır
CMD ["sh", "-c", "while ! nc -z postgres 5432; do sleep 2; done && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]