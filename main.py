import auth_token
import json
import requests
from datetime import datetime
from tqdm import tqdm


class VkDownloader:

    def __init__(self, access_token, user_id, album_id='profile', version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.album_id = album_id

    def get_profile_photos(self):
        url = f"https://api.vk.com/method/photos.get?owner_id={self.id}&access_token={self.token}" \
              f"&album_id={self.album_id}&extended=1?photo_sizes=1&v={self.version} HTTP/1.1"
        req = requests.get(url)
        src = req.json()
        photos = src["response"]["items"]
        data = []
        for photo in tqdm(photos, desc='Get links from VK'):
            photos_likes = photo["likes"]["count"]
            photos_date = photo["date"]
            sizes = photo["sizes"]
            ts = int(photos_date)
            photos_date = datetime.utcfromtimestamp(ts).strftime('%d-%m-%Y')
            max_width = 0
            max_height = 0
            for size in sizes:
                if size['width'] > max_width and size['height'] > max_height:
                    max_width = size['width']
                    max_height = size['height']
                    link = size['url']
                    type = size['type']
            photos_info = {
                'link': link,
                'name': f'{photos_likes}.jpg',
                'photos_date': photos_date,
                'type': type
                }
            for el in data:
                if photos_info['name'] == el['name']:
                    photos_info = {
                        'link': link,
                        'name': f'{photos_likes}_date_{photos_date}.jpg',
                        'photos_date': photos_date,
                        'type': type
                    }
            data.append(photos_info)
        return data

    def data_to_json(self, data):
        json_object = json.dumps(data, indent=4)
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)
        return f'Success! JSON created.'


class Yandex:

    def __init__(self, token):
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.token = token
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'OAuth {self.token}'}

    def create_folder(self, path):
        response = requests.put(f'{self.url}?path={path}', headers=self.headers)
        return response.json()['message']

    def load_photos(self):
        for el in tqdm(data, desc='Load to YandexDisk'):
            params = {'url': el['link'], 'path': f'{folder}/{el["name"]}'}
            response = requests.post(f'{self.url}/upload', headers=self.headers, params=params)


users_id = int(input('Введите ID профиля '))
name = 'davl'
album_id = 'profile'
vk_data = VkDownloader(auth_token.token_vk, users_id, album_id)
data = vk_data.get_profile_photos()
print(vk_data.data_to_json(data))

# TOKEN = auth_token.token_y
TOKEN = input('Введите токен Яндекс Диска')
folder = 'vk_photos'
yandex_loader = Yandex(TOKEN)
yandex_loader.create_folder(folder)
yandex_loader.load_photos()
