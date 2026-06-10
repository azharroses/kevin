import psycopg2
import psycopg2.extras
import oracledb
import os
import sys
from contextlib import contextmanager
from typing import List, Dict, Any

# DB_CONFIG_1 = {
#     "host"    : "10.22.11.99",a
#     "port"    : 5432,
#     "dbname"  : "cbasdigital",
#     "user"    : "cbasteko",
#     "password": "cb@suat",
#     "connect_timeout": 10,
# }


def GetEnviCbas ():
    conn = psycopg2.connect(
        host    = "10.22.11.99",
        port    = '5432',
        dbname  = "cbasdigital",
        user    = "cbasteko",
        password= "cb@suat"
    )

    return conn

def GetEnviB ():
    conn = psycopg2.connect(
        host    = "10.22.15.141",
        port    = '5432',
        dbname  = "mufacq_prm",
        user    = "uatuser",
        password= "uatuser"
    )
    return conn

# ==============================================================================
# CONTEXT MANAGER — PostgreSQL
# ==============================================================================

@contextmanager
def koneksi_db_EnviB():
    conn2 = None
    try:
        conn2 = GetEnviB()
        yield conn2
        conn2.commit()
    except Exception as e:
        if conn2 and not conn2.closed:  # ✅ Fix yang sama
            try:
                conn2.rollback()
            except Exception as rb_err:
                print(f"⚠️ Rollback gagal: {rb_err}")
        print(f"❌ Error transaksi PostgreSQL: {e}")
        raise  # ✅ Tambahkan raise agar error tidak tertelan
    finally:
        if conn2 and not conn2.closed:
            conn2.close()

@contextmanager
def koneksi_db():

    conn = None
    try:
        conn = GetEnviCbas()
        yield conn
        conn.commit()
    except Exception as e:
        if conn and not conn.closed:  # ✅ Fix yang sama
            try:
                conn.rollback()
            except Exception as rb_err:
                print(f"⚠️ Rollback gagal: {rb_err}")
        print(f"❌ Error transaksi PostgreSQL: {e}")
        raise  # ✅ Tambahkan raise agar error tidak tertelan
    finally:
        if conn and not conn.closed:
            conn.close()


# ==============================================================================
# CONTEXT MANAGER — Oracle (Thick Mode, DSN langsung tanpa tnsnames.ora)
# ==============================================================================
# @contextmanager
# def koneksi_oracle_db():
#     """
#     Context manager koneksi Oracle dengan Thick Mode.
#     DSN format host:port/service_name → tidak butuh tnsnames.ora.
#     """

#     conn = None
#     try:
#         conn = oracledb.connect(
#             user        = "bpialoy",
#             password    = "april2021",
#             host        = "10.22.15.25",
#             port        = "1521",
#             service_name = "mufuat10"
#         )
#         print("[Oracle] ✅ Koneksi berhasil.")
#         yield conn
#         conn.commit()
#     except Exception as e:
#         if conn:
#             conn.rollback()
#         print(f"❌ Error transaksi Oracle: {e}")
#         raise
#     finally:
#         if conn:
#             conn.close()
#             print("[Oracle] 🔒 Koneksi ditutup.")


# ==============================================================================
# FUNGSI QUERY
# ==============================================================================
def ambilData(query: str) -> List[Dict[str, Any]]:
    """Eksekusi SELECT pada PostgreSQL, kembalikan list of dict."""
    with koneksi_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
def ambilCabang (query:str)-> List[Dict[str, Any]]:
    with koneksi_db_EnviB() as conn:   # ✅ Koneksi ke DB yang benar
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [dict(row) for row in rows]


def queryGetData(nama_select: str, nama_table: str, nama_where: str) -> str:
    """Builder query SELECT sederhana."""

    if nama_where == '' or nama_where == None :
        return f"""
            SELECT {nama_select}
            FROM   {nama_table}
        """
    else :

        return f"""
            SELECT {nama_select}
            FROM   {nama_table}
            WHERE  {nama_where}
        """