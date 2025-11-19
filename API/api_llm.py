import sys
import os
sys.path.insert(0, '../RAG-Sqlites')



from  fastapi import FastAPI

from fastapi.responses import StreamingResponse
import uvicorn

import sqlite_vec


from code_base.database import *




from code_base.llm_fonctions import *
from test_dev.test_token import * 

app=FastAPI()




"""
une reponse en stream et cool pour les reduire le temps percu de reponse mais comment gerer une conversation continue avec un user ?
a priori cela veut l'ouverture d'une connection avec l'ia , garder la conversation tant que la connection n'est pas ferme , id par token pour acceder ala conversation 

streaming response 
token reco 

"""



@app.get("connection")
def check_connection(): 
    """
    cette fonction sert a verifier la connection avec l'api , disponibilité , temps de reponse ...
    """
    pass



@app.post("/request one shot")
async def one_shot_question(question): 
    rag_answer=questionnning_rag(question)

    return StreamingResponse(ollama_stream_response(question,rag_answer),)
       



@app.post("/stream conversation")
def discussion (prompt,token=""):

    rag_answer=questionnning_rag(prompt)

    if token=="" : 
        token=make_token(secret="secret",algorithm="HS256")
        response=ollama_response(prompt,rag_answer)
        save_historique(token,prompt,response)
        return token, response


    else  : 
        past_data=get_historique(token=token)
        print(past_data)
        response=ollama_response(prompt,rag_answer+past_data)
        save_historique(token,prompt,response)
        return token,response










if __name__=="__main__" : 
    uvicorn.run(app,host="127.0.0.1",port=8000)
