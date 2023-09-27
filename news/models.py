from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        post_rating = self.post_set.all().aggregate(post_rating=Sum('rating'))['post_rating'] or 0
        com_rating_from_author = self.user.comment_set.all().aggregate(rating_from=Sum('rating'))['rating_from'] or 0
        com_rating_on_author = Comment.objects.filter(post__author=self).exclude(user=self.user) \
            .aggregate(rating_on=Sum('rating'))['rating_on'] or 0

        self.rating = post_rating * 3 + com_rating_from_author + com_rating_on_author
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)


class Post(models.Model):
    NEWS = 'NW'
    ARTICLE = "AR"
    UNIT_TYPES = [(NEWS, "новость"), (ARTICLE, "статья")]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=UNIT_TYPES, default=NEWS)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:124] + '...'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    creation_datetime = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
