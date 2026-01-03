import praw               
import datetime         
import pandas as pd       
import urllib             
import ssl               
import xmltodict         
import certifi            
import numpy as np        

from Document import Document, RedditDocument, ArxivDocument  
from Author import Author                                     
from Corpus import Corpus       
from SearchEngine import SearchEngine                               


# 3.1 (TD4) – Création du corpus
Corpus_football = Corpus("football")


# 1.1 (TD3) : Reddit
# reddit = praw.Reddit(  
#     client_id='81OhpI-26eVNBGkhlKwnuA',
#     client_secret='Sb6DhRXXcR7D3YwoQDukpa3dHym_LQ',
#     user_agent='ruru'
# )

# ml_subreddit = reddit.subreddit('football')

# for post in ml_subreddit.hot(limit=50):
#     text = post.selftext.replace("\n", " ").replace("\r", " ")   # champ texte = selftext
#     title = post.title.replace("\n", " ").replace("\r", " ")   
#     url = post.url.replace("href", "")                         
#     if text != "":
#         docs = Document(  # 1.3 (TD4)
#             title,
#             str(post.author),
#             datetime.datetime.fromtimestamp(post.created_utc).date(),
#             url,
#             text
#         )
#         Corpus_football.add_doc(docs)


# 1.2 (TD3): Arxiv
# query = "football"
# url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=300'  # 1.2 (TD3)

# context = ssl.create_default_context(cafile=certifi.where())  
# url_read = urllib.request.urlopen(url, context=context).read()  
# data = url_read.decode()  
# datparsed = xmltodict.parse(data)  #

# entries = datparsed['feed']['entry'] 

# for e in entries[:50]:
#     summary = e.get("summary", "").strip().replace("\n", " ")   # champ texte = summary
#     title = e.get('title', '').strip().replace("\n", " ")       
#     title = title.replace("/r/", " ")                        
#     author_info = e.get('author', "")                           
#     url = e.get('id', '')                                    

#     if isinstance(author_info, list):
#         author_name = ", ".join([a.get('name', 'Inconnu') for a in author_info])  
#     elif isinstance(author_info, dict):
#         author_name = author_info.get('name', 'Inconnu')                           
#     else:
#         author_name = str(author_info)                                            

#     if summary != "":
#         docs = Document(                                                          # 1.3 (TD4)
#             title,
#             author_name,
#             datetime.datetime.strptime(e.get('published', ''), "%Y-%m-%dT%H:%M:%SZ").date(),
#             url,
#             summary
#         )
#         Corpus_football.add_doc(docs)


# 2.1 (TD3)
# ids = []          
# origines = []    
# texts = []  
# df_sans_err = []


# for i, (doc_id, doc) in enumerate(Corpus_football.documents.items(), start=1):
#     ids.append(i)
#     texts.append(doc.texte)
#     print(doc.url)
#     if "reddit" in doc.url.lower():
#         origines.append("reddit")     
#     elif "arxiv" in doc.url.lower():
#         origines.append("arxiv")      
#     else:
#         continue # pour éviter les erreurs sur des nombres de lignes qui diffèrent car le type n'a pas été trouvé dans l'url
#     df_sans_err.append({
#         "Id": i,
#         "Origine": origines,
#         "Text": doc.texte
#     })

# print("Nombre de lignes dans data_rows :", len(df_sans_err))

# df = pd.DataFrame(df_sans_err)  


# 2.2 (TD3)
# df.to_csv("docs.csv", index=False)     

# 2.3 (TD3) 
documents = pd.read_csv("docs.csv")    


# 3.1 à 3.4 (TD3)
textes = []   
mots = []    
phrases = []  

# 3.3 (TD3)
# -------------------------------
#fait à l'aide d'IA 
for i in range(len(documents)):
    if len(documents.loc[i, "Text"]) < 100:
        documents.drop(index=i, inplace=True)  

documents.reset_index(drop=True, inplace=True)  
# -------------------------------
Corpus_football.load("corpus.csv")  # 3.3 (TD4)

for i in range(len(documents)):        
    mots.append(len(documents.loc[i, "Text"].split(" ")))    
    phrases.append(len(documents.loc[i, "Text"].split("."))) 
    print("Nombre de mots à l'id :", documents.loc[i, "Id"], " = ",
          len(documents.loc[i, "Text"].split(" ")))         
    print("Nombre de phrases à l'id :", documents.loc[i, "Id"], " = ",
          len(documents.loc[i, "Text"].split(".")))          
    textes.append(documents.loc[i, "Text"])                  

texteslies = " ".join(textes)                                
# print(texteslies)                                            
print("Nombre de mots en moyenne :", np.mean(mots))          
print("Nombre total de phrasesc:", np.sum(phrases))        

#Tests (TD3)
# 2.3–2.4 (TD4) – Tests sur les auteurs
print("Auteurs dispos")
for nom, auteur in Corpus_football.authors.items():
    print(auteur) 

# 2.4 (TD4) stats pour le premier auteur
liste_auteurs = list(Corpus_football.authors.keys())
if liste_auteurs:
    nom_test = liste_auteurs[0]
    auteur_test = Corpus_football.authors[nom_test]
    print("=== Détails pour l'auteur :", nom_test, "===")
    print("Nb de documents :", auteur_test.nb_docs)
    print("Nb moyen de mots :", auteur_test.moyenne_mots())


# Tests (TD4) 
print("Info corpus")
print(Corpus_football)

print("Docs triés par date")
Corpus_football.afficher_trie("date")

print("Docs triés par titre")
Corpus_football.afficher_trie("titre")

# 3.3 (TD4)  Test sauvegarde & chargement du corpus
Corpus_football.save("corpus.csv")
print("Corpus sauvegardé dans corpus.csv")

Corpus_charge = Corpus("football_charge")
Corpus_charge.load("corpus.csv")
print("Corpus chargé avec corpus.csv")
print(Corpus_charge)


# Tests(TD5) 
reddit_doc = RedditDocument(
    "OL gagnants",
    "FanOL",
    datetime.date.today(),
    "https://reddit.com/r/football/ol",
    "Victoire écrasante",
    nb_commentaires=120
)
Corpus_football.add_doc(reddit_doc)

arxiv_doc= ArxivDocument(
    "Analyse tactique de l'OL",
    "Chercheur",
    datetime.date.today(),
    "https://arxiv.org/abs/1234.5678",
    "Top 5 des meilleurs tactiques.",
    co_auteurs=["Alexandre", "Memphis"]
)
Corpus_football.add_doc(arxiv_doc)

print("Affichage du doc :", reddit_doc)
print("Type du document :", reddit_doc.getType())
print("Affichage du doc :", arxiv_doc)
print("Type du document :", arxiv_doc.getType())


# Tests (TD6)
print("Stats (TD6)")
Corpus_football.stats(12)  

# Tests (TD7):
moteur = SearchEngine(Corpus_football)
print("Recheche du mot won :")
resultats = moteur.search("won", 5)
print(resultats[["score", "titre", "auteur"]])

print("Recheche du mot match :")
resultats_match = moteur.search("match", 15)
print(resultats_match[["score", "titre", "auteur"]])
