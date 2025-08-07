import openai
from openai import OpenAI
import streamlit as st

# Get your key from Streamlit secrets or environment
#openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(
    api_key = st.secrets["OPENAI_API_KEY"]
)

#if "u_inp" not in st.session_state:
#    st.session_state.u_inp = ""
#    st.session_state.result = ""

instructions = instructions = """You are given a morphological feature of a mosquito, and a user’s description of an observed specimen. Your task is to output a single integer indicating whether the given feature is true in the description.

Use the following rules:
- Write `1` if the feature is explicitly confirmed or strongly implied.
- Write `0` if the feature is explicitly ruled out, or strongly implied to be false.
- Write `None` if the description doesn’t provide enough information to decide.
- Don't add square brackets or any spaces to the final output. Only characters it can contain are "None", 1 or 0
- don't add any other text or explanations
- When unsure, output `None`

### First Example 
Input: "Feature: Wing entirely pale; Description: The mosquito has a dark wing with pale spots only on the leading edge"

Expected Output: `0`

## Second Example
Input: "Feature: Wing entirely pale; Description: The mosquito's legs are not speckled"

Expected output: `None`

### Additional context:
- "distal" means farther away from the mosquito's body
- "proximal" means closer to the mosquito's body
- each leg is named, from front to back: fore leg, mid leg, hind leg
- all legs have three portions, from proximal to distal: femur, tibia, tarsus
- each tarsus is made up of 5 segments called "tarsomeres", numbered 1 to 5, from proximal to distal
- hindtarsus or hind tarsus: distal portion of the hind leg
- hindtarsomere or hind tarsomere: segment of the hindtarsus
- midtarsus or mid tarsus: last portion of the middle leg
- midtarsomere or mid tarsomere: segment of the midtarsus
- foretarsus or fore tarsus: last portion of the front leg
- foretarsomere or fore tarsomere: segment of the foretarsus
- spots may be called "bands"
- consider "pale" and "white" as synonyms
- consider "dark" and "black" as synonyms
- the term "apical" might be described as "distal"
- consider the "apex" as the most distal part of the body part, or the "tip"
- "maxillary palpus", "palp" and "palpus" are synonyms, meaning each of the two projections from the mosquito's head, at either side of the proboscis.
- The antennae are not the same as the palpus, but they also project from the mosquito's head
- the wing contains veins that, from the top down are named: costa, sub-costa, vein 1, vein 2, vein 3, vein 4, vein 5 and vein 6
- veins 5 and 6 might be described as "posterior veins"
- the costa can be called the "top vein"
- vein 1 and 2 can be called "radial"
- vein 3 and 4 can be called "medial"
- vein 5 can be called "cubital"
- vein 6 can be called "anal"
- the feature "3rd main dark area of wing vein 1 with a pale interruption, sometimes fused with preceding pale spot)" can be described as a 'gambiae gap'

### Final check
before outputting `0`, double check if it should be `None` instead. A majority of the time, the output should be `None`

"""
def get_feature_bool(user_input: str, question: str, model="gpt-4.1-nano") -> str:
    concatenated_input = "Feature: " + question + "; Description: " + user_input
    response = client.chat.completions.create(
            model=model,
            messages=[
                 {"role": "system", "content": instructions},
                 {"role": "user", "content": concatenated_input}
            ]
         )
    return response.choices[0].message.content
