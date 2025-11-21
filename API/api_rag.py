import sys
import os

from sentence_transformers import SentenceTransformer
import sqlite_vec

import pymupdf4llm

from fastapi import FastAPI,Request,Form,Cookie,UploadFile,File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
import uvicorn

sys.path.insert(0, '../RAG-Sqlites')

from code_base.database import *


db="./db/manette_doc"
# mot de passe simple (en dur pour test)
Username="admin"
ADMIN_PASSWORD = "admin"


#Instanciation de l'application est du model 
app=FastAPI()
model = SentenceTransformer("distiluse-base-multilingual-cased-v2")

# Instanciation du moteur de modèles Jinja2 pour la gestion des templates HTML
templates = Jinja2Templates(directory="file")

# Instanciation de la connection SQlite et l'extension qui gere les vecteurs 
con,cursor=connection_to_sqlite_base(db)
con.enable_load_extension(True)
sqlite_vec.load(con)
con.enable_load_extension(False)


# Initialisation de la table d'index 
if len(check_existance_table(cursor,"index"))==0 : 
    create_binded_table(cursor,"index",["id INTEGER PRIMARY KEY ","texte"])

# Initialisation de la table d'utilisateur
if len(check_existance_table(cursor,"user"))==0 :
    create_table(cursor,"user",["id INTEGER PRIMARY KEY ","username","password","role"])
    cursor.execute("INSERT INTO user (username,password,role)  VALUES  ('admin','admin','admin')")
    con.commit()



@app.get("/", response_class=HTMLResponse)
def home(request: Request, auth: str = Cookie(default=None), message: str = None):

    """

        Redirige vers la page de connection  si l'utilisateur n'est pas authentifié

    """

    if auth != "ok":
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("template_admin.html", {"request": request, "message": message})

    
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, message: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "message": message})

@app.post("/login")
def login(request: Request,username: str = Form(...), password: str = Form(...)):
    if password == ADMIN_PASSWORD and username==Username:
        response = RedirectResponse(url="/", status_code=303)
        # on peut ici mettre un cookie simple pour la session
        response.set_cookie(key="auth", value="ok", httponly=True)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "message": "Mot de passe incorrect"})
    


@app.get("/logout",response_class=HTMLResponse)
def logout(request: Request, message: str = None):

    """

    Deconnecte l'utilisateur.
    Supprime le cookie de session.

    """

    response = RedirectResponse(url="/login", status_code=303)

    # On supprime le cookie 
    response.delete_cookie(
        key="auth",          # nom du cookie
        path="/",               # doit matcher le cookie original
    )

    return response



@app.get("/connection")
def check_connection(): 

    """
    Sert a verifier la connection la base de donnée

    """

    try : 

        con,cursor=connection_to_sqlite_base(db)
        assert con!=None

        return " connection fonctionnelle "
    
    except Exception as e : 

        return f"probleme de connection :{e}"
    

@app.get("/liste tables")
def liste_tables () : 
    con,cursor=connection_to_sqlite_base(db)
    return get_tables_names(cursor)


# #upload un document 
# @app.get("/upload")
# def upload(path): 

#     trajectory,name=os.path.split(path)
    


#     if name.split(".")[-1]!="pdf" : return "ce n'est pas un fichier pdf"
        
#     else :
#         new_name=name.split(".")[0]+".md"

#         new_path=os.path.join(trajectory,new_name)
    

#         with open(new_name,"w",encoding="utf-8") as file : 
#             file.write(pymupdf4llm.to_markdown(path))

#         insert_document_in_markdown_format(model,new_name)
#         os.remove(new_name)

@app.post("/upload")
async def upload(pdf: UploadFile = File(...)):
    # Vérif extension
    if not pdf.filename.lower().endswith(".pdf"):
        return "Ce n'est pas un PDF"

    # Lire le contenu du fichier uploadé
    contenu = await pdf.read()

    # Enregistrer temporairement
    temp_dir = "./temp"
    os.makedirs(temp_dir, exist_ok=True)  # crée ./temp si inexistant
    temp_path = os.path.join(temp_dir, pdf.filename)


    with open(temp_path, "wb") as f:
        f.write(contenu)

    # Convertir PDF → Markdown
    md_content = pymupdf4llm.to_markdown(temp_path)

    md_path = temp_path.replace(".pdf", ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Indexer dans ta base
    insert_document_in_markdown_format(model, md_path)

    # Nettoyage
    os.remove(temp_path)
    os.remove(md_path)

    return f"Document '{pdf.filename}' uploadé et indexé."


   
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

    if name=="user" : 
        return 'vous ne pouvez supprimer la table d"utilisateur'
    if name=="index" : 
        return 'vous ne pouvez supprimer la table d"index'
    
    del_binded_table(cursor,name)

    return f"table {name} supprimé"
   


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



