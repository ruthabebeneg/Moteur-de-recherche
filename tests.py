import datetime
import os
import tempfile

import pandas as pd
import numpy as np

from Document import Document, RedditDocument, ArxivDocument
from Author import Author
from Corpus import Corpus, factpattern
from SearchEngine import SearchEngine


def test_document_get_set():
    d = datetime.date(2024, 1, 1)
    doc = Document("Titre", "Auteur", d, "http://test.com", "texte", "Arxiv")
    assert doc.get_doc() == ("Titre", "Auteur", d, "http://test.com", "texte")
    d2 = datetime.date(2024, 2, 1)
    doc.set_doc("Nouveau", "Nouvel", d2, "http://autre.com", "nouveau texte")
    assert doc.get_doc() == ("Nouveau", "Nouvel", d2, "http://autre.com", "nouveau texte")
    assert str(doc) == "Nouveau"


def test_document_reddit():
    d = datetime.date(2024, 1, 1)
    doc = RedditDocument("Post", "User", d, "http://reddit.com", "contenu", 10)
    assert doc.get_nb_commentaires() == 10
    doc.set_nb_commentaires(20)
    assert doc.get_nb_commentaires() == 20
    assert doc.getType() == "reddit"


def test_document_arxiv():
    d = datetime.date(2024, 1, 1)
    doc = ArxivDocument("Article", "Auteur", d, "http://arxiv.org", "texte", ["a1", "a2"])
    assert doc.get_co_auteurs() == ["a1", "a2"]
    doc.set_co_auteurs(["a3"])
    assert doc.get_co_auteurs() == ["a3"]
    assert doc.getType() == "arxiv"


def test_author_moyenne_mots():
    auteur = Author("Auteur OL")
    d = datetime.date(2024, 1, 1)
    assert auteur.nb_docs == 0
    assert auteur.moyenne_mots() == 0
    doc1 = Document("M1", "Auteur OL", d, "u1", "allez l ol", "Reddit")   
    doc2 = Document("M2", "Auteur OL", d, "u2", "on gagne", "Reddit")  
    auteur.add(0, doc1)
    auteur.add(1, doc2)
    assert auteur.nb_docs == 2
    assert auteur.moyenne_mots() == 2.5


def test_corpus_add_doc_et_authors():
    corpus = Corpus("football")
    d = datetime.date(2024, 1, 1)
    doc1 = Document("Match 1", "Auteur1", d, "u1", "texte1", "Reddit")
    doc2 = Document("Match 2", "Auteur2", d, "u2", "texte2", "Reddit")
    corpus.add_doc(doc1)
    corpus.add_doc(doc2)
    assert len(corpus.documents) == 2
    assert "Auteur1" in corpus.authors
    assert "Auteur2" in corpus.authors
    assert corpus.authors["Auteur1"].nb_docs == 1
    assert corpus.authors["Auteur2"].nb_docs == 1


def test_corpus_save_load():
    corpus = Corpus("football")
    d = datetime.date(2024, 1, 1)
    corpus.add_doc(Document("M1", "A1", d, "u1", "t1", "Reddit"))
    corpus.add_doc(Document("M2", "A2", d, "u2", "t2", "Arxiv"))
    with tempfile.TemporaryDirectory() as tmp:
        chemin = os.path.join(tmp, "corpus.csv")
        corpus.save(chemin)
        df = pd.read_csv(chemin, sep=";")
        assert len(df) == 2
        corpus_charge = Corpus("chargé")
        corpus_charge.load(chemin)
        assert len(corpus_charge.documents) == 2
        titres = [doc.titre for doc in corpus_charge.documents.values()]
        assert "M1" in titres
        assert "M2" in titres


def test_corpus_search_trouve():
    corpus = Corpus("test")
    d = datetime.date(2024, 1, 1)
    doc1 = Document("Doc1", "A", d, "u1", "le football", "Reddit")
    doc2 = Document("Doc2", "B", d, "u2", "european league", "Arxiv")
    corpus.add_doc(doc1)
    corpus.add_doc(doc2)
    res = corpus.search("football")
    assert len(res) == 1
    assert res[0]["Titre"] == "Doc1"


def test_corpus_search_aucun():
    corpus = Corpus("test")
    d = datetime.date(2024, 1, 1)
    corpus.add_doc(Document("Doc1", "A", d, "u1", "aucun mot spécial ici.", "Reddit"))
    res = corpus.search("inexistant")
    assert res == []


def test_corpus_concorde():
    corpus = Corpus("test")
    d = datetime.date(2024, 1, 1)
    texte = "Le football est là. Encore du football dans le texte."
    corpus.add_doc(Document("Doc1", "A", d, "u1", texte, "Reddit"))
    df = corpus.concorde("football", 10)
    assert len(df) >= 2
    assert "Doc1" in set(df["Document"])


def test_corpus_stats():
    corpus = Corpus("test")
    d = datetime.date(2024, 1, 1)
    corpus.add_doc(Document("D1", "A", d, "u1", "coach", "Reddit"))
    corpus.add_doc(Document("D2", "B", d, "u2", "ronaldo", "Arxiv"))
    df = corpus.stats(n=2)
    mots = set(df["mot"])
    assert "coach" in mots
    assert "ronaldo" in mots


#fait à l'aide de l'IA
def test_factpattern_create_document():
    d = datetime.date(2024, 1, 1)
    doc_reddit = factpattern.create_document("Reddit", "T", "A", d, "u", "t", 5)
    assert isinstance(doc_reddit, RedditDocument)
    assert doc_reddit.get_nb_commentaires() == 5
    doc_arxiv = factpattern.create_document("Arxiv", "T2", "A2", d, "u2", "t2", ["C1"])
    assert isinstance(doc_arxiv, ArxivDocument)
    assert doc_arxiv.get_co_auteurs() == ["C1"]


def test_factpattern_type_inconnu():
    d = datetime.date(2024, 1, 1)
    try:
        factpattern.create_document("Inconnu", "T", "A", d, "u", "t")
        assert False
    except AssertionError:
        pass

def construire_corpus_search():
    corpus = Corpus("search")
    d = datetime.date(2024, 1, 1)
    corpus.add_doc(Document("Doc1", "A", d, "u1", "football lyon", "Reddit"))
    corpus.add_doc(Document("Doc2", "B", d, "u2", "paris", "Reddit"))
    corpus.add_doc(Document("Doc3", "C", d, "u3", "football marseille", "Reddit"))
    return corpus

#fait à l'aide de l'IA
def test_searchengine_vocab_et_tf():
    corpus = construire_corpus_search()
    moteur_recherche = SearchEngine(corpus)
    assert "football" in moteur_recherche.vocab
    assert "lyon" in moteur_recherche.vocab
    assert moteur_recherche.mat_TF.shape[0] == len(moteur_recherche.docs_list)
    assert moteur_recherche.mat_TF.shape[1] == len(moteur_recherche.vocab)


def test_searchengine_vecteur():
    corpus = construire_corpus_search()
    moteur_recherche = SearchEngine(corpus)
    vect = moteur_recherche.vecteur("lyon")
    assert vect[moteur_recherche.vocab["lyon"]["id"]] >= 1

#fait à l'aide de l'IA
def test_searchengine_calcul_similarite():
    corpus = construire_corpus_search()
    moteur_recherche = SearchEngine(corpus)
    vect = moteur_recherche.vecteur("football")
    mat = moteur_recherche.mat_TFxIDF
    sims = moteur_recherche.calcul_similarite(vect, mat)
    assert sims[0] > 0      
    assert sims[2] > 0    
    assert sims[1] == 0     

#fait à l'aide de l'IA
def test_searchengine_forme_resultats_simplifiee():
    corpus = construire_corpus_search()
    moteur_recherche = SearchEngine(corpus)
    requete = "football"
    vect = moteur_recherche.vecteur(requete)
    mat = moteur_recherche.mat_TFxIDF.tocsr()
    scores = moteur_recherche.calcul_similarite(vect, mat)
    indices = np.argsort(scores)[::-1]
    resultats = []
    for i in indices[:2]:
        if scores[i] > 0:
            doc = moteur_recherche.docs_list[i]
            resultats.append({
                "score": float(scores[i]),
                "titre": doc.titre,
                "auteur": doc.auteur,
                "date": doc.date,
                "url": doc.url,
                "texte": doc.texte,
            })

    df = pd.DataFrame(resultats)
    assert isinstance(df, pd.DataFrame)
    assert set(["score", "titre", "auteur", "date", "url", "texte"]).issubset(df.columns)
