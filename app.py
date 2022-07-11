from flask import Flask, render_template, jsonify

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta123@cluster0.g2dpd.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/login')
def log():
    return render_template('login.html')

@app.route('/member')
def member():
    return render_template('member.html')

# @app.route("/login")
# def comment_page():
#     return render_template("comment.html")


@app.route("/homework", methods=["POST"])
# def homework_post():
#     nickname_receive = request.form['nickname_give']
#     comment_receive = request.form['comment_give']
#     comment_list = list(db.homework.find({}, {'_id': False}))
#     count = len(comment_list) + 1
#
#     if(nickname_receive == ""):
#         return jsonify({'msg': '닉네임을 입력하시오'})
#     elif(comment_receive==""):
#         return jsonify({'msg': '댓글을 입력하시오'})
#     else:
#         doc = {
#             'num': count,
#             'nickname' : nickname_receive,
#             'comment': comment_receive
#         }
#         db.homework.insert_one(doc)
#
#     return jsonify({'msg': '댓글 작성 완료!'})

@app.route("/homework", methods=["GET"])
def homework_get():
    users = list(db.homework.find({}, {'_id': False}))


    return jsonify({'users': users})\


@app.route("/comment")
def comment():
    return  "comment page"



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
