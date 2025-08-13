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

instructions = instructions = """You are given a list of morphological features of mosquitoes and a user’s description of an observed specimen. Your task is to output a vector indicating whether each feature is present in the description.

Use the following rules:
- Write `1` if the feature is confirmed or strongly implied.
- Write `0` if the feature is ruled out.
- Write `None` if the description doesn’t provide enough information to decide.
- Separate the corresponding value for each feature with a comma.
- Don't add square brackets or any spaces to the final vector. Only characters it can contain are `None`, 1 and 0
- Remember not to add spaces to the final vector.
- verify that the output consists of 0s, 1s and empty values, all separated by commas
- if there are no usable features in the input, return the empty vector: ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
- don't add any other text or explanations
- before outputting anything, double check whether it should instead be `None`.
- Most of the elements should be `None`

### Feature List (in order):

1. Abdominal segments with laterally projecting tufts of scales on segments II-VII?
2. Hindtarsus with at least last 2 hindtarsomeres entirely pale?
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
15. Moderate-sized species; abdominal scale-tufts short and dark; 0.5 or more of hindtarsomere 1 pale
16. Pale fringe spot present opposite lower branch of vein 5
17. Hindtarsomere 5 and about apical 0.5 of 4 pale
18. Very small species (wing length 2.5-2.8 mm); wing with upper branch of vein 2 largely pale
19. Legs speckled
20. Hindtarsomeres 3 to 5 entirely pale
21. Maxillary palpus with 3 pale bands, usually with some speckling; vein 1 of wing with 2 pale spots in 2nd main dark area (median dark spot)
22. Midtarsomeres 2 to 4 entirely dark; vein 1 of wing dark at base, basal 0.5 of stem of vein 4 with small pale areas
23. Hindtarsomere 1 broadly pale at apex; vein 1 of wing with 2 pale spots in 2nd main dark area
24. Foretarsomere 1 with 5-9 pale rings; stem of vein 4 of wing largely pale
25. Fore- and midtarsomeres 2 and 3 pale at apex; wing with fringe spot opposite vein 6
26. Maxillary palpus very shaggy and unbanded or with 1-4 irregular narrow pale bands
27. Maxillary palpus with 1-4 pale bands; apex of hindtibia broadly or narrowly pale
28. Hindtarsomere 3 entirely pale
29. Base of hindtarsomere 1 dark; pale fringe spot present opposite lower branch of wing vein 5
30. Hind tarsomere 1 entirely dark basally or at most with a very narrow band of pale scales not as broad as the width of the tarsomere
31. Apex of hindtibia with a pale streak 3-5 times as long as broad; apical pale band on hindtarsomere 2 0.13-0.4 length of tarsomere
32. 3rd main dark area on wing vein 1 without a pale interruption; foretarsomeres 1 to 3 usually without distinct apical pale bands
33. Femora and tibiae speckled
34. Maxillary palpus shaggy; costa and vein 1 of wing without usual main dark areas
35. Maxillary palpus with 3 pale bands
36. Maxillary palpus with apical 2 pale bands very broad, speckling on palpus segment 3; 2nd main dark area on wing vein 1 with 2 pale interruptions
37. 3rd main dark area of wing vein 1 with a pale interruption, sometimes fused with preceding pale spot; scaling on abdomen very scanty, confined to tergum VIII or rarely VII
38. Maxillary palpus speckled
39. Foretarsomere 1 with some speckling; base of costa with 2 pale spots; stem of wing vein 2 entirely pale
40. All tarsi completely dark; wing without pale fringe spots posterior to vein 3
41. 3rd main dark area of vein 1 with a pale interruption, sometimes fused with preceding pale area
42. Hindtarsomere 2 with about apical 0.4 to 0.5 white and the rest dark
43. Hindtarsomeres 2 to 4 with apical pale rings and otherwise dark except for 1 to 2 pale spots; no pale fringe spot opposite wing vein 6
44. Foretarsomeres mainly pale with narrow dark markings
45. Scales on abdominal tergum VIII dense and distributed over whole tergum, sometimes with a few scales on lateral borders of tergum VII
46. Wings entirely dark or unicolorous
47. Maxillary palpus with 2 well-marked pale bands; hindfemur and hindtibia narrowly pale at apex
48. Large species, wing length 4 mm or more
49. Very pale brown species with glossy scutum; semi-arid regions only
50. Maxillary palpus with 2 to 3 pale bands, pale at apex (sometimes indistinct)
51. Erect head scales narrow, rod-like, all scales yellowish throughout; semi-arid regions only
52. Pale and dark areas on wing poorly contrasted; semi-arid regions only
53. Pale areas on wing very narrow, subcostal pale spot present on costa only; cave-dwelling
54. Maxillary palpus with 3 pale bands, dark at apex
55. Semi-arid regions; pale brown species with poorly contrasting light and dark areas on wing
56. Erect head scales narrow, rod-like, all scales yellowish throughout
57. Maxillary palpus shaggy to near tip
58. Maxillary palpus entirely dark; hindtarsomeres 3 and 4 dark or narrowly pale at apices
59. Maxillary palpus with apex dark, sometimes only narrowly so
60. Stem of wing vein 4 largely pale, upper branch of vein 5 with 2 pale spots or largely pale, fringe spots present opposite vein 4 and upper branch of vein 5
61. Costa entirely dark except for a few indistinct pale scales subapically; maxillary palpus with a broad apical pale band and otherwise dark except for a narrow basal pale band
62. Maxillary palpus with 3 pale bands, subapical band broad and about equal in length to apical band
63. Wing, apart from costa, generally very pale, basal 0.5 of stems of veins 2 and 4 entirely pale
64. Pale fringe spots present opposite all veins from wing apex to vein 5, stem of vein 5 broadly dark near base
65. Wing vein 5 entirely dark except for a single pale spot on the upper branch
66. Hindtarsomeres 1 to 4 with distinct apical pale bands; scutum clothed with very narrow scales
67. Median scutal scales yellowish or bronze, white elsewhere
68. Maxillary palpus entirely dark or without distinct pale bands
69. Small, pale brown species, pale patches on wing indistinct, basal 0.25-0.5 of costa entirely dark; head scales narrow and yellowish
70. Costa with humeral pale spot, no subapical (preapical) pale spot on costa and vein 1
71. Wing with pale fringe spots opposite all veins except vein 6
72. Wing generally pale, contrast between pale and dark areas, apart from costa and vein 1, poorly defined
73. 2nd main dark area of wing vein 1 with 2 pale interruptions
74. Pale bands on maxillary palpus very narrow, at apices of segments 2 to 4 and not overlapping the joints; upper branch of wing vein 5 with a single pale spot
75. Wing, apart from costa and vein 1, predominantly dark, no pale spots on basal 0.25 of costa
76. Wing vein 6 with proximal pale spot
77. Basal 0.2 of wing vein 1 either dark or with a proximal pale patch not extending to base
78. Wings scantily scaled, all wing scales very narrow
79. Basal pale band of maxillary palpus about equal to or slightly shorter than median band, broadly overlapping base of 3rd segment
80. Base of costa pale
81. 3rd main dark area of wing vein 1 with a pale interruption
82. Abdominal terga clothed with yellowish scales; hindtarsomeres 1 to 4 with broad apical pale bands
83. Second main dark area of wing vein 1 with 2 pale interruptions
84. Pale bands on maxillary palpus broad, basal band overlapping base of 3rd segment
85. Pale fringe spots on wing present opposite veins posterior to vein 3, sometimes including vein 6; femora and tibiae not speckled
86. Stem of wing vein 5 pale, at and adjacent to the fork
87. Wing length 4 mm or less; decumbent scutal scales not extending onto scutellum
88. 2nd and 3rd main dark areas present on vein 1
89. Hindtarsomere 5 entirely pale, hindtarsomere 4 with broad apical and basal pale bands
90. Upper branch of wing vein 5 with 1 pale spot, sometimes a vestigial 2nd pale spot
91. Pale fringe spot present opposite wing vein 6; foretarsomeres 1 to 4 with conspicuous basal and apical pale bands
92. Subapical pale band on maxillary palpus very narrow, confined to apex of 3rd segment
93. Wing with base of costa with 2 pale interruptions
94. Hindtarsomeres either all dark or with pale bands on tarsomeres 1 and 2 only
95. Scutal fossae and lateral areas of scutum above wing root (supraalar area) with scattered or abundant broadish scales
96. Subapical pale band on maxillary palpus about equal to or slightly shorter than apical band
97. Apical pale bands on hindtarsomeres 1 to 4 very broad, at least twice the apical width of the tarsomeres
98. Wing vein 3 largely dark or broadly dark at either end; scutal scales very narrow and golden
99. Scutal scales as in (A, B, C or D):
100. Maxillary palpus with only apical pale band
101. Subapical pale band on maxillary palpus broad, about equal to or longer than apical dark band
102. Bases of hindtarsomeres dark
103. 2nd main dark area on wing vein 1 with 2 pale interruptions; bases of hindtarsomeres 4 and 5 broadly or narrowly pale
104. Base of costa with 1 pale interruption, 3rd main dark area on costa and vein 1 much broader than subcostal pale spot
105. Pale fringe spot present opposite wing vein 6
106. Apices of hindtarsomeres 3 and 4 dark or at most with a few pale scales
107. Base of costa with 2 pale interruptions
108. Wing vein 6 either with pale fringe spot or with pale scales at apex of vein
109. Scutal scales fairly broad, extending over whole scutum and onto scutellum
110. Very small species, wing length 2.8 mm or less
111. Hindtarsomeres entirely dark; preaccessory dark spot on wing vein 1 usually absent
112. 3rd main dark area much longer than subapical pale spot
113. Scutal scales broadish and white, only slightly less dense on posterior 0.33 of scutum than anteriorly, and extending onto scutellum
114. Moderate-sized species, wing length more than 3.2 mm
115. Foretarsomere 4 with well-marked apical pale band; wing with fringe spot opposite vein 6
116. 3rd main dark area of costa equal to or shorter than subapical pale spot
117. Wing with fork of vein 5 pale
118. Base of costa with two pale interruptions
119. Small species, wing length about 2.4-3.3 mm
120. Maxillary palpus with only apex pale
121. Base of costa with large (presector) pale spot, base of vein 1 pale
122. Lower branch of wing vein 2 and upper branch of vein 4 with distinct pale spots
123. Subapical pale spot on costa and wing vein 1 about as long as apical dark spot, fringe spots present opposite veins 3, lower branch of 4 and both branches of 5
124. Hindtarsomeres 1 to 4 with pale bands overlapping the joints, at least hindtarsomere 5 pale basally
125. Preaccessory dark spot on wing vein 1 about twice as long as pale spot on either side of it
126. Basal area of wing vein 1 proximal to 1st main dark area, pale with a broad dark spot
127. Subapical pale band on maxillary palpus longer than or equal to apical dark band AND 3rd main dark area of costa and vein 1 equal to or shorter than subapical pale spot
128. Moderate-sized species, wing length more than 3.3 mm
129. Tip of wing vein 6 dark with no fringe spot

### Example Input:
'The mosquito has tufts on abdominal segments 4-7. Its wing is completely dark, and the costa has no spots.'

### Expected Output for this example:
1,,,,,,,,,,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

Return a vector with values in the same order as the feature list. 

### Additional context:
- tarsus: most distal portion of the leg
- tarsomere: segment of the last portion of the leg
- spots may be called bands on ocassion
- consider 0.5 as roughly around half
- consider "white" and "pale" as synonyms
- consider "dark" and "black" as synonyms
- the term "apical" might be described as "distal"
- the wing contains veins that, from the top down are named: costa, sub-costa, vein 1, vein 2, vein 3, vein 4, vein 5 and vein 6
- veins 5 and 6 might be described as "posterior veins"
- the costa can be called the "top vein"
- the feature "3rd main dark area of wing vein 1 with a pale interruption, sometimes fused with preceding pale spot" can be described as a "gambiae gap"
"""
def get_feature_vector(user_input: str, model = "gpt-4.1-nano") -> str:
    response = client.chat.completions.create(
            model=model,
            messages=[
                 {"role": "system", "content": instructions},
                 {"role": "user", "content": user_input}
            ]
         )
    return response.choices[0].message.content
# User input
#user_input = st.text_area("Describe the mosquito in detail:", placeholder="The wings are pale, the first main dark area of the costa has a pale interruption...")

#if st.button("Submit"):
#        st.session_state.u_inp = user_input
    
#        response = client.chat.completions.create(
#            model="gpt-4o-mini",
#            messages=[
#                 {"role": "system", "content": instructions},
#                 {"role": "user", "content": user_input}
#            ]
#         )
#        st.session_state.result= response.choices[0].message.content
#        st.rerun()
#st.write(st.session_state.result)

