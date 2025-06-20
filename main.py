import streamlit as st

# Feature list and questions
questions = [
    "Is it a fly with needle-like mouthparts, scales on the body and wings?",
    "Are the antennae bushy or feather-like?",
    "Are the palpi as long as the proboscis?",
    "Are the palpi bushy or paddle-shaped?",
    "Is the apical half of the proboscis strongly recurved?",
    "Are abdominal scales dark dorsally and pale ventrally, and is the mesopostnotum with setae?",
    "Are abdominal scales banded or spotted, and mesopostnotum without setae?",
    "Does vein 1A end before or at the level with the mcu intersection?",
    "Is the thorax marked with lines of iridescent blue scales?",
    "Are prespiracular setae present?",
    "Are postspiracular setae present?",
    "Row of bristles at base of subcostal vein under wing?",
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
    {"name": "an Anopheles",         0: 1, 1: 1, 2: 1, 3: 0, 5: 0, "image": "anopheles.png"},
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

# Initialize session state
if "index" not in st.session_state:
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.answers = {}

st.title("Mosquito Genus Identifier")
st.markdown("Answer the following morphological questions to identify the genus:")

def filter_candidates(index, ans):
    if ans == 1:
        return [c for c in st.session_state.candidates if c.get(index, -1) == 1]
    elif ans == 0:
        return [c for c in st.session_state.candidates if c.get(index, -1) != 1]
    else:  # I don't know
        return st.session_state.candidates

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
        st.success(f"The specimen is **{st.session_state.candidates[0]['name']}**")
        st.image(st.session_state.candidates[0]['image'], caption="Mosquito morphology")
    elif len(st.session_state.candidates) > 1:
        st.warning("Possible genera:")
        for c in st.session_state.candidates:
            st.write("- " + c["name"])
            st.image(c["image"], caption="Mosquito morphology")

    else:
        st.error("No matching genus found.")

if st.button("🔄 Restart"):
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.answers = {}
    st.rerun()
