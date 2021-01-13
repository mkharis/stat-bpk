import mysql.connector
from credential import *

db = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

cursor = db.cursor()

def get_lk():
    cursor.execute('SELECT * FROM lk')
    result = cursor.fetchall()
    return result

def get_masalah():
    cursor.execute('SELECT * FROM masalah')
    result = cursor.fetchall()
    return result

def get_masalah_dengan_nilai():
    cursor.execute('SELECT * FROM masalah_dengan_nilai')
    result = cursor.fetchall()
    return result

def get_temuan_by_lk_only(id_lk):
    cursor.execute('SELECT temuan.jumlah, temuan.tahun, temuan.semester, masalah.masalah, masalah.jenis FROM temuan INNER JOIN lk ON temuan.id_lk=lk.id INNER JOIN masalah ON temuan.id_masalah=masalah.id WHERE temuan.id_lk=%s', (id_lk,))
    result = cursor.fetchall()
    return result

def get_temuan(id_lk, id_masalah):
    cursor.execute('SELECT temuan.jumlah, temuan.tahun, temuan.semester FROM temuan INNER JOIN lk ON temuan.id_lk=lk.id INNER JOIN masalah ON temuan.id_masalah=masalah.id WHERE temuan.id_lk=%s AND temuan.id_masalah=%s', (id_lk, id_masalah))
    result = cursor.fetchall()
    return result

def get_temuan_dengan_nilai_by_lk_only(id_lk):
    cursor.execute('SELECT temuan_dengan_nilai.jumlah, temuan_dengan_nilai.nilai, temuan_dengan_nilai.tahun, temuan_dengan_nilai.semester, masalah_dengan_nilai.masalah, masalah_dengan_nilai.jenis FROM temuan_dengan_nilai INNER JOIN lk ON temuan_dengan_nilai.id_lk=lk.id INNER JOIN masalah_dengan_nilai ON temuan_dengan_nilai.id_masalah=masalah_dengan_nilai.id WHERE temuan_dengan_nilai.id_lk=%s', (id_lk,))
    result = cursor.fetchall()
    return result

def get_temuan_dengan_nilai(id_lk, id_masalah):
    cursor.execute('SELECT temuan_dengan_nilai.jumlah, temuan_dengan_nilai.nilai, temuan_dengan_nilai.tahun, temuan_dengan_nilai.semester FROM temuan_dengan_nilai INNER JOIN lk ON temuan_dengan_nilai.id_lk=lk.id INNER JOIN masalah_dengan_nilai ON temuan_dengan_nilai.id_masalah=masalah_dengan_nilai.id WHERE temuan_dengan_nilai.id_lk=%s AND temuan_dengan_nilai.id_masalah=%s', (id_lk, id_masalah))
    result = cursor.fetchall()
    return result

def get_twitter(id_lk):
    cursor.execute('SELECT id, time, description, source, target, tweets, usertweets, hashtags, location, retweets, likes, verified, following, followers, url FROM twitter WHERE id_lk=%s', (id_lk,))
    result = cursor.fetchall()
    return result
