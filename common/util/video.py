import socket
import requests


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# for get real ip address from arvan cloud service
# https://help.arvancloud.com/hc/fa/articles/360034320513?source=search
def get_real_ip_addr(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    remote_addr = request.META.get('REMOTE_ADDR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    elif remote_addr:
        ip = remote_addr
    else:
        ip = request.META.get('AR_REAL_IP')

    return ip


def get_secure_video_link(request, video_id):
    request_id = get_client_ip(request)
    request_url = "https://napi.arvancloud.com/vod/2.0/videos/" + str(video_id)

    params = {'secure_ip': request_id, }
    headers = {
        'Authorization': 'Apikey 5bd1c41d-c756-4cdd-b20f-78359663792d'
    }

    response = requests.request(
        "GET", request_url, headers=headers, params=params)

    return response.json()["data"]["player_url"]
