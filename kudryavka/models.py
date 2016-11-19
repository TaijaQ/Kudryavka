from django.conf import settings
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import FieldError
import pytz

from django.db import models
from django.db.models import Lookup, SubfieldBase
from django.db.models.query import QuerySet

try:
    from django.db.models.fields.related import SingleRelatedObjectDescriptor
except ImportError:
    from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor as SingleRelatedObjectDescriptor

import mptt
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey, TreeOneToOneField, TreeManyToManyField
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet
from mptt.signals import node_moved


#####################
#   CUSTOM FIELDS   #
#####################

class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class CustomDateField(models.DateTimeField):
    description = "Custom date time"

    def __init__(self, verbose_name=None, editable=False, name=None, is_dst=True, tz=None, **kwargs):
        self.is_dst, self.timezone = self.time_settings(is_dst)
        self.editable = editable
        models.DateTimeField.__init__(self, verbose_name, name, **kwargs)

    def __str__(self):
        return self.description

    # Custom date settings, here to accommodate for a possible later need
    # for more customized setting implementation
    def time_settings(self, is_dst):
        this_is_dst = is_dst
        if settings.USE_TZ:
            tz_setting = settings.TIME_ZONE
            this_timezone = tz_setting
        else:
            this_timezone = 'Europe/Helsinki'
        return this_is_dst, this_timezone

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if value:
            is_dst, local_tz = self.time_settings(self.is_dst)
            local_time = timezone.localtime(value)
            return local_time
        return value

    def make_utc(self, dt):
        if not dt.tzinfo:
            dt = timezone.make_aware(dt)
        return dt.astimezone(pytz.utc)

    def get_prep_value(self, value):
        if value:
            value = self.make_utc(value)
        return value


# Automatically saves whenever it is modified
class AutoDateTimeField(CustomDateField):
    def pre_save(self, model_instance, add):
        return timezone.now()


# Automatically saves when it is created
class CreatedDateTimeField(CustomDateField):
    def pre_save(self, model_instance, add):
        if not add:
            return getattr(model_instance, self.attname)
        else:
            return timezone.now()


#####################
#   QUERYSET BASE   #
#####################

class InheritanceQuerySet(QuerySet):
    def select_subclasses(self, *subclasses):
        if not subclasses:
            subclasses = [o for o in dir(self.model)
                          if isinstance(getattr(self.model, o), SingleRelatedObjectDescriptor)\
                          and issubclass(getattr(self.model,o).related.model, self.model)]
        new_qs = self.select_related(*subclasses)
        new_qs.subclasses = subclasses
        return new_qs

    def _clone(self, klass=None, setup=False, **kwargs):
        try:
            kwargs.update({'subclasses': self.subclasses})
        except AttributeError:
            pass
        return super(InheritanceQuerySet, self)._clone(**kwargs)

    def iterator(self):
        iter = super(InheritanceQuerySet, self).iterator()
        if getattr(self, 'subclasses', False):
            for obj in iter:
                obj = [getattr(obj, s) for s in self.subclasses if getattr(obj, s)] or [obj]
                yield obj[0]
        else:
            for obj in iter:
                yield obj


#####################
#     SETTINGS      #
#####################


class SettingMixin(object):
    def save(self, *args, **kwargs):
        return super(SettingManager, self).save(*args, **kwargs)


class SettingQuerySet(InheritanceQuerySet, SettingMixin):
    pass


class SettingManager(models.Manager, SettingMixin):
    def get_queryset(self):
        return SettingQuerySet(self.model, using=self.db)


class Setting(models.Model):

    name = models.CharField(max_length=60, null=False, blank=False)
    description = models.CharField(null=True, blank=True, max_length=120)
    slug = models.CharField(max_length=50, null=False, blank=False, unique=True)
    active = models.BooleanField(default=True)
    value = models.CharField(null=True, blank=True, max_length=200)

    objects = SettingManager()

    def __str__(self):
        return self.slug


#####################
#     PROJECTS      #
#####################


class ProjectMixin(object):

    def active(self):
        return self.filter(archived=False)

    def archived(self):
        return self.filter(archived=True)

    def child_posts(self):
        return Post.objects.filter(project=self)

    def child_notes(self):
        return Post.objects.notes().filter(project=self)

    def child_headlines(self):
        return Post.objects.headlines().filter(project=self)

    def child_todos(self):
        return Post.objects.todos().filter(project=self)

    def category(self, catid):
        return self.filter(category=catid)


class ProjectQuerySet(InheritanceQuerySet, ProjectMixin):
    pass


class ProjectManager(TreeManager, ProjectMixin):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self.db)


class Project(MPTTModel):
    title = models.CharField(max_length=50)
    category = models.ForeignKey('ProjectCategory', on_delete=models.PROTECT)
    description = models.TextField()
    parent = TreeForeignKey('self', blank=True, null=True, db_index=True)
    progress = IntegerRangeField(min_value=0, max_value=100, default=0)
    archived = models.BooleanField(default=False)
    modified = AutoDateTimeField(null=True, blank=True)
    created = CreatedDateTimeField(blank=True, editable=False)

    objects = ProjectManager()

    class MPTTMeta:
        order_insertion_by=['title']

    def __str__(self):
        return self.title

    def delete(self):
        for obj in self:
            if obj.archived:
                self.force_delete(obj)
            else:
                self.archive(obj)

    def archive(self):
        for obj in self:
            children = obj.get_descendants().filter(archived=False)
            if len(children):
                for child in children:
                    child.update(parent=obj.parent)
            obj.update(archived=True)

    def force_delete(self):
        for obj in self:
            children = obj.get_descendants().filter(archived=False)
            if len(children):
                for child in children:
                    child.update(parent=obj.parent)
            obj.delete()



#####################
#       NODES       #
#####################


class PostMixin(object):
    def notes(self):
        return self.filter(post_type__slug='n')

    def todos(self):
        return self.filter(post_type__slug='t')

    def with_headlines(self, nro):
        return self.filter(size=nro)

    def only_headlines(self):
        return self.exclude(size="5")

    def by_project(self, p_id):
        return self.filter(project=p_id)

    def by_type(self, type):
        return self.filter(post_type__slug=type)

    def count_progress(self):
        return self.filter(count_progress=True)

    def done(self):
        return self.filter(state="2")

    def inactive(self):
        return self.filter(state="0")

    def working(self):
        return self.filter(state="1")


class PostQuerySet(InheritanceQuerySet, PostMixin):
    pass


class PostManager(TreeManager, PostMixin):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self.db)


class ArchiveManager(TreeManager, PostMixin):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self.db)


class Post(MPTTModel):
    title = models.CharField(max_length=120)
    parent = TreeForeignKey('self', blank=True, null=True, db_index=True, related_name='children')
    state = models.ForeignKey(
        'State', blank=True, null=True, on_delete=models.SET_NULL)
    priority = models.ForeignKey('Priority', blank=True, null=True)
    count_progress = models.BooleanField(default=False)
    modified = AutoDateTimeField(blank=True, editable=False)
    text = models.TextField(blank=True, null=True)
    project = models.ForeignKey('Project', default=None, on_delete=models.PROTECT)
    tags = models.ManyToManyField('PostTag', blank=True)
    post_type = models.ForeignKey('PostType', null=True, default=None, on_delete=models.PROTECT)
    size = IntegerRangeField(min_value = 1, max_value = 5, default=5)
    created = CreatedDateTimeField(blank=True, editable=False)
    link = models.URLField(max_length=200, null=True, blank=True)

    objects = PostManager()

    class Meta:
        order_with_respect_to = 'created'

    def __str__(self):
        return self.title


class Archive(MPTTModel):
    title = models.CharField(max_length=120)
    parent = TreeForeignKey('self', blank=True, null=True, db_index=True, related_name='children')
    archived = CreatedDateTimeField(blank=True, editable=False)
    text = models.TextField(blank=True, null=True)
    project = models.ForeignKey('Project', default=None, on_delete=models.PROTECT)
    tags = models.ManyToManyField('PostTag', blank=True)
    post_type = models.ForeignKey('PostType', null=True, default=None, on_delete=models.PROTECT)
    size = IntegerRangeField(min_value = 1, max_value = 5, default=5)
    created = CreatedDateTimeField(blank=True, editable=False)

    objects = ArchiveManager()

    class MPTTMeta:
        order_insertion_by=['archived']

    def __str__(self):
        return self.title


class PostTag(MPTTModel):
    title = models.CharField(max_length=120)
    description = models.TextField()
    parent = TreeForeignKey('self', blank=True, null=True, db_index=True)

    class MPTTMeta:
        order_insertion_by=['title']

    def __str__(self):
        return self.title


class ProjectCategory(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()

    class Meta:
        verbose_name = 'Project category'
        verbose_name_plural = 'Project categories'

    def __str__(self):
        return self.title


class PostType(models.Model):
    slug = models.CharField(max_length=1)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class State(models.Model):
    ACTIVITY = (
        (0, 'Inactive'),
        (1, 'Active'),
        (2, 'Done'),
    )
    title = models.CharField(max_length=120)
    description = models.TextField()
    active = models.IntegerField(choices=ACTIVITY)

    def __str__(self):
        return self.title


class Priority(models.Model):
    slug = models.CharField(max_length=1)
    title = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Priority'
        verbose_name_plural = 'Priorities'

    def __str__(self):
        return "%s: %s" % (self.slug, self.title)


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return "%s, %s" % (self.last_name, self.first_name)