from django.forms import ModelForm

from .models import Directory, File

class DirectoryForm(ModelForm):
    class Meta:
        model = Directory
        fields = ['name', 'parent', 'desc']

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner')
        super(DirectoryForm, self).__init__(*args, **kwargs)

class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['name', 'directory', 'file_data', 'desc']

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner')
        super(FileForm, self).__init__(*args, **kwargs)
