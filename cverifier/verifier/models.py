from django.db import models
import datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from django.conf import settings


class User(AbstractBaseUser):
    login = models.CharField(max_length=40, unique=True)
    USERNAME_FIELD = 'login'
    name = models.CharField(max_length=256)


class Directory(models.Model):
    #owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name = models.TextField(max_length=256)
    desc = models.TextField(blank=True)
    creation_date = models.DateTimeField()
    availability_flag = models.BooleanField()
    def get_my_path(self):
        return (settings.MEDIA_ROOT if self.parent is None else Directory.objects.get(pk=self.parent.pk).get_my_path()) + self.name + '/'
    def get_absolute_url(self):
        return reverse('verifier:index')
    def __str__(self):
        return self.name


class WithSections(models.Model):
    pass


class FileSection(WithSections):
    parent = models.ForeignKey(WithSections, on_delete=models.CASCADE, related_name='file_parent')
    name = models.CharField(max_length=256, blank=True)
    desc = models.TextField(blank=True)
    creation_date = models.DateTimeField()


def upload_path(instance, filename):
    return Directory.objects.get(pk=instance.directory.pk).get_my_path() + filename


class File(WithSections):
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE)
    #owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=256)
    file_cont = models.FileField('file', upload_to=upload_path)
    desc = models.TextField(blank=True)
    creation_date = models.DateTimeField('creation date')
    availability_flag = models.BooleanField()
    def get_absolute_url(self):
        return reverse('verifier:index')
    def __str__(self):
        return self.name


class SectionCategory(models.Model):
    class CategoryType(models.TextChoices):
        PROCEDURE = 'proc', _('Procedure')
        PROPERTY = 'prop', _('Property')
        LEMMA = 'lemma', _('Lemma')
        ASSERTION = 'assert', _('Assert')
        INVARIANT = 'inv', _('Invariant')
        PRECONITION = 'precond', _('Precondition')
        POSTCONDITION = 'postcond', _('Postcondition')

    file_section = models.OneToOneField(
        FileSection,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    category_type = models.CharField(
        max_length=8,
        choices=CategoryType.choices,
        default=CategoryType.INVARIANT,
    )


class SectionStatus(models.Model):
    class StatusType(models.TextChoices):
        PROVED = 'prov', _('Proved')
        INVALID = 'inv', _('Invalid')
        COUNTEREXAMPLE = 'counter', _('Counterexample')
        UNCHECKED = 'unch', _('Unchecked')

    file_section = models.OneToOneField(
        FileSection,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    category_type = models.CharField(
        max_length=8,
        choices=StatusType.choices,
        default=StatusType.UNCHECKED,
    )


class StatusData(models.Model):
    content = models.TextField()
    status = models.ForeignKey(SectionStatus, on_delete=models.CASCADE)
