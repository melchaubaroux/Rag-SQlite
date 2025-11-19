"""
ce fichier construit la classe vectoriseur 

utilisation des design pattern 



"""







class Vectoriseur () : 

    """
    on definit ici  les actions que peuvent faire le vectoriseur  a savoir :
    
    
    """
    pass



from transformers import AutoTokenizer, AutoModel

# Chargement du modèle et du tokenizer
tokenizer = AutoTokenizer.from_pretrained("Bert")
model = AutoModel.from_pretrained("BERT")

# Exemple d'utilisation
input_text = "Bonjour, comment allez-vous?"  # ou "Hello, how are you?"
inputs = tokenizer(input_text, return_tensors="pt")
outputs = model(**inputs)

# Affichage des informations utiles
print("\nInformations sur les outputs :")
print(f"- Shape des derniers états cachés : {outputs.last_hidden_state.shape}")
print(f"- Nombre de couches : {len(outputs.hidden_states)}")
print("\nPremier token décodé :")
print(tokenizer.decode(outputs.last_hidden_state[0, 0], skip_special_tokens=True))

# Pour voir tous les états cachés
for i, hidden_state in enumerate(outputs.hidden_states):
    print(f"\nÉtat caché couche {i}:")
    print(hidden_state[:, 0, :5])  # Affiche les 5 premières dimensions du premier token