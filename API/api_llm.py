import sys
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from prometheus_client import Summary, Histogram, make_asgi_app
import uvicorn
import time

sys.path.insert(0, '../RAG-Sqlites')

from code_base.database import *
from code_base.llm_fonctions import *
from test_dev.test_token import *

app = FastAPI()

# Définition des métriques Prometheus
REQUEST_TIME = Summary('api_request_latency_seconds', 'Temps de traitement des requêtes')
HIST_TIME = Histogram('api_request_latency_seconds_hist', 'Histogramme du temps de traitement')

# Intégration de Prometheus dans FastAPI
app.mount("/metrics", make_asgi_app())

# Decorateur pour mesurer le temps sur les endpoints FastAPI
def track_time(func):
    async def wrapper(question):
        start = time.time()
        result = await func(question)
        elapsed = time.time() - start
        REQUEST_TIME.observe(elapsed)
        HIST_TIME.observe(elapsed)
        return result
    return wrapper

@app.get("/connection")
@track_time
async def check_connection():
    """
    Vérifie la disponibilité et le temps de réponse de l'API.
    """
    return {"status": "ok"}

@app.post("/request_one_shot")
@track_time
async def one_shot_question(question: str):
    rag_answer = questionnning_rag(question)
    return StreamingResponse(ollama_stream_response(question, rag_answer))

@app.post("/stream_conversation")
@track_time
async def discussion(prompt: str, token: str = ""):
    rag_answer = questionnning_rag(prompt)

    if token == "":
        token = make_token(secret="secret", algorithm="HS256")
        response = ollama_response(prompt, rag_answer)
        save_historique(token, prompt, response)
        return {"token": token, "response": response}

    else:
        past_data = get_historique(token=token)
        response = ollama_response(prompt, rag_answer + past_data)
        save_historique(token, prompt, response)
        return {"token": token, "response": response}

if __name__ == '__main__':
    uvicorn.run(app, port=8000)