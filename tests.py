import datetime
import os
import tempfile
import pandas as pd
import numpy as np

from Document import Document, RedditDocument, ArxivDocument
from Author import Author
from Corpus import Corpus, factpattern


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