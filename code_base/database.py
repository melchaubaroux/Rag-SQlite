"""
fichier de fonction pour les interactions avec une base sqlite3 et l'add on sqlite_vec 
"""

import os
import sqlite3
import sqlite_vec
from code_base.splitter_fonctions import parse_markdown

db="./db/manette_doc"
stringify= lambda x : ",".join(map ( lambda y :f'"{y}"',x))
stringify_one= lambda x : f'"{x}"'
stringify_list= lambda x : "("+",".join(map(stringify_one,x))+")"
stringify_list_list = lambda x : ",".join(map (stringify_list,x))



def connection_to_sqlite_base(string): 
    con=sqlite3.connect(string)
    cur=con.cursor()
    return con,cur

def create_table(cursor,name:str,colonnes:list[str]):
    cursor.execute("CREATE TABLE '{}'({})".format(name,",".join(colonnes)))

def suppress_table(cursor,name:str):
    cursor.execute("DROP TABLE [{}]".format(name))

def request_table(cursor,name:str,colonnes:list[str]):

    cursor.execute("SELECT   from '{}' ({}) ".format(name,",".join(colonnes)),)
    return cursor.fetchall()

def check_existance_table(cursor,name:str):
   cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{}' ".format(name))
   return cursor.fetchall()


def get_tables_names (cursor) : 
   
    cursor.execute(f"""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    AND name NOT LIKE 'sqlite_%'
    -- exclure tables virtuelles FTS / vector
    AND (sql NOT LIKE 'CREATE VIRTUAL TABLE%' )
    -- exclure tables internes générées
    AND name NOT LIKE '%_embedding%'
    AND name NOT LIKE '%_chunks%'
    AND name NOT LIKE '%_rowids%'
    AND name NOT LIKE '%_vector_chunks%';""")
    return cursor.fetchall()
    

def add_row_in_table (cursor,name:str,colonnes:list[str],values=list[str]): 
    cursor.execute("INSERT INTO '{}' ({})  VALUES {stringify_list(values)}".format(name,",".join(colonnes)))


def add_rows_in_table (cursor,name:str,colonnes:list[str],values=list[list[str]]):
    cursor.execute("INSERT INTO '{}' ({}) VALUES {}".format(name,",".join(colonnes),stringify_list_list(values)))

def add_elements_in_table(cursor,name:str,colonnes,values:list[str]):
    if type(values[0])==str :  add_row_in_table(cursor,name,colonnes,values)
       
    else :  add_rows_in_table(cursor,name,colonnes,values)
       

def create_virtual_table (cursor,name:str): 
    cursor.execute("CREATE VIRTUAl TABLE '{}_embedding' using vec0  ( embedding float [512] )".format(name))


def create_binded_table (cursor,name:str,colonnes:list[str]):

    create_table(cursor,name,colonnes)
    create_virtual_table(cursor,name)




def add_elements_in_binded_table(cursor,name,values): 
    if type(values[0])==str :
        
        cursor.execute("INSERT INTO '{}' (texte)  VALUES (?)".format(name),[values[0]])
        _id=cursor.lastrowid
        cursor.execute("INSERT INTO '{}_embedding'(rowid,embedding) VALUES (?,?)".format(name),[_id,values[1]])

    else : 
        for texte,vecteur in values : 
            cursor.execute("INSERT INTO '{}' (rowid,texte)  VALUES ('{texte}')".format(name))
            _id=cursor.lastrowid
            cursor.execute("INSERT INTO '{}_embedding' (rowid,embedding) VALUES (?,?)".format(name),[_id,vecteur])


def del_row_in_binded_table (cursor,table,value) : 
    if type(value)==int : 
        _id=value
        cursor.execute("DELETE FROM '{}' WHERE id = {value};".format(table))
        cursor.execute("DELETE FROM '{}_embedding' WHERE rowid = {};".format(table,_id))


    if type(value)==str : 
        _id=cursor.execute("SELECT id FROM '{}' WHERE texte='{}'".format(table,value)).fetchall()
        cursor.execute("DELETE FROM '{}' WHERE texte LIKE '{}';".format(table,value))
        cursor.execute("DELETE FROM '{}_embedding' WHERE rowid = {};".format(table,_id))



def del_binded_table (cursor,table):
    suppress_table(cursor,table)
    suppress_table(cursor,table+"_embedding")
    



def search_in_vtable (cursor,table,query,limit):

    vresults=[]

    print(table)


    # """
    #     SELECT
    #         rowid
    #     FROM '{}_embedding'
    #     WHERE embedding MATCH ?
    #     ORDER BY distance
    #     LIMIT {}
    #     """

    # """
    #     SELECT
    #         rowid
    #     FROM '{}_embedding'
    #     WHERE embedding MATCH ?
    #     AND vec_distance_l2(embedding, ?) <=1
    #     AND k={}
    #     ORDER BY distance
        
    #     """
    
    

    vresults+=cursor.execute(
        """
        SELECT
            rowid
        FROM '{}_embedding'
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT {}
        """.format(table,limit),[query]).fetchall()
        # """
        # SELECT * from '{}_embedding'
        # limit {}
        # """.format(table,limit)).fetchall()
    
    
    
    tresults=[]

    print(vresults)

     
    tresults+=cursor.execute(
        """
        SELECT
            texte
        FROM '{}'
        WHERE id in ({})
        """.format(table,",".join(["?"] * len(vresults))),[x[0] for x in vresults]
        ).fetchall()
    
    print(tresults)
    

    return tresults



def search_in_vbase (cursor,query,limit):

    related_document=search_in_vtable(cursor,"index",query,limit)

    result=[]

    for document in related_document : 
        result+=search_in_vtable(cursor,document[0],query,limit)

    return result


def insert_document_in_markdown_format (model,path) : 

    arbo,temps=parse_markdown(path)
    table_name=os.path.split(path)[1].split(".")[0]


    con,cursor=connection_to_sqlite_base(db)

    with con : 

        con.enable_load_extension(True)
        sqlite_vec.load(con)
        con.enable_load_extension(False)

        nested_list=[a+t for a,t  in zip (arbo,temps)]
        g=[item for sublist in nested_list for item in sublist]

        vdocument=model.encode("\n".join(g))
        add_elements_in_binded_table(cursor,"index",[table_name,vdocument])

        create_binded_table(cursor,table_name,["id INTEGER PRIMARY KEY ","texte"])

        for a,t in zip(arbo,temps) : 

            titles="\n".join(a)
            texte="".join(t)


            texte_to_vectorise =  "\n".join([titles,texte])
            assert type(texte_to_vectorise)== str
            vector=model.encode(texte_to_vectorise)
            add_elements_in_binded_table(cursor,table_name,[texte_to_vectorise,vector])


        con.commit()
        cursor.close()








#TODO rejouter le commmit 

# con,cursor=connection_to_sqlite_base(":memory:")
# con.enable_load_extension(True)
# sqlite_vec.load(con)
# con.enable_load_extension(False)
# test fonctionnel :

# create_table(cursor,"movie",["title", "year", "score"])
# print(check_existance_table(cursor,"movie"))
# request_table(cursor,"movie",["title", "year", "score"])
# cursor.execute("INSERT INTO movie (title, year, score)  VALUES ('blob','1990','10');")
# print(cursor.fetchall())

# request_table(cursor,"movie",["title", "year", "score"])
# add_row_in_table(cursor,"movie",["title", "year", "score"],['blob','1990','10'])
# add_rows_in_table(cursor,"movie",["title", "year", "score"],[['blob','1990','10'],['bob','1997','10'],['blo','1996','10'],['lob','1995','10']])
# request_table(cursor,"movie",["title", "year", "score"])
# add_elements_in_table(cursor,"movie",["title", "year", "score"],['blob','1990','10'])
# add_elements_in_table(cursor,"movie",["title", "year", "score"],[['blob','1990','10'],['bob','1997','10'],['blo','1996','10'],['lob','1995','10']])
# print(request_table(cursor,"movie",["title", "year", "score"]))
# suppress_table(cursor,"movie")
import struct
from typing import List
def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)


# cursor.execute("INSERT INTO test (texte)  VALUES ('blob');")
# print(request_table(cursor,"test",["*"]))
# cursor.execute(f"INSERT INTO test_embedding(rowid,embedding)  VALUES (?,?);",[1,serialize_f32([0.11])])
# create_binded_table(cursor,"test",["id INTEGER PRIMARY KEY ","texte"])
# add_elements_in_binded_table(cursor,"test",["test1",serialize_f32([1.0])])
# add_elements_in_binded_table(cursor,"test",["test2",serialize_f32([2.0])])
# del_row_in_binded_table("test",2)
# add_elements_in_binded_table(cursor,"test",["test3",serialize_f32([3.0])])
# print(request_table(cursor,"test",["*"]))
# print(request_table(cursor,"test_embedding",["*"]))















