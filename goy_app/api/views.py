from django.db.models import query
from django.http import request
from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from core.models import *
import hashlib
import json
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model
import urllib.parse
import json


def parse_auth_header(input_string):
    parsed_url = urllib.parse.urlparse(f"?{input_string}")
    query_params = urllib.parse.parse_qs(parsed_url.query)

    user_json = query_params.get('user', [])[0]
    user_data = json.loads(urllib.parse.unquote(user_json))

    result = {
        'query_id': query_params.get('query_id', [])[0],
        'tg_user_id': user_data.get('id'),
        'first_name': user_data.get('first_name', ''),
        'last_name': user_data.get('last_name', ''),
        'username': user_data.get('username', ''),
        'language_code': user_data.get('language_code', ''),
        'is_premium': user_data.get('is_premium', False),
        'allows_write_to_pm': user_data.get('allows_write_to_pm', False),
        'auth_date': query_params.get('auth_date', [])[0],
        'hash': query_params.get('hash', [])[0]
    }

    return result


def is_authorised(request):
    init_data = request.headers.get('telegram-init-data')
    if not init_data:
        return JsonResponse({'error': 'Missing telegram-init-data header'}, status=400)

    parsed_data = parse_auth_header(init_data)
    
    user, created = User.objects.get_or_create(
        tg_user_id=parsed_data['tg_user_id'],
        defaults={
            'first_name': parsed_data['first_name'],
            'last_name': parsed_data['last_name'],
            'username': parsed_data['username'],
            'language_code': parsed_data['language_code'],
            'is_premium': parsed_data['is_premium'],
            'allows_write_to_pm': parsed_data['allows_write_to_pm'],
            'auth_hash': parsed_data['hash']
        }
    )

    is_authorised = False
    if not created:
        if user.auth_hash == parsed_data['hash'] and user.tg_user_id == parsed_data['tg_user_id']:
            is_authorised = True

    if created or is_authorised:
        return True, user
    else:
        return False, None
            

class CreateUserView(views.APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
            
        is_auth, user = is_authorised(request)

        if is_auth:

            if 'who_invited' in request.data:
                try:
                    ref_user = User.objects.get(tg_user_id=request.data['who_invited'])
                    user.who_invited = ref_user
                    user.save()

                except User.DoesNotExist:
                    pass

            return JsonResponse({'status': 'authorised', 
                                 'username': user.username, 
                                    'first_name': user.first_name,
                                    'last_name': user.last_name,
                                    'language_code': user.language_code,
                                    'ton_balance': user.ton_balance,
                                    'goy_balance': user.goy_balance,
                                    'has_paid': user.has_paid,
                                 }, status=200)
        else:
            return JsonResponse({'status': 'not authorised'}, status=400)