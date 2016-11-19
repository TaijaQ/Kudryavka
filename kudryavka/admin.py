from django.contrib import admin
from kudryavka.models import (
    Post, Project, PostTag, Priority,
    ProjectCategory, State, PostType,
    Setting, Archive
)
from django.utils.html import format_html

from mptt.admin import DraggableMPTTAdmin


class PostListFilter(admin.SimpleListFilter):
    title = 'post type'
    parameter_name = 'post_type'
    related_filter_parameter = "headline"
    default_value = None

    def lookups(self, request, model_admin):
        if self.related_filter_parameter in request.GET:
            rel_param = request.GET[self.related_filter_parameter]
            if rel_param is True:
                types = PostType.objects.filter(slug='n')
            else:
                types = PostType.objects.all()
        else:
            types = PostType.objects.all()
        return [(type.slug, type.title) for type in types]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            queryset = queryset.by_type(value)
        return queryset


class HeadlineFilter(admin.SimpleListFilter):
    title = 'headlines'
    parameter_name = 'headline'
    related_filter_parameter = "post_type"
    default_value = True

    def lookups(self, request, model_admin):
        choices = (
            (5, 'Exclude'),
            (1, 'H1'),
            (2, 'H2'),
            (3, 'H3'),
            (4, 'H4'),
            (6, 'Only')
        )
        return choices

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            if value == "6":
                queryset = queryset.only_headlines()
            else:
                queryset = queryset.with_headlines(value)
        return queryset


class DraggableAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions','upper_type', 'indented_title', 'state', 'priority', 'level', 'tree_id', 'lft', 'rght', 'created',)
    list_display_links = ('indented_title',)
    empty_value_display = '(None)'
    list_filter = (PostListFilter, HeadlineFilter, 'project', 'tags',)
    fieldsets = (
        ('Info', {
            'fields': ('title', 'text', 'link',),
        }),
        ('Relations', {
            'fields': ('project', 'parent', 'tags', ('post_type', 'size',)),
        }),
        ('Todo options', {
            'classes': ('collapse',),
            'fields': ('count_progress', 'state', 'priority',),
        }))
    mptt_level_indent = 15

    def upper_type(self, obj):
        if obj.size < 5:
            return ("H%s" % (obj.size)).upper()
        else:
            the_type = PostType.objects.get(title=obj.post_type)
            slug = the_type.slug
            return ("%s" % (slug)).upper()

    upper_type.short_description = ' '


class SettingAdmin(admin.ModelAdmin):
    empty_value_display = '(None)'
    list_display = ('name', 'description', 'active', 'value')


class TagAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'description',)
    list_display_links = ('indented_title',)
    empty_value_display = '(None)'


class ProjectAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'category', 'description', 'created', 'modified',)
    list_display_links = ('indented_title',)
    empty_value_display = '(None)'
    list_filter = ('category', 'archived',)
    fieldsets = (
        ('Info', {
            'fields': ('title', 'description', 'category',),
        }),
        ('Relations', {
            'fields': ('parent',),
        }),
        ('Extra options', {
            'classes': ('collapse',),
            'fields': ('progress', 'archived',),
        }))

#admin.site.register(Setting, SettingAdmin)
admin.site.register(Post, DraggableAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(PostTag, TagAdmin)
admin.site.register(PostType)
admin.site.register(ProjectCategory)
admin.site.register(State)
admin.site.register(Priority)