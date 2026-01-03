
import pandas as pd
from Document import Document,RedditDocument, ArxivDocument

from Author import Author
import re


# 3.1 (TD4)
class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.documents = {}
        self.authors = {}
        self.id_document = 0
    
    #SINGLETON 4.1 (TD5)
    # _instance = None

    # def __new__(cls, nom="Singleton"):
    #     if cls._instance is None:
    #         cls._instance = super(Corpus, cls).__new__(cls)
    #     return cls._instance

    # def __init__(self, nom="Singleton"):
    #     if not hasattr(self, "_initialized"):
    #         self.nom = nom
    #         self.documents = {}
    #         self.authors = {}
    #         self.id_document = 0
    #         self._initialized = True


    # 1.3 (TD4) / 2.3 (TD4)
    def add_doc(self, doc):
        self.id_document += 1
        self.documents[self.id_document] = doc
        # 2.3 (TD4) 
        if doc.auteur not in self.authors:
            self.authors[doc.auteur] = Author(doc.auteur)
        self.authors[doc.auteur].add(self.id_document, doc)

    # 3.2 (TD4) 
    def afficher_trie(self, critere="date"):
        if critere == "date":
            docs_trie = sorted(self.documents.values(), key=lambda d: d.date)
        elif critere == "titre":
            docs_trie = sorted(self.documents.values(), key=lambda d: d.titre.lower())
        else:
            docs_trie = list(self.documents.values())
        for doc in docs_trie:
            print(doc)

    # 3.2 (TD4)
    def __repr__(self):
        return f"Corpus '{self.nom}' : {len(self.documents)} documents, {len(self.authors)} auteurs"

    # 3.3 (TD4)
    def save(self, filename):
        data = [
            {"titre": doc.titre, "auteur": doc.auteur, "date": doc.date,
             "url": doc.url, "texte": doc.texte}
            for doc in self.documents.values()
        ]
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, sep=';')

    # 3.3 (TD4)
    def load(self, filename):
        df = pd.read_csv(filename, sep=';')
        for _, row in df.iterrows():
            doc = Document(
                row['titre'],
                row['auteur'],
                pd.to_datetime(row['date']).date(),
                row['url'],
                row['texte']
            )
            self.add_doc(doc)

#1.1 (TD6)
    def search(self, mot):
        results = []
        for doc_id, doc in self.documents.items():
            phrases = doc.texte.split(".")
            for phrase in phrases:
                if mot.lower() in phrase.lower(): 
                    results.append({
                        "Id": doc_id,
                        "Titre": doc.titre,
                        "Auteur": doc.auteur,
                        "Phrase": phrase.strip()
                    })
        if results:
            print(f"Passages avec le mot: '{mot}'")
            for r in results:
                print(f"{r['Phrase']}")
        else:
            print(f"Aucun passage trouvé pour le mot:'{mot}'")
        return results
    
 #1.2 (TD6)
 # ---------------------------------
 # Fait à l'aide de l'IA       
    def concorde(self, expression, contexte):

        lignes = []
        pattern = rf"(.{{0,{contexte}}})({re.escape(expression)})(.{{0,{contexte}}})"

        for doc_id, doc in self.documents.items():
            matches = re.findall(pattern, doc.texte, flags=re.IGNORECASE)
            for gauche, motif, droit in matches:
                lignes.append({
                    "Document": doc.titre,
                    "Contexte gauche": gauche.strip(),
                    "Motif trouvé": motif,
                    "Contexte droit": droit.strip()
                })

        # Création du tableau
        df = pd.DataFrame(lignes, columns=["Document", "Contexte gauche", "Motif trouvé", "Contexte droit"])

        # Affichage
        if not df.empty:
            print(f"Concordancier pour '{expression}' ({len(df)} occurrences):")
            print(df.to_string(index=False))
        else:
            print(f"Aucune occurrence trouvée pour '{expression}'.")

        return df
# ---------------------------------

#Partie 2 (TD6)
    def _nettoyer_texte(self, texte):
        texte = texte.lower()
        texte = texte.replace("\n", " ")
        texte = texte.replace("\r", " ")
        texte = re.sub(r"[\d]", " ", texte)
        texte = re.sub(r"[^\w\s]", " ", texte)
        return texte

    def stats(self, n=10):
        vocab = {}        # mot -> fréquence totale
        mot_dans_doc = {} # mot -> nb de documents contenant ce mot

        for doc in self.documents.values():
            texte_nettoye = self._nettoyer_texte(doc.texte)
            mots = texte_nettoye.split()

            for mot in mots:
                vocab[mot] = vocab.get(mot, 0) + 1

            mots_uniques = set(mots)
            for mot in mots_uniques:
                mot_dans_doc[mot] = mot_dans_doc.get(mot, 0) + 1

        mots_et_freqs = []
        for mot, freq in vocab.items():
            mots_et_freqs.append({
                "mot": mot,
                "frequence": freq,
                "nb_docs": mot_dans_doc.get(mot, 0)
            })

        df = pd.DataFrame(mots_et_freqs)
        df = df.sort_values(by="frequence", ascending=False)

        print("Nb de mots différents :", len(vocab))
        print("Mots les + fréquents :")
        print(df.head(n))
        return df





class factpattern:
    @staticmethod
    def create_document(doc_type, titre, auteur, date, url, texte, extra=None):
        if doc_type == "Reddit":
            return RedditDocument(titre, auteur, date, url, texte, extra)
        if doc_type == "Arxiv":
            return ArxivDocument(titre, auteur, date, url, texte, extra)
        assert 0, "Erreur :" + doc_type + " est inconnu"
