# django_quest
## Деплой
~~~
pip install -r requirements.txt
~~~
~~~
cd django_quest
python manage.py migrate
python manage.py loaddata dump.json
~~~
Админка: admin:root
В админ-зоне реализована поддержка ссылочной целостности:
При изменении узла меню обновляются ссылки всех связанных узлов.
Подробнее: [здесь](https://github.com/P90Master/django_quest/blob/bc4e50f621e5f801b1fcc0917bb31c1e3dad1dc9/django_quest/menu/admin.py#L38)

## Реализация
Выгрузка меню в 1 запрос реализована с помощью рекурсивного raw-запроса.
(понимаю, что это не лучшая практика в проде из-за обслуживания sql-кода)
Как вариант можно выгрузить сразу все узлы меню и уже в проге отсеить лишние,
но первый вариант мне показался интереснее.

Скрин с debug toolbar:
![image](https://user-images.githubusercontent.com/61431365/222961990-e3642547-db3b-4dee-a6dd-0c5388ff750d.png)
