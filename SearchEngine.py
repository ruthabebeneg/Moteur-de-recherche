import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from Corpus import Corpus
from tqdm.auto import tqdm

class SearchEngine:
    def __init__(self, corpus: Corpus):  # 1.1 (TD7)
        self.corpus = corpus
        self.docs_list = list(self.corpus.documents.values())
        self.vocab = {}
        self.mat_TF = None
        self.mat_TFxIDF = None

        self.dic_vocab()
        self.matrice_TF()
        self.statistiques()
        self.matrice_TFxIDF()

    def dic_vocab(self):
        vocab = {}
        id_mot = 0

        for doc in self.docs_list:
            texte = self.corpus._nettoyer_texte(doc.texte)
            mots = texte.split()
            for m in mots:
                if m not in vocab:
                    vocab[m] = {"id": id_mot, "tf": 0, "df": 0}
                    id_mot += 1

        vocab = dict(sorted(vocab.items(), key=lambda x: x[0]))
        self.vocab = vocab

    # 1.2 (TD7)
    #------------------------------------
    #fait à l'aide d'IA
    def matrice_TF(self):
        rows, cols, data = [], [], []

        for i, doc in enumerate(self.docs_list):
            texte = self.corpus._nettoyer_texte(doc.texte)
            mots = texte.split()

            dic_nb_mots = {}
            for m in mots:
                info = self.vocab.get(m)
                if info is None:
                    continue
                j = info["id"]
                dic_nb_mots[j] = dic_nb_mots.get(j, 0) + 1

            for j, c in dic_nb_mots.items():
                rows.append(i)
                cols.append(j)
                data.append(c)

        nb_docs = len(self.docs_list)
        nb_mots = len(self.vocab)
        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(nb_docs, nb_mots))
    
    #------------------------------------

    # 1.3 (TD7)
    def statistiques(self):
        somme_valeurs = np.array(self.mat_TF.sum(axis=0)).ravel()
        nb_de_docs = np.array((self.mat_TF > 0).sum(axis=0)).ravel()
        inv_vocab = {info["id"]: mot for mot, info in self.vocab.items()}

        for col_id, mot in inv_vocab.items():
            self.vocab[mot]["tf"] = int(somme_valeurs[col_id])
            self.vocab[mot]["df"] = int(nb_de_docs[col_id])

    # 1.4 (TD7)
    def matrice_TFxIDF(self):
        nb_docs = self.mat_TF.shape[0]
        df_cols = (self.mat_TF > 0).sum(axis=0)
        df_cols = np.array(df_cols).ravel()

        # idf
        rarete = np.log((nb_docs + 1) / (df_cols + 1))
        self.mat_TFxIDF = self.mat_TF.multiply(rarete)

    # 2.1 (TD7)
    def vecteur(self, requete: str):
        vect = np.zeros(len(self.vocab))
        texte = self.corpus._nettoyer_texte(requete)
        mots = texte.split()

        for mot in mots:
            if mot in self.vocab:
                i = self.vocab[mot]["id"]
                vect[i] += 1
        return vect

    # 2.2 (TD7)
    #------------------------------------
    #fait à l'aide d'IA

        # 2.2 (TD7)
    def calcul_similarite(self, vecteur_requete, mat):
        # mat : matrice (TF ou TFxIDF) de taille (nb_docs, nb_mots)
        numerateur = mat.dot(vecteur_requete)  # shape = (nb_docs,)

        # norme requête
        n_q = np.linalg.norm(vecteur_requete)
        if n_q == 0:
            return np.zeros(mat.shape[0])

        # normes docs
        tailles = np.sqrt(mat.multiply(mat).sum(axis=1))
        tailles = np.asarray(tailles).ravel()
        tailles[tailles == 0] = 1e-10

        return (numerateur / (tailles * n_q)).ravel()
    #------------------------------------

    # 2.3 (TD7)
    def search(self, requete, n):
        vect = self.vecteur(requete)
        matrice = self.mat_TFxIDF.tocsr()
        scores = self.calcul_similarite(vect, matrice)
        indices = np.argsort(scores)[::-1]
        res = []
        for i in tqdm(indices[:n], total=min(n, len(indices)), desc="Résultts en cours"):
            if scores[i] > 0:
                doc = self.docs_list[i]
                res.append({
                    "score": float(scores[i]),
                    "titre": doc.titre,
                    "auteur": doc.auteur,
                    "date": doc.date,
                    "url": doc.url,
                    "texte": doc.texte
                })

        return pd.DataFrame(res)

