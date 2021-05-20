from bootstrap_modal_forms.forms import BSModalModelForm
from django.forms import ModelForm
from .models import Directory, File

class DirectoryForm(BSModalModelForm):
    class Meta:
        model = Directory
        fields = ['name', 'parent', 'desc']

    #def __init__(self, *args, **kwargs):
        #owner = kwargs.pop('owner')
        #super(DirectoryForm, self).__init__(*args, **kwargs)

class FileForm(BSModalModelForm):
    class Meta:
        model = File
        fields = ['name', 'directory', 'file_cont', 'desc']

    #def __init__(self, *args, **kwargs):
        #owner = kwargs.pop('owner')
        #super(FileForm, self).__init__(*args, **kwargs)
