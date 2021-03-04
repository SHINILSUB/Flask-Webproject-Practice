from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = "SPARTA"

client = MongoClient("localhost", 27017)
db = client.dbsparta_plus_week4


@app.route("/")
def home():
    return render_template("01_main.html")


def login_decorator(func):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"id": payload["id"]})
        return render_template("index.html", nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("02_login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("02_login", msg="로그인 정보가 존재하지 않습니다."))


@app.route("/login")
def login():
    msg = request.args.get("msg")
    return render_template("02_login.html", msg=msg)


@app.route("/sign_in", methods=["POST"])
def sign_in():
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]

    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one({"username": username_receive, "password": pw_hash})

    if result is not None:
        # payload란 토큰을 디코딩하면 나오게 될 사용자에 대한 정보이다.
        payload = {
            "id": username_receive,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 3),  # 로그인 3시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"result": "success", "token": token})
    else:
        return jsonify({"result": "fail", "msg": "아이디/비밀번호가 일치하지 않습니다."})


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    nickname_receive = request.form["nickname_give"]
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    # DB에 username, nickname, 암호화한 password 저장
    doc = {
        "username": username_receive,
        "password": password_hash,
        "nickname": nickname_receive,  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({"result": "success"})


@app.route("/sign_up/check_dup", methods=["POST"])
def check_dup():
    username_receive = request.form["username_give"]
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({"result": "success", "exists": exists})


@app.route("/map")
def test_map():
    return render_template("03_map.html")


## HTML을 주는 부분
@app.route("/memo", methods=["GET"])
def listing():
    articles = list(db.articles.find({}, {"_id": False}))
    return jsonify({"all_articles": articles})


## API 역할을 하는 부분
@app.route("/memo", methods=["POST"])
def saving():
    usertitle_receive = request.form["usertitle_give"]
    user_receive = request.form["user_give"]
    url_receive = request.form["url_give"]
    comment_receive = request.form["comment_give"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
    }
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, "html.parser")

    image = soup.select_one('meta[property="og:image"]')["content"]
    title = soup.select_one('meta[property="og:title"]')["content"]
    desc = soup.select_one('meta[property="og:description"]')["content"]

    doc = {
        "usertitle": usertitle_receive,
        "user": user_receive,
        "image": image,
        "title": title,
        "url": url_receive,
        "desc": desc,
        "comment": comment_receive,
    }
    db.articles.insert_one(doc)

    return jsonify({"msg": "저장이 완료되었습니다."})


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)

