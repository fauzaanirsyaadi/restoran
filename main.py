from typing import Optional, Union

from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from typing import List

app = FastAPI()

class Kategori(BaseModel):
    nama_kategori: str
    class Config:
        orm_mode = True

class Bahan(BaseModel):
    nama_bahan: str

class Resep(BaseModel):
    nama_resep: str
    id_kategori: int

class ResepBahan(BaseModel):
    id_bahan: int

def create_conn():
    return psycopg2.connect(
        host="localhost",
        database="restaurant",
        user="postgres",
        password="admin",
        port="5432"
    )

def create_table(conn):
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS kategori (id_kategori SERIAL PRIMARY KEY, nama_kategori VARCHAR(255))")
    cur.execute("CREATE TABLE IF NOT EXISTS bahan (id_bahan SERIAL PRIMARY KEY, nama_bahan VARCHAR(255))")
    cur.execute("CREATE TABLE IF NOT EXISTS resep (id_resep SERIAL PRIMARY KEY, nama_resep VARCHAR(255), id_kategori INT REFERENCES kategori(id_kategori))")
    cur.execute("CREATE TABLE IF NOT EXISTS resep_bahan (id_resep INT REFERENCES resep(id_resep), id_bahan INT REFERENCES bahan(id_bahan))")
    conn.commit()
    cur.close()

# migrate database
conn = create_conn()
create_table(conn)


# dokumen swagger untuk API CRUD terletak di sini http://127.0.0.1:8000/docs

# 1. API CRUD untuk data kategori:
def insert_kategori(conn, kategori):
    cur = conn.cursor()
    cur.execute("INSERT INTO kategori (nama_kategori) VALUES (%s)", (kategori.nama_kategori,))
    conn.commit()
    cur.close()

@app.post("/kategori", response_model=Kategori)
def create_kategori(kategori: Kategori):
    conn = create_conn()
    insert_kategori(conn, kategori)
    conn.close()
    return kategori

# test dengan pytest
def test_create_kategori():
    conn = create_conn()
    kategori = Kategori(nama_kategori="Makanan")
    insert_kategori(conn, kategori)
    conn.close()

# call test
test_create_kategori()

# - Read/Index: GET /kategori untuk menampilkan seluruh kategori. 
def get_all_kategori(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM kategori")
    rows = cur.fetchall()
    cur.close()
    kategoris = []
    for row in rows:
        kategori = Kategori(id_kategori=row[0], nama_kategori=row[1])
        kategoris.append(kategori)
    return kategoris

@app.get("/kategori", response_model=List[Union[Kategori, None]])
def read_all_kategori():
    conn = create_conn()
    rows = get_all_kategori(conn)
    conn.close()
    return rows

# test dengan pytest
def test_read_all_kategori():
    conn = create_conn()
    kategoris = get_all_kategori(conn)
    conn.close()
    assert len(kategoris) > 0

# call test
test_read_all_kategori()

# GET /kategori/{id} untuk menampilkan kategori berdasarkan id_kategori.
def get_kategori_by_id(conn, id_kategori):
    cur = conn.cursor()
    cur.execute("SELECT * FROM kategori WHERE id_kategori=%s", (id_kategori,))
    row = cur.fetchone()
    cur.close()
    kategori = Kategori(id_kategori=row[0], nama_kategori=row[1])
    return kategori

@app.get("/kategori/{id}", response_model=Union[Kategori, None])
def read_kategori_by_id(id: int):
    conn = create_conn()
    row = get_kategori_by_id(conn, id)
    conn.close()
    return row

# test read_kategori_by_id
def test_read_kategori_by_id():
    conn = create_conn()
    # get last id_kategori
    cur = conn.cursor()
    cur.execute("SELECT * FROM kategori ORDER BY id_kategori DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    kategori = get_kategori_by_id(conn, row[0])
    conn.close()
    assert kategori.nama_kategori == "Makanan"

# call test
test_read_kategori_by_id()

# - Update: PUT /kategori/{id} dengan request body berisi nama_kategori yang baru.
def update_kategori(conn, id_kategori, kategori):
    cur = conn.cursor()
    cur.execute("UPDATE kategori SET nama_kategori=%s WHERE id_kategori=%s", (kategori.nama_kategori, id_kategori))
    conn.commit()
    cur.close()

@app.put("/kategori/{id}", response_model=Union[Kategori, None])
def update_kategori_by_id(id: int, kategori: Kategori):
    conn = create_conn()
    update_kategori(conn, id, kategori)
    conn.close()
    return kategori

# test update_kategori_by_id
def test_update_kategori_by_id():
    conn = create_conn()
    # get last id_kategori
    cur = conn.cursor()
    cur.execute("SELECT * FROM kategori ORDER BY id_kategori DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    kategori = Kategori(id_kategori=row[0], nama_kategori="Minuman")
    update_kategori(conn, row[0], kategori)
    conn.close()
    assert kategori.nama_kategori == "Minuman"

# call test
test_update_kategori_by_id()

# - Delete: DELETE /kategori/{id} untuk menghapus kategori berdasarkan id_kategori.
def delete_kategori(conn, id_kategori):
    cur = conn.cursor()
    cur.execute("DELETE FROM kategori WHERE id_kategori=%s", (id_kategori,))
    conn.commit()
    cur.close()

@app.delete("/kategori/{id}", response_model=Union[Kategori, None])
def delete_kategori_by_id(id: int):
    conn = create_conn()
    row = get_kategori_by_id(conn, id)
    delete_kategori(conn, id)
    conn.close()
    return row

# test delete_kategori_by_id
def test_delete_kategori_by_id():
    conn = create_conn()
    # get last id_kategori
    cur = conn.cursor()
    cur.execute("SELECT * FROM kategori ORDER BY id_kategori DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    kategori = get_kategori_by_id(conn, row[0])
    delete_kategori(conn, row[0])
    conn.close()
    assert kategori.nama_kategori == "Minuman"

# call test
test_delete_kategori_by_id()

# 2. API CRUD untuk data bahan:
# - Create: POST /bahan dengan request body berisi nama_bahan.
def insert_bahan(conn, bahan):
    cur = conn.cursor()
    cur.execute("INSERT INTO bahan (nama_bahan) VALUES (%s)", (bahan.nama_bahan,))
    conn.commit()
    cur.close()

@app.post("/bahan", response_model=Bahan)
def create_bahan(bahan: Bahan):
    conn = create_conn()
    insert_bahan(conn, bahan)
    conn.close()
    return bahan

# test insert_bahan
def test_insert_bahan():
    conn = create_conn()
    bahan = Bahan(nama_bahan="Gula")
    insert_bahan(conn, bahan)
    conn.close()
    assert bahan.nama_bahan == "Gula"

# call test
test_insert_bahan()

# - Read/Index: GET /bahan untuk menampilkan seluruh bahan. 
def get_all_bahan(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM bahan")
    rows = cur.fetchall()
    cur.close()
    bahans = []
    for row in rows:
        bahan = Bahan(id_bahan=row[0], nama_bahan=row[1])
        bahans.append(bahan)
    return bahans

@app.get("/bahan", response_model=List[Union[Bahan, None]])
def read_all_bahan():
    conn = create_conn()
    rows = get_all_bahan(conn)
    conn.close()
    return rows

# test get_all_bahan
def test_get_all_bahan():
    conn = create_conn()
    bahans = get_all_bahan(conn)
    conn.close()
    assert bahans[0].nama_bahan == "Gula"

# call test
test_get_all_bahan()

# GET /bahan/{id} untuk menampilkan bahan berdasarkan id_bahan.
def get_bahan_by_id(conn, id_bahan):
    cur = conn.cursor()
    cur.execute("SELECT * FROM bahan WHERE id_bahan=%s", (id_bahan,))
    row = cur.fetchone()
    cur.close()
    bahan = Bahan(id_bahan=row[0], nama_bahan=row[1])
    return bahan

@app.get("/bahan/{id}", response_model=Union[Bahan, None])
def read_bahan_by_id(id: int):
    conn = create_conn()
    row = get_bahan_by_id(conn, id)
    conn.close()
    return row

# test get_bahan_by_id
def test_get_bahan_by_id():
    conn = create_conn()
    # get last id_bahan
    cur = conn.cursor()
    cur.execute("SELECT * FROM bahan ORDER BY id_bahan DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    bahan = get_bahan_by_id(conn, row[0])
    conn.close()
    assert bahan.nama_bahan == "Gula"

# call test
test_get_bahan_by_id()

# - Update: PUT /bahan/{id} dengan request body berisi nama_bahan yang baru.
def update_bahan(conn, id_bahan, bahan):
    cur = conn.cursor()
    cur.execute("UPDATE bahan SET nama_bahan=%s WHERE id_bahan=%s", (bahan.nama_bahan, id_bahan))
    conn.commit()
    cur.close()

@app.put("/bahan/{id}", response_model=Union[Bahan, None])
def update_bahan_by_id(id: int, bahan: Bahan):
    conn = create_conn()
    update_bahan(conn, id, bahan)
    conn.close()
    return bahan

# test update_bahan
def test_update_bahan():
    conn = create_conn()
    # get last id_bahan
    cur = conn.cursor()
    cur.execute("SELECT * FROM bahan ORDER BY id_bahan DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    bahan = get_bahan_by_id(conn, row[0])
    bahan.nama_bahan = "Gula Pasir"
    update_bahan(conn, row[0], bahan)
    conn.close()
    assert bahan.nama_bahan == "Gula Pasir"

# call test
test_update_bahan()

# - Delete: DELETE /bahan/{id} untuk menghapus bahan berdasarkan id_bahan.
def delete_bahan(conn, id_bahan):
    cur = conn.cursor()
    cur.execute("DELETE FROM bahan WHERE id_bahan=%s", (id_bahan,))
    conn.commit()
    cur.close()

@app.delete("/bahan/{id}", response_model=Union[Bahan, None])
def delete_bahan_by_id(id: int):
    conn = create_conn()
    row = get_bahan_by_id(conn, id)
    delete_bahan(conn, id)
    conn.close()
    return row

# test delete_bahan
def test_delete_bahan():
    conn = create_conn()
    # get last id_bahan
    cur = conn.cursor()
    cur.execute("SELECT * FROM bahan ORDER BY id_bahan DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    bahan = get_bahan_by_id(conn, row[0])
    delete_bahan(conn, row[0])
    conn.close()
    assert bahan.nama_bahan == "Gula Pasir"

# call test
test_delete_bahan()

# 3. API CRUD untuk data resep:
# - Create: POST /resep dengan request body berisi nama_resep dan id_kategori.
def insert_resep(conn, resep):
    cur = conn.cursor()
    cur.execute("INSERT INTO resep (nama_resep, id_kategori) VALUES (%s, %s)", (resep.nama_resep, resep.id_kategori))
    conn.commit()
    cur.close()

@app.post("/resep", response_model=Resep)
def create_resep(resep: Resep):
    conn = create_conn()
    insert_resep(conn, resep)
    conn.close()
    return resep

# test insert_resep
def test_insert_resep():
    conn = create_conn()
    resep = Resep(nama_resep="Nasi Goreng", id_kategori=1)
    insert_resep(conn, resep)
    conn.close()
    assert resep.nama_resep == "Nasi Goreng"

# call test
test_insert_resep()

# - Read/Index: GET /resep untuk menampilkan seluruh resep beserta kategori dan bahan-bahan yang digunakan. 
def get_all_resep(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM resep")
    rows = cur.fetchall()
    cur.close()
    reseps = []
    for row in rows:
        resep = Resep(id_resep=row[0], nama_resep=row[1], id_kategori=row[2])
        reseps.append(resep)
    return reseps

@app.get("/resep", response_model=List[Union[Resep, None]])
def read_all_resep():
    conn = create_conn()
    rows = get_all_resep(conn)
    conn.close()
    return rows

# test get_all_resep
def test_get_all_resep():
    conn = create_conn()
    rows = get_all_resep(conn)
    conn.close()
    assert len(rows) > 0

# call test
test_get_all_resep()

# GET /resep/{id} untuk menampilkan resep berdasarkan id_resep.
def get_resep_by_id(conn, id_resep):
    cur = conn.cursor()
    cur.execute("SELECT * FROM resep WHERE id_resep=%s", (id_resep,))
    row = cur.fetchone()
    cur.close()
    resep = Resep(id_resep=row[0], nama_resep=row[1], id_kategori=row[2])
    return resep

@app.get("/resep/{id}", response_model=Union[Resep, None])
def read_resep_by_id(id: int):
    conn = create_conn()
    row = get_resep_by_id(conn, id)
    conn.close()
    return row

# test get_resep_by_id
def test_get_resep_by_id():
    conn = create_conn()
    # get last id_resep
    cur = conn.cursor()
    cur.execute("SELECT * FROM resep ORDER BY id_resep DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    resep = get_resep_by_id(conn, row[0])
    conn.close()
    assert resep.nama_resep == "Nasi Goreng"

# call test
test_get_resep_by_id()

# GET /resep/{id}/bahan untuk menampilkan bahan-bahan yang digunakan pada resep tersebut.
def get_bahan_by_resep_id(conn, id_resep):
    cur = conn.cursor()
    cur.execute("SELECT * FROM resep_bahan WHERE id_resep=%s", (id_resep,))
    rows = cur.fetchall()
    cur.close()
    bahans = []
    for row in rows:
        bahan = Bahan(id_bahan=row[1], nama_bahan=row[2])
        bahans.append(bahan)
    return bahans

@app.get("/resep/{id}/bahan", response_model=List[Union[Bahan, None]])
def read_bahan_by_resep_id(id: int):
    conn = create_conn()
    rows = get_bahan_by_resep_id(conn, id)
    conn.close()
    return rows

# - Update: PUT /resep/{id} dengan request body berisi nama_resep dan/atau id_kategori yang baru. 
# PUT /resep/{id}/bahan dengan request body berisi id_bahan yang baru untuk menambahkan bahan pada resep tersebut.
def update_resep(conn, id_resep, resep):
    cur = conn.cursor()
    cur.execute("UPDATE resep SET nama_resep=%s, id_kategori=%s WHERE id_resep=%s", (resep.nama_resep, resep.id_kategori, id_resep))
    conn.commit()
    cur.close()

@app.put("/resep/{id}", response_model=Union[Resep, None])
def update_resep_by_id(id: int, resep: Resep):
    conn = create_conn()
    update_resep(conn, id, resep)
    conn.close()
    return resep

def insert_resep_bahan(conn, id_resep, id_bahan):
    cur = conn.cursor()
    cur.execute("INSERT INTO resep_bahan (id_resep, id_bahan) VALUES (%s, %s)", (id_resep, id_bahan))
    conn.commit()
    cur.close()

@app.put("/resep/{id}/bahan", response_model=Union[Bahan, None])
def update_bahan_by_resep_id(id: int, bahan: Bahan):
    conn = create_conn()
    insert_resep_bahan(conn, id, bahan.id_bahan)
    conn.close()
    return bahan

# - Delete: DELETE /resep/{id} untuk menghapus resep berdasarkan id_resep. 
# DELETE /resep/{id}/bahan/{id_bahan} untuk menghapus bahan pada resep tersebut.
def delete_resep(conn, id_resep):
    cur = conn.cursor()
    cur.execute("DELETE FROM resep WHERE id_resep=%s", (id_resep,))
    conn.commit()
    cur.close()

@app.delete("/resep/{id}", response_model=Union[Resep, None])
def delete_resep_by_id(id: int):
    conn = create_conn()
    row = get_resep_by_id(conn, id)
    delete_resep(conn, id)
    conn.close()
    return row

def delete_resep_bahan(conn, id_resep, id_bahan):
    cur = conn.cursor()
    cur.execute("DELETE FROM resep_bahan WHERE id_resep=%s AND id_bahan=%s", (id_resep, id_bahan))
    conn.commit()
    cur.close()

@app.delete("/resep/{id}/bahan/{id_bahan}", response_model=Union[Bahan, None])
def delete_bahan_by_resep_id(id: int, id_bahan: int):
    conn = create_conn()
    row = get_bahan_by_id(conn, id_bahan)
    delete_resep_bahan(conn, id, id_bahan)
    conn.close()
    return row


# 4. API untuk menampilkan list/index/read resep berdasarkan search/filter bahan dan kategori yang digunakan:
# - GET /resep?kategori={nama_kategori}&bahan={nama_bahan} untuk menampilkan resep berdasarkan kategori dan/atau bahan yang digunakan.
def get_resep_by_kategori_bahan(conn, id_kategori, id_bahan):
    cur = conn.cursor()
    cur.execute("SELECT * FROM resep WHERE id_kategori=%s AND id_resep IN (SELECT id_resep FROM resep_bahan WHERE id_bahan=%s)", (id_kategori, id_bahan))
    rows = cur.fetchall()
    cur.close()
    reseps = []
    for row in rows:
        resep = Resep(id_resep=row[0], nama_resep=row[1], id_kategori=row[2])
        reseps.append(resep)
    return reseps

@app.get("/resep", response_model=List[Union[Resep, None]])
def read_resep_by_kategori_bahan(kategori: Optional[str] = None, bahan: Optional[str] = None):
    conn = create_conn()
    id_kategori = get_kategori_by_nama(conn, kategori).id_kategori
    id_bahan = get_bahan_by_nama(conn, bahan).id_bahan
    rows = get_resep_by_kategori_bahan(conn, id_kategori, id_bahan)
    conn.close()
    return rows

# test case untuk API search/filter
def test_get_resep_by_kategori_bahan():
    conn = create_conn()
    reseps = get_resep_by_kategori_bahan(conn, 1, 1)
    conn.close()
    assert len(reseps) == 1
    assert reseps[0].nama_resep == "Nasi Goreng"

# call test
test_get_resep_by_kategori_bahan()
