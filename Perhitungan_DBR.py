import re
import Database 

def hitung_rac_dbr(
    kategori: str,
    platform : str,
    onPasangan : str,
    pendapatan_debitur: int,
    pendapatan_pasangan: int,
    pendapatanDebiturRange : str,
    angsuran_lain_debitur: int,
    angsuran_lain_pasangan: int,
    angsuran_diajukan: int,
    angsuran_muf: int,
) -> dict:

    
    result = rumus_RAC_DBR(
        platform,
        onPasangan,
        kategori,
        pendapatanDebiturRange,
        angsuran_diajukan,
        angsuran_muf,
        angsuran_lain_debitur,
        pendapatan_debitur,
        angsuran_lain_pasangan,
        pendapatan_pasangan
        )
    
    
    hasil_dbr = result["dbr_pct"]
    status_lulus = result["lulus"]

    #print(f"ini adalah hasul DBR Sebelum Di kali 100% : {hasil_dbr}")

    hasil_dbr = hasil_dbr *100

    #print(f"ini adalah hasul DBR setelah Di kali 100% : {hasil_dbr}")


    return {
        #"total_pendapatan": total_pendapatan,
        #"total_angsuran": total_angsuran,
        "dbr_pct": hasil_dbr,
        #"batas_dbr": batas_dbr,
        "lulus": status_lulus,
    }

def rumus_RAC_DBR (platform:str, onPasangan:str, kategori:str,pendapatanDebiturRange:str, angsuran_diajukan:int,angsuran_muf:int, angsuran_lain_debitur:int, pendapatan_debitur:int, angsuran_lain_pasangan:int, pendapatan_pasangan:int ):
    firstRange = 0
    secondRange = 0
    dbr_pct = 0
    lulus = ""
    if platform == "LIVIN": 
        if (onPasangan == "TIDAK"):
            dbr_pct = (angsuran_diajukan + angsuran_muf + angsuran_lain_debitur)/pendapatan_debitur
        else :
            dbr_pct = (angsuran_diajukan + angsuran_muf + angsuran_lain_debitur + angsuran_lain_pasangan)/(pendapatan_debitur + pendapatan_pasangan)

            
        if  kategori == "LIVINREGPRIO" or kategori == "LIVINREGPRIVATE":
                lulus = "OKAY"
        if  kategori == "LIVINREGCORPORATE1" or kategori == "LIVINEKOSISTEMCORP2" or kategori == "LIVINEKOSISTEMCORP3" or kategori == "LIVINREGPEMANDIRIAN1" or kategori == "LIVINREGPEMANDIRIAN2" or kategori == "LIVINREGMANDIRIAN3" or kategori == "LAINNYA" :

            if (pendapatan_debitur <= 10000000 and (dbr_pct*100) < 40) or ((pendapatan_debitur >10000000 and pendapatan_debitur <20000000) and  ((dbr_pct*100) <= 50)) or (pendapatan_debitur >= 20000000 and  (dbr_pct*100) <= 60)  :
                lulus = "OKAY" 
            else :
                lulus = ""
    else :
        partPendapatanRange = pendapatanDebiturRange.split('-')
        firstRange = int(partPendapatanRange[0])
        secondRange = int(partPendapatanRange[1])
        hasilPerhitunganPendapatan = (((firstRange*1000000) + (secondRange*1000000))/2)
        if (onPasangan == "TIDAK"):
            dbr_pct = (angsuran_diajukan + angsuran_muf + angsuran_lain_debitur)/(hasilPerhitunganPendapatan ) 
        else :
            dbr_pct = (angsuran_diajukan + angsuran_muf + angsuran_lain_debitur)/(hasilPerhitunganPendapatan + pendapatan_pasangan) 
    
        if  (kategori == "NASABAH PRIORITAS" or kategori == "NASABAH PRIVATE" or kategori == "NASABAH PAYROLL BSI" or kategori == "LAINNYA") and ((hasilPerhitunganPendapatan <=10000000 and  dbr_pct *100 <= 40)) or ((hasilPerhitunganPendapatan >10000000 and  dbr_pct *100 <= 50)):
            lulus = "OKAY"
        else :
            lulus = ""

    #print (f"ini adalah DPRPCT di Fungsi {dbr_pct}")
    return {
        "dbr_pct": dbr_pct, 
        "lulus": lulus
    }



def mengambilDataAngsuran (ktp :str, ktpPasangan : str, noOrder : str) :
    queryGetCabang = Database.queryGetData(
        'poid_br_id as branch_code',
        'prm_master.mst_branch_outlet',
        ''
    )

    
    
    dataCabang = Database.ambilCabang(queryGetCabang)

    str_branch = ", ".join([f"'{b['branch_code']}'" for b in dataCabang])
    
    
    queryDebitur = Database.queryGetData(
        'SUM(afs.installment) AS total_installment_deb',
        'cbasdigital.cbas_data.applicant A '
        'inner join cbasdigital.cbas_data.appfacilityscore AFS on A.appid = AFS.appid '
        'inner join cbasdigital.cbas_data.requestdata rd on rd.reffnumber = A.reffnumber',
        f"""A.ktp in ('{ktp}')
        and AFS.kondisiket = 'Fasilitas Aktif'
        AND AFS.ljkket  <> 'PT Mandiri Utama Finance'
        AND NOT (
            LENGTH(AFS.noakadawal) = 12 
            AND SUBSTR(AFS.noakadawal, 1, 4) IN ({str_branch})
        )
        and rd.reffnumber = (
            select rda.reffnumber from cbasdigital.cbas_data.requestdata rda
            where rda.reqnonota = '{noOrder}'
            ORDER BY rd.reqdate desc limit 1
        )"""
    )

    queryDebiturDanPasangan = Database.queryGetData(
        f"""SUM(CASE WHEN A.ktp = '{ktp}' THEN afs.installment ELSE 0 END) AS total_installment_deb,
        SUM(CASE WHEN A.ktp = '{ktpPasangan}' THEN afs.installment ELSE 0 END) AS total_installment_pas""",
        'cbasdigital.cbas_data.applicant A '
        'inner join cbasdigital.cbas_data.appfacilityscore AFS on A.appid = AFS.appid '
        'inner join cbasdigital.cbas_data.requestdata rd on rd.reffnumber = A.reffnumber',
        f"""A.ktp in ('{ktp}', '{ktpPasangan}')
        and AFS.kondisiket = 'Fasilitas Aktif'
        AND AFS.ljkket  <> 'PT Mandiri Utama Finance'
        AND NOT (
            LENGTH(AFS.noakadawal) = 12 
            AND SUBSTR(AFS.noakadawal, 1, 4) IN ({str_branch})
        )
        and rd.reffnumber = (
            select rda.reffnumber from cbasdigital.cbas_data.requestdata rda
            where rda.reqnonota = '{noOrder}'
            ORDER BY rd.reqdate desc limit 1
        )"""
    )


    if ktpPasangan == "" or ktpPasangan is None:
        data = Database.ambilData(queryDebitur)
        hasilDataAngsuranPasangan = 0

        if data[0]['total_installment_deb'] == "" or data[0]['total_installment_deb'] is None :
            hasilDataAngsuranDebitur = 0
        else :
            hasilDataAngsuranDebitur = int (data[0]['total_installment_deb']) 

    else :
        data = Database.ambilData(queryDebiturDanPasangan)

        if ((data[0]['total_installment_deb'] == "" or data[0]['total_installment_deb'] is None) and (data[0]['total_installment_pas'] == "" or data[0]['total_installment_pas'] is None )):
            hasilDataAngsuranDebitur = 0
            hasilDataAngsuranPasangan = 0

        if data[0]['total_installment_deb'] == "" or data[0]['total_installment_deb'] is None :
            hasilDataAngsuranDebitur = 0
            hasilDataAngsuranPasangan = int (data[0]['total_installment_pas'])
        
        if data[0]['total_installment_pas'] == "" or data[0]['total_installment_pas'] is None :
            hasilDataAngsuranDebitur = int (data[0]['total_installment_deb']) 
            hasilDataAngsuranPasangan = 0
        else :
            hasilDataAngsuranDebitur = int (data[0]['total_installment_deb']) 
            hasilDataAngsuranPasangan = int (data[0]['total_installment_pas'])
        

       
        


    return (hasilDataAngsuranDebitur, hasilDataAngsuranPasangan)
