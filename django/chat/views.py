from django.views import generic
from django.utils.safestring import mark_safe
from django.contrib.auth.mixins import LoginRequiredMixin

import json

from .models import (
    Room,
    Message,
)

from .forms import (
    MessageCreateForm,
    RoomCreateForm,
)


class IndexView(generic.TemplateView):
    template_name = 'index.djhtml'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update(rooms_names=self.rooms_names())
        return context

    def rooms_names(self):
        return mark_safe([
            room.get('name')
            for room in Room.objects.all().values('name')
        ])


class RoomDetailView(LoginRequiredMixin, generic.DetailView):
    model = Room
    template_name = 'room.djhtml'
    login_url = 'users:login'


    def get_context_data(self, **kwargs):
        context = super(RoomDetailView, self).get_context_data(**kwargs)
        self.object = self.get_object()
        context.update(room_name_json=mark_safe(json.dumps(self.object.name)))
        return context


class RoomCreateView(LoginRequiredMixin, generic.edit.CreateView):
    template_name = 'room_create.djhtml'
    form_class = RoomCreateForm
    login_url = 'users:login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(RoomCreateView, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()
