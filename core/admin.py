from django.contrib import admin
from .models import Place, Borsch, AppUser, Rating, Comment, CommentLike, CommentReply, FavoriteBorsch

admin.site.register(Place)
admin.site.register(Borsch)
admin.site.register(AppUser)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(CommentReply)
admin.site.register(FavoriteBorsch)
