from rest_framework import serializers
from .models import Place, Borsch, AppUser, Rating, Comment, CommentLike, CommentReply, FavoriteBorsch


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class BorschListSerializer(serializers.ModelSerializer):
    """Борщ для списку (без вкладених даних)."""
    place_name = serializers.CharField(source='place.name', read_only=True)
    place_city = serializers.CharField(source='place.city', read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)

    class Meta:
        model = Borsch
        fields = '__all__'


class BorschDetailSerializer(serializers.ModelSerializer):
    """Борщ з деталями."""
    place = PlaceSerializer(read_only=True)
    place_id = serializers.IntegerField(write_only=True)
    ratings = RatingSerializer(many=True, read_only=True)

    class Meta:
        model = Borsch
        fields = '__all__'


class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = '__all__'


class CommentReplySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = CommentReply
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    replies = CommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class FavoriteBorschSerializer(serializers.ModelSerializer):
    borsch = BorschListSerializer(read_only=True)

    class Meta:
        model = FavoriteBorsch
        fields = '__all__'
