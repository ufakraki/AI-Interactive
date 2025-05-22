# Flask API ile skor bilgisini kullanıcıya sunan endpoint
from flask import Flask, request, jsonify
from redis import Redis
import json

app = Flask(__name__)
r = Redis(host="redis", port=6379)

@app.route("/get_score", methods=["GET"])
def get_score():
    city = request.args.get("city")
    raw = r.get(f"data_{city}")
    if not raw:
        return jsonify({"error": "Veri bulunamadı"}), 404

    data = json.loads(raw)
    return jsonify({
        "score": data["score"],
        "status": "Verimli" if data["score"] >= 75 else "Orta" if data["score"] >= 50 else "Zayıf",
        "details": data["details"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
