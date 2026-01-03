import pandas as pd
from Document import Document, RedditDocument, ArxivDocument
from Author import Author


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

#4.1 (TD5)
class factpattern:
    @staticmethod
    def create_document(doc_type, titre, auteur, date, url, texte, extra=None):
        if doc_type == "Reddit":
            return RedditDocument(titre, auteur, date, url, texte, extra)
        if doc_type == "Arxiv":
            return ArxivDocument(titre, auteur, date, url, texte, extra)
        assert 0, "Erreur :" + doc_type + " est inconnu"

