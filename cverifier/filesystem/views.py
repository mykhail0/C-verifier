import os

from django.shortcuts import render
from django.views.generic import CreateView, DeleteView
from django.utils import timezone
from django.urls import reverse

from .models import Directory, File
from .forms import DirectoryForm, FileForm

def index(request):
    directories = Directory.objects.filter(parent=None)
    files = File.objects.all
    context = {
        'directories': directories,
        'files': files,
        'theme': 'root'
    }
    return render(request, 'filesystem/index.html', context)


def detail(request, pk):
    file_obj = File.objects.get(pk=pk)
    file_content = []
    if file_obj != None:
        try:
            with file_obj.file_cont.open('r') as f:
                file_content = f.readlines()
        except:
            pass

    directories = Directory.objects.filter(parent=None)
    files = File.objects.all
    context = {
        'directories': directories,
        'files': files,
        'file_content': file_content,
        'theme': 'root',
        'pk': pk
    }
    return render(request, 'filesystem/detail.html', context)


class DirectoryCreateView(CreateView):
    form_class = DirectoryForm
    template_name = 'filesystem/form.html'

    def form_valid(self, form):
        form.instance.creation_date = timezone.now()
        x = form.instance.availability_flag
        form.instance.availability_flag = True if x is None else x
        try:
            os.mkdir(form.instance.get_my_path())
        except:
            pass
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(DirectoryCreateView, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs


class DirectoryDeleteView(DeleteView):
    model = Directory
    template_name = 'filesystem/del_form.html'
    def get_success_url(self):
        return reverse('filesystem:index')


class FileCreateView(CreateView):
    form_class = FileForm
    template_name = 'filesystem/form.html'

    def form_valid(self, form):
        form.instance.creation_date = timezone.now()
        x = form.instance.availability_flag
        form.instance.availability_flag = True if x is None else x
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(FileCreateView, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs

class FileDeleteView(DeleteView):
    model = File
    template_name = 'filesystem/del_form.html'
    def get_success_url(self):
        return reverse('filesystem:index')
