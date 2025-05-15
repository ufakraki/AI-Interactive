FROM node:22-alpine

WORKDIR /app

# Önce bağımlılıkları kopyala ve yükle
COPY package*.json ./
RUN npm install --legacy-peer-deps --force

# Uygulama kodunu kopyala
COPY . .

# Build işlemi
RUN npm run build

# Development için çalıştırma komutu
CMD ["npm", "start"]