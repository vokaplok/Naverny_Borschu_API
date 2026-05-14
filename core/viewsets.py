from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Avg, Q
import os
from django.conf import settings

from .models import Place, Borsch, AppUser, Rating, Comment, CommentLike, CommentReply, FavoriteBorsch
from .serializers import (
    PlaceSerializer, BorschListSerializer, BorschDetailSerializer,
    AppUserSerializer, RatingSerializer, CommentSerializer,
    CommentReplySerializer, FavoriteBorschSerializer
)


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'address', 'city']

    def get_queryset(self):
        qs = super().get_queryset()
        city = self.request.query_params.get('city')
        place_type = self.request.query_params.get('type')
        ids = self.request.query_params.get('ids')
        bbox = self.request.query_params.get('bbox')
        if city:
            qs = qs.filter(city__icontains=city)
        if place_type:
            # `type` can be a single value (icontains, backward compatible) or
            # a comma-separated list (?type=Паб,Бістро) returning a union — places
            # whose type matches ANY of the listed values.
            type_values = [t.strip() for t in place_type.split(',') if t.strip()]
            if len(type_values) > 1:
                q = Q()
                for t in type_values:
                    q |= Q(type__icontains=t)
                qs = qs.filter(q)
            elif type_values:
                qs = qs.filter(type__icontains=type_values[0])
        if ids:
            # Filter by list of place ids: ?ids=1,2,3
            # Invalid/non-numeric values are silently skipped.
            id_list = []
            for raw in ids.split(','):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    id_list.append(int(raw))
                except ValueError:
                    continue
            qs = qs.filter(id__in=id_list) if id_list else qs.none()
        if bbox:
            # Viewport filter: ?bbox=sw_lat,sw_lng,ne_lat,ne_lng
            # Returns places within the rectangle defined by SW + NE corners.
            try:
                sw_lat, sw_lng, ne_lat, ne_lng = (float(x) for x in bbox.split(','))
                # Clamp to a sane range so a malformed request can't blow up the query.
                if -90 <= sw_lat <= 90 and -90 <= ne_lat <= 90 and -180 <= sw_lng <= 180 and -180 <= ne_lng <= 180:
                    qs = qs.filter(
                        latitude__gte=min(sw_lat, ne_lat),
                        latitude__lte=max(sw_lat, ne_lat),
                        longitude__gte=min(sw_lng, ne_lng),
                        longitude__lte=max(sw_lng, ne_lng),
                    )
            except (ValueError, AttributeError):
                # Bad bbox — ignore filter rather than 500.
                pass
        return qs


class BorschViewSet(viewsets.ModelViewSet):
    queryset = Borsch.objects.select_related('place').prefetch_related('ratings')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BorschDetailSerializer
        return BorschListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        place_id = self.request.query_params.get('place_id')
        type_meat = self.request.query_params.get('type_meat')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        search = self.request.query_params.get('search')
        
        if place_id:
            qs = qs.filter(place_id=place_id)
        if type_meat:
            qs = qs.filter(type_meat__icontains=type_meat)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request, pk=None):
        borsch = self.get_object()
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'No photo provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save to /var/www/navernyborshchu/photos/<borsch_id>/
        photo_dir = f'/var/www/navernyborshchu/photos/{borsch.id}/'
        os.makedirs(photo_dir, exist_ok=True)
        photo_path = os.path.join(photo_dir, photo.name)
        
        with open(photo_path, 'wb+') as f:
            for chunk in photo.chunks():
                f.write(chunk)
        
        photo_url = f'https://navernyborshchu.com/photos/{borsch.id}/{photo.name}'
        urls = borsch.photo_urls or []
        urls.append(photo_url)
        borsch.photo_urls = urls
        borsch.save()
        
        return Response({'photo_url': photo_url}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def reviews(self, request, pk=None):
        """GET: list reviews for borsch. POST: create review."""
        borsch = self.get_object()
        if request.method == 'GET':
            comments = Comment.objects.filter(borschi=borsch).select_related('user').prefetch_related('replies', 'likes')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        # POST - create comment/review
        data = request.data.copy()
        data['borschi'] = borsch.id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppUserViewSet(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user by email (query param)."""
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'email param required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = AppUser.objects.get(email=email)
            return Response(AppUserSerializer(user).data)
        except AppUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def favorites(self, request, pk=None):
        user = self.get_object()
        favs = FavoriteBorsch.objects.filter(user=user).select_related('borsch', 'borsch__place')
        serializer = FavoriteBorschSerializer(favs, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('user').prefetch_related('replies', 'likes')
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        borsch_id = self.request.query_params.get('borsch_id')
        if borsch_id:
            qs = qs.filter(borschi_id=borsch_id)
        return qs

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
        like, created = CommentLike.objects.get_or_create(user_id=user_id, comment=comment)
        if not created:
            like.delete()
            return Response({'liked': False})
        return Response({'liked': True}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        comment = self.get_object()
        data = request.data.copy()
        data['comment'] = comment.id
        serializer = CommentReplySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        borsch_id = self.request.query_params.get('borsch_id')
        if borsch_id:
            qs = qs.filter(borschi_id=borsch_id)
        return qs


class FavoriteBorschViewSet(viewsets.ModelViewSet):
    queryset = FavoriteBorsch.objects.select_related('borsch', 'borsch__place')
    serializer_class = FavoriteBorschSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs
