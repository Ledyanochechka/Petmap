# 🐾 API и сервисы для карты районов Москвы с pet‑friendly местами

Этот документ — аккуратный **чеклист API и сервисов** для проекта:
**интерактивная карта районов Москвы** с отмеченными:
- 🐕 парками/площадками для собак
- 🏥 ветеринарными клиниками
- 🛍️ зоомагазинами и магазинами для животных

Плюс:
- личный кабинет пользователя
- избранное
- личные заметки (приватные)
- загрузка фото

---

## 🗺️ Карты и география

### Яндекс Карты
Хорошо подходят для Москвы и РФ.

- JS API (карта на сайте):  
  https://yandex.ru/dev/maps/jsapi/
- Геокодер (адрес ⇄ координаты):  
  https://yandex.ru/dev/geocode/
- Общая документация:  
  https://yandex.ru/dev/maps/

**Использование:**
- отображение карты
- полигоны районов
- базовая навигация

---

### OpenStreetMap (open‑source)

- Основной сайт:  
  https://www.openstreetmap.org
- Overpass API (получение объектов по тегам):  
  https://overpass-turbo.eu/
- Документация Overpass API:  
  https://wiki.openstreetmap.org/wiki/Overpass_API

**Подходит для:**
- парков для собак (`leisure=dog_park`)
- пользовательских/неофициальных мест

---

### Leaflet (отрисовка карты)

- Сайт:  
  https://leafletjs.com/
- Документация:  
  https://leafletjs.com/reference.html

**Использование:**
- фронтенд‑карта
- кастомные маркеры
- кластеры точек

---

### Mapbox (альтернатива тайлам)

- https://www.mapbox.com/
- Документация:  
  https://docs.mapbox.com/

---

## 🏥 Организации: ветклиники и зоомагазины

### 2ГИС API
Очень сильный источник данных по организациям.

- Портал разработчика:  
  https://dev.2gis.ru/
- Search / Places API:  
  https://dev.2gis.ru/api/search/overview
- Maps API:  
  https://dev.2gis.ru/api/maps/

**Использование:**
- поиск ветклиник
- поиск зоомагазинов
- категории и фильтры

---

### Google Places API (опционально)

- Overview:  
  https://developers.google.com/maps/documentation/places/web-service/overview
- Pricing:  
  https://developers.google.com/maps/documentation/places/web-service/usage-and-billing

⚠️ Возможны ограничения по доступности и условиям в РФ.

---

## 🧠 Backend (личный кабинет, избранное, заметки)

### FastAPI (Python)

- Сайт:  
  https://fastapi.tiangolo.com/
- Tutorial:  
  https://fastapi.tiangolo.com/tutorial/

**Использование:**
- REST API
- авторизация
- избранное
- личные заметки
- связь с картой

---

### PostgreSQL + PostGIS

- PostgreSQL:  
  https://www.postgresql.org/
- PostGIS:  
  https://postgis.net/
- Документация:  
  https://postgis.net/documentation/

**Использование:**
- геопоиск (в радиусе, в районе)
- хранение координат
- полигоны районов Москвы

---

## 🖼️ Хранение фото (S3‑совместимое)

Рекомендуется хранить изображения вне БД.

### Варианты:

- Yandex Object Storage  
  https://cloud.yandex.ru/services/storage

- VK Cloud Object Storage  
  https://cloud.vk.com/docs/storage

- Selectel Object Storage  
  https://selectel.ru/services/cloud/storage/

**Паттерн:**
- backend выдаёт pre‑signed URL
- фронт грузит файл напрямую

---

## 🔐 Аутентификация

### JWT

- https://jwt.io/
- JWT в FastAPI:  
  https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

---

### OAuth (соц‑логин)

- Google Identity:  
  https://developers.google.com/identity
- VK OAuth:  
  https://dev.vk.com/ru/api/access-token/authcode-flow

---

## 🧪 Инструменты разработки

- Postman (тестирование API):  
  https://www.postman.com/

- Swagger / OpenAPI:  
  https://swagger.io/specification/

---

## ✅ Рекомендованная сборка (MVP → масштабирование)

**Минимально жизнеспособный и масштабируемый стек:**

- Карта: **Яндекс или OSM + Leaflet**
- Организации: **2ГИС API**
- Парки для собак: **OSM + собственная база**
- Backend: **FastAPI**
- База данных: **PostgreSQL + PostGIS**
- Фото: **S3‑storage**

---

## 🚀 Дальнейшие шаги

- Спроектировать схему БД
- Определить API эндпоинты
- Добавить модерацию пользовательских мест
- Подготовить мобильную версию

🐶 Проект отлично масштабируется и легко превращается в полноценный pet‑сервис для города.

