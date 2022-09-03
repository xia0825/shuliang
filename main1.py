import random
from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os
from lxml import etree
import random
import jsonpath


def get_color():
    # 获取随机颜色
    color='#'
    list1 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A','B','C','D','E','F']
    for i in range(6):
        color_str=random.choice(list1)
        color+=color_str
    return color


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token


def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    life_suggestion_url = 'https://devapi.qweather.com/v7/indices/1d?type=3,5,9,13,16&location={}&key={}'.format(
        location_id, key)
    response = get(weather_url, headers=headers).json()
    response1 = get(life_suggestion_url, headers=headers).json()
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]

    type_names = jsonpath.jsonpath(response1, '$..name')
    indexs = jsonpath.jsonpath(response1, '$..category')
    texts = jsonpath.jsonpath(response1, '$..text')

    dressing_index = type_names[0]  # 穿衣指数
    UV_index = type_names[1]  # 紫外线指数
    cold_index = type_names[2]  # 感冒指数
    makeup_index = type_names[3]  # 化妆指数
    SPF_index = type_names[4]  # 防晒指数

    cy_grade = indexs[0]
    zwx_grade = indexs[1]
    gm_grade = indexs[2]
    hz_grade = indexs[3]
    fs_grade = indexs[4]

    cy_suggestion = texts[0]
    zwx_suggestion = texts[1]
    gm_suggestion = texts[2]
    hz_suggestion = texts[3]
    fs_suggestion = texts[4]

    return weather, temp, wind_dir, dressing_index, UV_index, cold_index, makeup_index, SPF_index, cy_grade, zwx_grade \
        , gm_grade, hz_grade, fs_grade, cy_suggestion, zwx_suggestion, gm_suggestion, hz_suggestion, fs_suggestion


def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)

    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day


def get_ciba():
    """美句函数"""
    url = "http://open.iciba.com/dsapi/"
    # url = "https://www.wenanwang.com/qg/1704.html"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    # r = get(url, headers=headers).content.decode('utf-8')
    # xpath_html = etree.HTML(r)
    # sentent_list = xpath_html.xpath('//*[@id="ML"]/div[1]/div[2]/p/text()')
    # sentent = random.choice(sentent_list)
    # print(sentent)

    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    print(note_en)
    print(note_ch)
    return note_ch, note_en


def send_message(to_user, access_token, region_name, weather, temp, wind_dir, dressing_index, UV_index, cold_index
                 , makeup_index, SPF_index, cy_grade, zwx_grade, gm_grade, hz_grade, fs_grade, cy_suggestion,
                 zwx_suggestion
                 , gm_suggestion, hz_suggestion, fs_suggestion, note_ch, note_en):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取所有生日数据
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "https://user.qzone.qq.com/1249206729/infocenter",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": "#8B0000"
            },
            "region": {
                "value": region_name,
                "color": "#FF8C00"
            },
            "weather": {
                "value": weather,
                "color": "#00FF00"
            },
            "temp": {
                "value": temp,
                "color": "#00FF00"
            },
            "wind_dir": {
                "value": wind_dir,
                "color": "#8B0000"
            },
            "love_day": {
                "value": love_days,
                "color": "#D2691E"
            },
            "note_en": {
                "value": note_en,
                "color": "#FF8C00"
            },
            "note_ch": {
                "value": note_ch,
                "color": "#FF8C00"
            },
            "cy_grade": {
                "value": cy_grade,
                "color": "#1E90FF"
            },
            "zwx_grade": {
                "value": zwx_grade,
                "color": "#1E90FF"
            },
            "gm_grade": {
                "value": gm_grade,
                "color": "#1E90FF"
            },
            "hz_grade": {
                "value": hz_grade,
                "color": "#1E90FF"
            },
            "fs_grade": {
                "value": fs_grade,
                "color": "#1E90FF"
            },
            "cy_suggestion": {
                "value": cy_suggestion,
                "color": "#800080"
            },
            "zwx_suggestion": {
                "value": zwx_suggestion,
                "color": "#800080"
            },
            "gm_suggestion": {
                "value": gm_suggestion,
                "color": "#800080"
            },
            "hz_suggestion": {
                "value": hz_suggestion,
                "color": "#800080"
            },
            "fs_suggestion": {
                "value": fs_suggestion,
                "color": "#800080"
            }
        }
    }
    for key, value in birthdays.items():
        # 获取距离下次生日的时间
        birth_day = get_birthday(value["birthday"], year, today)
        if birth_day == 0:
            birthday_data = "今天{}生日哦，祝{}生日快乐！".format(value["name"], value["name"])
        else:
            birthday_data = "距离{}的生日还有{}天".format(value["name"], birth_day)
        # 将生日数据插入data
        data["data"][key] = {"value": birthday_data, "color": "#DC143C"}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


if __name__ == "__main__":
    get_ciba()
    # try:
    #     with open("config.txt", encoding="utf-8") as f:
    #         config = eval(f.read())
    # except FileNotFoundError:
    #     print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
    #     os.system("pause")
    #     sys.exit(1)
    # except SyntaxError:
    #     print("推送消息失败，请检查配置文件格式是否正确")
    #     os.system("pause")
    #     sys.exit(1)
    #
    # # 获取accessToken
    # accessToken = get_access_token()
    # # 接收的用户
    # users = config["user"]
    # # 传入地区获取天气信息
    # region = config["region"]
    # weather, temp, wind_dir, dressing_index, UV_index, cold_index, makeup_index, SPF_index, cy_grade, zwx_grade, gm_grade \
    #     , hz_grade, fs_grade, cy_suggestion, zwx_suggestion, gm_suggestion, hz_suggestion, fs_suggestion = get_weather(
    #     region)
    # note_ch = config["note_ch"]
    # note_en = config["note_en"]
    # if note_ch == "" and note_en == "":
    #     # 获取词霸每日金句
    #     note_ch, note_en = get_ciba()
    # # 公众号推送消息
    # for user in users:
    #     send_message(user, accessToken, region, weather, temp, wind_dir, dressing_index, UV_index
    #                  , cold_index, makeup_index, SPF_index, cy_grade, zwx_grade, gm_grade, hz_grade, fs_grade,
    #                  cy_suggestion
    #                  , zwx_suggestion, gm_suggestion, hz_suggestion, fs_suggestion, note_ch, note_en)
    # os.system("pause")