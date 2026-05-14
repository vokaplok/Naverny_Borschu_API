"""
Моделі даних для Naverny Borschu API.
Mapped to existing PostgreSQL schema (integer PKs, existing table names).
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User


class Place(models.Model):
    """Заклад харчування."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, default='')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    type = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'places'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.city})'


class Borsch(models.Model):
    """Борщ у закладі."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='borsches', db_column='place_id')
    photo_urls = ArrayField(models.TextField(), default=list, blank=True)
    grams = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    type_meat = models.TextField(blank=True, default='')
    extras = models.TextField(blank=True, default='')
    dish_features = models.TextField(blank=True, default='')
    date = models.DateTimeField(null=True, blank=True)
    rating_count = models.IntegerField(default=0)
    rating_sum = models.IntegerField(default=0)

    class Meta:
        db_table = 'borschi'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.place.name})'


class AppUser(models.Model):
    """Користувач додатку (custom users table, not Django auth)."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, default='')
    surname = models.CharField(max_length=100, blank=True, default='')
    email = models.CharField(max_length=255, unique=True)
    photo_url = models.CharField(max_length=500, blank=True, default='')
    following_borsch = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'users'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} {self.surname}'


class Rating(models.Model):
    """Оцінки борщу (aggregated per borsch)."""
    id = models.AutoField(primary_key=True)
    borschi = models.ForeignKey(Borsch, on_delete=models.CASCADE, related_name='ratings', db_column='borschi_id')
    rating_salt = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rating_meat = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rating_beet = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rating_density = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rating_aftertaste = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rating_serving = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_rating = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = 'ratings'

    def __str__(self):
        return f'Rating for {self.borschi.name}: {self.overall_rating}'


class Comment(models.Model):
    """Відгук/коментар користувача."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='comments', db_column='user_id')
    borschi = models.ForeignKey(Borsch, on_delete=models.CASCADE, related_name='comments', db_column='borschi_id')
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, default='')
    rating_salt = models.IntegerField(default=0)
    rating_meat = models.IntegerField(default=0)
    rating_beet = models.IntegerField(default=0)
    rating_density = models.IntegerField(default=0)
    rating_aftertaste = models.IntegerField(default=0)
    rating_serving = models.IntegerField(default=0)
    overall_rating = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.name} on {self.borschi.name}'


class CommentLike(models.Model):
    """Лайк на коментар."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='comment_likes', db_column='user_id')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', db_column='comment_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment_likes'
        unique_together = [['user', 'comment']]


class CommentReply(models.Model):
    """Відповідь на коментар."""
    id = models.AutoField(primary_key=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies', db_column='comment_id')
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='comment_replies', db_column='user_id')
    message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment_replies'
        ordering = ['created_at']


class FavoriteBorsch(models.Model):
    """Обраний борщ."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='favorites', db_column='user_id')
    borsch = models.ForeignKey(Borsch, on_delete=models.CASCADE, related_name='favorited_by', db_column='borsch_id')

    class Meta:
        db_table = 'favorite_borschi'
        unique_together = [['user', 'borsch']]
