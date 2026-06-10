import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from API import ambil_api
from Perhitungan_DBR import mengambilDataAngsuran


app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.errorhandler(Exception)
def handle_error(exc):
    app.logger.exception("Unhandled server error")
    return jsonify({
        "error": "Gagal memproses request di server.",
        "detail": str(exc),
    }), 500


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.post("/api/cek-angsuran")
def cek_angsuran():
    payload = request.get_json(silent=True) or {}
    ktp_debitur = str(payload.get("ktp_debitur", "")).strip()
    ktp_pasangan = str(payload.get("ktp_pasangan", "")).strip()
    no_order = str(payload.get("no_order", "")).strip()

    if ktp_debitur and (not ktp_debitur.isdigit() or len(ktp_debitur) != 16):
        return jsonify({"error": "NIK KTP Debitur harus 16 digit angka."}), 400

    if ktp_pasangan and (not ktp_pasangan.isdigit() or len(ktp_pasangan) != 16):
        return jsonify({"error": "NIK KTP Pasangan harus 16 digit angka."}), 400

    if not ktp_debitur and not ktp_pasangan:
        return jsonify({"error": "Masukkan minimal satu NIK KTP."}), 400

    try:
        angsuran_debitur, angsuran_pasangan = mengambilDataAngsuran(
            ktp_debitur,
            ktp_pasangan,
            no_order,
        )
        angsuran_muf = ambil_api(ktp_debitur) if ktp_debitur else 0
    except Exception as exc:
        app.logger.exception("Gagal cek angsuran")
        return jsonify({
            "error": "Gagal mengambil data angsuran.",
            "detail": str(exc),
        }), 500

    return jsonify({
        "angsuran_debitur": int(angsuran_debitur or 0),
        "angsuran_pasangan": int(angsuran_pasangan or 0),
        "angsuran_muf": int(angsuran_muf or 0),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
