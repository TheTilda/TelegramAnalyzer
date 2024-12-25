from fastapi import FastAPI
import requests


app = FastAPI()

access_token_token_vk = ""

token_telegram_bot = ""

@app.get("/checkInfoVk")
def check_info_vk(group_id: str):
    url = f"https://api.vk.com/method/groups.getById?access_token={access_token_token_vk}&v=5.199&group_id={group_id}&fields=members_count,description"

    req = (requests.get(url)).json()['response']['groups'][0]
    result = {
        'name' : req['name'],
        'description' : req['description'],
        'members_count' : req['members_count'],
        'photo': req['photo_200']
    } 

    return result

@app.get("/checkInfoTelegram")
def check_info_tg(group_id: str):
    url = f"https://api.telegram.org/bot{token_telegram_bot}/getChat?chat_id={group_id}"

    req = requests.get(url).json()
    print(req)

    return req