import os

import requests

# 1. Tentukan Endpoint (URL API)
endpoint = os.environ.get(
    "MUF_OID_API_ENDPOINT",
    "https://api-mass-pub-uat-b.muf.co.id/mass-api/oid-group-individu/getOidByNik",
)

# 2. Tentukan Parameter Body (Sesuaikan dengan kebutuhan API Anda)


def ambil_api (NIK):
    grand_total = 0
    body_param = {
        "nik_debitur": f"{NIK}"
    # tambahkan parameter lain di sini jika ada, contoh: "bulan": "juni"
    }
    try:
        # 3. Request ke API menggunakan metode POST dan parameter body (json)
        response = requests.post(endpoint, json=body_param, timeout=20)
        
        # 4. Pastikan response sukses (status code 200)
        response.raise_for_status()
        
        # 5. Ubah response menjadi dictionary Python
        hasil_json = response.json()
        
        # 6. Ambil nilai 'total_angsuran' dengan menembak Key-nya secara berjenjang
        # Struktur: hasil_json -> ['data'] -> ['total_angsuran']

        grand_total = 0
        if hasil_json.get("status") is True:
            list_data = hasil_json.get("data")
            # KONDISI 1: Jika data ternyata kosong / None
            if not list_data:
                grand_total = 0

            # KONDISI 2: Jika data berbentuk Dictionary Tunggal (Hanya 1 data angsuran)
            elif isinstance(list_data, dict):
                grand_total = int(list_data.get("total_angsuran", 0))

            # KONDISI 3: Jika data berbentuk List/Array (Lebih dari 1 data angsuran)
            elif isinstance(list_data, list):
                grand_total = 0
                for item in list_data:
                    # Jika item di dalam list adalah Dictionary/Objek (Sesuai ekspektasi awal)
                    if isinstance(item, dict):
                        grand_total += int(item.get("total_angsuran", 0))
                    
                    # Jika item di dalam list ternyata String Angka langsung (Contoh: ["9955000", "1500000"])
                    elif isinstance(item, (str, int)):
                        grand_total += int(item)
        else:
            grand_total = 0

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan koneksi API: {e}")
    except KeyError:
        print("Struktur JSON berubah, Key 'total_angsuran' tidak ditemukan.")

    return grand_total
