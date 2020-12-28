import requests, os

# Resize and save image to the disk
def save_picture(form_picture):
    url = 'https://api.imgbb.com/1/upload'
    files = {
        'image': form_picture
    }
    params = {
        'key': os.environ['IMBB_KEY']
    }
    res = requests.post(url, params=params, files=files)
    print(res.json())

    return res.json()['data']['url']