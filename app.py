from bson import ObjectId
from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)
import jwt
import datetime
import hashlib
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import certifi
from datetime import datetime

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.a5dm1.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

from datetime import datetime




## HTML을 주는 부분
@app.route('/')
def home():
    # 로그인이 안됐을때 홈으로
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



############# 게시물 업로드 #############

## 게시물업로드 페이지 경로
@app.route('/register')
def regi():
    return render_template('upload.html')


## upload.html 에서 DB 로 올리기
@app.route('/memo', methods=['POST'])
def saving():
    # 로그인 해야 들어올수있도록 추가
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        name_receive = request.form['name_give']
        desc_receive = request.form['desc_give']
        price_receive = request.form['price_give']
        star_receive = request.form['star_give']
        file = request.files["file_give"]
        count_list =  list(db.cars.find({}, {'_id': False}))
        count = len(count_list) + 1
        # 유저네임도 함께  저쟝
        username = user_info['username']

        extension = file.filename.split('.')[-1]

        today = datetime.now()
        mytime = today.strftime('%Y-%m-%H-%M-%S')

        imagename = f'file-{mytime}'

        save_to = f'static/{imagename}.{extension}'
        file.save(save_to)

        doc = {
            'username': username,
            'name': name_receive,
            'desc': desc_receive,
            'price': price_receive,
            'file': f'{imagename}.{extension}',
            'count':count,
            'star': star_receive
        }

        db.cars.insert_one(doc)

        return jsonify({'msg': '등록이 완료되었습니다!'})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


## DB 에서 게시물 전체 index.html 로 내리기
@app.route("/memo", methods=["GET"])
def uploaded():
    car_list = list(db.cars.find({}, {'_id': False}))
    return jsonify({'drcars': car_list})



########### 로그인,회원가입 #############

# 로그인 구현
# 로그인 url 부여
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


# 로그인 아이디 패스워드부여
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60)  # 로그인 1시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 로그인 아이디중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 서버에 회원가입 입력내용
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "file": "",  # 사진 파일 이름
        "price": "",  # 가격
        "desc": ""  # 자랑
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


########## 상세 페이지 #############

# 상세페이지구현
@app.route('/<username>')
def detail(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('detail.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



# 상세페이지 수정
@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        price_receive = request.form["price_give"]
        count_receive = request.form["count_give"]

        star_receive = request.form["star_give"]

        if(name_receive == None):
            return jsonify({'result':"fail", 'msg':'name을 입력하세요'})


        new_doc = {
            "name": name_receive,
            "desc": about_receive,
            "price": price_receive,
            "star": star_receive,
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path

        db.cars.update_one({'username': payload['id']}, {'$set': new_doc})
        db.cars.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '정보를 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 상세페이지 삭제
@app.route('/delete_article', methods=['POST'])
def delete_review():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        review_id = ObjectId(request.form["delete_id"])
        review = db.cars.find_one({'_id': review_id})
        access_info = db.cars.find_one({'user_id': payload['id']})
        if str(access_info['_id']) == str(review['member_id']):
            db.reviews.delete_one({'_id': review_id})
            return jsonify({'result': True, 'msg': '리뷰가 삭제되었습니다.'})
        else:
            return jsonify({'result': False, 'msg': '본인의 리뷰만 삭제할 수 있습니다.'})
    except:
        return jsonify({'result': False,'msg': '로그인 한뒤에 이용해주세요.'})


######### 댓글 기능 구현 ##########
    ## 댓글 DB 로 올리기
@app.route('/cmt', methods=['post'])
def comment():

    comment_receive = request.form['comment_give']

    doc = {'comment': comment_receive}
    db.comments.insert_one(doc)

    return jsonify({'msg': '댓글 감사합니다!'})

## 댓글 DB 에서 내리기
@app.route("/cmt", methods=["GET"])
def cmt():
    comment_list = list(db.comments.find({}, {'_id': False}))
    return jsonify({'comment': comment_list})





if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)
