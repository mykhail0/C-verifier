from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView
from django.utils import timezone

from .models import Directory, File
from .forms import DirectoryForm, FileForm

def index(request):
    directories = Directory.objects.all
    files = File.objects.all
    #directories = Directory.objects.order_by('name')
    #files = File.objects.order_by('owner')
    context = {
        'directories': directories,
        'files': files,
        'theme': 'dark'
    }
    return render(request, 'filesystem/index.html', context)


class DirectoryCreateView(CreateView):
    form_class = DirectoryForm
    template_name = 'filesystem/directory_form.html'

    def form_valid(self, form):
        # form.instance.owner = self.request.user
        form.instance.creation_date = timezone.now()
        x = form.instance.availability_flag
        form.instance.availability_flag = True if x is None else x
        return super().form_valid(form)

    # idk jakas magia TODO
    def get_form_kwargs(self):
        kwargs = super(DirectoryCreateView, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs


class FileCreateView(CreateView):
    form_class = FileForm
    template_name = 'filesystem/file_form.html'

    def form_valid(self, form):
        # form.instance.owner = self.request.user
        form.instance.creation_date = timezone.now()
        x = form.instance.availability_flag
        form.instance.availability_flag = True if x is None else x
        return super().form_valid(form)

    # idk jakas magia TODO
    def get_form_kwargs(self):
        kwargs = super(FileCreateView, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs
