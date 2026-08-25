# Проект **YaMDb**

## Описание проекта

Проект **YaMDb** собирает отзывы пользователей на произведения. Сами произведения в **YaMDb** не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

Произведения делятся на категории.

Произведению может быть присвоен жанр из списка предустановленных. 

Добавлять произведения, категории и жанры может только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти; из пользовательских оценок формируется усреднённая оценка произведения - рейтинг. На одно произведение пользователь может оставить только один отзыв.

Пользователи могут оставлять комментарии к отзывам.

Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

## Стек технологий

- Python 3.12.7
- Django 5.1.1
- Django REST Framework 3.15.2
- Djoser 2.3.1
- Djangorestframework-simplejwt 5.4.0
- Django-filter 24.3
- Flake8 - линтер
- Python-dotenv
- Sqlite

## Как развернуть проект

Клонировать репозиторий и перейти в него в командной строке:
 
```bash
git clone https://github.com/alevtinamuz/api-yamdb.git
cd api_yamdb
```
 
Создать и активировать виртуальное окружение:
 
```bash
python -m venv venv
source venv/Scripts/activate    # Windows (Git Bash)
source venv/bin/activate        # Linux / macOS
```
 
Установить зависимости из файла requirements.txt:
 
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
 
Создать файл `.env` в корне проекта и заполнить необходимые переменные окружения.
 
Выполнить миграции:
 
```bash
cd api_yamdb
python manage.py migrate
```
 
Наполнить базу данных содержимым из подготовленных csv-файлов (директория `static/data`):
 
```bash
python manage.py load_csv
```
 
Создать суперпользователя:
 
```bash
python manage.py createsuperuser
```
 
Запустить проект:
 
```bash
python manage.py runserver
```
 
Проект будет доступен по адресу `http://127.0.0.1:8000/`.

## Документация API
 
Полная документация со всеми эндпоинтами, схемами запросов/ответов и кодами ошибок доступна после запуска проекта по адресу:
 
```
http://127.0.0.1:8000/redoc/
```
 
Для отладки и проверки работы API также подготовлена коллекция запросов для Postman (директория `postman_collection`, инструкция - в `postman_collection/README.md`).

## Примеры запросов
 
### Регистрация нового пользователя
 
`POST /api/v1/auth/signup/`
 
```json
{
  "email": "user@example.com",
  "username": "user"
}
```
 
### Получение JWT-токена
 
`POST /api/v1/auth/token/`
 
```json
{
  "username": "user",
  "confirmation_code": "string"
}
```
 
Ответ:
 
```json
{
  "token": "string"
}
```
 
### Получение списка всех произведений
 
`GET /api/v1/titles/`
 
Доступна фильтрация по параметрам `category`, `genre`, `name`, `year`.
 
```json
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "name": "string",
      "year": 0,
      "rating": 0,
      "description": "string",
      "genre": [
        {
          "name": "string",
          "slug": "string"
        }
      ],
      "category": {
        "name": "string",
        "slug": "string"
      }
    }
  ]
}
```
 
### Добавление произведения
 
`POST /api/v1/titles/`
 
Права доступа: администратор.
 
```json
{
  "name": "string",
  "year": 2024,
  "description": "string",
  "genre": ["string"],
  "category": "string"
}
```
 
### Добавление отзыва к произведению
 
`POST /api/v1/titles/{title_id}/reviews/`
 
Права доступа: аутентифицированные пользователи. Один отзыв на произведение от одного пользователя.
 
```json
{
  "text": "string",
  "score": 10
}
```
 
### Добавление комментария к отзыву
 
`POST /api/v1/titles/{title_id}/reviews/{review_id}/comments/`
 
Права доступа: аутентифицированные пользователи.
 
```json
{
  "text": "string"
}
```
 
### Получение данных своей учётной записи
 
`GET /api/v1/users/me/`
 
Права доступа: любой авторизованный пользователь.
 
### Изменение данных своей учётной записи
 
`PATCH /api/v1/users/me/`
 
Права доступа: любой авторизованный пользователь. Поле `role` доступно только для чтения.
 
```json
{
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "bio": "string"
}
```
 
## Авторы
 
Проект выполнен командой в рамках учебного курса Яндекс.Практикум.
 
- [Екатерина Пащина](https://github.com/pashchinakate) — управление пользователями: регистрация, аутентификация, права доступа, работа с токеном, подтверждение через e-mail
- [Алевтина Музыченко](https://github.com/alevtinamuz) — модели, представления и эндпоинты для произведений, категорий, жанров; импорт данных из csv
- [Федор Коряков](https://github.com/FedorKoryakov) — отзывы, комментарии, рейтинги произведений
