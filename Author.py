class Author:  
    def __init__(self, name):  # Q2.1(TD4)
        self.name = name  
        self.nb_docs = 0  
        self.production = {}  

    def add(self, doc_id, doc):  # Q2.2 (TD4)
        self.production[doc_id] = doc 
        self.nb_docs += 1 

    def __str__(self):  # Q2.2
        return f"{self.name} ({self.nb_docs} documents)" 

    def moyenne_mots(self):
        if self.nb_docs == 0:
            return 0
        total_mots = sum(len(doc.texte.split()) for doc in self.production.values())
        return total_mots / self.nb_docs