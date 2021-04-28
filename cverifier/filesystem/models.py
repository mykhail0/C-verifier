import datetime

from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings


class User(AbstractBaseUser):
    login = models.CharField(max_length=40, unique=True)
    USERNAME_FIELD = 'login'
    name = models.CharField(max_length=256)


class Directory(models.Model):
    #owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=256)
    desc = models.TextField('description', blank=True)
    creation_date = models.DateTimeField('creation date');
    availability_flag = models.BooleanField()
    def get_my_path(self):
        return (settings.MEDIA_ROOT if self.parent is None else Directory.objects.get(pk=self.parent.pk).get_my_path()) + self.name + '/'
    def get_absolute_url(self):
        return reverse('filesystem:index')
    def __str__(self):
        return self.name


class HasSection(models.Model):
    pass


class FileSection(HasSection):
    parent = models.ForeignKey(HasSection, on_delete=models.CASCADE, related_name='parent_has_section')
    name = models.CharField('name', max_length=256, blank=True)
    desc = models.TextField('description', blank=True)
    creation_date = models.DateTimeField('creation date');


def upload_path(instance, filename):
    return Directory.objects.get(pk=instance.directory.pk).get_my_path() + filename


class File(HasSection):
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    #owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    file_data = models.FileField('file', upload_to=upload_path)
    desc = models.TextField('description', blank=True)
    creation_date = models.DateTimeField('creation date');
    availability_flag = models.BooleanField()
    def get_absolute_url(self):
        return reverse('filesystem:index')
    def __str__(self):
        return self.name


class SectionCategory(models.Model):
    class CategoryType(models.TextChoices):
        PROCEDURE = 'PROC', _('Procedure')
        PROPERTY = 'PROP', _('Property')
        LEMMA = 'LEM', _('Lemma')
        ASSERTION = 'ASRT', _('Assert')
        INVARIANT = 'INV', _('Lemma')
        PRECONITION = 'PREC', _('Precondition')
        POSTCONDITION = 'POST', _('Postcondition')

    file_section = models.OneToOneField(
        FileSection,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    category_type = models.CharField(
        max_length=4,
        choices=CategoryType.choices,
        default=CategoryType.PROCEDURE,
    )


class SectionStatus(models.Model):
    class StatusType(models.TextChoices):
        PROVED = 'PROV', _('Proved')
        INVALID = 'INV', _('Invalid')
        COUNTEREXAMPLE = 'COUN', _('Counterexample')
        UNCHECKED = 'UNCH', _('Unchecked')

    file_section = models.OneToOneField(
        FileSection,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    category_type = models.CharField(
        max_length=4,
        choices=StatusType.choices,
        default=StatusType.UNCHECKED,
    )


class StatusData(models.Model):
    content = models.TextField()
    status = models.ForeignKey(SectionStatus, on_delete=models.CASCADE)
    #owner = models.ForeignKey(User, on_delete=models.CASCADE)
