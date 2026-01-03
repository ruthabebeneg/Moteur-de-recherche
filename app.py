import os
import datetime

import streamlit as st
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix

from Corpus import Corpus
from SearchEngine import SearchEngine


fichier = "corpus.csv"
corpus = Corpus("football")
if os.path.exists(fichier):
    corpus.load(fichier)

engine = SearchEngine(corpus)

st.title("Corpus football")

mode = st.sidebar.radio(
    "Mode",
    ("Recherche", "Comparaison de corpus", "Évolution temporelle"),
)

if mode == "Recherche":
    st.header("Recherche par mots-clés")
    query = st.text_input("Mots-clés")

    auteurs = ["Tous"] + sorted(corpus.authors.keys())
    auteur = st.selectbox("Auteur", auteurs)

    types_source = ["Tous", "Reddit", "Arxiv"]
    source = st.selectbox("Source", types_source)

    dates = [doc.date for doc in corpus.documents.values()]
    if dates:
        mindate, maxdate = min(dates), max(dates)
    else:
        mindate, maxdate = datetime.date(2016, 1, 1), datetime.date(2016, 12, 31)

    start, end = st.slider(
        "Période",
        min_value=mindate,
        max_value=maxdate,
        value=(mindate, maxdate),
    )

    nbdocs = st.slider("Nombre de documents à afficher", 1, 50, 10)

    if st.button("Rechercher") and query:
        df_res = engine.search(query, n=nbdocs) 

        if auteur != "Tous":
            df_res = df_res[df_res["auteur"] == auteur]
        if source != "Tous":
            if source == "Reddit":
                df_res = df_res[df_res["url"].str.contains("reddit", case=False, na=False)]
            elif source == "Arxiv":
                df_res = df_res[df_res["url"].str.contains("arxiv.org", case=False, na=False)]

        df_res = df_res[(df_res["date"] >= start) & (df_res["date"] <= end)]

        st.subheader("Résultats")
        if isinstance(df_res, pd.DataFrame) and not df_res.empty:
            st.dataframe(df_res[["score", "titre", "auteur", "date", "url"]])
        else:
            st.info("Aucun document trouvé, changez vos filtres ou vos mots-clés.")



elif mode == "Comparaison de corpus":
    st.header("Comparaison de deux sous-corpus (Reddit vs Arxiv)")

    choix_corpus = ["Reddit", "Arxiv"]
#-------------------------------------------
# fait à l'aide de l'IA
    corpusA = st.selectbox("Corpus A", choix_corpus, index=0)
    corpusB = st.selectbox("Corpus B", choix_corpus, index=1)

    nbmots = st.slider("Nombre de mots à afficher par corpus", 5, 50, 20)

    if st.button("Comparer"):
        st.write("Calcul des scores TF-IDF par sous-corpus…")

        def compute_tfidf_for_type(corpustype: str) -> pd.DataFrame:
            indices = []
            for i, doc in enumerate(engine.docs_list):
                url = (doc.url or "").lower()
                if corpustype == "Reddit" and "reddit" in url:
                    indices.append(i)
                elif corpustype == "Arxiv" and "arxiv.org" in url:
                    indices.append(i)

            if not indices:
                return pd.DataFrame(columns=["mot", "score"]).set_index("mot")

            mat = engine.mat_TFxIDF
            if not isinstance(mat, csr_matrix):
                mat = mat.tocsr()

            sub = mat[indices, :]
            scores = np.array(sub.mean(axis=0)).ravel()

            inv_vocab = {info["id"]: mot for mot, info in engine.vocab.items()}
            data = []
            for col_id, mot in inv_vocab.items():
                data.append({"mot": mot, "score": float(scores[col_id])})

            df = pd.DataFrame(data).set_index("mot")
            df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0.0)
            return df

        tfidfA = compute_tfidf_for_type(corpusA)
        tfidfB = compute_tfidf_for_type(corpusB)

        tfidfA["score"] = pd.to_numeric(tfidfA["score"], errors="coerce").fillna(0.0)
        tfidfB["score"] = pd.to_numeric(tfidfB["score"], errors="coerce").fillna(0.0)

        dfA = tfidfA.nlargest(nbmots, "score").copy()
        dfB = tfidfB.nlargest(nbmots, "score").copy()

        st.subheader(f"Mots les plus spécifiques à {corpusA}")
        st.dataframe(dfA[["score"]])

        st.subheader(f"Mots les plus spécifiques à {corpusB}")
        st.dataframe(dfB[["score"]])

        communs = tfidfA.join(tfidfB, how="inner", lsuffix="A", rsuffix="B")
        communs["scoreA"] = pd.to_numeric(communs["scoreA"], errors="coerce").fillna(0.0)
        communs["scoreB"] = pd.to_numeric(communs["scoreB"], errors="coerce").fillna(0.0)

        communs = communs.nlargest(nbmots, "scoreA")[["scoreA", "scoreB"]]
        communs = communs.reset_index().rename(columns={"index": "mot"})

        st.subheader("Mots communs (scores TF-IDF)")
        st.dataframe(communs)

#-----------------------------------------------------------------------
elif mode == "Évolution temporelle":
    st.header("Évolution d’un mot dans le temps")
    mot = st.text_input("Mot à suivre")
    unite = st.selectbox("Granularité :", ["Année", "Mois"])

    if st.button("Afficher") and mot:
        mott = corpus._nettoyer_texte(mot).strip()
        if mott not in engine.vocab:
            st.info("Mot absent du vocabulaire.")
        else:
            j = engine.vocab[mott]["id"]

            mat_tf = engine.mat_TF
            mat_tfidf = engine.mat_TFxIDF
            if not isinstance(mat_tf, csr_matrix):
                mat_tf = mat_tf.tocsr()
            if not isinstance(mat_tfidf, csr_matrix):
                mat_tfidf = mat_tfidf.tocsr()

            lignes = []
            for i, doc in enumerate(engine.docs_list):
                if unite == "Année":
                    periode = doc.date.year
                else:
                    periode = f"{doc.date.year}-{doc.date.month:02d}"

                freq = float(mat_tf[i, j])
                importance = float(mat_tfidf[i, j])

                lignes.append({
                    "periode": periode,
                    "frequence": freq,
                    "importance": importance
                })

            df = pd.DataFrame(lignes)
            if df.empty:
                st.info("Aucune occurrence trouvée pour ce mot.")
            else:
                serie = (
                    df.groupby("periode")
                      .agg({"frequence": "sum", "importance": "sum"})
                      .reset_index()
                      .sort_values("periode")
                )

                st.subheader(f"Rareté du mot : {mot} »dans le temps")
                st.line_chart(serie.set_index("periode")["importance"])
                st.subheader(f"Fréquence du mot :{mot} ")
                st.line_chart(serie.set_index("periode")["frequence"])
                st.dataframe(serie)
