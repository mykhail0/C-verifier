from django.db import models
import datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.urls import reverse
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, login, password=None):
        user = self.model(login=login)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None):
        user = self.create_user(login, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    name = models.CharField(max_length=256)
    login = models.CharField(max_length=40, unique=True)
    USERNAME_FIELD = 'login'
    is_admin = models.BooleanField(default=False)
    objects = UserManager()
    
    def __str__(self):
        return self.login

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

class Directory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name = models.TextField(max_length=256)
    desc = models.TextField(blank=True)
    creation_date = models.DateTimeField()
    availability_flag = models.BooleanField()
    def get_my_path(self):
        return ('' if self.parent is None else Directory.objects.get(pk=self.parent.pk).get_my_path()) + self.name + '/'
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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
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
        VARIANT = 'var', _('Variant')
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
