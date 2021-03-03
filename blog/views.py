import requests
from bs4 import BeautifulSoup

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
        

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/contact.html', {'title': 'About'})

def globe(request):
    return render(request, 'blog/global.html', {'title': 'globe'})

def statedata(request):
    data_request = requests.get('https://api.covid19india.org/data.json')
    update_data = requests.get('https://api.covid19india.org/states_daily.json')
    update = update_data.json()
    data = data_request.json()
    deceased = update['states_daily'][-1]
    recovered = update['states_daily'][-2]
    confirmed = update['states_daily'][-3]
    # print(data['statewise'][1])
    table_data = []
    for i in range(1, len(data['statewise'])):
        state_data = data['statewise'][i]
        da = {'state': state_data['state'], 'confirmed': state_data['confirmed'], 'active': state_data['active'],
              'deaths': state_data['deaths'], 'recovered': state_data['recovered'],
              'latest_confirm': confirmed[state_data['statecode'].lower()],
              'latest_recovered': recovered[state_data['statecode'].lower()], 'latest_deaths': deceased[state_data['statecode'].lower()]}
        table_data.append(da)
    return render(request, 'blog/statewise.html', {'context': table_data})


def country(request):
    url = 'https://coronavirus-19-api.herokuapp.com/countries'
    html_content = requests.get(url)
    country_data=html_content.json()
    context=[]

    for c in country_data:
        ci={'name':c['country'],'confirmed':c['cases'],'recovered':c['recovered'],'deaths':c['deaths']}
        context.append(ci)
    return render(request, 'blog/country.html',{'context':context})

def news(request):

    
    url = "http://newsapi.org/v2/top-headlines?country=in&category=health&apiKey=38f476a7b8fe450eb9ee0482ae30c808"
    data = requests.get(url)
    news_data = data.json()
    news = news_data['articles']
    latest_news = []
    for d in news:
        di = {'source': d['source']['name'], 'pic': d['urlToImage'], 'heading': d['title'],
              'content': d['description'], 'link': d['url']}
        latest_news.append(di)
    return render(request, 'blog/news.html', {'context': latest_news})



