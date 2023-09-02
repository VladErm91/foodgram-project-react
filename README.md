#### Примечаение это моя первая попытка и я очень волнуюсь. Есть некоторые проблемы с djoser которые пока не удалось до конца разрешить (для неавторизованного пользователя нет доступа к страницам юзеров хотя функционал этого реализован)
### Опиание проекта.
Сайт Foodgram, «Продуктовый помощник». Онлайн-сервис и API где пользователь может опубликовать свои рецепты, подписаться на рецепты других пользователей, собрать список понравившихся рецептов в «Избранное», а перед походом в магазин сформировать и загрузить список необходимых для приготовления выбранных рецептов продуктов.

## Проект доступен по ссылке:

```
hoffsfoodgram.ddns.net
```

## Учетная запись администратора:

```
- логин: root
- почта:alexin.91@mail.ru 
- пароль: 1244
```

### Стэк технологий:
- Python
- Django Rest Framework
- Postgres
- Nginx
- Docker

### Функционал проекта Foodgram:

- Просмотр рецептов
- Создание,удаление и редактирование рецептов
- Формирование и загрузка списка покупок
- Добавление рецептов в избранное и подписка на авторов рецептов

## Инструкции по установке
***- Клонируйте репозиторий:***
```
git clone git@github.com:VladErm/foodgram-project-react.git
```
### Сборка и запуск контейнеров:

Из папки infra/  развертываем контейнеры при помощи docker compose:
```
docker compose up -d --build
```
Выполняем миграции:
```
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

```

Сбор статики и наполнение базы данных пулом тегов и ингридиентов:
```
docker compose exec backend python manage.py collectstatic --no-input
docker compose exec backend python manage.py load_data

```

### Необходимые переменные среды (.env)

```
SECRET_KEY = 'django-insecure-cg6-example'

DEBUG = False

ALLOWED_HOSTS=*

# .env
POSTGRES_USER=django_foodgram
POSTGRES_PASSWORD=foodgram12
POSTGRES_DB=django_foodgram
#
DB_HOST=db
DB_PORT=5432
```

