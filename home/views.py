from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.http import Http404
from home.models import Blog
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Q
import random
import re

@cache_page(60 * 15)
def index (request):
    latest_blogs = Blog.objects.order_by('-time')[:5]
    context = {'latest_blogs': latest_blogs}
    return render(request, 'index.html', context)

def about (request):
    return render(request, 'about.html')

def thanks(request):
    return render(request, 'thanks.html')

def contact (request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        invalid_imput = ['', ' ']
        if name in invalid_imput or email in invalid_imput or phone in invalid_imput or message in invalid_imput:
            messages.error(request, 'One or more fields are empty!')
        else:
            email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            phone_pattern = re.compile(r'^[0-9]{10}$')

            if email_pattern.match(email) and phone_pattern.match(phone):
                form_data = {
                'name':name,
                'email':email,
                'phone':phone,
                'message':message,
                }
                message = '''
                From:\n\t\t{}\n
                Message:\n\t\t{}\n
                Email:\n\t\t{}\n
                Phone:\n\t\t{}\n
                '''.format(form_data['name'], form_data['message'], form_data['email'],form_data['phone'])
                send_mail('You got a mail!', message, '', ['siamaphilbert@outlook.com'])
                messages.success(request, 'Your message was sent.')
                # return HttpResponseRedirect('/thanks')
            else:
                messages.error(request, 'Email or Phone is Invalid!')
    return render(request, 'contact.html', {})

@cache_page(60 * 15)
def blog(request):
    blogs = Blog.objects.order_by('-time')
    paginator = Paginator(blogs, 3)
    page = request.GET.get('page')
    try:
        blogs_page = paginator.page(page)
    except PageNotAnInteger:
        blogs_page = paginator.page(1)
    except EmptyPage:
        blogs_page = paginator.page(paginator.num_pages)
    context = {'blogs': blogs_page}
    return render(request, 'blog.html', context)

@cache_page(60 * 15)
def category(request, category):
    category_posts = Blog.objects.filter(category=category).order_by('-time')
    if not category_posts.exists():
        message = f"No posts found in category: '{category}'"
        return render(request, "category.html", {"message": message})
    paginator = Paginator(category_posts, 3)
    page = request.GET.get('page')

    try:
        category_posts_page = paginator.page(page)
    except PageNotAnInteger:
        category_posts_page = paginator.page(1)
    except EmptyPage:
        category_posts_page = paginator.page(paginator.num_pages)
    context = {
        "category": category,
        "category_posts": category_posts_page,
    }
    return render(request, "category.html", context)


@cache_page(60 * 15)
def categories(request):
    all_categories = Blog.objects.values('category').distinct().order_by('category')
    return render(request, "categories.html", {'all_categories': all_categories})

@cache_page(60 * 15)
def search(request):
    query = request.GET.get('q')
    query_list = query.split()
    results = Blog.objects.none()
    for word in query_list:
        results = results | Blog.objects.filter(Q(title__contains=word) | Q(content__contains=word)).order_by('-time')
    paginator = Paginator(results, 3)
    page = request.GET.get('page')
    results = paginator.get_page(page)
    if len(results) == 0:
        message = "Sorry, no results found for your search query."
    else:
        message = ""
    return render(request, 'search.html', {'results': results, 'query': query, 'message': message})


@cache_page(60 * 15)
def blogpost (request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        context = {'blog': blog}
        return render(request, 'blogpost.html', context)
    except Blog.DoesNotExist:
        context = {'message': 'Blog post not found'}
        return render(request, '404.html', context, status=404)
