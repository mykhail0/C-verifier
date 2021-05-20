import os

from django.shortcuts import render
from django.views.generic import CreateView, DeleteView
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from bootstrap_modal_forms.generic import BSModalCreateView

from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Directory, File
from .forms import DirectoryForm, FileForm

@ensure_csrf_cookie
def index(request):
    directories = Directory.objects.filter(parent=None)
    files = File.objects.all
    context = {
        'directories': directories,
        'files': files
    }
    return render(request, 'verifier/index.html', context)

class DirectoryCreateView(BSModalCreateView):
    template_name = 'verifier/form.html'
    form_class = DirectoryForm
    success_message = 'Success: directory was created.'
    success_url = reverse_lazy('verifier:index')

    def form_valid(self, form):
        form.instance.creation_date = timezone.now()
        x = form.instance.availability_flag
        form.instance.availability_flag = True if x is None else x
        return super().form_valid(form)

class FileCreateView(BSModalCreateView):
    template_name = 'verifier/form.html'
    form_class = FileForm
    success_message = 'Success: file was created.'
    success_url = reverse_lazy('verifier:index')

    def form_valid(self, form):
        form.instance.creation_date = timezone.now()
        x = form.instance.availability_flag
        form.instance.availability_flag = True if x is None else x
        return super().form_valid(form)

class DirectoryDelete(DeleteView):
    model = Directory
    success_url = reverse_lazy('verifier:index')

class FileDelete(DeleteView):
    model = File
    success_url = reverse_lazy('verifier:index')

def code(request, pk):
    data = {}
    if request.method == 'POST':
        file_obj = File.objects.get(pk=pk)
        if file_obj != None:
            try:
                with file_obj.file_cont.open('r') as f:
                    data['filecontent'] = f.readlines()
            except:
                pass
    return JsonResponse(data)
