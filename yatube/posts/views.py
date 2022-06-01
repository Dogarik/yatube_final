from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.models import User


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = (user.is_authenticated
                 and Follow.objects.filter(user=user, author=author).exists())
    context = {
        'page_obj': page_obj,
        'author': author,
        'posts_count': author.posts.count(),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    comments_form = CommentForm(request.POST or None)
    author = post.author
    posts_count = author.posts.count()
    context = {
        'post': post,
        'posts_count': posts_count,
        'comments': comments,
        'comments_form': comments_form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    title = 'Добавить запись'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    context = {
        'form': form,
        'title': title
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    title = 'Редактировать запись'
    post = get_object_or_404(
        Post,
        pk=post_id
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'title': title
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(
        Post,
        pk=post_id
    )
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        # comment.created = datetime.now()
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('author', 'group')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow_check = Follow.objects.get_or_create(
        author=author,
        user=user
    )
    if author != user and not follow_check:
        Follow.objects.create(author=author, user=user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow_check = Follow.objects.filter(author=author, user=user)
    if request.user != author and follow_check:
        Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('posts:profile', username=username)
