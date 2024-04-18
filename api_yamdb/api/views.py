import requests
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from users.models import User


class UserViewSet(BaseUserViewSet):
    """Вьюсет кастомного пользователя, унаследованный от djoser."""
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()


class ScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        date = request.query_params.get('date')
        if not date:
            return Response({'error': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        url = f'http://strange:3333/api/v1/schedule/day'
        params = {
            'date': date,
            'user-id': user_id
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return Response(response.json())
            else:
                return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        user_id = request.user.id
        description = request.data.get('description')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')

        data = {
            "name": name,
            "user_id": user_id,
            "description": description,
            "date_from": date_from,
            "date_to": date_to
        }
        url = 'http://strange:3333/api/v1/schedule/reserve'
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200 or response.status_code == 201:
                return Response(response.json())
            else:
                return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)