import streamlit as st
import pandas as pd
import os
import numpy as np
import csv
from io import StringIO
from LLM2vec import get_feature_vector
from nb import build_masked_nb
from dbn_model import build_dbn

@st.cache_resource
def load_dbn():
    model, inference, features = build_dbn("linked_ds.csv")
    return model, inference, features

@st.cache_resource
def load_nb():
    return build_masked_nb()

# Initialize session state
if "index" not in st.session_state:
    database = []
    st.session_state.index = 0
    st.session_state.candidates = database.copy()
    st.session_state.eliminated = []
    st.session_state.ranking_candidates = database.copy()
    st.session_state.c_prev = database
    st.session_state.species_initialized = False
    st.session_state.o_prev = []
    st.session_state.prior = []
    st.session_state.u_inp = ""
    st.session_state.clicked_back = False
    st.session_state.answered = []
    st.session_state.just_el = []
    st.session_state.threshold = 0.4
    st.session_state.evidence = {}

def infer_species_probs(model, evidence):
    """
    evidence: dict[int_feature_index -> value]
    """
    features = model["features"]
    species = model["species"]
    prior = model["prior"]
    likelihood = model["likelihood"]

    log_probs = {}

    for sp in species:
        logp = np.log(prior.get(sp, 1e-12))

        for idx, val in evidence.items():
            f = features[int(idx)]

            if f not in likelihood[sp]:
                continue
            p = likelihood[sp][f].get(val, 1e-6)
            logp += np.log(p)

        log_probs[sp] = logp

    max_log = max(log_probs.values())
    probs = {
        sp: np.exp(lp - max_log)
        for sp, lp in log_probs.items()
    }

    Z = sum(probs.values())
    return {sp: p / Z for sp, p in probs.items()}

def update_probabilities(ans, index, candidates, thresh, factor=.25):
  just_el = []
  if ans is None:
    return candidates, just_el
  for i, candidate in enumerate(candidates):
    c_ans = candidate.get(index, np.nan)
    if pd.isna(c_ans) or ans == c_ans:
      just_el.append(0)
      if ans == c_ans and not pd.isna(c_ans) and c_ans != -1:  
        candidate["prob"] = candidate["prob"]*1.1
    elif ans != c_ans and c_ans != -1:
      candidate["prob"] = candidate["prob"]*factor
      if candidate["prob"] < thresh:
        candidate["considered"] = 0
        just_el.append(1) #add index of candidate that was eliated to list, to be used by filter_candidates
      else:
          just_el.append(0)
      
  max_prob = max(c["prob"] for c in candidates)
  if max_prob >.9:
      for i, candidate in enumerate(candidates):
          candidate["prob"] = candidate["prob"]/max_prob
  return candidates, just_el
      
def filter_candidates(candidates, just_el):
        candidates = [c for c, keep in zip(candidates, just_el) if keep == 0]
        return candidates 

def sanitize_evidence(evidence):
    clean = {}
    for idx, val in evidence.items():
        try:
            v = int(val)
        except (TypeError, ValueError):
            continue
        if v in [0,1,2,3]:
            clean[idx] = v
    return clean

 
st.header("Species Identification")
@st.cache_data(ttl=6) #for optimization
def load_data():
        df = pd.read_csv("linked_ds.csv", header=0)
        questions = [col for col in df.columns if col not in ("Species", "Considered", "Probability", "Region", "Image")]

        database = []
        for _, row in df.iterrows():
            entry = {"name": row["Species"], "prob": row["Probability"], "considered": row["Considered"], "image": row["Image"], "region": row["Region"]}
            for i, q in enumerate(questions):
                val = row[q]
                if pd.notna(val):
                    v = pd.to_numeric(val, errors="coerce")
                    if not pd.isna(v):
                        entry[i] = int(v)

            database.append(entry)

        return questions, database

# ---- Load questions and database ----
questions, database = load_data()

index_to_feature = {i: f for i, f in enumerate(questions)}
feature_to_index = {f: i for i, f in index_to_feature.items()}

qbs = StringIO(',,,,,Wing without a pale spot on basal 0.5 of costa,Maxillary palpus with apex pale,Maxillary palpus with less than 4 pale bands ,3rd main dark area without pale interruption,Wing with I pale spot on upper branch of vein 5,"Wing with abundant pale areas, costa with at least 4 pale spots","Hindtarsomeres 1 to 4, at least, with apical pale bands",Hindtarsomeres 1 and 2 with pale bands at apices only,,"Very large species, abdoal segments II–VII with long lateral tufts of yellowish and dark scales; hindtarsomere 1 largely dark",No pale fringe spot opposite lower branch of vein 5,Hindtarsomere 5 all dark and 4 with much less than apical 0.5 pale,Small to moderate-sized species (wing length 2.7–4.5 mm); wing with upper branch of vein 2 either entirely dark apart from apex or with a few scattered pale scales only,Legs not speckled,Hindtarsomere 3 dark at base,"Maxillary palpus with 4 pale bands, unspeckled; vein 1 of wing with at most 1 pale spot in 2nd main dark area","Midtarsomeres 2 to 4 with pale apices; vein 1 of wing pale at base, basal 0.5 of stem of vein 4 entirely pale",Hindtarsomere 1 narrowly pale or dark at apex; vein 1 of wing with 1 pale spot in 2nd main dark area,Foretarsomere 1 with 2–4 pale rings; stem of vein 4 of wing largely dark,Fore- and midtarsomeres 2 and 3 dark apically; no fringe spot opposite vein 6,"Maxillary palpus smooth with 3 pale bands, the 2 distal ones broad or rarely fused",Maxillary palpus without pale bands; no pale spot at apex of hindtibia or base of hindtarsomere 1,Hindtarsomere 3 dark at base,Base of hindtarsomere 1 broadly pale; no pale fringe spot opposite lower branch of wing vein 5,"Hind tarsomere 1 broadly pale at base, pale area at least as long as broad","Pale streak on hindtibia 1–3 times as long as broad; apical pale band on hindtarsomere 2 narrow, 0.07–0.13 length of segment","3rd main dark area on wing vein 1 with a pale interruption, or with a short extension of the subcostal pale spot into the dark area on vein 1; foretarsomeres 1 to 3 with apical pale bands",Femora and tibiae with at most apical bands only,Maxillary palpus smooth; 2nd main dark area of wing vein 1 well defined and with 2 pale interruptions,Maxillary palpus with 4 pale bands,Maxillary palpus with apical dark spot about equal to or longer than apical pale band; 2nd main dark area on wing vein 1 with 1 pale interruption,"3rd main dark area of wing vein 1 without a pale interruption; abdoal terga fairly heavily clothed with cream or yellowish scales, especially on terga VI and VII",Maxillary palpus not speckled,Foretarsomere 1 not speckled; base of costa with 1 pale spot; stem of wing vein 2 extensively dark,Tarsomeres 1 to 4 with conspicuous pale bands on at least the apices; wing with pale fringe spots up to lower branch of vein 5 or 6,3rd main dark area without pale interruption,Hindtarsomere 2 either with less than apical 0.4 white or else prominently marked with dark and pale bands,Hindtarsomeres 2 to 4 with conspicuous dark and pale rings in addition to apical pale bands; pale fringe spot present opposite vein 6,Foretarsomeres mainly dark with narrow pale rings,Scales on tergum VIII scanty and confined to posterior margin,"Wings with at least some areas of paler scales on costa or vein 1, these being sometimes inconspicuous ",Maxillary palpus and legs entirely dark,"Small species, wing length 3.5 mm or less","General coloration dark brown, scutum not so; cave-dwelling","Maxillary palpus with or without pale bands, dark at apex","Erect head scales broader, scales white on vertex, dark laterally; all regions",Pale and dark areas on wing well contrasted,"Pale areas on wing broader, subcostal pale spot on costa and vein 1",Maxillary palpus unbanded or banding indistinct,Cave-dwelling species; colour and contrast of dark and pale areas on wing variable,"Erect head scales broader, scales white on vertex, dark laterally",Maxillary palpus smooth except at extreme base,Maxillary palpus with pale scales forming more or less definite pale bands; hindtarsomeres 3 and 4 narrowly or broadly pale at apices,Maxillary palpus with apex pale,"Stem of wing vein 4 largely dark, upper branch of vein 5 with one narrow pale area, pale fringe spots absent",Outer 0.5 of costa with 1–3 well-marked pale areas; maxillary palpus not so,Maxillary palpus either with 4 pale bands or if with 3 bands then subapical band much shorter than the apical band,"Dark areas on wing greater than or about equal to pale areas, basal 0.5 of stems of veins 2 and 4 largely dark ","No pale fringe spots posterior to wing vein 3, stem of vein 5 pale except at fork and sometimes narrowly near base","Wing vein 5 with extensive pale areas, upper branch of vein 5 with 2 pale spots",Hindtarsomeres 1 to 4 entirely dark or with a few pale scales at apices of 1 to 3; scutum scales broad,Scutal scales white throughout,Maxillary palpus with 3 pale bands,"Wing with well-contrasting pale and dark areas, basal 0.25 of costa with at least 1 pale area, even if narrow; head scales not so","Costa without a humeral pale spot, subapical pale spot present on costa and vein 1",Wing with no pale fringe spots posterior to vein 3,Wing with well-contrasting pale and dark areas,2nd main dark area of wing vein 1 with at most 1 pale interruption,"Pale bands on maxillary palpus variable in width, distal 2 bands overlapping the joints; upper branch of wing vein 5 with 2 pale spots","Pale and dark areas on wing about equally distributed, humeral and presector pale spots present on costa",Wing vein 6 dark,Basal 0.2 of wing vein 1 entirely pale,"Wings heavily scaled, upstanding scales moderately broad","Basal pale band of maxillary palpus either much shorter than median band, scarcely overlapping base of 3rd segment, or both basal and median pale bands very narrow",Base of costa dark,3rd main dark area without a pale interruption,Abdominal terga without such scales; hindtarsomeres entirely dark or with a few pale scales at apices of hindtarsomeres 1 to 3,2nd main dark area of wing vein 1 with 1 pale interruption,"Pale bands on maxillary palpus mostly narrow, basal band not overlapping base of 3rd segment",No pale fringe spots on wing posterior to vein 3; femora and tibiae inconspicuously speckled,Fork of wing vein 5 dark,Wing length 4.4 mm or more; some decumbent scales present on scutellum as well as scutum,2nd and 3rd main dark areas of wing (median and preapical dark spots) absent from vein 1,"Hindtarsomere 5 entirely dark, hindtarsomere 4 with narrow apical and basal pale bands",Upper branch of wing vein 5 with 2 well-developed pale spots,No pale fringe spot opposite wing vein 6; foretarsomeres 1 to 4 narrowly pale apically only,"Subapical pale band on maxillary palpus broad, overlapping apex of 3rd and base of 4th segment",Basal 0.25 of costa entirely dark,Hindtarsomeres 1 to 4 with well-marked apical pale bands,Scutal fossae and lateral areas of scutum above wing root (supraalar area) without scales,Subapical pale band on maxillary palpus much narrower than apical band,"Hindtarsomeres 1 to 4 with narrow pale bands, as long or shorter than the width of the tarsomeres",Wing vein 3 narrowly dark at ends; scutal scales various,,Maxillary palpus with 3 pale bands,Apical dark band much longer than subapical pale band,"Apical pale band on hindtarsomere 4, and sometimes on hindtarsomeres 2 and 3, extending onto bases of succeeding tarsomeres",2nd main dark area on wing vein 1 with 1 pale interruption; bases of hindtarsomeres 4 and 5 at most narrowly pale,"Base of costa with 2 pale interruptions, 3rd main dark area equal to or narrower than subcostal pale spot",No pale fringe spot opposite vein 6,"Apices of hindtarsomeres 1 to 3 and sometimes 4, distinctly pale banded",Base of costa with 1 or no pale interruption,Wing vein 6 without pale fringe spot and no pale scales at apex,"Scutal scales variable, but decumbent scales confined to at most anterior 0.66 of scutum","Small or moderate species, wing length 2.9 mm or more",Hindtarsomeres 1 and 2 narrowly but distinctly pale apically; preaccessory dark spot present on wing vein 1,3rd main dark area of costa equal to or shorter than subapical pale spot,"Scutal scales on posterior 0.33 of scutum scanty, narrow and yellowish-brown","Small species, wing length 3.0 mm or less",Foretarsomere 4 dark or indistinctly pale at apex; wing usually without pale fringe spot opposite vein 6,3rd main dark area of costa much longer than subapical pale spot,Wing with fork of vein 5 dark,Base of costa with 1 or no pale interruption,"Small or moderate-sized species, wing length 2.9–4.2 mm",Maxillary palpus with 3 pale bands,"Base of costa dark or with small pale spot, base of vein 1 dark",These veins dark,"Subapical pale spot shorter, usually much shorter, than apical dark spot, no pale fringe spot opposite upper branch of vein 5",Pale banding on hindtarsomeres narrow and apical only,"Preaccessory dark spot absent or, if present, shorter or only slightly longer than adjoining pale spots",Basal area of wing vein 1 entirely pale,"Subapical pale band on maxillary palpus much shorter than apical dark band, OR 3rd main dark area longer than subapical pale spot","Small species, wing length 3.2 mm or less","Tip of wing vein 6 with a few pale scales, sometimes with fringe spot present "')
reader = csv.reader(qbs)
questions_b = [item for item in reader]

others_by_group = [[],[], [],[],[],[],[],[],[],[],[]]

# ---- Session Initialization ----
if st.session_state.species_initialized == False:
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.ranking_candidates = database
    st.session_state.others = []
    st.session_state.species_initialized = True
    
st.title("Anopheles Species Identifier")
st.session_state.threshold = st.slider(0.0,1.0,.4)

if st.session_state.index == 0:
    st.session_state.candidates = database # Reset candidates before applying prior
    st.session_state.others = []
    if st.session_state.prior:
        prior_size = sum(1 for el in st.session_state.prior if el in [0,1,2,3])
        for idx, el in enumerate(st.session_state.prior):
             if el in [0,1,2,3]:
                 st.session_state.c_prev = st.session_state.candidates
                 if prior_size <= 2:
                     factor = 0.3
                 elif prior_size <= 5:
                     factor  = 0.35
                 else:
                     factor = 0.4
                 candidates, st.session_state.just_el = update_probabilities(el, idx, st.session_state.candidates, st.session_state.threshold, factor)
                 st.session_state.evidence[idx] = el
                 st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
        removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
        st.session_state.eliminated.append(removed)

# ---- Starting with Prior Text ----
if st.session_state.index == 0:
    nl_input = st.text_area("(Optional) Start with prior:", key="prior_text_input", placeholder="Describe the mosquito in detail...")
    
    if st.button("Submit Prior", use_container_width = True):
        st.session_state.u_inp = nl_input

        ### VECTOR VERSION ###
        prior = get_feature_vector(nl_input,"o3-mini")
        raw = get_feature_vector(nl_input, "o3-mini")

        tokens = raw.upper().replace(" ", "").split(",")
        
        prior = []
        
        for i, tok in enumerate(tokens):
            if tok == "":
                prior.append(None)
                continue        
            # ---- FEATURE 98 SPECIAL CASE ----
            if i == 98:
                mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
                prior.append(mapping.get(tok, None))
            else:
                mapping = {"A": 1, "B": 0}
                prior.append(mapping.get(tok, None))
        
        st.session_state.prior = prior

        st.session_state.c_prev = st.session_state.candidates
        st.session_state.candidates = database # Reset candidates before applying prior
        for idx, el in enumerate(st.session_state.prior):
            if el in [0,1,2,3]: 
                 candidates, st.session_state.just_el = update_probabilities(el, idx, st.session_state.candidates, st.session_state.threshold, .39)
                 st.session_state.evidence[idx] = el
                 st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
        removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
        st.session_state.eliminated.append(removed)
        st.warning(f"Applied prior: {st.session_state.prior}")
        st.rerun()
if st.session_state.prior:        
    #st.warning(f"Applied prior: {st.session_state.prior}")
    st.markdown("Applied prior.")
#st.markdown("Answer the following morphological questions to identify the species of Anopheles:")

# ---- Main Loop ----

#st.warning(f"Prior: {st.session_state.prior}")
_, mid, _ = st.columns(3)
mid.write(f"**Remaining candidates:** {len(st.session_state.candidates)}")
        
if not st.session_state.clicked_back:
    while st.session_state.index < len(questions):
        # Skip uninformative questions
        #values = {c.get(st.session_state.index, -1) for c in st.session_state.candidates if c.get(st.session_state.index, -1) != -1}
        values = {
            c.get(st.session_state.index,-1)
            for c in st.session_state.candidates
            if st.session_state.index in c and c.get(st.session_state.index,-1) != -1
        }
        num_with_values = sum(
            1 for c in st.session_state.candidates
            if st.session_state.index in c and c.get(st.session_state.index,-1) != -1
        )


        # Skip if all answers are the same or only one candidate has data
        if st.session_state.prior and st.session_state.index < len(st.session_state.prior) and st.session_state.prior[st.session_state.index] in [0,1,2,3]:
            if st.session_state.prior[st.session_state.index] in [0, 1,2,3]:
                st.session_state.index += 1
                st.warning("prior long line")
                continue

        if len(values) <= 1 or num_with_values <= 1:
            st.session_state.index += 1
        else:
            break
else:
    st.session_state.clicked_back = False
    
if st.session_state.index < len(questions):
    if st.session_state.prior:
        if st.button("Skip to ranking", key="skip", use_container_width=True):
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index = len(questions)
            st.session_state.eliminated.append([])
            st.rerun()
    q = questions[st.session_state.index]
    q_b = questions_b[0][st.session_state.index]
    if st.session_state.index == 98:
        st.write(f"**Q98**:")
        col1, col2 = st.columns(2)
        imga = "images/A.png"
        imgb = "images/B.png"
        imgc = "images/C.png"
        imgd = "images/D.png"
        #st.session_state.elim_prev = st.session_state.eliminated

        if col1.button("Scutal scales as in A", key="a", use_container_width=True):
             st.session_state.c_prev = st.session_state.candidates
             candidates, st.session_state.just_el = update_probabilities(0, 98, st.session_state.candidates, st.session_state.threshold)
             st.session_state.evidence[98] = 0
             st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
             removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
             st.session_state.eliminated.append(removed)
             st.session_state.answered.append(st.session_state.index)
             st.session_state.index += 1
             st.rerun()
        if col2.button("Scutal scales as in B", key="b", use_container_width=True):
            st.session_state.c_prev = st.session_state.candidates
            st.session_state.evidence[st.session_state.index] = 1
            candidates, st.session_state.just_el = update_probabilities(1, 98, st.session_state.candidates, st.session_state.threshold)
            st.session_state.evidence[98] = 1
            st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
            removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
        col1.image(imga)
        col2.image(imgb)
        
        if col1.button("Scutal scales as in C", key="c", use_container_width=True):
            st.session_state.c_prev = st.session_state.candidates
            st.session_state.evidence[st.session_state.index] = 2
            candidates, st.session_state.just_el = update_probabilities(2, 98, st.session_state.candidates, st.session_state.threshold)
            st.session_state.evidence[98] = 2
            st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
            removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
        if col2.button("Scutal scales as in D", key="d", use_container_width=True):
            st.session_state.c_prev = st.session_state.candidates
            st.session_state.evidence[st.session_state.index] = 3
            candidates, st.session_state.just_el = update_probabilities(3, 98, st.session_state.candidates, st.session_state.threshold)
            st.session_state.evidence[98] = 3
            st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
            removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
        col1.image(imgc)
        col2.image(imgd)
    
    if q_b != "" and q_b != None and st.session_state.index != 98:
        st.write(f"**Q{st.session_state.index}:**")
        col1, col2, col3 = st.columns(3)
        imgstrunique = "images/"+str(st.session_state.index)+".png"
        if os.path.exists(imgstrunique):
            st.image(imgstrunique)
        else:
            tr, fal = st.columns(2)
            imgstry = "images/"+str(st.session_state.index)+"y.png"
            imgstrn = "images/"+str(st.session_state.index)+"n.png"
            if os.path.exists(imgstry):
                tr.image(imgstry)
            if os.path.exists(imgstrn):
                fal.image(imgstrn)
        if col1.button(q,key=f"q_sp_{st.session_state.index}", use_container_width = True):
            if st.session_state.index < len(others_by_group) and not st.session_state.others:
                 st.session_state.o_prev = st.session_state.others
                 st.session_state.others = others_by_group[st.session_state.index] #get group of other, less relevant species
            st.session_state.c_prev = st.session_state.candidates
            #st.session_state.elim_prev = st.session_state.eliminated
            
            if st.session_state.index == 3:
                 candidates, st.session_state.just_el = update_probabilities(1, 18, st.session_state.candidates, st.session_state.threshold)
                 st.session_state.evidence[18] = 1
                 st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
            
            candidates, st.session_state.just_el = update_probabilities(1, st.session_state.index, st.session_state.candidates, st.session_state.threshold)
            st.session_state.evidence[st.session_state.index] = 1
            st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
            removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
        if col3.button(f"{q_b}",key=f"qb_sp_{st.session_state.index}", use_container_width = True):
            st.session_state.c_prev = st.session_state.candidates
            #st.session_state.elim_prev = st.session_state.eliminated
            if st.session_state.index == 3:
                 candidates, st.session_state.just_el = update_probabilities(0, 18, st.session_state.candidates, st.session_state.threshold)
                 st.session_state.evidence[18] = 0
                 st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)          
            candidates, st.session_state.just_el = update_probabilities(0, st.session_state.index, st.session_state.candidates, st.session_state.threshold)
            st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
            st.session_state.evidence[st.session_state.index] = 0
            removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
        if col2.button("I don't know",key=f"idk_hasqb_sp_{st.session_state.index}", use_container_width = True):
            st.session_state.c_prev = st.session_state.candidates
            removed = [[]]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()

    elif st.session_state.index != 98:
        st.write(f"**Q{st.session_state.index + 1}: {q}**")

        col1, col2, col3 = st.columns(3)

        imgstrunique = "images/"+str(st.session_state.index)+".png"
        if os.path.exists(imgstrunique):
            st.image(imgstrunique)
        else:
            tr, fal = st.columns(2)
            imgstry = "images/"+str(st.session_state.index)+"y.png"
            imgstrn = "images/"+str(st.session_state.index)+"n.png"
            if os.path.exists(imgstry):
                tr.image(imgstry)
            if os.path.exists(imgstrn):
                fal.image(imgstrn)
        if col1.button("Yes",key=f"y_sp_{st.session_state.index}", use_container_width = True):
            if st.session_state.index < len(others_by_group) and not st.session_state.others:
                 st.session_state.o_prev = st.session_state.others
                 st.session_state.others = others_by_group[st.session_state.index] #get group of other, less relevant species
            st.session_state.c_prev = st.session_state.candidates
            #st.session_state.elim_prev = st.session_state.eliminated
            if st.session_state.index == 3:
                 candidates, st.session_state.just_el = update_probabilities(1, 18, st.session_state.candidates, st.session_state.threshold)
                 st.session_state.evidence[18] = 1
                 st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)          
            candidates, st.session_state.just_el = update_probabilities(1, st.session_state.index, st.session_state.candidates, st.session_state.threshold)
            st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
            st.session_state.evidence[st.session_state.index] = 1
            removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
        if col3.button("No",key=f"n_sp_{st.session_state.index}", use_container_width = True):
            st.session_state.c_prev = st.session_state.candidates
            #st.session_state.elim_prev = st.session_state.eliminated
            if st.session_state.index == 3:
                candidates, st.session_state.just_el = update_probabilities(0, 18, st.session_state.candidates, st.session_state.threshold)
                st.session_state.evidence[18] = 0
                st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
                removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                st.session_state.eliminated.append(removed)
            candidates, st.session_state.just_el = update_probabilities(0, st.session_state.index, st.session_state.candidates, st.session_state.threshold)
            st.session_state.evidence[st.session_state.index] = 0
            st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
            removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
        if col2.button("I don't know",key=f"idk_sp_{st.session_state.index}", use_container_width = True):
            st.session_state.c_prev = st.session_state.candidates
            #st.session_state.elim_prev = st.session_state.eliminated
            removed = [[]]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()

else:
    st.subheader("Likely species")
    
    
    if st.session_state.evidence:
        #bn_model, bn_inference, bn_features = load_dbn()
        nb_model = load_nb()
        clean_evidence = sanitize_evidence(st.session_state.evidence)
        
        #dbn_probs = infer_species_probs(
        #    bn_inference,
        #    clean_evidence,
        #    questions
        #)
        nb_probs = infer_species_probs(
            nb_model,
            clean_evidence
        )

        # override heuristic probabilities
        ranked = sorted(
            st.session_state.ranking_candidates,
            key=lambda c: nb_probs.get(c["name"], 0),
            reverse=True
        )
        
        for c in ranked:
            if nb_probs[c["name"]] > st.session_state.threshold:
                st.write(f"**Anopheles {c["name"]}** Match: {nb_probs[c["name"]]*100:.2f}%")

        #st.session_state.candidates.sort(
        #    key=lambda c: c["prob"], reverse=True
        #)
    
        #for c in st.session_state.candidates:
        #    st.write(
        #        f"- **Anopheles {c['name']}** "
        #        f"(Match: {c['prob']*151*100:.2f}%)"
         #   )
    else:
      st.error("No matching relevant species.")

bn1, bn2 = st.columns(2)
    
if st.session_state.index > 0:
    if bn1.button("Previous question",key="prev_spec", use_container_width=True)  and st.session_state.answered:
        st.session_state.index = st.session_state.answered.pop()
        restore = st.session_state.eliminated.pop()
        st.session_state.candidates.extend(e for e in restore if isinstance(e, dict))
        st.session_state.others = st.session_state.o_prev
        st.session_state.clicked_back = True
        st.rerun()
        

if bn2.button("Restart",key="restart_sp", use_container_width = True):
    st.session_state.index = 0
    st.session_state.eliminated = []
    st.session_state.candidates = database
    st.session_state.others = []
    st.session_state.species_initialized = False
    st.session_state.prior = []
    st.rerun()
st.markdown("Coetzee, M. Key to the females of Afrotropical Anopheles mosquitoes (Diptera: Culicidae). Malar J 19, 70 (2020). https://doi.org/10.1186/s12936-020-3144-9")
#if len(st.session_state.others) >0:
#  if st.button("See rare species"):
#    for name in others:
#          st.write("- " + name)
