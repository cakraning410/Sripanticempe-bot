import os
import tempfile
import telebot
import requests
import firebase_admin
from firebase_admin import credentials, storage, db
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton
import datetime
import random 
from flask import Flask, request

cred = credentials.Certificate(
    "sripanticempe-firebase-adminsdk-afhs4-e59637c7ba.json"
)
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://sripanticempe-default-rtdb.asia-southeast1.firebasedatabase.app',
    'storageBucket': "sripanticempe.appspot.com"
})

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(
        request.stream.read().decode('utf-8')
    )
    bot.process_new_updates([update])
    return 'OK', 200

def markup_warta():
    markup = InlineKeyboardMarkup(
        row_width=2
    )
    btn_warta = InlineKeyboardButton(text="Kirimkan Saya Warta Gereja 📄", callback_data='send_warta')
    btn_ulasan = InlineKeyboardButton(text="Memberi Ulasan 📝", callback_data='feedback')
    btn_lokasi = InlineKeyboardButton(text="Lokasi Gereja 📍", callback_data='lokasi')
    markup.add(
        btn_warta,
        btn_ulasan,
        btn_lokasi
    )
    return markup

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, f"Hi, {msg.chat.first_name} 👋\nSaya Bot Sripanticempe dibuat untuk membantu jemaat GKJ Cakraningratan.\nSaat ini saya hanya dapat diperintah untuk mengirimkan Warta Gereja terbaru ya!")
    bot.send_message(msg.chat.id, "Klik tombol dibawah untuk mendapatkan Warta Gereja!", reply_markup=markup_warta())
     
def get_warta():
    db_ref = db.reference('/Warta')
    data = db_ref.get()
    return list(data.values())[-1]['url'] if data != '' else ''
    


@bot.callback_query_handler(func=lambda msg: msg.data == "send_warta")
def send_warta(msg):
        bot.send_message(msg.message.chat.id, "Baik, mohon ditunggu data sedang dimuat ya😄")
        if get_warta() != '':
                bot.send_document(msg.message.chat.id, get_warta())
        else:
                bot.send_message(msg.message.chat.id, "Sayang sekali, saat ini tidak ada data apapun di database saya")
                
user_status = {}

@bot.callback_query_handler(func= lambda msg: msg.data == "feedback")
def send_ulasan(msg):
    user_id = msg.message.chat.id
    user_status[user_id] = "waiting"
    bot.send_message(msg.message.chat.id, "Silahkan kirimkan ulasan Anda, saya bersedia menerima masukan apapun 😁")
    
@bot.message_handler(commands=["post"])
def post_warta(msg):
        bot.reply_to(msg, "Silahkan menambahkan file melalui dahshboard Firebase")
        db_ref = db.reference('/Warta')
        db_ref.push({
                    'name': '{}pdf'.format(datetime.datetime.now()),
                    'url':''
                })        
        
@bot.callback_query_handler(func=lambda msg: msg.data == "lokasi")
def send_location(msg):
    bot.send_message(msg.message.chat.id, "Berikut lokasi GKJ CAKRANINGRATAN")
    rec_lokasi = db.reference("/Location").get()
    latitude = list(rec_lokasi.values())[0]["latitude"]
    longitude = list(rec_lokasi.values())[0]["longitude"]
    bot.send_location(msg.message.chat.id, latitude=latitude, longitude=longitude)    
    

@bot.message_handler(func=lambda msg:  True)
def greet_handler(msg):
    user_id = msg.chat.id
    respon = [
    "Maaf saya tidak dapat mengerti maksud Anda, jika ada pertanyaan silahkan hubungi pemogram saya di @NeoYuli",
    "Waduh😥, bot tidak memahami maksud Anda, jika ada kendala hubungi pemogram saya di @NeoYuli",
    "Currently, I'm not able to understand what you're ordering, please contact my creator : @NeoYuli ",
    "Nu, ik niet begrijpen wat je praten, contact mijn creator alstublief : @NeoYuli"
    ]

    if str(msg.text).lower() in ["terima kasih","sap", "mantap" , "nuwun", "thanks", "thank you", "maturnuwun"]:
        bot.send_message(msg.chat.id, "Saya senang mendengarnya 😃, senang telah membantu Anda! GBU❤️")
    elif user_id in user_status and user_status[user_id] == "waiting":
        db_ref = db.reference("/Feedback")
        db_ref.push({
            "user": msg.chat.first_name,
            "ulasan" : msg.text
        })
        user_status[user_id] = "done"
        bot.reply_to(msg,"Terima kasih atas ulasan-nya, ulasan Anda membantu pengembang untuk meningkatkan kualitas pelayanan bot ini 🙏")
    else:
        bot.send_message(msg.chat.id, respon[random.randint(0,3)])        
    

if __name__ == "__main__":
    
    bot.remove_webhook()
    bot.set_webhook(url=f'https://sripanticempe-bot.osc-fr1.scalingo.io/webhook')
    
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get('PORT', 5000))
    )
       





                             
