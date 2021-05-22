import re
import os
import html
import subprocess as sub

from django.shortcuts import render, redirect
from django.views.generic import CreateView, DeleteView
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import logout

from .models import *
from .forms import DirectoryForm, FileForm

def logged_in_only(view):
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        return HttpResponseForbidden()
    return inner

def logout_view(request):
    logout(request)
    return redirect('/verifier')

@ensure_csrf_cookie
@login_required(login_url='login/')
def index(request):
    directories = Directory.objects.filter(parent=None)
    files = File.objects.all
    context = {
        'directories': directories,
        'files': files
    }
    return render(request, 'verifier/index.html', context)

class DirectoryCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'verifier/form.html'
    form_class = DirectoryForm
    success_message = 'Success: directory was created.'
    success_url = reverse_lazy('verifier:index')

    def form_valid(self, form):
        form.instance.creation_date = timezone.now()
        x = form.instance.availability_flag
        form.instance.availability_flag = True if x is None else x
        form.instance.owner = self.request.user
        return super().form_valid(form)

class FileCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'verifier/form.html'
    form_class = FileForm
    success_message = 'Success: file was created.'
    success_url = reverse_lazy('verifier:index')

    def form_valid(self, form):
        form.instance.creation_date = timezone.now()
        x = form.instance.availability_flag
        form.instance.availability_flag = True if x is None else x
        form.instance.owner = self.request.user
        return super().form_valid(form)

class DirectoryDelete(LoginRequiredMixin, DeleteView):
    model = Directory
    success_url = reverse_lazy('verifier:index')

class FileDelete(LoginRequiredMixin, DeleteView):
    model = File
    success_url = reverse_lazy('verifier:index')

@logged_in_only
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

@logged_in_only
def frama_output(request, pk):
    data = {}
    if request.method == 'POST':
        file_path = File.objects.get(pk=pk).file_cont.path
        params = request.POST.getlist('params[]')
        data['result'], goals = parse(sub.run(['frama-c'] + params + [file_path], capture_output=True).stdout.decode().splitlines(True))
        for key in goals:
            fs = FileSection.objects.create(parent=File.objects.get(pk=pk), creation_date=timezone.now())
            SectionCategory.objects.create(file_section=fs, category_type=goals[key][1])
            ss = SectionStatus.objects.create(file_section=fs, category_type=goals[key][2])
            StatusData.objects.create(status=ss, content=goals[key][3])
    return JsonResponse(data)

def parse(lines):
    p = re.compile(r'^-{60}\n$')

    # 0 -> goal lines, 1 -> result lines
    int_lines = [[], []]

    mp = {
        'post-condition': 'postcond',
        'pre-condition': 'precond',
        'lemma': 'lemma',
        'assertion': 'assert',
        'property': 'prop',
        'variant': 'var'
    }

    res_mp = {
        'unknown': 'unch',
        'valid': 'prov',
        'failed': 'counter',
        'false': 'counter',
        'invalid': 'inv'
    }

    color_mp = {
        'unch': 'white',
        'prov': 'green',
        'counter': 'orange',
        'inv': 'red'
    }

    for i, pair in enumerate(zip(lines, lines[1:])):
        for _ in range(2):
            if p.match(pair[_]) and pair[1 - _] == '\n':
                int_lines[_].append(i + 2 - 3 * _)

    if len(int_lines[0]) is not len(int_lines[1]):
        print('Could not parse frama-c output.')
        return '', ''

    goals = {}
    for gl, res in zip(int_lines[0], int_lines[1]):
        # Assign (line number, goal name, result, section content) for each goal line number in goal lines.
        # Goal name relates to the section name.
        line = lines[gl].strip()
        words = line.split()
        res_words = lines[res].strip().split()
        result = res_words[res_words.index('returns') + 1].lower()
        # len('Goal ') == 5
        goal_str = line[5:line.find('(') - 1].lower()
        if 'invariant' in goal_str:
            goal_str = 'inv'
        else:
            for key in mp:
                if key in goal_str:
                    goal_str = mp[key]
                    break
        goals[gl] = (int(re.search(r'\d+', words[words.index('line') + 1]).group()), goal_str, res_mp.get(result, result), ''.join(lines[gl:res + 1]))

    to_print = '<pre>\n'
    s, e = 0, 0
    for i, line in enumerate(lines):
        to_print += html.escape(line)
        if int_lines[0] and i == int_lines[0][s]:
            to_print += '<button onclick="$(document).ready(() => {{$(\'#goal{}\').toggle();}});">Hide/Unhide</button>\n'.format(i)
            to_print += '<div id="goal{0}" style="background-color:{1};">\n'.format(i, color_mp[goals[i][2]])
            s += 1
            if s >= len(int_lines[0]):
                s = 0
        if int_lines[1] and i == int_lines[1][e]:
            to_print += '</div>\n'
            e += 1
            if e >= len(int_lines[1]):
                e = 0
    to_print += '</pre>\n'
    return to_print, goals
