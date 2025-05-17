# Use Python Alpine image as base
FROM python:alpine

# Sistem paketlerini güncelle ve gereksiz paketleri kaldır
RUN apk update && \
    apk add --no-cache \
    netcat-openbsd \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev

# Güvenlik açıklarını azaltmak için pip ve setuptools'u güncelle
RUN pip install --no-cache-dir --upgrade pip setuptools

# (Devamı aynı)

# Python ortam ayarları
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=core.settings

# Setuptools'u güvenli sürüme yükselt
RUN pip install --no-cache-dir setuptools>=70.0.0

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