import openai
from openai import OpenAI
import streamlit as st

# Get your key from Streamlit secrets or environment
#openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(
    api_key = st.secrets["OPENAI_API_KEY"]
)

if "index" not in st.session_state:
    st.session_state.u_inp = ""

instructions = """You are given a list of morphological features of mosquitoes and a user’s description of an observed specimen. Your task is to output a vector indicating whether each feature is present in the description.

Use the following rules:
- Output `1` if the feature is explicitly confirmed or strongly implied.
- Output `0` if the feature is explicitly ruled out.
- Output `` if the description doesn’t provide enough information to decide.
- Don't add square brackets or any spaces to the final vector. Only characters it can contain are ",", 1 and 0

### Feature List (in order):

1. Abdominal segments with laterally projecting tufts of scales on segments II–VII
2. Hindtarsus with at least last 2 hindtarsomeres entirely pale
3. Hindtarsomere 5 mainly or entirely dark, hindtarsomere 4 white
4. Legs speckled, sometimes sparsely
5. Wing entirely dark or with pale spots confined to costa and vein 1
6. Wing with at least 1 pale spot on basal 0.5 of costa
7. Maxillary palpus with apex dark
8. Maxillary palpus with 4 pale bands
9. Wing with pale interruption in 3rd main dark area (preapical dark spot) of vein 1, sometimes fused with preceding pale area
10. Wing with 2 pale spots on upper branch of vein 5
11. Wing almost entirely dark, costa without pale spots
12. Hindtarsomeres 1 to 5 entirely dark
13. Hindtarsomeres 1 and 2 with definite pale and dark rings in addition to apical pale bands
14. Hindtarsomeres 3 and 4 all white or narrowly dark basally, 5 all dark or at least basal 0.5 dark
15. Hindtarsomere 5 and about apical 0.5 of 4 pale
16. Legs speckled
17. Maxillary palpus very shaggy and unbanded or with 1–4 irregular narrow pale bands
18. Maxillary palpus with 1–4 pale bands; apex of hindtibia broadly or narrowly pale
19. Hindtarsomere 3 entirely pale
20. Hind tarsomere 1 entirely dark basally or at most with a very narrow band of pale scales not as broad as the width of the tarsomere
21. Apex of hindtibia with a pale streak 3–5 times as long as broad; apical pale band on hindtarsomere 2 0.13–0.4 length of tarsomere
22. Maxillary palpus with 3 pale bands
23. Maxillary palpus with apical 2 pale bands very broad, speckling on palpus segment 3; 2nd main dark area on wing vein 1 with 2 pale interruptions
24. 3rd main dark area of wing vein 1 with a pale interruption, sometimes fused with preceding pale spot; scaling on abdomen very scanty, confined to tergum VIII or rarely VII
25. All tarsi completely dark; wing without pale fringe spots posterior to vein 3
26. 3rd main dark area of vein 1 with a pale interruption, sometimes fused with preceding pale area
27. Maxillary palpus with only apex pale
28. Base of costa with large (presector) pale spot, base of vein 1 pale
29. Subapical pale spot on costa and wing vein 1 about as long as apical dark spot, fringe spots present opposite veins 3, lower branch of 4 and both branches of 5
30. Hindtarsomeres 1 to 4 with pale bands overlapping the joints, at least hindtarsomere 5 pale basally
31. Preaccessory dark spot on wing vein 1 about twice as long as pale spot on either side of it
32. Basal area of wing vein 1 proximal to 1st main dark area, pale with a broad dark spot
33. Subapical pale band on maxillary palpus longer than or equal to apical dark band AND 3rd main dark area of costa and vein 1 equal to or shorter than subapical pale spot
34. Moderate-sized species, wing length more than 3.3 mm
35. Tip of wing vein 6 dark with no fringe spot


### Example Input:
"The mosquito has a dark wing with pale spots only on the leading edge, and the maxillary palpus shows 4 pale bands."

### Expected Output:
,,,,1,,,1,...,


Return a vector with values in the same order as the feature list.

### Additional context:
- tarsus: leg
- tarsomere: leg segment
- spots may be called bands on ocassion
- consider 0.5 as roughly around half
- the term apical might be described as distal
- the wing contains veins that, from the top down are named: costa, sub-costa, vein 1, vein 2, vein 3... vein 6
- veins 5 and 6 might be described as "posterior veins"
- the costa can be called the "top vein"
- feature 24 (3rd main dark area of wing vein 1 with a pale interruption, sometimes fused with preceding pale spot) can be described as a "gambiae gap"
- Remember not to add spaces to the final vector.
"""
# User input
user_input = st.text_area("Describe the mosquito in detail:", placeholder="The wings are pale, the first main dark area of the costa has a pale interruption...")

if st.button("Submit"):
        st.session_state.u_inp = user_input
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                 {"role": "system", "content": instructions},
                 {"role": "user", "content": user_input}
            ]
         )
        st.write(response.choices[0].message.content)
        st.rerun()
# user_input = st.text_area("Describe the mosquito in detail:", placeholder="The wings are pale, the first main dark area of the costa has a pale interruption...")
# API call
#response = client.chat.completions.create(
#    model="gpt-4o-mini",
#    messages=[
#        {"role": "system", "content": instructions},
#        {"role": "user", "content": user_input}
#    ]
#)
#st.write(response.choices[0].message.content)
