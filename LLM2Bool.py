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

instructions = instructions = """You are given a morphological feature of a mosquito, and a user’s description of an observed specimen. Your task is to output a single integer indicating whether the given feature is present in the description.

Use the following rules:
- Write `1` if the feature is explicitly confirmed or strongly implied.
- Write `0` if the feature is explicitly ruled out, or strongly implied to be false.
- Write `None` if the description doesn’t provide enough information to decide.
- Don't add square brackets or any spaces to the final output. Only characters it can contain are "None", 1 or 0
- Remember not to add spaces to the final output.
- don't add any other text or explanations

### Example Input:
"Feature: Wing entirely pale; Description: The mosquito has a dark wing with pale spots only on the leading edge"

### Expected Output for this example:
0

### Additional context:
- tarsus: most distal portion of the leg
- tarsomere: segment of the last portion of the leg
- spots may be called bands on ocassion
- consider 0.5 as roughly around half
- the term "apical" might be described as "distal"
- the wing contains veins that, from the top down are named: costa, sub-costa, vein 1, vein 2, vein 3, vein 4, vein 5 and vein 6
- veins 5 and 6 might be described as "posterior veins"
- the costa can be called the "top vein"
- the feature "3rd main dark area of wing vein 1 with a pale interruption, sometimes fused with preceding pale spot)" can be described as a 'gambiae gap'
"""
def get_feature_bool(user_input: str, model, question: str) -> str:
    concatenated_input = "Feature: " + question + "; Description: " + user_input
    response = client.chat.completions.create(
            model=model,
            messages=[
                 {"role": "system", "content": instructions},
                 {"role": "user", "content": concatenated_input}
            ]
         )
    return response.choices[0].message.content
