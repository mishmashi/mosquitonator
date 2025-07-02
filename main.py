import streamlit as st
import pandas as pd

database = []
# Initialize session state
if "index" not in st.session_state:
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.answers = {}
    st.session_state.phase = "start"
    st.session_state.species_initialized = False
    st.session_state.prior = []
    
def filter_candidates(index, ans, candidates):
        if ans == 1:
            return [c for c in candidates if c.get(index, -1) == 1]
        elif ans == 0:
            return [c for c in candidates if c.get(index, -1) != 1]
        else:
            return candidates

if st.session_state.phase == "start":
    st.header("Mosquito Identification")
    choice = st.radio("Is the specimen an *Anopheles*?", ["Yes", "I don't know"])
    if st.button("Continue"):
        if choice == "Yes":
            st.session_state.phase = "species"
        else:
            st.session_state.phase = "genus"
elif st.session_state.phase == "genus":
    st.header("Determine the Genus")
    st.markdown("Answer the following morphological questions to identify the genus:")
    # Feature list and questions
    questions = [
        "Is it a fly with needle-like mouthparts, scales on the body and wings?",
        "Are the antennae bushy or feather-like?",
        "Are the palpi as long as the proboscis?",
        "Are the palpi bushy or paddle-shaped?",
        "Is the apical half of the proboscis strongly recurved?",
        "Are abdominal scales dark dorsally and pale ventrally, and does the mesopostnotum have setae?",
        "Are abdominal scales banded or spotted, and is the mesopostnotum without setae?",
        "Does vein 1A end before or at the level with the mcu intersection?",
        "Is the thorax marked with lines of iridescent blue scales?",
        "Are prespiracular setae present?",
        "Are postspiracular setae present?",
        "Is there a row of bristles at the base of the subcostal vein under the wing?",
        "Is the abdomen pointed in dorsal view?",
        "Are the wing scales narrow on dorsal surface?",
        "Are there mixed brown and white wing scales dorsally?",
        "Are the antennae longer than the proboscis?",
        "Is flagellomere 1 twice as long as flagellomere 2?",
        "Are there fine longitudinal lines of white scales on mesonotum?",
        "Does tarsomere 1 have a pale ring in the middle?",
        "Does the abdomen have metallic violet/silver scales?",
        "Is there a silvery scale band from scutum to coxae?"
    ]
    
    database = [
        {"name": "an Aedes",             0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 10: 0, 12: 1, 18: 0, 19: 0, "image": "images/aedes.png"},
        {"name": "an Anopheles",         0: 1, 1: 1, 2: 1, 3: 0, 5: 0, "image": "images/anopheles.png"},
        {"name": "a Coquillettidia",    0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 1, 18: 0, 19: 1, "image": "images/coquillettidia.png"},
        {"name": "a Culex",    0: 1, 1: 0, 2:0, 4: 0, 5: 0, 6: 1, 7: 0, 9: 0, 10: 0, 11:0, 12:0, 13: 1, 15:0, 16:0, "image": "images/culex.png"},
        {"name": "a Culiseta",          0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 9: 1, 11: 1, "image": "images/culiseta.png"},
        {"name": "a Deinocerites",      0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 12: 0, 13: 1, 15: 1, 16: 1, "image": "images/deinocerites.png"},
        {"name": "a Haemagogus",        0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 12: 1, 16: 1, 17: 1, "image": "images/haemagogus.png"},
        {"name": "a Mansonia",          0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 10: 1, 11: 0, 12: 0, 13: 0, 14: 1, 18: 0, 19: 0, "image": "images/mansonia.png"},
        {"name": "an Orthopodomyia",     0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 15: 1, "image": "images/orthopodomyia.png"},
        {"name": "a Psorophora",        0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 9: 1, 10: 1, 12: 1, "image": "images/psorophora.png"},
        {"name": "a Toxorhynchites",    0: 1, 1: 0, 2: 0, 4: 1, "image": "images/toxorhynchites.png"},
        {"name": "an Uranotaenia",       0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 1, 8: 1, "image": "images/uranotaenia.png"},
        {"name": "a Wyeomyia",          0: 1, 1: 0, 2: 0, 5: 1, "image": "images/wyeomyia.png"},
        {"name": "not a mosquito",    0: 0, "image": "images/other.png"},
        {"name": "a male mosquito",     0: 1, 1: 1, 2: 1, 3: 1, "image": "images/male.png"}
    ]

    if st.session_state.index == 0:
        st.session_state.candidates = database

    # Skip uninformative questions
    while st.session_state.index < len(questions):
        values = {c.get(st.session_state.index, -1) for c in st.session_state.candidates}
        if len(values) <= 1:
            st.session_state.index += 1
        else:
            break
    
    if st.session_state.index < len(questions):
        q = questions[st.session_state.index]
        st.write(f"**Q{st.session_state.index + 1}: {q}**")
    
        col1, col2, col3 = st.columns(3)
        if col1.button("Yes",key="y_genus"):
            st.session_state.candidates = filter_candidates(st.session_state.index, 1, st.session_state.candidates)
            st.session_state.index += 1
            st.rerun()
        if col2.button("No",key="n_genus"):
            st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
            st.session_state.index += 1
            st.rerun()
        if col3.button("I don't know",key="idk_genus"):
            st.session_state.candidates = filter_candidates(st.session_state.index, None, st.session_state.candidates)
            st.session_state.index += 1
            st.rerun()
    else:
        if len(st.session_state.candidates) == 1:
            st.success(f"The specimen is **{st.session_state.candidates[0]['name']}**")
            st.image(st.session_state.candidates[0]['image'], caption="Mosquito morphology")
        elif len(st.session_state.candidates) > 1:
            st.warning("Possible genera:")
            for c in st.session_state.candidates:
                st.write("- " + c["name"])
                st.image(c["image"], caption="Mosquito morphology")
    
        else:
            st.error("No matching genus found.")
    
    if st.button("🔄 Restart", key="restart_genus"):
        st.session_state.index = 0
        st.session_state.candidates = database
        st.session_state.answers = {}
        st.session_state.phase = "start"
        st.rerun()

    if len(st.session_state.candidates) == 1 and st.session_state.candidates[0]["name"] == "an Anopheles":
        if st.button("Determine species",key="determine_sp"):
            st.session_state.others = []
            st.session_state.index = 0
            st.session_state.phase = "species"
elif st.session_state.phase == "species":
            
        st.header("Species Identification")    
        @st.cache_data #for optimization
        def load_data():
                import pandas as pd
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
        if st.session_state.species_initialized == False:
            st.session_state.index = 0
            st.session_state.candidates = database
            st.session_state.answers = {}
            st.session_state.others = []
            st.session_state.species_initialized = True
        
        st.title("Anopheles Species Identifier")
        if st.button("Start with prior",key="prior"):
            prior = st.text_input("Prior",
            placeholder="Enter prior vector",
            )
            st.markdown(f"Type: {type(prior)}")

            
        st.markdown("Answer the following morphological questions to identify the species of Anopheles:")
        
        # ---- Main Loop ----
        while st.session_state.index < len(questions):
            if len(st.session_state.candidates) <= 1:
                st.session_state.index += 1 #skip question if candidate has been picked, or all have been eliminated
            # Get all values for this question
            #values = {c.get(st.session_state.index, -1) for c in st.session_state.candidates}
        
            # Skip q if all candidates have the same value, so no impurity gain
            #if sum(1 for c in st.session_state.candidates if st.session_state.index in c) <=1:
             #   st.session_state.index += 1
            values = {c.get(st.session_state.index, -1) for c in st.session_state.candidates}
            num_with_values = sum(1 for c in st.session_state.candidates if st.session_state.index in c)
        
            # Skip if all answers are the same or only one candidate has data
            if st.session_state.index >10:
                    if len(values) <= 1 or num_with_values <= 1:
                        st.session_state.index += 1
                    else:
                            break
            else:
                break  
                    
        if st.session_state.index <= 9:
            q = questions[st.session_state.index]
            st.write(f"**Q{st.session_state.index + 1}: {q}**")
        
            col1, col2, col3 = st.columns(3)
            if col1.button("Yes",key="y_sp"):
                st.session_state.others = others_by_group[st.session_state.index] #get group of other, less relevant species 
                st.session_state.candidates = filter_candidates(st.session_state.index, 1, st.session_state.candidates)
                st.session_state.index = 10
                st.rerun()
            if col2.button("No",key="n_sp"):
                if st.session_state.index == 9:
                        st.session_state.index += 1
                        st.session_state.others = others_by_group[10]
                        st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
                        st.rerun()
                else:
                        st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
                        st.session_state.index += 1
                        st.rerun()
            if col3.button("I don't know",key="idk_sp"):
                st.session_state.index += 1
                st.rerun()
        
        elif st.session_state.index < len(questions):
            q = questions[st.session_state.index]
            st.write(f"**Q{st.session_state.index + 1}: {q}**")
        
            col1, col2, col3 = st.columns(3)
            if col1.button("Yes",key="y_sp2"):
                st.session_state.candidates = filter_candidates(st.session_state.index, 1, st.session_state.candidates)
                st.session_state.index += 1
                st.rerun()
            if col2.button("No",key="n_sp2"):
                st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
                st.session_state.index += 1
                st.rerun()
            if col3.button("I don't know",key="idk_sp2"):
                st.session_state.candidates = filter_candidates(st.session_state.index, None, st.session_state.candidates)
                st.session_state.index += 1
                st.rerun()
        else:
            if len(st.session_state.candidates) == 1:
                st.success(f"The specimen is an **Anopheles {st.session_state.candidates[0]['name']}**")
                #st.image(st.session_state.candidates[0]['image'], caption="Mosquito morphology")
            elif len(st.session_state.candidates) > 1:
                st.warning("Possible species:")
                for c in st.session_state.candidates:
                    st.write(f"- **Anopheles {c['name']}")
                   # st.image(c["image"], caption="Example of species")
        
           # elif len(st.session_state.candidates) == 0 and len(st.session_state.others) >0:
            #    st.warning("Possible species:")
             #   for name in st.session_state.others:
              #    st.write("- Anopheles " + name)
            else: 
              st.error("No matching relevant species.")
            if st.session_state.others:
                st.warning("Less likely species:")
                for name in st.session_state.others:
                        st.write(f"- **Anopheles {name}**")
        
        if st.button("🔄 Restart from Genus",key="restart_all"):
            st.session_state.index = 0
            st.session_state.candidates = []
            st.session_state.others = []
            st.session_state.answers = {}
            st.session_state.species_initialized = False
            st.session_state.phase = "start"
            st.rerun()

        if st.button("Back to Species",key="restart_sp"):
            st.session_state.index = 0
            st.session_state.phase = "species"
            st.session_state.candidates = database
            st.session_state.others = []
            st.session_state.answers = {}
            st.session_state.species_initialized = False
            st.rerun()
        st.markdown("Coetzee, M. Key to the females of Afrotropical Anopheles mosquitoes (Diptera: Culicidae). Malar J 19, 70 (2020). https://doi.org/10.1186/s12936-020-3144-9")
        #if len(st.session_state.others) >0:
        #  if st.button("See rare species"):
        #    for name in others:
        #          st.write("- " + name)
