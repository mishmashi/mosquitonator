import streamlit as st
import pandas as pd
import numpy as np
import os
from LLM2vecSA import get_feature_vector_SA

# Initialize session state
if "index" not in st.session_state:
    database = []
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.c_prev = database
    st.session_state.species_initialized = False
    st.session_state.prior = []
    st.session_state.u_inp = ""
    st.session_state.clicked_back = False
    st.session_state.answered = []

def filter_candidates(index, ans, candidates):
    if ans == 1:
        return [c for c in candidates if c.get(index, -1) != 0]
    elif ans == 0:
        return [c for c in candidates if c.get(index, -1) != 1]
    else:
        return candidates

st.header("Species Identification")

@st.cache_data(ttl=600)  # for optimization
def load_data():
    import pandas as pd
    df = pd.read_csv("Colombia.csv", header=2)
    questions = [col for col in df.columns if col not in ("Species")]

    database = []
    for _, row in df.iterrows():
        entry = {"name": row["Species"]}
        for i, q in enumerate(questions):
            if pd.notna(row[q]) and row[q] != "":
                entry[i] = int(row[q])
        database.append(entry)

    return questions, database

# ---- Load questions and database ----
questions, database = load_data()
others = [
    "nimbus", "thomasi", "acanthotorynus", "kompi", "canorii", "lepidotus", "pholidotus", "boliviensis", "gonzalezrinconesi", "rollai", 
    "bambusicolus", "auyantepuiensis", "bellator", "laneanus", "cruzii", "homunculus", "squamifemur", "eiseni eiseni", "eiseni geometricus",
    "peryassui", "vestitipennis", "mattogrossensis", "minor", "shannoni", "guarao", "punctimacula", "mediopunctatus", "costai", "forattinii", 
    "fluminensis", "malefactor", "neomaculipalpus", "anchietai", "maculipes", "pseudomaculipes", "bustamentei", "apicimacula", "medialis", "rachoui",
    "evandroi", "tibiamaculatus", "gilesi", "pseudotibiamaculatus", "vargasi", "oiketorakras", "gomezdelatorrei", "annulipalpis", "halophylus", "triannulatus", "triannulatus C", 
    "rondoni", "ininii", "oswaldoi", "konderi", "rangeli", "aquasalis", "galvaoi", "dunhami", "trinkae", "goeldii", "evansae", "strodei", "nigritarsis", "lutzii",
    "guarani", "parvus", "antunesi", "pristinus", "pictipennis", "atacamensis", "lanei", "sawyeri", "argyritarsis", "braziliensis", "marajoara", "janconnae", "oryzalimnetes",
    "deaneorum", "albitarsis"
]

# ---- Session Initialization ----
if st.session_state.species_initialized == False:
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.others = []
    st.session_state.species_initialized = True

st.title("Anopheles Species Identifier")

if st.session_state.index == 0:
    st.session_state.candidates = database  # Reset candidates before applying prior
    st.session_state.others = []
    if st.session_state.prior:
        for idx, el in enumerate(st.session_state.prior):
            if el in [0, 1]:
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.candidates = filter_candidates(idx, el, st.session_state.candidates)

# ---- Starting with Prior Text ----
nl_input = st.text_area("(Optional) Start with prior:", key="prior_text_input", placeholder="Describe the mosquito in detail...")

if st.button("Submit Prior", use_container_width=True):
    st.session_state.u_inp = nl_input
    prior = get_feature_vector_SA(nl_input)
    prior_list = [int(p) if p.isdigit() else None for p in prior.split(",")]
    st.session_state.prior = prior_list
    st.session_state.c_prev = st.session_state.candidates
    st.session_state.candidates = database  # Reset candidates before applying prior
    for idx, el in enumerate(st.session_state.prior):
        if el in [0, 1]:
            st.session_state.candidates = filter_candidates(idx, el, st.session_state.candidates)
    st.rerun()

_, mid, _ = st.columns(3)
mid.write(f"**Remaining candidates:** {len(st.session_state.candidates)}")

if not st.session_state.clicked_back:
    while st.session_state.index < len(questions):
        values = {c.get(st.session_state.index, -1) for c in st.session_state.candidates}
        num_with_values = sum(1 for c in st.session_state.candidates if st.session_state.index in c)

        # Skip if all remaining candidates have the same value, or only one has data
        if len(values) <= 1 or num_with_values <= 1:
            st.session_state.index += 1
            continue

        # Skip if prior already answered this
        if (st.session_state.prior and 
            st.session_state.index < len(st.session_state.prior) and 
            st.session_state.prior[st.session_state.index] in [0, 1]):
            st.session_state.index += 1
            continue
        break
else:
    st.session_state.clicked_back = False

if st.session_state.index < len(questions):
    q = questions[st.session_state.index]
    st.write(f"**Q{st.session_state.index + 1}: {q}**")

    col1, col2, col3 = st.columns(3)

    if col1.button("Yes", key=f"y_sp_{st.session_state.index}", use_container_width=True):
        if st.session_state.index < len(others):
            st.session_state.others = others  # get group of other, less relevant species
        st.session_state.c_prev = st.session_state.candidates
        st.session_state.candidates = filter_candidates(st.session_state.index, 1, st.session_state.candidates)
        st.session_state.answered.append(st.session_state.index)
        st.session_state.index += 1
        st.rerun()

    if col3.button("No", key=f"n_sp_{st.session_state.index}", use_container_width=True):
        st.session_state.c_prev = st.session_state.candidates
        st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
        st.session_state.answered.append(st.session_state.index)
        st.session_state.index += 1
        st.rerun()

    if col2.button("I don't know", key=f"idk_sp_{st.session_state.index}", use_container_width=True):
        st.session_state.c_prev = st.session_state.candidates
        st.session_state.candidates = filter_candidates(st.session_state.index, None, st.session_state.candidates)
        st.session_state.answered.append(st.session_state.index)
        st.session_state.index += 1
        st.rerun()

else:
    if len(st.session_state.candidates) == 1:
        st.success(f"The specimen is an **Anopheles {st.session_state.candidates[0]['name']}**")
    elif len(st.session_state.candidates) > 1:
        if not np.isnan(st.session_state.candidates[0]):
            st.warning(f"index: {st.session_state.index}, Possible species:")
            for c in st.session_state.candidates:
                st.write(f"- **Anopheles {c['name']}**")
    else:
        st.error("No matching vectors.")

    if st.session_state.others:
        st.warning("Other possible species:")
        for name in st.session_state.others:
            st.write(f"- **Anopheles {name}**")

    bn1, bn2, bn3 = st.columns(3)

    if bn2.button("Back to genus", key="restart_all", use_container_width=True):
        st.session_state.index = 0
        st.session_state.candidates = []
        st.session_state.species_initialized = False
        st.session_state.prior = []
        st.rerun()

    if st.session_state.index > 0:
        if bn1.button("Previous question", key="prev_spec", use_container_width=True) and st.session_state.answered:
            st.session_state.index = st.session_state.answered.pop()
            st.session_state.candidates = st.session_state.c_prev
            st.session_state.clicked_back = True
            st.rerun()

    if bn3.button("Restart", key="restart_sp", use_container_width=True):
        st.session_state.index = 0
        st.session_state.candidates = database
        st.session_state.species_initialized = False
        st.session_state.prior = []
        st.rerun()
