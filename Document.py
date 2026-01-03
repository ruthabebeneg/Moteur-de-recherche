# 1.1 (TD4)
class Document:
    def __init__(self, titre, auteur, date, url, texte, type=""):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.type = type   # 3.2 (TD5)

    # 1.1 (TD4)
    def get_doc(self):
        return self.titre, self.auteur, self.date, self.url, self.texte

    # 1.1 (TD4)
    def set_doc(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte

    # 1.1 (TD4)
    def get_author(self):
        return self.auteur

    # 1.2 (TD4)
    def afficher_infos_instance(self):
        print("Titre :", self.titre)
        print("Auteur :", self.auteur)
        print("Date de publication :", self.date)
        print("URL :", self.url)
        print("Texte :", self.texte)

    # 1.2 (TD4)
    def __str__(self):
        return self.titre


# 1.1 (TD5)
class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nb_commentaires):
        super().__init__(titre, auteur, date, url, texte, type="reddit")
        self.nb_commentaires = nb_commentaires

    # 1.1 (TD5)
    def get_nb_commentaires(self):
        return self.nb_commentaires

    # 1.1 (TD5)
    def set_nb_commentaires(self, nb_commentaires):
        self.nb_commentaires = nb_commentaires

    # 1.1 (TD5)
    def __str__(self):
        return f"Reddit : {self.titre} - {self.auteur} ({self.date}) | Commentaires : {self.nb_commentaires}"

    # 3.2 (TD5)
    def getType(self):
        return self.type


# 2.1 (TD5)
class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, co_auteurs):
        super().__init__(titre, auteur, date, url, texte, type="arxiv")
        self.co_auteurs = co_auteurs

    # 2.1 (TD5)
    def get_co_auteurs(self):
        return self.co_auteurs

    # 2.1 (TD5)
    def set_co_auteurs(self, co_auteurs):
        self.co_auteurs = co_auteurs

    # 2.1 (TD5)
    def __str__(self):
        return f"[Arxiv] {self.titre} - {self.auteur} ({self.date}) | Co-auteurs : {', '.join(self.co_auteurs)}"

    # 3.2 (TD5)
    def getType(self):
        return self.type
