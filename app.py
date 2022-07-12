from flask import Flask, render_template, jsonify, request
app = Flask(__name__)


from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.a5dm1.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta


from datetime import datetime

## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index2.html')


@app.route('/register')
def regi():
    return render_template('index.html')


## API 역할을 하는 부분
@app.route('/memo', methods=['POST'])
def saving():

    desc_receive = request.form['desc_give']
    price_receive = request.form['price_give']

    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%H-%M-%S')

    imagename = f'file-{mytime}'


    save_to = f'static/{imagename}.{extension}'
    file.save(save_to)

    doc = {

        'desc':desc_receive,
        'price':price_receive,
        'file': f'{imagename}.{extension}'
    }

    db.cars.insert_one(doc)

    return jsonify({'msg':'등록이 완료되었습니다!'})


@app.route("/memo", methods=["GET"])
def web_mars_get():
    car_list = list(db.cars.find({}, {'_id': False}))
    return jsonify({'drcars':car_list})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)