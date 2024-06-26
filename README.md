###  Онлайн-сервис для обмена кулинарных рецептов.
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) 
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) 

Сайт «Продуктовый помощник». Онлайн-сервис и API где пользователь может опубликовать свои рецепты, подписаться на рецепты других пользователей, 
собрать список понравившихся рецептов в «Избранное», а перед походом в магазин сформировать и загрузить список необходимых для приготовления выбранных рецептов продуктов.


### Функционал проекта Foodgram:
- Регистрация пользователя
- Просмотр рецептов
- Создание,редактирование и удаление рецептов
- Добавление рецептов в избранное и подписка на авторов рецептов
- Формирование и загрузка списка покупок

### Технологии проекта:
- Python 3.9 либо выше
- Django Rest Framework
- React
- Postgres
- Nginx
- Docker

## Учетная запись администратора:

```
- логин: root
- почта:alexin.91@mail.ru 
- пароль: 1244
```

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
SECRET_KEY = ''
DEBUG = False

ALLOWED_HOSTS=*

POSTGRES_USER=django_foodgram
POSTGRES_PASSWORD=foodgram12
POSTGRES_DB=django_foodgram

DB_HOST=db
DB_PORT=5432
```

Автор: [VladErm91](https://github.com/VladErm91)
