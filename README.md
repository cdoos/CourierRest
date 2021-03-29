# CourierRest
Небольшое Rest API приложение для распределение курьеров написанное на Django Rest Framework.
# Установка
1. Скачать проект с гитхаба: ```git clone https://github.com/cdoos/CourierRest.git```
2. Установить необходимые библиотеки: 
```
pip install -r requirements.txt
ИЛИ
pip install Django
pip install djangorestframework
pip install psycopg2-binary
```
3. Указать данные о базе данных Postgresql в CourierRest/settings.py
4. Выполнить миграции: 
```
./manage.py makemigrations
./manage.py migrate
```
5. Запустить сервис: ```./manage.py runserver```
# Тесты
Для запуска тестов введите комманду: ```./manage.py test couriers```
