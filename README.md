# django_quest
Ancestors and descendants of node in 1 query

## Деплой
~~~
pip install -r requirements.txt
~~~
~~~
cd django_quest
python manage.py migrate
python manage.py loaddata data.json
~~~
Админка: admin:root

## Реализация
Выгрузка меню в 1 запрос реализована с помощью рекурсивного raw-запроса.
Как вариант можно выгрузить сразу все узлы меню и уже в проге отсеить лишние,
но первый вариант мне показался интереснее.

Скрин с debug toolbar:
![image](https://user-images.githubusercontent.com/61431365/222961990-e3642547-db3b-4dee-a6dd-0c5388ff750d.png)
