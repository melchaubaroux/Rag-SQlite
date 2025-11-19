from sentence_transformers import SentenceTransformer

# Chargement du modèle
model = SentenceTransformer("distiluse-base-multilingual-cased-v2")

# # Calcul des embeddings
# sentences = ["Le temps est magnifique aujourd'hui.", "The weather is beautiful today","the weather is nice today","The weather is  very beautiful today"]
# embeddings = model.encode(sentences)
# print(len(embeddings[0]))

# # Calcul des similarités
# similarites = model.similarity(embeddings, embeddings)

# print(similarites)


def vectorise (model,texte) : 

    """
    use the given model for output an embedding of the given text

    args :
        model 
        text

    """

    return   model.encode(texte)




