

from ollama import chat
from ollama import ChatResponse

import json 

from sentence_transformers import SentenceTransformer
model = SentenceTransformer("distiluse-base-multilingual-cased-v2")

from code_base.database import *

db="./db/manette_doc"




def ollama_stream_response (request,contexte) : 

    stream = chat(
    model='llama3.2',
    messages=[{'role': 'user', 'content': f'  je voudrais que tu reponde a la question  suivante : {request} .en utilisant les informations suivantes : [{contexte}] '}],
    stream=True,
    )
    for chunk in stream: 
        content = chunk["message"]["content"]
        if content:  # éviter d'envoyer des vides
            yield content.encode("utf-8")


def ollama_response (request,contexte) : 

    ChatResponse = chat(
    model='llama3.2',
    messages=[{'role': 'user', 'content': f'  je voudrais que tu reponde a la question  suivante : {request} .en utilisant les informations suivantes : [{contexte}] '}],
    stream=False,
    )
    
    return ChatResponse["message"]["content"] 
       

       

# streamed_response = ollama_stream_response("comment je m'appel","je m'appel mel ")

# for chunk in streamed_response:
#   print(chunk['message']['content'], end='', flush=True)






# class LLM () : 
#     def __init__(self,model):
#         self.model=model
#         self.memory=[]

    
#     def __call__(self, request):
#         self.memory.append(request)
#         answer=self.model.run(request)
#         self.memory.append(answer)

#         return answer


def init (): 

    con,cur=connection_to_sqlite_base("token_base")
    if check_existance_table(cur,"token_table")==[]: 
        print("creation de la table de token ")
        create_table(cur,"token_table",["token","value"])
    

def get_historique(token) : 

    """
    fonction de recuperation de l'historique 

    """
    con,cur=connection_to_sqlite_base("token_base")
    data=cur.execute("SELECT value from token_table where token=?",[token]).fetchall()

    
    cur.close()
    con.close()

    return data


def save_historique (token,prompt,data) : 

    con,cur=connection_to_sqlite_base("token_base")
    
    last_data=cur.execute("SELECT value from token_table where token=?",[token]).fetchone()
    print("last_data value and type ",last_data, type(last_data))

    
    



    if last_data==None: 
        formatted_data=json.dumps({f"{prompt}":f"{data}"})
        print(" type formatted_data:",type(formatted_data))
        print(" formatted_data:",formatted_data)
        cur.execute("INSERT INTO token_table (token,value) VALUES (?,?)",[token,formatted_data])
        #add_row_in_table(cur,"token_table",["token","value"],[token,formatted_data])

    else : 
        last_data=json.loads(last_data[0])
        last_data.update({prompt:data})
        
        #data=" ".join([*last_data,data])
        data=json.dumps(last_data)
       

        cur.execute("UPDATE token_table SET value = ? where token = ? ",(data,token))

    con.commit()

    cur.close()
    con.close()


def questionnning_rag(request): 
    con,cursor=connection_to_sqlite_base(db)
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)

    query=model.encode(request)
    answer=search_in_vbase(cursor,query,1)



    return answer


# import test_token
# token=test_token.make_token("secret","HS256")
# data1="dieu n'aime pas les epinard"
# data2="mais le diable aime pas les epinard"
# init()
# save_historique(token,data1)
# first_data=get_historique(token)
# print(first_data)
# save_historique(token,data2)
# get_historique(token)
# second_data=get_historique(token)

# print(second_data)

# con,cur=connection_to_sqlite_base("token_base")
# print(cur.execute("SELECT * from token_table").fetchall())



       

    





        






    



        
        

