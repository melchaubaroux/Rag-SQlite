# RAG-SQlite

Ce Repos est un projet de RAG avec SQLITE


## mise a jour : 

Ajout du fichier yml prometheus 

## Installation de l'environnement

### Prérequis

* Ollama
* Git
* Sous Windows : Visual Studio 2019 (C/C++ Development Tools)

### Clonage du dépôt

```bash
git clone https://github.com/melchaubaroux/Rag-SQlite
cd Rag-SQlite
```

### Environnement virtuel

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Téléchargement du modèle LLM

```bash
ollama pull llama3.2
```

### Vérification du modèle

```bash
ollama list
```

### Activation du LLM

```bash
ollama serve
```

(Sur Windows : cliquer sur l'icône Ollama)

### Lancement des APIs

Dans deux terminaux séparés :

```bash
python api/admin.py   # port 8000
python api/user.py    # port 8001
```


### Connection a l'api admin 

Default Username : admin    
Default password : admin    

---

## Architecture

```
Rag-SQlite/
├── api/
│   ├── __init__.py
│   ├── admin.py          # API administration (port 8000)
│   └── user.py           # API utilisateur (port 8001)
│
├── core/                 # Logique métier, services, utilitaires
├── database/
├── tests/                # Ressources de test
├── file/                 # Config, templates, ressources
├── bootstrap/            # Scripts de démarrage (optionnel)
├── requirements.txt
└── README.md
```
