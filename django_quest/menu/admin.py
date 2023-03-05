from django.contrib import admin

from .models import MenuNode


EMPTY = '-пусто-'


@admin.register(MenuNode)
class MenuNodeAdmin(admin.ModelAdmin):
    exclude = (
        'url',
    )
    list_display = (
        'pk',
        'name',
        'slug',
        'url',
        'parent',
    )
    list_editable = (
        'name',
        'slug',
        'parent',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
        'slug',
        'parent',
    )
    empty_value_display = EMPTY
    prepopulated_fields = {'slug': ('name',)}

    def save_model(self, request, obj, form, change):
        '''
        При сохранении/изменении ноды обновляется ее url:
        он заново собирается на основе собственного slug и slug'ов предков.
        Хотелось бы избежать лишних запросов к родительским нодам
        в случаях, когда поле slug не менялось, но проверить это
        не представляется возможным.

        В целях сохранения ссылочной целостности, url меняются и у
        потомков (если таковые имеются).

        Так как любое изменение полей триггерит пересборку url, то
        изменение поля parent также приводит к обновлению url всех связанных нод.

        Таким образом, изменяя связи нод, можно менять положение
        целых веток в дереве без потери ссылочной целостности.
        (Можно вкладывать целое меню внутрь другого)

        Важно: при изменении slug'a корневого узла нужно также изменить slug в
        {% draw_menu '<Новый slug>' %} в templates/index.html
        Если тэг получит для отрисовки slug несуществующего меню, то выбросит 404.

        Баг: Если узлу в поле parent указать самого себя, (или другим способом
        превратить дерево в граф с циклом), то функция попадет
        в бесконечную рекурсию, и сайт упадет.
        '''
        obj.url = self.new_url_builder(obj)

        if change:
            childs = obj.childs.all()
            if childs:
                new_child_url = obj.url + childs[0].slug + '/'
                # Если url было изменено, то оно не будет совпадать с хранящимся
                # url у дочерней ноды
                if new_child_url != childs[0].url:
                    for child in childs:
                        self.save_model(request, child, form, change)

        super().save_model(request, obj, form, change)

    @staticmethod
    def new_url_builder(obj):
        '''
        Проход по всем потомкам и сбор их slug'ов
        '''
        family_slugs = [obj.slug]
        node = obj.parent

        while node:
            family_slugs.append(node.slug)
            node = node.parent

        new_url = '/' + '/'.join(family_slugs[::-1]) + '/'
        return new_url
