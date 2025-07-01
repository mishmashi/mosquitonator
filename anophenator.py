import streamlit as st
import pandas as pd

# ---- Load Data from Google Sheets or CSV ----

@st.cache_data #for optimization
def load_data():
        df = pd.read_csv("Mosquito traits by genus.csv", header=2)
#        st.write("Available columns:", df.columns.tolist())
        questions = [col for col in df.columns if col not in ("Species", "Image")]

        database = []
        for _, row in df.iterrows():
            entry = {"name": row["Species"], "image": row["Image"]}
            for i, q in enumerate(questions):
                if pd.notna(row[q]) and row[q] != "":
                    entry[i] = int(row[q])
            database.append(entry)

        return questions, database

# ---- Load questions and database ----
questions, database = load_data()
others = []
others_by_group = [["Brumpti", "Argenteolobatus", "Murphyi", "Cinctus", "Cristipalpis", "Okuensis", "Implexus", "Swahilicus", "Squamosus", "Cyddipis"],
 ["Maculipalpis", "Maliensis", "Deemingi", "Pretoriensis", "Machardyi", "Natalensis", "Buxtoni", "Caliginosus", "Paludis", "Tenebrosus", "Crypticus", "Ziemanni", "Namibiensis", "Rufipes", "Hancocki", "Brohieri", "Theileri"],
 ["Kingi", "Symesi", "Rufipes"],
 ["Hervyi", "Salbaii", "Dancalicus", "Vernus", "Multicinctus", "Ardensis", "Vinckei", "Dureni", "Millecampsi"],
 ["Concolor", "Ruarinus", "Rhodesiensis", "Caroni", "Dthali", "Rodhaini", "Lounibosi", "Smithii", "Hamoni", "Vanhoofi", "Azaniae"],
 ["Obscurus", "Tenebrosus", "Tchekedii", "Smithii", "Daudi", "Wellcomei", "Erepens", "Keniensis", "Fuscivenosus", "Disctinctus", "Schwetzi", "Walravensi"],
 ["Azaniae", "Obscurus", "Jebudensis", "Faini", "Turkhudi", "Wilsoni", "Rufipes", "Rageaui", "Smithii", "Fontinalis", "Lovettae", "Cinereus", "Multicolor", "Listeri", "Azevedoi", "Seretsei"],
 ["Christyi", "Schwetzi", "Wilsoni", "Cinereus", "Vernus", "Garnhami", "Demeilloni", "Carteri"],
 ["Wellcomei", "Seydeli", "Mortiauxi", "Berghei", "Brunnipes", "Walravensi", "Harperi", "Njombiensis", "Austensii", "Gibbinsi", "Hargreavesi", "Mousinhoi", "Marshallii", "Letabensis", "Kosiensis", "Hughi"],
 ["Gabonensis", "Rufipes", "Domicolus", "Lloreti", "Barberellus", "Brucei", "Rivulorum", "Carteri", "Brucei", "Freetownensis", "Demeilloni", "Flavicosta", "Keniensis", "Moucheti", "Bervoetsi", "Garnhami"],
 ["Ovengensis", "Longipalpis", "Fuscivenosus", "Culicifacies", "Aruni", "Demeilloni", "Parensis", "Sergentii", "Cameroni"]]



# ---- Session Initialization ----
if "index" not in st.session_state:
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.answers = {}
    st.session_state.others = others

st.title("Anopheles Species Identifier")
st.markdown("Answer the following morphological questions to identify the species of Anopheles:")

# ---- Filtering Logic ----
def filter_candidates(index, ans):
    if ans == 1:
        return [c for c in st.session_state.candidates if c.get(index, -1) == 1]
    elif ans == 0:
        return [c for c in st.session_state.candidates if c.get(index, -1) != 1]
    else:
        return st.session_state.candidates

# ---- Main Loop ----
while st.session_state.index < len(questions):
    if len(st.session_state.candidates) <= 1:
        break #skip question if candidate has been picked

    # Get all values for this question
    values = {c.get(st.session_state.index, -1) for c in st.session_state.candidates}

    # Skip q if all candidates have the same value, so no impurity gain
    if values in [{-1}, {0}, {1}]:
        st.session_state.index += 1
    else:
        break  
            
if st.session_state.index <= 9:
    q = questions[st.session_state.index]
    st.write(f"**Q{st.session_state.index + 1}: {q}**")

    col1, col2, col3 = st.columns(3)
    if col1.button("Yes"):
        st.session_state.others = others_by_group[st.session_state.index] #get group of other species 
        st.session_state.index = 9
        st.rerun()
    if col2.button("No"):
        if st.session_state.index == 9:
                st.session_state.index += 1
                st.session_state.others = others_by_group[10]
                st.rerun()
        else:
                st.session_state.index += 1
                st.rerun()
    if col3.button("I don't know"):
        st.session_state.index += 1
        st.rerun()

elif st.session_state.index < len(questions):
    q = questions[st.session_state.index]
    st.write(f"**Q{st.session_state.index + 1}: {q}**")

    col1, col2, col3 = st.columns(3)
    if col1.button("Yes"):
        st.session_state.candidates = filter_candidates(st.session_state.index, 1)
        st.session_state.index += 1
        st.rerun()
    if col2.button("No"):
        st.session_state.candidates = filter_candidates(st.session_state.index, 0)
        st.session_state.index += 1
        st.rerun()
    if col3.button("I don't know"):
        st.session_state.candidates = filter_candidates(st.session_state.index, None)
        st.session_state.index += 1
        st.rerun()
else:
    if len(st.session_state.candidates) == 1:
        st.success(f"The specimen is an Anopheles **{st.session_state.candidates[0]['name']}**")
        #st.image(st.session_state.candidates[0]['image'], caption="Mosquito morphology")
    elif len(st.session_state.candidates) > 1:
        st.warning("Possible species:")
        for c in st.session_state.candidates:
            st.write("- Anopheles " + c["name"])
           # st.image(c["image"], caption="Example of species")
    elif len(st.session_state.candidates) == 0 and len(st.session_state.others) >0:
        st.warning("Possible species:")
        for name in st.session_state.others:
          st.write("- Anopheles " + name)
    else: 
      st.error("No matching species found.")

if st.button("🔄 Restart"):
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.others = []
    st.session_state.answers = {}
    st.rerun()
st.markdown("Coetzee, M. Key to the females of Afrotropical Anopheles mosquitoes (Diptera: Culicidae). Malar J 19, 70 (2020). https://doi.org/10.1186/s12936-020-3144-9")
#if len(st.session_state.others) >0:
#  if st.button("See rare species"):
#    for name in others:
#          st.write("- " + name)
