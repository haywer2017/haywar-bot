# Haywar Marketing WhatsApp Bot
import os, json, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "haywar123")
CUSTOMER_SERVICE_NUMBER = os.environ.get("CUSTOMER_SERVICE_NUMBER", "967777000000")

GRAPH_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"

SERVICES = """اهلا بك في شركة هايوار للتسويق والاعلان

اختر الخدمة:
1 - ادارة حسابات التواصل الاجتماعي
2 - تصميم شعارات وهوية بصرية
3 - حملات اعلانية ممولة
4 - تصميم فيديو / موشن جرافيك
5 - التحدث مع خدمة العملاء

اكتب رقم الخدمة (1-5)"""

PRICES = {
    "1": "ادارة حسابات التواصل:\n- باقة شهرية: 150$ / شهر\n- تشمل 12 تصميم + ادارة كاملة\nاكتب 0 للرجوع للقائمة",
    "2": "تصميم شعار وهوية بصرية:\n- شعار احترافي: 80$\n- هوية كاملة: 200$\nاكتب 0 للرجوع للقائمة",
    "3": "حملات اعلانية ممولة:\n- تبدا من 100$ + ميزانية الاعلان\nاكتب 0 للرجوع للقائمة",
    "4": "فيديو / موشن جرافيك:\n- فيديو 30 ثانية: 70$\n- فيديو 60 ثانية: 120$\nاكتب 0 للرجوع للقائمة",
    "5": f"خدمة العملاء:\nتواصل معنا واتساب مباشرة:\nhttps://wa.me/{CUSTOMER_SERVICE_NUMBER}\nاكتب 0 للرجوع للقائمة",
}

def send_message(to, text):
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        return
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    try:
        requests.post(GRAPH_URL, headers=headers, json=payload, timeout=20)
    except Exception as e:
        print("send error", e)

@app.route("/", methods=["GET"])
def home():
    return "Haywar Bot is Running", 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    try:
        entry = data["entry"][0]
        change = entry["changes"][0]
        value = change.get("value", {})
        messages = value.get("messages", [])
        if messages:
            msg = messages[0]
            from_number = msg.get("from")
            text = msg.get("text", {}).get("body", "").strip()
            if text == "0":
                send_message(from_number, SERVICES)
            elif text in PRICES:
                send_message(from_number, PRICES[text])
            else:
                send_message(from_number, SERVICES)
    except Exception as e:
        print("webhook error", e)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
