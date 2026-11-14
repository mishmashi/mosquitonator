from typing import Any

import streamlit as st
import pandas as pd
import os
import csv
from openai import OpenAI

from vosk import Model, KaldiRecognizer
import pyttsx3
import wave
import json
from io import StringIO
import typesafe_sdk
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

openai_key = st.secrets["openai_key"]
jev_key = st.secrets["jev_key"]
client = TypeSafeClient(api_key= jev_key )

import threading, queue

@st.cache_resource
def get_tts_queue():
     tts_q = queue.Queue()
#
     def worker():
         # import pythoncom; pythoncom.CoInitialize()   # uncomment on Windows if silent
         import pyttsx3
         engine = pyttsx3.init()
         engine.setProperty("rate", 175)
         engine.setProperty("volume", 0.9)
         voices = engine.getProperty("voices")
         engine.setProperty("voice", voices[164].id)
         while True:
             text = tts_q.get()
             try:
                 engine.say(text)
                 engine.runAndWait()
             except RuntimeError:
                 engine.stop()

     threading.Thread(target=worker, daemon=True).start()
     return tts_q


def jev_answer(description, u_inp, A_raw, B_raw):
    state = f'System question: "{description}" User response: "{u_inp}"'

    questions = {
        "intent": Choice(instructions="What was the user's intent?", criteria={
            "repeat": "Does the user want to hear the question again?",
            "clarify": "Is the user asking for clarification?",
            "respond": "Is the user responding to the system's question?",
        }),
        "answer": Choice(
            instructions="Which option did the user mean to select?", criteria={
                "Answer_A": f"{A_raw}",
                "Answer_B": f"{B_raw}",
                "answer_none": "Neither answer matches, or both answers match"
            }
        ),
    }
    result = client.system_one(state, questions)

    intent_choice = result.choices["intent"].choice
    intent_score = result.choices["intent"].confidence
    answer_choice = result.choices["answer"].choice
    answer_score = result.choices["answer"].confidence
    return intent_choice, intent_score, answer_choice, answer_score

def clarify(description, u_inp, model: str= "gpt-4o-mini", openai_key: str=""):
    prompt_instructions = f"""You are assisting a user doing morphological mosquito identification.
    The user asked for clarification, saying this:
    \"\"\"
    {u_inp}. 
    \"\"\"
    This is the question the user is trying to answer: {description}.

    Generate a spoken response to the user's query that can help answer the question. Be as brief as possible, ONLY clarify what the user is asking.

    Some context for your answer:
    - area: a broad, less defined region of color or texture. For example, a "dark area" on the wing could mean a large portion covered by dark scales, without a sharp boundary.
    - band: a continuous stripe that runs across a segment, usually transverse. For example, a "pale band on the tarsus" means a light-colored ring that encircles the segment.
    - spot: a relatively small, discrete patch of scales that is clearly localized, not coninuous.
    - patch: similar to a spot but usually larger and less regularly shaped, often referring to a cluster of scales.
    - ring: specifically circular or encircling markings, often used on leg segments.
    - interruption: when a marking (often a band or ring) is broken or incomplete.
    - speckled: with small, irregular markings that don't go across the entire segment, unlike bands, which are generally more well-defined.
    - hind leg: one of the third pair of legs, back leg.
    - fore leg: one of the first pair of legs, front leg.
    - mid leg: one of the second pair of legs, middle leg.
    - femur: most proximal portion of the leg. It generally extends upwards. 
    - tibia: portion of the leg in between the femur and the tarsus. Second long segment of the leg.
    - tarsus: most distal portion of the leg.
    - tarsomere: segment of the last portion of the leg. They are counted 1-5 from proximal to distal.
    - When something is described as "dark at apex", it means the tip of it is dark, even if there are pale bands before it. 
    - consider "white" and "pale" as synonyms. Occasionally, "white" might be used to show a sharper contrast, but consider them synonyms for the most part.
    - consider "dark" and "black" as synonyms
    - the term "apical" might be described as "distal"
    - the wing contains veins that, from the top down are named: costa, sub-costa or subcosta, vein 1, vein 2, vein 3, vein 4, vein 5 and vein 6
    - "wing vein 1 without usual main dark areas" generally implies that they are missing entirely, rather than one being absent or the set of bands being replaced by a different set.
    - veins 5 and 6 might be described as "posterior veins"
    - something "without distinct bands" may not be uniform in color; it just means it has no clearly defined, crisp regions that encircle the segment and stand out as bands.
    - the costa can be called the "top vein" or "leading edge". It's the very first vein, at the top of the wing, making up the upper edge.
    - the subcosta is right under the costa. At its base, it's fused with vein 1. Then, it branches out and fuses with the costa on the distal end. 
    - wing vein 1 can be called the radius 1, "R1", or the "first branch of the radius". It is the vein right below the subcosta. It starts fused with the subcosta at its base, then appears to fuse with the subcosta and costa at the end.
    - wing vein 2 can be called Radius 2+3, "r2+3", or the "second branch of the radius". It is right below vein 1, and it's the first vein from the top that branches into two. Its base appears to be floating. 
    - wing vein 3 can be called Radius 4+5, "r4+5", or the "third branch of the radius". It's a straight vein in between two veins that branch into two. Its base appears to be floating. 
    - wing vein 4 can be called Media, "M", or "medial vein".  It's the second vein from the top down that branches into two.
    - wing vein 5 can be called Cubitus, "Cu" or "cubital vein". It's the second vein from the bottom up, and it branches into two.
    - wing vein 6 can be called Anal, "A", or "anal vein". It's the first vein from the bottom up. It doesn't branch into two.
    - The spots on the wing can be called "humeral spot" (at the base of the wing, near the costa, or "basal costal spot"); "presector spot" (just before sector vein along costa, or "costal pre-sector spot"); "median spot" (mid-wing on radial veins, or "central spot"); "preaccessory spot" (before accessory vein along costa, or "costal pre-accessory spot"); "preapical spot" (near wing tip, not at apex, or "subapical"); "subapical spot" (just before apex along main veins, or "distal costal spot"). They can also be described relative to the costa or specific veins.
    - the feature "3rd main dark area of wing vein 1 with a pale interruption, sometimes fused with preceding pale spot" can be described as a "gambiae gap"
    - Decumbent scales: scales that lie flat or nearly flat against the surface they cover, rather than sticking out (erect scales) or lying completely appressed. They can be on various body parts-  commonly the thorax, scutum, head and legs, depending on the species. They lay along the surface, often forming background coloration rather than highlighting a structure.
    - Usually, a band would be described as "narrow" if it covered roughly a quarter or less of the segment's length or width, unless otherwise stated.
    - usually, a band would be described as "broad" if it covered  roughly half or more of the segment's length or width
    - intermediate" or "moderate" bands are anything in between narrow and broad.
    - the top part of the wing can have distinctive markings called "main dark areas". There are three of these (first, second and third main dark area, from proximal to distal). 
    - Main dark areas are found roughly in the first, second and last thirds of the wing. They can cover the costa, subcosta and vein 1. 
    - Main dark areas can vary in size, but the overall pattern will be the same.         

    """
    client = OpenAI(
        api_key= openai_key
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt_instructions},
            {"role": "user", "content": f"Respond to the user's request for clarification: {u_inp}"}
        ]
    )
    return response.choices[0].message.content.strip()

#def speak_once(text):
 #    if st.session_state.get("last_spoken") != text:
  #       st.session_state.last_spoken = text
   #      get_tts_queue().put(text)


# Initialize session state
if "index" not in st.session_state:
    database = []
    # st.session_state.engine = pyttsx3.init()
    # st.session_state.engine.setProperty('rate', 170)  # Speed of speech (default is usually ~200)
    # st.session_state.engine.setProperty('volume', 0.9)  # Volume level between 0 and 1
    # st.session_state.voices = st.session_state.engine.getProperty('voices')  # getting details of current voice
    # st.session_state.engine.setProperty('voice', st.session_state.voices[164].id) #favs: 164, 64,  82, 132, 18, 14
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.eliminated = []
    st.session_state.elim_prev = []
    st.session_state.c_prev = database
    st.session_state.phase = "start"
    st.session_state.species_initialized = False
    st.session_state.o_prev = []
    st.session_state.u_inp = ""
    st.session_state.last_phase = "start"
    st.session_state.clicked_back = False
    st.session_state.answered = []
    st.session_state.jev_int_thresh = .7
    st.session_state.jev_ans_thresh = .8
    st.session_state.df_eval = pd.read_csv('simulated_user_responses.csv', index_col=0)
    st.session_state.intent_choices = []
    st.session_state.intent_confidences = []
    st.session_state.answer_choices = []
    st.session_state.answer_confidences = []
    st.session_state.descriptions = st.session_state.df_eval[st.session_state.df_eval["Answer_type"]=="Answer_A"]["description"]
    st.session_state.A_name = st.session_state.df_eval[st.session_state.df_eval["Answer_type"]=="Answer_A"]["A_name"]
    st.session_state.B_name = st.session_state.df_eval[st.session_state.df_eval["Answer_type"]=="Answer_B"]["B_name"]

def filter_candidates(index, ans, candidates):
    if ans == 1:
        return [c for c in candidates if c.get(index, -1) != 0 and c.get(index, -1) != 2 and c.get(index, -1) != 3]
    elif ans == 0:
        return [c for c in candidates if c.get(index, -1) != 1 and c.get(index, -1) != 2 and c.get(index, -1) != 3]
    elif ans == 2:
        return [c for c in candidates if c.get(index, -1) != 0 and c.get(index, -1) != 1 and c.get(index, -1) != 3]
    elif ans == 3:
        return [c for c in candidates if c.get(index, -1) != 0 and c.get(index, -1) != 1 and c.get(index, -1) != 2]
    else:
        return candidates


if st.session_state.phase == "start":
    st.header("Mosquito Identification")
    choice = st.radio("Is the specimen an *Anopheles*?", ["Yes", "Unsure"])
    if st.button("Continue"):
        if choice == "Yes":
            st.session_state.phase = "species"
            st.rerun()
        else:
            st.session_state.phase = "genus"
            st.rerun()
elif st.session_state.phase == "genus":
    st.header("Determine the Genus")
    # st.markdown("Answer the following morphological questions to identify the genus:")
    # Feature list and questions
    questions_db = [
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
        {"name": "an Aedes", 0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 10: 0, 12: 1, 18: 0, 19: 0,
         "image": "images/aedes.png"},
        {"name": "an Anopheles", 0: 1, 1: 0, 2: 1, 3: 0, 5: 0, "image": "images/anopheles.png"},
        {"name": "a Coquillettidia", 0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 1, 18: 0,
         19: 1, "image": "images/coquillettidia.png"},
        {"name": "a Culex", 0: 1, 1: 0, 2: 0, 4: 0, 5: 0, 6: 1, 7: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 1, 15: 0, 16: 0,
         "image": "images/culex.png"},
        {"name": "a Culiseta", 0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 9: 1, 11: 1, "image": "images/culiseta.png"},
        {"name": "a Deinocerites", 0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 12: 0, 13: 1, 15: 1, 16: 1,
         "image": "images/deinocerites.png"},
        {"name": "a Haemagogus", 0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 12: 1, 16: 1, 17: 1,
         "image": "images/haemagogus.png"},
        {"name": "a Mansonia", 0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 10: 1, 11: 0, 12: 0, 13: 0, 14: 1, 18: 0, 19: 0,
         "image": "images/mansonia.png"},
        {"name": "an Orthopodomyia", 0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 15: 1, "image": "images/orthopodomyia.png"},
        {"name": "a Psorophora", 0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 0, 9: 1, 10: 1, 12: 1,
         "image": "images/psorophora.png"},
        {"name": "a Toxorhynchites", 0: 1, 1: 0, 2: 0, 4: 1, "image": "images/toxorhynchites.png"},
        {"name": "an Uranotaenia", 0: 1, 1: 0, 2: 0, 5: 0, 6: 1, 7: 1, 8: 1, "image": "images/uranotaenia.png"},
        {"name": "a Wyeomyia", 0: 1, 1: 0, 2: 0, 5: 1, "image": "images/wyeomyia.png"},
        {"name": "not a mosquito", 0: 0, "image": "images/other.png"},
        {"name": "a male mosquito", 0: 1, 1: 1, 2: 1, 3: 1, "image": "images/male.png"}
    ]

    if st.session_state.index == 0:
        st.session_state.candidates = database
        st.session_state.c_prev = database

    # Skip uninformative questions
    if not st.session_state.clicked_back:
        while st.session_state.index < len(questions_db):
            values = {c.get(st.session_state.index, -1) for c in st.session_state.candidates}
            if len(values) <= 1:
                st.session_state.index += 1
            else:
                break
    else:
        st.session_state.clicked_back = False  # reset flag
        st.session_state.last_spoken = None

    # Main loop - genus:
    if st.session_state.index < len(questions_db):
        q = questions_db[st.session_state.index]
        st.write(f"**Q{st.session_state.index + 1}: {q}**")
        #speak_once(q)
        col1, col2, col3 = st.columns(3)
        #answer = st.text_input("Type your answer here. You can also ask for clarifications \nor ask to hear the question again.")

        if col1.button("Yes", key="y_genus", use_container_width=True):
            st.session_state.c_prev = st.session_state.candidates
            st.session_state.elim_prev = st.session_state.eliminated
            st.session_state.candidates = filter_candidates(st.session_state.index, 1, st.session_state.candidates)
            removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
        if col2.button("No", key="n_genus", use_container_width=True):
            st.session_state.c_prev = st.session_state.candidates
            st.session_state.elim_prev = st.session_state.eliminated
            st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
            removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
            st.session_state.eliminated.append(removed)
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
        if col3.button("I don't know", key="idk_genus", use_container_width=True):
            st.session_state.c_prev = st.session_state.candidates
            st.session_state.elim_prev = st.session_state.eliminated
            st.session_state.candidates = filter_candidates(st.session_state.index, None, st.session_state.candidates)
            st.session_state.eliminated.append([])
            st.session_state.answered.append(st.session_state.index)
            st.session_state.index += 1
            st.rerun()
    else:
        if len(st.session_state.candidates) == 1:
            st.success(f"The specimen is **{st.session_state.candidates[0]['name']}**")
            #speak_once(f"The specimen is {st.session_state.candidates[0]['name']}")

            st.image(st.session_state.candidates[0]['image'], caption="Mosquito morphology")
        elif len(st.session_state.candidates) > 1:
            st.warning("Possible genera:")
            #speak_once(f"We narrowed down the specimen to {len(st.session_state.candidates)} genera.")

            for c in st.session_state.candidates:
                st.write("- " + c["name"])
                st.image(c["image"], caption="Example specimen")
        else:
            st.error("No matching genus found.")
            #speak_once(f"No matching genus found. Try again?")

    if st.button("🔄 Restart", key="restart_genus", use_container_width=True):
        st.session_state.index = 0
        st.session_state.candidates = database
        st.session_state.c_prev = database
        st.session_state.phase = "start"
        st.session_state.last_phase = "genus"
        st.session_state.last_spoken = None
        st.rerun()
    if st.button("Back", key="prev_genus", use_container_width=True) and st.session_state.index > 0:
        st.session_state.index = st.session_state.answered.pop()
        restore = st.session_state.eliminated.pop()
        st.session_state.candidates.extend(e for e in restore if isinstance(e, dict))
        st.session_state.phase = "genus"
        st.session_state.last_phase = "genus"
        st.session_state.clicked_back = True
        st.session_state.last_spoken = None
        st.rerun()

    if len(st.session_state.candidates) == 1 and st.session_state.candidates[0]["name"] == "an Anopheles":
        if st.button("Determine species", key="determine_sp", use_container_width=True):
            st.session_state.index = 0
            st.session_state.candidates = database
            st.session_state.c_prev = database
            st.session_state.phase = "species"

elif st.session_state.phase == "species":
    st.header("Species Identification")


    @st.cache_data(ttl=6)  # for optimization
    def load_data():
        import pandas as pd
        df = pd.read_csv("traits.csv", header=3)
        questions = [col for col in df.columns if
                     col not in ("Species", "Considered", "Probability", "Region", "Image")]

        database = []
        for _, row in df.iterrows():
            entry = {"name": row["Species"], "image": row["Image"], "region": row["Region"]}
            for i, q in enumerate(questions):
                if pd.notna(row[q]) and row[q] != "":
                    entry[i] = int(row[q])
            database.append(entry)

        return questions, database

    # ---- Load questions and database ----
    questions_db, database = load_data()
    qbs = StringIO(
        ',,,,,Wing without a pale spot on basal 0.5 of costa,Maxillary palpus with apex pale,Maxillary palpus with less than 4 pale bands ,3rd main dark area without pale interruption,Wing with I pale spot on upper branch of vein 5,"Wing with abundant pale areas, costa with at least 4 pale spots","Hindtarsomeres 1 to 4, at least, with apical pale bands",Hindtarsomeres 1 and 2 with pale bands at apices only,,"Very large species, abdominal segments II–VII with long lateral tufts of yellowish and dark scales; hindtarsomere 1 largely dark",No pale fringe spot opposite lower branch of vein 5,Hindtarsomere 5 all dark and 4 with much less than apical 0.5 pale,Small to moderate-sized species (wing length 2.7–4.5 mm); wing with upper branch of vein 2 either entirely dark apart from apex or with a few scattered pale scales only,Legs not speckled,Hindtarsomere 3 dark at base,"Maxillary palpus with 4 pale bands, unspeckled; vein 1 of wing with at most 1 pale spot in 2nd main dark area","Midtarsomeres 2 to 4 with pale apices; vein 1 of wing pale at base, basal 0.5 of stem of vein 4 entirely pale",Hindtarsomere 1 narrowly pale or dark at apex; vein 1 of wing with 1 pale spot in 2nd main dark area,Foretarsomere 1 with 2–4 pale rings; stem of vein 4 of wing largely dark,Fore- and midtarsomeres 2 and 3 dark apically; no fringe spot opposite vein 6,"Maxillary palpus smooth with 3 pale bands, the 2 distal ones broad or rarely fused",Maxillary palpus without pale bands; no pale spot at apex of hindtibia or base of hindtarsomere 1,Hindtarsomere 3 dark at base,Base of hindtarsomere 1 broadly pale; no pale fringe spot opposite lower branch of wing vein 5,"Hind tarsomere 1 broadly pale at base, pale area at least as long as broad","Pale streak on hindtibia 1–3 times as long as broad; apical pale band on hindtarsomere 2 narrow, 0.07–0.13 length of segment","3rd main dark area on wing vein 1 with a pale interruption, or with a short extension of the subcostal pale spot into the dark area on vein 1; foretarsomeres 1 to 3 with apical pale bands",Femora and tibiae with at most apical bands only,Maxillary palpus smooth; 2nd main dark area of wing vein 1 well defined and with 2 pale interruptions,Maxillary palpus with 4 pale bands,Maxillary palpus with apical dark spot about equal to or longer than apical pale band; 2nd main dark area on wing vein 1 with 1 pale interruption,"3rd main dark area of wing vein 1 without a pale interruption; abdominal terga fairly heavily clothed with cream or yellowish scales, especially on terga VI and VII",Maxillary palpus not speckled,Foretarsomere 1 not speckled; base of costa with 1 pale spot; stem of wing vein 2 extensively dark,Tarsomeres 1 to 4 with conspicuous pale bands on at least the apices; wing with pale fringe spots up to lower branch of vein 5 or 6,3rd main dark area without pale interruption,Hindtarsomere 2 either with less than apical 0.4 white or else prominently marked with dark and pale bands,Hindtarsomeres 2 to 4 with conspicuous dark and pale rings in addition to apical pale bands; pale fringe spot present opposite vein 6,Foretarsomeres mainly dark with narrow pale rings,Scales on tergum VIII scanty and confined to posterior margin,"Wings with at least some areas of paler scales on costa or vein 1, these being sometimes inconspicuous ",Maxillary palpus and legs entirely dark,"Small species, wing length 3.5 mm or less","General coloration dark brown, scutum not so; cave-dwelling","Maxillary palpus with or without pale bands, dark at apex","Erect head scales broader, scales white on vertex, dark laterally; all regions",Pale and dark areas on wing well contrasted,"Pale areas on wing broader, subcostal pale spot on costa and vein 1",Maxillary palpus unbanded or banding indistinct,Cave-dwelling species; colour and contrast of dark and pale areas on wing variable,"Erect head scales broader, scales white on vertex, dark laterally",Maxillary palpus smooth except at extreme base,Maxillary palpus with pale scales forming more or less definite pale bands; hindtarsomeres 3 and 4 narrowly or broadly pale at apices,Maxillary palpus with apex pale,"Stem of wing vein 4 largely dark, upper branch of vein 5 with one narrow pale area, pale fringe spots absent",Outer 0.5 of costa with 1–3 well-marked pale areas; maxillary palpus not so,Maxillary palpus either with 4 pale bands or if with 3 bands then subapical band much shorter than the apical band,"Dark areas on wing greater than or about equal to pale areas, basal 0.5 of stems of veins 2 and 4 largely dark ","No pale fringe spots posterior to wing vein 3, stem of vein 5 pale except at fork and sometimes narrowly near base","Wing vein 5 with extensive pale areas, upper branch of vein 5 with 2 pale spots",Hindtarsomeres 1 to 4 entirely dark or with a few pale scales at apices of 1 to 3; scutum scales broad,Scutal scales white throughout,Maxillary palpus with 3 pale bands,"Wing with well-contrasting pale and dark areas, basal 0.25 of costa with at least 1 pale area, even if narrow; head scales not so","Costa without a humeral pale spot, subapical pale spot present on costa and vein 1",Wing with no pale fringe spots posterior to vein 3,Wing with well-contrasting pale and dark areas,2nd main dark area of wing vein 1 with at most 1 pale interruption,"Pale bands on maxillary palpus variable in width, distal 2 bands overlapping the joints; upper branch of wing vein 5 with 2 pale spots","Pale and dark areas on wing about equally distributed, humeral and presector pale spots present on costa",Wing vein 6 dark,Basal 0.2 of wing vein 1 entirely pale,"Wings heavily scaled, upstanding scales moderately broad","Basal pale band of maxillary palpus either much shorter than median band, scarcely overlapping base of 3rd segment, or both basal and median pale bands very narrow",Base of costa dark,3rd main dark area without a pale interruption,Abdominal terga without such scales; hindtarsomeres entirely dark or with a few pale scales at apices of hindtarsomeres 1 to 3,2nd main dark area of wing vein 1 with 1 pale interruption,"Pale bands on maxillary palpus mostly narrow, basal band not overlapping base of 3rd segment",No pale fringe spots on wing posterior to vein 3; femora and tibiae inconspicuously speckled,Fork of wing vein 5 dark,Wing length 4.4 mm or more; some decumbent scales present on scutellum as well as scutum,2nd and 3rd main dark areas of wing (median and preapical dark spots) absent from vein 1,"Hindtarsomere 5 entirely dark, hindtarsomere 4 with narrow apical and basal pale bands",Upper branch of wing vein 5 with 2 well-developed pale spots,No pale fringe spot opposite wing vein 6; foretarsomeres 1 to 4 narrowly pale apically only,"Subapical pale band on maxillary palpus broad, overlapping apex of 3rd and base of 4th segment",Basal 0.25 of costa entirely dark,Hindtarsomeres 1 to 4 with well-marked apical pale bands,Scutal fossae and lateral areas of scutum above wing root (supraalar area) without scales,Subapical pale band on maxillary palpus much narrower than apical band,"Hindtarsomeres 1 to 4 with narrow pale bands, as long or shorter than the width of the tarsomeres",Wing vein 3 narrowly dark at ends; scutal scales various,,Maxillary palpus with 3 pale bands,Apical dark band much longer than subapical pale band,"Apical pale band on hindtarsomere 4, and sometimes on hindtarsomeres 2 and 3, extending onto bases of succeeding tarsomeres",2nd main dark area on wing vein 1 with 1 pale interruption; bases of hindtarsomeres 4 and 5 at most narrowly pale,"Base of costa with 2 pale interruptions, 3rd main dark area equal to or narrower than subcostal pale spot",No pale fringe spot opposite vein 6,"Apices of hindtarsomeres 1 to 3 and sometimes 4, distinctly pale banded",Base of costa with 1 or no pale interruption,Wing vein 6 without pale fringe spot and no pale scales at apex,"Scutal scales variable, but decumbent scales confined to at most anterior 0.66 of scutum","Small or moderate species, wing length 2.9 mm or more",Hindtarsomeres 1 and 2 narrowly but distinctly pale apically; preaccessory dark spot present on wing vein 1,3rd main dark area of costa equal to or shorter than subapical pale spot,"Scutal scales on posterior 0.33 of scutum scanty, narrow and yellowish-brown","Small species, wing length 3.0 mm or less",Foretarsomere 4 dark or indistinctly pale at apex; wing usually without pale fringe spot opposite vein 6,3rd main dark area of costa much longer than subapical pale spot,Wing with fork of vein 5 dark,Base of costa with 1 or no pale interruption,"Small or moderate-sized species, wing length 2.9–4.2 mm",Maxillary palpus with 3 pale bands,"Base of costa dark or with small pale spot, base of vein 1 dark",These veins dark,"Subapical pale spot shorter, usually much shorter, than apical dark spot, no pale fringe spot opposite upper branch of vein 5",Pale banding on hindtarsomeres narrow and apical only,"Preaccessory dark spot absent or, if present, shorter or only slightly longer than adjoining pale spots",Basal area of wing vein 1 entirely pale,"Subapical pale band on maxillary palpus much shorter than apical dark band, OR 3rd main dark area longer than subapical pale spot","Small species, wing length 3.2 mm or less","Tip of wing vein 6 with a few pale scales, sometimes with fringe spot present "')
    reader = csv.reader(qbs)
    questions_b = [item for item in reader]
    # ---- Session Initialization ----
    if not st.session_state.species_initialized:
        st.session_state.index = 0
        st.session_state.candidates = database
        st.session_state.species_initialized = True

    st.title("Anopheles Species Identifier")

    if st.session_state.index == 0:
        st.session_state.candidates = database  # Reset candidates before applying prior

    # ---- Main Loop ----
    _, mid, _ = st.columns(3)
    mid.write(f"**Remaining candidates:** {len(st.session_state.candidates)}")
    if not st.session_state.clicked_back:
        while st.session_state.index < len(questions_db):
            # Skip uninformative questions
            values = {c.get(st.session_state.index, -1) for c in st.session_state.candidates}
            num_with_values = sum(1 for c in st.session_state.candidates if st.session_state.index in c)

            if st.session_state.index >= 10:
                if len(values) <= 1 or num_with_values <= 1:
                    st.session_state.index += 1
                else:
                    break
            else:
                if len(values) <= 1 or num_with_values <= 1:
                    st.session_state.index += 1
                else:
                    break
    else:
        st.session_state.clicked_back = False

    # Main loop - Anopheles species
    if st.session_state.index < len(questions_db):
        q = questions_db[st.session_state.index]
        q_b = questions_b[0][st.session_state.index]

        if st.session_state.index == 98:
            st.write(f"**Q98**:")
            col1, col2 = st.columns(2)
            imga = "images/A.png"
            imgb = "images/B.png"
            imgc = "images/C.png"
            imgd = "images/D.png"
            st.session_state.elim_prev = st.session_state.eliminated
            #speak_once("Which of these four images looks most like the scutal scales on the specimen? Select A, B, C or D")

            if col1.button("Scutal scales as in A", key="a", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
                removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()
            if col2.button("Scutal scales as in B", key="b", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.candidates = filter_candidates(st.session_state.index, 1, st.session_state.candidates)
                removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()
            col1.image(imga)
            col2.image(imgb)

            if col1.button("Scutal scales as in C", key="c", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.candidates = filter_candidates(st.session_state.index, 2, st.session_state.candidates)
                removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()
            if col2.button("Scutal scales as in D", key="d", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.candidates = filter_candidates(st.session_state.index, 3, st.session_state.candidates)
                removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()
            col1.image(imgc)
            col2.image(imgd)

        if q_b != "" and q_b is not None and st.session_state.index != 98:  # if there are two statements
            st.write(f"**Q{st.session_state.index}:**")
            st.session_state.u_inp = st.text_input(st.session_state.descriptions.iloc[st.session_state.index], help= "Type your answer or ask a question")

            col1, col2, col3 = st.columns(3)
            print(st.session_state.descriptions)

            if st.session_state.u_inp != "":
                intent,_, answer, answer_score = jev_answer(st.session_state.descriptions.iloc[st.session_state.index],
                                                    st.session_state.u_inp, q, q_b)
                if intent == "respond":
                    st.session_state.c_prev = st.session_state.candidates
                    st.session_state.elim_prev = st.session_state.eliminated
                    if answer == "Answer_A":
                        st.session_state.candidates = filter_candidates(st.session_state.index, 1, st.session_state.candidates)
                    elif answer == "Answer_B":
                        st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
                    else:
                        st.session_state.candidates = filter_candidates(st.session_state.index, None,
                                                                        st.session_state.candidates)
                    removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                    st.session_state.eliminated.append(removed)
                    st.session_state.answered.append(st.session_state.index)
                    st.session_state.index += 1
                    st.session_state.u_inp = ""
                    st.rerun()
                elif intent == "clarify":
                    response = clarify(st.session_state.descriptions.iloc[st.session_state.index], st.session_state.u_inp, "gpt-4o-mini",openai_key)
                    st.write(response)
                    st.session_state.u_inp = ""
                else:
                    st.session_state.u_inp = ""
            #speak_once(f"If {q}, say yes. If instead, {q_b}, say no")

            imgstrunique = "images/" + str(st.session_state.index) + ".png"
            if os.path.exists(imgstrunique):
                st.image(imgstrunique)
            else:
                tr, fal = st.columns(2)
                imgstry = "images/" + str(st.session_state.index) + "y.png"
                imgstrn = "images/" + str(st.session_state.index) + "n.png"
                if os.path.exists(imgstry):
                    tr.image(imgstry)
                if os.path.exists(imgstrn):
                    fal.image(imgstrn)
            if col1.button(q, key=f"q_sp_{st.session_state.index}", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.elim_prev = st.session_state.eliminated

                if st.session_state.index == 3:
                    st.session_state.candidates = filter_candidates(18, 1, st.session_state.candidates)

                st.session_state.candidates = filter_candidates(st.session_state.index, 1, st.session_state.candidates)
                removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()
            if col3.button(f"{q_b}", key=f"qb_sp_{st.session_state.index}", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.elim_prev = st.session_state.eliminated
                if st.session_state.index == 3:
                    st.session_state.candidates = filter_candidates(18, 0, st.session_state.candidates)
                st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
                removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()
            if col2.button("I don't know", key=f"idk_hasqb_sp_{st.session_state.index}", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.elim_prev = st.session_state.eliminated
                st.session_state.candidates = filter_candidates(st.session_state.index, None,
                                                                st.session_state.candidates)
                removed = [[]]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()

        elif st.session_state.index != 98:  # If there's only one statement
            st.write(f"**Q{st.session_state.index + 1}: {q}**")
            #speak_once(f"{q}?")
            st.session_state.u_inp = st.text_input(st.session_state.descriptions.iloc[st.session_state.index],
                                                   help= "Type your answer or ask a question")

            if st.session_state.u_inp != "":
                intent, _, answer, answer_score = jev_answer(st.session_state.descriptions.iloc[st.session_state.index],
                                                             st.session_state.u_inp,
                                                             q,
                                                             q_b)
                if intent == "respond":
                    st.session_state.c_prev = st.session_state.candidates
                    st.session_state.elim_prev = st.session_state.eliminated
                    if answer == "Answer_A":
                        st.session_state.candidates = filter_candidates(st.session_state.index, 1,
                                                                        st.session_state.candidates)
                    elif answer == "Answer_B":
                        st.session_state.candidates = filter_candidates(st.session_state.index, 0,
                                                                        st.session_state.candidates)
                    else:
                        st.session_state.candidates = filter_candidates(st.session_state.index, None,
                                                                        st.session_state.candidates)
                    removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                    st.session_state.eliminated.append(removed)
                    st.session_state.answered.append(st.session_state.index)
                    st.session_state.index += 1
                    st.session_state.u_inp = ""
                    st.rerun()
                elif intent == "clarify":
                    response = clarify(st.session_state.descriptions.iloc[st.session_state.index], st.session_state.u_inp, "gpt-4o-mini", openai_key)
                    st.write(response)
                    st.session_state.u_inp = ""
                else:
                    st.session_state.u_inp = ""

            col1, col2, col3 = st.columns(3)

            imgstrunique = "images/" + str(st.session_state.index) + ".png"
            if os.path.exists(imgstrunique):
                st.image(imgstrunique)

            else:
                tr, fal = st.columns(2)
                imgstry = "images/" + str(st.session_state.index) + "y.png"
                imgstrn = "images/" + str(st.session_state.index) + "n.png"
                if os.path.exists(imgstry):
                    tr.image(imgstry)
                if os.path.exists(imgstrn):
                    fal.image(imgstrn)
            if col1.button("Yes", key=f"y_sp_{st.session_state.index}", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.elim_prev = st.session_state.eliminated
                if st.session_state.index == 3:
                    st.session_state.candidates = filter_candidates(18, 1, st.session_state.candidates)

                st.session_state.candidates = filter_candidates(st.session_state.index, 1, st.session_state.candidates)
                removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()
            if col3.button("No", key=f"n_sp_{st.session_state.index}", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.elim_prev = st.session_state.eliminated
                if st.session_state.index == 3:
                    st.session_state.candidates = filter_candidates(18, 0, st.session_state.candidates)
                st.session_state.candidates = filter_candidates(st.session_state.index, 0, st.session_state.candidates)
                removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()
            if col2.button("I don't know", key=f"idk_sp_{st.session_state.index}", use_container_width=True):
                st.session_state.c_prev = st.session_state.candidates
                st.session_state.elim_prev = st.session_state.eliminated
                st.session_state.candidates = filter_candidates(st.session_state.index, None,
                                                                st.session_state.candidates)
                removed = [[]]
                st.session_state.eliminated.append(removed)
                st.session_state.answered.append(st.session_state.index)
                st.session_state.index += 1
                st.rerun()

    else:
        if len(st.session_state.candidates) == 1:
            st.success(f"The specimen is an Anopheles {st.session_state.candidates[0]['name']}")
            #speak_once(f"The specimen is an Anopheles {st.session_state.candidates[0]['name']}")

        elif len(st.session_state.candidates) > 1:
            st.warning(f"Possible species:")
            #speak_once(f"We narrowed down the specimen to {len(st.session_state.candidates)} species.")

            for c in st.session_state.candidates:
                if pd.notna(c['region']):
                    st.write(f"- **Anopheles {c['name']}**, region: {c['region']}")
                else:
                    st.write(f"- **Anopheles {c['name']}**")
        else:
            st.error("No matching relevant species.")
            #speak_once("No matching species found. Try again?")

    bn1, bn2, bn3 = st.columns(3)
    if bn2.button("Try a different genus", key="restart_all", use_container_width=True):
        st.session_state.index = 0
        st.session_state.candidates = []
        st.session_state.species_initialized = False
        st.session_state.phase = "start"
        st.session_state.last_spoken = None
        st.rerun()

    if st.session_state.index > 0:
        if bn1.button("Previous question", key="prev_spec", use_container_width=True) and st.session_state.answered:
            st.session_state.index = st.session_state.answered.pop()
            restore = st.session_state.eliminated.pop()
            st.session_state.candidates.extend(e for e in restore if isinstance(e, dict))
            st.session_state.clicked_back = True
            st.session_state.last_spoken = None
            st.session_state.phase = "species"
            st.rerun()

    if bn3.button("Restart", key="restart_sp", use_container_width=True):
        st.session_state.index = 0
        st.session_state.phase = "species"
        st.session_state.eliminated = []
        st.session_state.elim_prev = []
        st.session_state.candidates = database
        st.session_state.species_initialized = False
        st.session_state.last_spoken = None
        st.rerun()
    st.markdown(
        "Coetzee, M. Key to the females of Afrotropical Anopheles mosquitoes (Diptera: Culicidae). Malar J 19, 70 (2020). https://doi.org/10.1186/s12936-020-3144-9")
    # if len(st.session_state.others) >0:
    #  if st.button("See rare species"):
    #    for name in :
    #          st.write("- " + name)
