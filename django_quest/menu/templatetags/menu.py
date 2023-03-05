from django import template
from django.shortcuts import get_object_or_404

from ..models import MenuNode


register = template.Library()


@register.inclusion_tag('menu.html', takes_context=True)
def draw_menu(context, menu_slug):
    raw_path = context['request'].path
    path_list = raw_path.split('/')[1:-1]
    if not path_list or path_list[0] != menu_slug:
        # Если запрашивается главная страница или эл-т другого меню
        return draw_empty_menu(menu_slug)

    current_node_slug = path_list[-1]
    familyQuery = get_all_ancestors_and_childs(current_node_slug)
    if not familyQuery:
        # QuerySet пуст, если запрашиваемый узел не найден
        return draw_empty_menu(menu_slug)

    current_node, ancestors, childs = query_split(familyQuery, menu_slug)
    if current_node.url != raw_path:
        # Если url выбранного узла не совпадает с запрашиваемым
        # Пример: /root-1/node-1-2-2/ - пропущен узел node-1-2
        return draw_empty_menu(menu_slug)

    return {
        'current_node': current_node,
        'ancestors': ancestors,
        'childs': childs,
        'root': menu_slug,
    }


def draw_empty_menu(menu_slug):
    '''
    Отрисовка свернутого меню.
    '''
    root = get_object_or_404(MenuNode, slug=menu_slug)
    return {
        'current_node': None,
        'ancestors': [root],
        'childs': None,
        'root': menu_slug,
    }


def get_all_ancestors_and_childs(current_node_slug):
    '''
    Рекурсивный запрос на основе CTE.
    Результирующая выборка имеет следующий порядок:
    Выбранный узел -> Предки от материнского узла до рута -> Потомки
    '''
    familyQuery = MenuNode.objects.raw(
        '''
        WITH RECURSIVE
        ancestors (id, name, slug, url, parent_id)
        AS (
            SELECT m.id, m.name, m.slug, m.url, m.parent_id
            FROM menu_menunode m
            WHERE slug = %s

            UNION ALL

            SELECT m.id, m.name, m.slug, m.url, m.parent_id
            FROM menu_menunode m
            JOIN ancestors a ON a.parent_id = m.id
        )
        SELECT id, name, slug, url, parent_id FROM ancestors
        
        UNION ALL

        SELECT id, name, slug, url, parent_id FROM menu_menunode
        WHERE parent_id = (
        select id from menu_menunode WHERE slug = %s
        );
        ''',
        [current_node_slug, current_node_slug]
    )
    # Финализируем запрос
    return list(familyQuery)


def query_split(query, root):
    '''
    Разделение результирующей выборки на предков и потомков
    и извлечение из нее текущего узла.
    '''
    childs_part_begins = 1
    for node in query:
        # В конечном итоге дойдем до рута, у которого нет родителя
        if node.parent_id is None:
            break

        childs_part_begins += 1

    current_node = query[0]
    ancestors = query[1:childs_part_begins:][::-1]
    childs = query[childs_part_begins:]

    return (current_node, ancestors, childs)