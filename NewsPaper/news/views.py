from .models import Post
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from .filters import PostFilter
from .forms import PostForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


class PostsList(ListView):

    queryset = Post.objects.order_by('-datetime_post')
    template_name = 'posts.html'
    context_object_name = 'news'
    paginate_by = 10


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'news'
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            return render(request, 'no_post.html', status=404)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class PostsSearchList(ListView):
    model = Post
    ordering = '-datetime_post'
    template_name = 'search.html'
    context_object_name = 'news'
    paginate_by = 1

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class PostCreateView(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/article/create/':
            post.post_type = 'AR'
        post.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['get_title'] = self.get_type()['title']
        context['get_type'] = self.get_type()['content']
        return context

    def get_type(self):
        if self.request.path == '/article/create/':
            return {'title': 'Добавить статью', 'content': 'Добавление статьи'}
        else:
            return {'title': 'Добавить новость', 'content': 'Добавление новости'}


class PostUpdateView(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create_edit.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['get_title'] = self.get_type()['title']
        context['get_type'] = self.get_type()['content']
        return context

    def get_type(self):
        if 'article' in self.request.path:
            return {'title': 'Изменить статью', 'content': 'Редактировать статью'}
        else:
            return {'title': 'Изменить новость', 'content': 'Редактировать новость'}


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    pk_url_kwarg = 'id'