# Modules externe
import sys 
#import sqlite_vec


sys.path.insert(0, '../RAG-Sqlites')

# Module a tester
from code_base.database import *


# Base de test (mémoire temporaire)
db=":memory:"


# Test de connection 
def test_connection() : 

    con,cursor=connection_to_sqlite_base(db)
    assert con !=None
    assert cursor !=None


# Test de chargement de l'extension  
def test_chargement_extension() : 

        con,cursor=connection_to_sqlite_base(db)
        con.enable_load_extension(True)
        sqlite_vec.load(con)
        con.enable_load_extension(False)


# Test creation de table classique
def test_create_table (): 

    con,cursor=connection_to_sqlite_base(db)
    create_table(cursor,"movie",["title", "year", "score"])
    assert "movie" in  check_existance_table(cursor,"movie")



# Test modif 'manuel' de table classique
def test_manual_filing_table (): 

    con,cursor=connection_to_sqlite_base(db)
    create_table(cursor,"movie",["title", "year", "score"])
    cursor.execute("INSERT INTO movie (title, year, score)  VALUES ('blob','1990','10');")
    result =request_table(cursor,"movie",["title", "year", "score"])

    assert ('blob','1990','10') in result,"les données n'ont pas été sauvegardé"


# Test modif fonctionnel de table classique
def test_add_row_in_table (): 

    con,cursor=connection_to_sqlite_base(db)
    create_table(cursor,"movie",["title", "year", "score"])
    add_row_in_table(cursor,"movie",["title", "year", "score"],['blob','1990','10'])
    result =request_table(cursor,"movie",["title", "year", "score"])

    assert ('blob','1990','10') in result,"les données n'ont pas été sauvegardé"


# Test multiple modif fonctionnel de table classique
def test_add_rows_in_table (): 

    con,cursor=connection_to_sqlite_base(db)
    create_table(cursor,"movie",["title", "year", "score"])
    add_rows_in_table(cursor,"movie",["title", "year", "score"],[['blob','1990','10'],['bob','1997','10'],['blo','1996','10'],['lob','1995','10']])
    result =request_table(cursor,"movie",["title", "year", "score"])

    assert ('blob','1990','10') in result
    assert ('bob','1997','10') in result
    assert ('blo','1996','10') in result
    assert ('lob','1995','10') in result

    

# Test gestion appel modifieur  de table classique
def test_add_element_in_table (): 

    con,cursor=connection_to_sqlite_base(db)
    create_table(cursor,"movie",["title", "year", "score"])
    add_elements_in_table(cursor,"movie",["title", "year", "score"],['blob','1990','10'])
    result =request_table(cursor,"movie",["title", "year", "score"])

    assert ('blob','1990','10') in result,"les données n'ont pas été sauvegardé"


# Test gestion appel mutiple modifieur  de table classique
def test_add_elements_in_table (): 

    con,cursor=connection_to_sqlite_base(db)
    create_table(cursor,"movie",["title", "year", "score"])
    add_elements_in_table(cursor,"movie",["title", "year", "score"],[['blob','1990','10'],['bob','1997','10'],['blo','1996','10'],['lob','1995','10']])
    result =request_table(cursor,"movie",["title", "year", "score"])

    assert ('blob','1990','10') in result
    assert ('bob','1997','10') in result
    assert ('blo','1996','10') in result
    assert ('lob','1995','10') in result


# Test suppression de table classique
def test_delete_table (): 
    con,cursor=connection_to_sqlite_base(db)
    create_table(cursor,"movie",["title", "year", "score"])
    suppress_table(cursor,"movie")
    result=check_existance_table(cursor,"movie")
    assert result== None



# Test de creation manuel de table virtuel avec  l'extension  
def test_create_vectoriel_table_manual() : 

    con,cursor=connection_to_sqlite_base(db)
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)

    # -> création d’une table VEC (type fourni par sqlite-vec)
    cursor.execute("CREATE VIRTUAL TABLE 'test_vec' USING vec0 ( embedding float [512] );")

    # Si la commande passe sans erreur, l’extension est bien active
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_vec';")
    result = cursor.fetchone()

    assert result !=None, "La table VEC n'a pas été créée "
    assert result[0] == "test_vec", f"Nom inattendu: {result!r}"


# Test de creation fonctionnel de table virtuel avec  l'extension  
def test_create_vectoriel_table_fonctionnal() : 

    con,cursor=connection_to_sqlite_base(db)
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)

    # -> création d’une table VEC (type fourni par sqlite-vec)
    create_virtual_table (cursor,'test_vec')

    # Si la commande passe sans erreur, l’extension est bien active
    result =check_existance_table(cursor,"test_vec_embedding")
    

    assert result !=None, "La table VEC n'a pas été créée "
    assert result[0] == "test_vec_embedding", f"Nom inattendu: {result!r}"




# Test de creation de tables liés 
def test_create_binded_table(): 

    con,cursor=connection_to_sqlite_base(db)
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)


    create_binded_table(cursor,"movies",["id INTEGER PRIMARY KEY ","texte"])
    classique_table=check_existance_table(cursor,"movies")
    virtuel_table=check_existance_table(cursor,"movies_embedding")

    assert classique_table !=None, "La table texte n'a pas été crée "
    assert virtuel_table !=None, "La table VEC n'a pas été créée "

    assert classique_table[0] == "movies", f"Nom inattendu: {classique_table!r}"
    assert virtuel_table[0] == "movies_embedding", f"Nom inattendu: {virtuel_table!r}"


# Test de modifications de tables lié
def test_filling_binded_table(): 

    con,cursor=connection_to_sqlite_base(db)
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)


    create_binded_table(cursor,"test",["id INTEGER PRIMARY KEY ","texte"])

    add_elements_in_binded_table(cursor,"test",["test1",serialize_f32(list(map(float,range(512))))])
    add_elements_in_binded_table(cursor,"test",["test2",serialize_f32(list(map(float,range(1,513))))])

    classique_table_values = [x for y in request_table(cursor,"test",["*"]) for x in y]
    virtuel_table_values = [x for y in request_table(cursor,"test_embedding",["*"]) for x in y]


    assert "test1" in  classique_table_values
    assert "test2" in  classique_table_values
    assert serialize_f32(list(map(float,range(512)))) in virtuel_table_values
    assert serialize_f32(list(map(float,range(1,513)))) in virtuel_table_values


    del_row_in_binded_table(cursor,"test",1)
    del_row_in_binded_table(cursor,"test","test2")

    classique_table_values=request_table(cursor,"test",["*"])
    virtuel_table_values=request_table(cursor,"test",["*"])

    assert classique_table_values == []
    assert virtuel_table_values == []












   






     
     

# cursor.execute(f"INSERT INTO test_embedding(rowid,embedding)  VALUES (?,?);",[1,serialize_f32([0.11])])
# create_binded_table(cursor,"test",["id INTEGER PRIMARY KEY ","texte"])
# add_elements_in_binded_table(cursor,"test",["test1",serialize_f32([1.0])])
# add_elements_in_binded_table(cursor,"test",["test2",serialize_f32([2.0])])
# del_row_in_binded_table("test",2)
# add_elements_in_binded_table(cursor,"test",["test3",serialize_f32([3.0])])
# print(request_table(cursor,"test",["*"]))
# print(request_table(cursor,"test_embedding",["*"]))



