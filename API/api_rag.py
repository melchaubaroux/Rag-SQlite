

import sys
import os
from fastapi import FastAPI,Request

from sentence_transformers import SentenceTransformer
import uvicorn
import sqlite_vec
import pymupdf4llm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi import Form


sys.path.insert(0, '../RAG-Sqlites')

from code_base.database import *

print(sys.path)
model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
con,cursor=connection_to_sqlite_base("manette_doc")





app=FastAPI()


# Instance du moteur de modèles Jinja2 pour la gestion des templates HTML
templates = Jinja2Templates(directory="file")

db="./db/manette_doc"


con,cursor=connection_to_sqlite_base(db)
con.enable_load_extension(True)
sqlite_vec.load(con)
con.enable_load_extension(False)

if len(check_existance_table(cursor,"index"))==0 : create_binded_table(cursor,"index",["id INTEGER PRIMARY KEY ","texte"])


from fastapi import Cookie

@app.get("/", response_class=HTMLResponse)
def home(request: Request, auth: str = Cookie(None), message: str = None):
    if auth != "ok":
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("template_admin.html", {"request": request, "message": message})

    

# @app.get("/", response_class=HTMLResponse)
# def home(request: Request, message: str = None):
#     return templates.TemplateResponse("template_admin.html", {"request": request, "message": message})



# mot de passe simple (en dur pour test)
ADMIN_PASSWORD = "monmotdepasse"

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, message: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "message": message})

@app.post("/login")
def login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/", status_code=303)
        # on peut ici mettre un cookie simple pour la session
        response.set_cookie(key="auth", value="ok", httponly=True)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "message": "Mot de passe incorrect"})



@app.get("/connection")
def check_connection(): 

    """
    cette fonction sert a verifier la connection avec l'api , disponibilité , temps de reponse ...
    """

    try : 

        con,cursor=connection_to_sqlite_base(db)
        assert con!=None

        return " connection fonctionnel "
    
    except : 

        return "probleme de connection"
    

@app.get("/liste tables")
def liste_tables () : 
    con,cursor=connection_to_sqlite_base(db)
    return get_tables_names(cursor)


#upload un document 
@app.get("/upload")
def upload(path): 

    trajectory,name=os.path.split(path)
    


    if name.split(".")[-1]!="pdf" : return "ce n'est pas un fichier pdf"
        
    else :
        new_name=name.split(".")[0]+".md"

        new_path=os.path.join(trajectory,new_name)
    

        with open(new_name,"w",encoding="utf-8") as file : 
            file.write(pymupdf4llm.to_markdown(path))

        insert_document_in_markdown_format(model,new_name)
        os.remove(new_name)


   
#remplace un document
@app.get("/replace")
def replace(name,path): 
    delete(name)
    upload(path)



#supprime un document 
@app.get("/delete")
def delete(name): 

    con,cursor=connection_to_sqlite_base(db)
    
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)
    del_binded_table(cursor,name)
   


#chercher des infos 
@app.get("/request")
def search(request,limit): 

    con,cursor=connection_to_sqlite_base(db)
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)

    query=model.encode(request)
    answer=search_in_vbase(cursor,query,limit)

    return answer


if __name__=="__main__" : 
    uvicorn.run(app,host="127.0.0.1",port=8001)



