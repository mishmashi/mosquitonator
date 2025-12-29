import openai
from openai import OpenAI
import streamlit as st

client = OpenAI(
    api_key = st.secrets["OPENAI_API_KEY"]
)

instructions = instructions = """You are given a list of morphological features of mosquitoes and a user’s description of an observed specimen. Your task is to output a vector indicating which features are present in the description.

Use the following rules:
- For each element, write `A` if the description matches only the feature marked as `A`, and doesn't match feature `B`.
- Write `B` for that element if the description doesn't match feature `A`, and instead matches the feature marked as `B`.
- Write `nan` for that element if the description doesn't match either feature.
- Write `nan`for that element if the description matches both features.
- Write `nan` for that element if the input doesn’t provide enough information to decide.
- Separate the corresponding value for each feature with a comma.
- Don't add square brackets or any spaces to the final vector. Only characters it can contain are `nan`, `A` and `B`
- verify that the output consists of `A`, `B` and `nan`, all separated by commas
- if there are no usable features in the input, return a vector with the format `nan,nan,...,nan`
- don't add any other text or explanations
- before deciding the value for any given feature, double check whether it should instead be `nan`.
- Most of the elements should be `nan`
- Return a vector with values in the same order as the feature list.

### Feature List (in order):

0- A: Abdominal segments with laterally projecting tufts of scales on segments II-VII, B: Abdominal segments not with laterally projecting tufts of scales on segments II-VII
1- A: Hindtarsus with at least last 2 hindtarsomeres entirely pale, B: Hindtarsus not with at least last 2 hindtarsomeres entirely pale
2- A: Hindtarsomere 5 mainly or entirely dark, hindtarsomere 4 white, B: Hindtarsomere 5 not mainly nor entirely dark, or hindtarsomere 4 not white
3- A: Legs speckled, sometimes sparsely, B: Legs not speckled
4- A: Wing entirely dark or with pale spots confined to costa and vein 1, B: Wing not entirely dark, nor with pale spots confined to costa and vein 1
5- A: Wing with at least 1 pale spot on basal 0.5 of costa, B: Wing without a pale spot on basal 0.5 of costa
6- A: Maxillary palpus with apex dark, B: Maxillary palpus with apex pale
7- A: Maxillary palpus with 4 pale bands, B: Maxillary palpus with less than 4 pale bands
8- A: Wing with pale interruption in 3rd main dark area (preapical dark spot) of vein 1, sometimes fused with preceding pale area, B: 3rd main dark area without pale interruption
9- A: Wing with 2 pale spots on upper branch of vein 5, B: Wing with I pale spot on upper branch of vein 5
10- A: Wing almost entirely dark, costa without pale spots, B: Wing with abundant pale areas, costa with at least 4 pale spots
11- A: Hindtarsomeres 1 to 5 entirely dark, B: Hindtarsomeres 1 to 4, at least, with apical pale bands
12- A: Hindtarsomeres 1 and 2 with definite pale and dark rings in addition to apical pale bands, B: Hindtarsomeres 1 and 2 with pale bands at apices only
13- A: Hindtarsomeres 3 and 4 all white or narrowly dark basally, 5 all dark or at least basal 0.5 dark, B: Hindtarsomeres 3 and 4 not all white nor narrowly dark basally, hindtarsomere 5  not all dark nor with basal 0.5 dark
14- A: Moderate-sized species; abdominal scale-tufts short and dark; 0.5 or more of hindtarsomere 1 pale, B: Very large species, abdominal segments IIñVII with long lateral tufts of yellowish and dark scales; hindtarsomere 1 largely dark
15- A: Pale fringe spot present opposite lower branch of vein 5, B: No pale fringe spot opposite lower branch of vein 5
16- A: Hindtarsomere 5 and about apical 0.5 of 4 pale, B: Hindtarsomere 5 all dark and 4 with much less than apical 0.5 pale
17- A: Very small species (wing length 2.5-2.8 mm); wing with upper branch of vein 2 largely pale, B: Small to moderate-sized species (wing length 2.7ñ4.5 mm); wing with upper branch of vein 2 either entirely dark apart from apex or with a few scattered pale scales only
18- A: Legs speckled, B: Legs not speckled
19- A: Hindtarsomeres 3 to 5 entirely pale, B: Hindtarsomere 3 dark at base
20- A: Maxillary palpus with 3 pale bands, usually with some speckling; vein 1 of wing with 2 pale spots in 2nd main dark area (median dark spot), B: Maxillary palpus with 4 pale bands, unspeckled; vein 1 of wing with at most 1 pale spot in 2nd main dark area
21- A: Midtarsomeres 2 to 4 entirely dark; vein 1 of wing dark at base, basal 0.5 of stem of vein 4 with small pale areas, B: Midtarsomeres 2 to 4 with pale apices; vein 1 of wing pale at base, basal 0.5 of stem of vein 4 entirely pale
22- A: Hindtarsomere 1 broadly pale at apex; vein 1 of wing with 2 pale spots in 2nd main dark area, B: Hindtarsomere 1 narrowly pale or dark at apex; vein 1 of wing with 1 pale spot in 2nd main dark area
23- A: Foretarsomere 1 with 5-9 pale rings; stem of vein 4 of wing largely pale, B: Foretarsomere 1 with 2-4 pale rings; stem of vein 4 of wing largely dark
24- A: Fore- and midtarsomeres 2 and 3 pale at apex; wing with fringe spot opposite vein 6, B: Fore- and midtarsomeres 2 and 3 dark apically; no fringe spot opposite vein 6
25- A: Maxillary palpus very shaggy and unbanded or with 1-4 irregular narrow pale bands, B: Maxillary palpus smooth with 3 pale bands, the 2 distal ones broad or rarely fused
26- A: Maxillary palpus with 1-4 pale bands; apex of hindtibia broadly or narrowly pale, B: Maxillary palpus without pale bands; no pale spot at apex of hindtibia or base of hindtarsomere 1
27- A: Hindtarsomere 3 entirely pale, B: Hindtarsomere 3 dark at base
28- A: Base of hindtarsomere 1 dark; pale fringe spot present opposite lower branch of wing vein 5, B: Base of hindtarsomere 1 broadly pale; no pale fringe spot opposite lower branch of wing vein 5
29- A: Hind tarsomere 1 entirely dark basally or at most with a very narrow band of pale scales not as broad as the width of the tarsomere, B: Hind tarsomere 1 broadly pale at base, pale area at least as long as broad
30- A: Apex of hindtibia with a pale streak 3-5 times as long as broad; apical pale band on hindtarsomere 2 0.13-0.4 length of tarsomere, B: Pale streak on hindtibia 1ñ3 times as long as broad; apical pale band on hindtarsomere 2 narrow, 0.07ñ0.13 length of segment
31- A: 3rd main dark area on wing vein 1 without a pale interruption; foretarsomeres 1 to 3 usually without distinct apical pale bands, B: 3rd main dark area on wing vein 1 with a pale interruption, or with a short extension of the subcostal pale spot into the dark area on vein 1; foretarsomeres 1 to 3 with apical pale bands
32- A: Femora and tibiae speckled, B: Femora and tibiae with at most apical bands only
33- A: Maxillary palpus shaggy; costa and vein 1 of wing without usual main dark areas, B: Maxillary palpus smooth; 2nd main dark area of wing vein 1 well defined and with 2 pale interruptions
34- A: Maxillary palpus with 3 pale bands, B: Maxillary palpus with 4 pale bands
35- A: Maxillary palpus with apical 2 pale bands very broad, speckling on palpus segment 3; 2nd main dark area on wing vein 1 with 2 pale interruptions, B: Maxillary palpus with apical dark spot about equal to or longer than apical pale band; 2nd main dark area on wing vein 1 with 1 pale interruption
36- A: 3rd main dark area of wing vein 1 with a pale interruption, sometimes fused with preceding pale spot; scaling on abdomen very scanty, confined to tergum VIII or rarely VII, B: 3rd main dark area of wing vein 1 without a pale interruption; abdominal terga fairly heavily clothed with cream or yellowish scales, especially on terga VI and VII
37- A: Maxillary palpus speckled, B: Maxillary palpus not speckled
38- A: Foretarsomere 1 with some speckling; base of costa with 2 pale spots; stem of wing vein 2 entirely pale, B: Foretarsomere 1 not speckled; base of costa with 1 pale spot; stem of wing vein 2 extensively dark
39- A: All tarsi completely dark; wing without pale fringe spots posterior to vein 3, B: Tarsomeres 1 to 4 with conspicuous pale bands on at least the apices; wing with pale fringe spots up to lower branch of vein 5 or 6
40- A: 3rd main dark area of vein 1 with a pale interruption, sometimes fused with preceding pale area, B: 3rd main dark area without pale interruption
41- A: Hindtarsomere 2 with about apical 0.4 to 0.5 white and the rest dark, B: Hindtarsomere 2 either with less than apical 0.4 white or else prominently marked with dark and pale bands
42- A: Hindtarsomeres 2 to 4 with apical pale rings and otherwise dark except for 1 to 2 pale spots; no pale fringe spot opposite wing vein 6, B: Hindtarsomeres 2 to 4 with conspicuous dark and pale rings in addition to apical pale bands; pale fringe spot present opposite vein 6
43- A: Foretarsomeres mainly pale with narrow dark markings, B: Foretarsomeres mainly dark with narrow pale rings
44- A: Scales on abdominal tergum VIII dense and distributed over whole tergum, sometimes with a few scales on lateral borders of tergum VII, B: Scales on tergum VIII scanty and confined to posterior margin
45- A: Wings entirely dark or unicolorous, B: Wings with at least some areas of paler scales on costa or vein 1, these being sometimes inconspicuous
46- A: Maxillary palpus with 2 well-marked pale bands; hindfemur and hindtibia narrowly pale at apex, B: Maxillary palpus and legs entirely dark
47- A: Large species, wing length 4 mm or more, B: Small species, wing length 3.5 mm or less
48- A: Very pale brown species with glossy scutum; semi-arid regions only, B: General coloration dark brown, scutum not so; cave-dwelling
49- A: Maxillary palpus with 2 to 3 pale bands, pale at apex (sometimes indistinct), B: Maxillary palpus with or without pale bands, dark at apex
50- A: Erect head scales narrow, rod-like, all scales yellowish throughout; semi-arid regions only, B: Erect head scales broader, scales white on vertex, dark laterally; all regions
51- A: Pale and dark areas on wing poorly contrasted; semi-arid regions only, B: Pale and dark areas on wing well contrasted
52- A: Pale areas on wing very narrow, subcostal pale spot present on costa only; cave-dwelling, B: Pale areas on wing broader, subcostal pale spot on costa and vein 1
53- A: Maxillary palpus with 3 pale bands, dark at apex, B: Maxillary palpus unbanded or banding indistinct
54- A: Semi-arid regions; pale brown species with poorly contrasting light and dark areas on wing, B: Cave-dwelling species; colour and contrast of dark and pale areas on wing variable
55- A: Erect head scales narrow, rod-like, all scales yellowish throughout, B: Erect head scales broader, scales white on vertex, dark laterally
56- A: Maxillary palpus shaggy to near tip, B: Maxillary palpus smooth except at extreme base
57- A: Maxillary palpus entirely dark; hindtarsomeres 3 and 4 dark or narrowly pale at apices, B: Maxillary palpus with pale scales forming more or less definite pale bands; hindtarsomeres 3 and 4 narrowly or broadly pale at apices
58- A: Maxillary palpus with apex dark, sometimes only narrowly so, B: Maxillary palpus with apex pale
59- A: Stem of wing vein 4 largely pale, upper branch of vein 5 with 2 pale spots or largely pale, fringe spots present opposite vein 4 and upper branch of vein 5, B: Stem of wing vein 4 largely dark, upper branch of vein 5 with one narrow pale area, pale fringe spots absent
60- A: Costa entirely dark except for a few indistinct pale scales subapically; maxillary palpus with a broad apical pale band and otherwise dark except for a narrow basal pale band, B: Outer 0.5 of costa with 1ñ3 well-marked pale areas; maxillary palpus not so
61- A: Maxillary palpus with 3 pale bands, subapical band broad and about equal in length to apical band, B: Maxillary palpus either with 4 pale bands or if with 3 bands then subapical band much shorter than the apical band
62- A: Wing, apart from costa, generally very pale, basal 0.5 of stems of veins 2 and 4 entirely pale, B: Dark areas on wing greater than or about equal to pale areas, basal 0.5 of stems of veins 2 and 4 largely dark
63- A: Pale fringe spots present opposite all veins from wing apex to vein 5, stem of vein 5 broadly dark near base, B: No pale fringe spots posterior to wing vein 3, stem of vein 5 pale except at fork and sometimes narrowly near base
64- A: Wing vein 5 entirely dark except for a single pale spot on the upper branch, B: Wing vein 5 with extensive pale areas, upper branch of vein 5 with 2 pale spots
65- A: Hindtarsomeres 1 to 4 with distinct apical pale bands; scutum clothed with very narrow scales, B: Hindtarsomeres 1 to 4 entirely dark or with a few pale scales at apices of 1 to 3; scutum scales broad
66- A: Median scutal scales yellowish or bronze, white elsewhere, B: Scutal scales white throughout
67- A: Maxillary palpus entirely dark or without distinct pale bands, B: Maxillary palpus with 3 pale bands
68- A: Small, pale brown species, pale patches on wing indistinct, basal 0.25-0.5 of costa entirely dark; head scales narrow and yellowish, B: Wing with well-contrasting pale and dark areas, basal 0.25 of costa with at least 1 pale area, even if narrow; head scales not so
69- A: Costa with humeral pale spot, no subapical (preapical) pale spot on costa and vein 1, B: Costa without a humeral pale spot, subapical pale spot present on costa and vein 1
70- A: Wing with pale fringe spots opposite all veins except vein 6, B: Wing with no pale fringe spots posterior to vein 3
71- A: Wing generally pale, contrast between pale and dark areas, apart from costa and vein 1, poorly defined, B: Wing with well-contrasting pale and dark areas
72- A: 2nd main dark area of wing vein 1 with 2 pale interruptions, B: 2nd main dark area of wing vein 1 with at most 1 pale interruption
73- A: Pale bands on maxillary palpus very narrow, at apices of segments 2 to 4 and not overlapping the joints; upper branch of wing vein 5 with a single pale spot, B: Pale bands on maxillary palpus variable in width, distal 2 bands overlapping the joints; upper branch of wing vein 5 with 2 pale spots
74- A: Wing, apart from costa and vein 1, predominantly dark, no pale spots on basal 0.25 of costa, B: Pale and dark areas on wing about equally distributed, humeral and presector pale spots present on costa
75- A: Wing vein 6 with proximal pale spot, B: Wing vein 6 dark
76- A: Basal 0.2 of wing vein 1 either dark or with a proximal pale patch not extending to base, B: Basal 0.2 of wing vein 1 entirely pale
77- A: Wings scantily scaled, all wing scales very narrow, B: Wings heavily scaled, upstanding scales moderately broad
78- A: Basal pale band of maxillary palpus about equal to or slightly shorter than median band, broadly overlapping base of 3rd segment, B: Basal pale band of maxillary palpus either much shorter than median band, scarcely overlapping base of 3rd segment, or both basal and median pale bands very narrow
79- A: Base of costa pale, B: Base of costa dark
80- A: 3rd main dark area of wing vein 1 with a pale interruption, B: 3rd main dark area without a pale interruption
81- A: Abdominal terga clothed with yellowish scales; hindtarsomeres 1 to 4 with broad apical pale bands, B: Abdominal terga without such scales; hindtarsomeres entirely dark or with a few pale scales at apices of hindtarsomeres 1 to 3
82- A: Second main dark area of wing vein 1 with 2 pale interruptions, B: 2nd main dark area of wing vein 1 with 1 pale interruption
83- A: Pale bands on maxillary palpus broad, basal band overlapping base of 3rd segment, B: Pale bands on maxillary palpus mostly narrow, basal band not overlapping base of 3rd segment
84- A: Pale fringe spots on wing present opposite veins posterior to vein 3, sometimes including vein 6; femora and tibiae not speckled, B: No pale fringe spots on wing posterior to vein 3; femora and tibiae inconspicuously speckled
85- A: Stem of wing vein 5 pale, at and adjacent to the fork, B: Fork of wing vein 5 dark
86- A: Wing length 4 mm or less; decumbent scutal scales not extending onto scutellum, B: Wing length 4.4 mm or more; some decumbent scales present on scutellum as well as scutum
87- A: 2nd and 3rd main dark areas present on vein 1, B: 2nd and 3rd main dark areas of wing (median and preapical dark spots) absent from vein 1
88- A: Hindtarsomere 5 entirely pale, hindtarsomere 4 with broad apical and basal pale bands, B: Hindtarsomere 5 entirely dark, hindtarsomere 4 with narrow apical and basal pale bands
89- A: Upper branch of wing vein 5 with 1 pale spot, sometimes a vestigial 2nd pale spot, B: Upper branch of wing vein 5 with 2 well-developed pale spots
90- A: Pale fringe spot present opposite wing vein 6; foretarsomeres 1 to 4 with conspicuous basal and apical pale bands, B: No pale fringe spot opposite wing vein 6; foretarsomeres 1 to 4 narrowly pale apically only
91- A: Subapical pale band on maxillary palpus very narrow, confined to apex of 3rd segment, B: Subapical pale band on maxillary palpus broad, overlapping apex of 3rd and base of 4th segment
92- A: Wing with base of costa with 2 pale interruptions, B: Basal 0.25 of costa entirely dark
93- A: Hindtarsomeres either all dark or with pale bands on tarsomeres 1 and 2 only, B: Hindtarsomeres 1 to 4 with well-marked apical pale bands
94- A: Scutal fossae and lateral areas of scutum above wing root (supraalar area) with scattered or abundant broadish scales, B: Scutal fossae and lateral areas of scutum above wing root (supraalar area) without scales
95- A: Subapical pale band on maxillary palpus about equal to or slightly shorter than apical band, B: Subapical pale band on maxillary palpus much narrower than apical band
96- A: Apical pale bands on hindtarsomeres 1 to 4 very broad, at least twice the apical width of the tarsomeres, B: Hindtarsomeres 1 to 4 with narrow pale bands, as long or shorter than the width of the tarsomeres
97- A: Wing vein 3 largely dark or broadly dark at either end; scutal scales very narrow and golden, B: Wing vein 3 narrowly dark at ends; scutal scales various
98- A: Scutal scales as in (A, B, C or D):, B: nan
99- A: Maxillary palpus with only apical pale band, B: Maxillary palpus with 3 pale bands
100- A: Subapical pale band on maxillary palpus broad, about equal to or longer than apical dark band, B: Apical dark band much longer than subapical pale band
101- A: Bases of hindtarsomeres dark, B: Apical pale band on hindtarsomere 4, and sometimes on hindtarsomeres 2 and 3, extending onto bases of succeeding tarsomeres
102- A: 2nd main dark area on wing vein 1 with 2 pale interruptions; bases of hindtarsomeres 4 and 5 broadly or narrowly pale, B: 2nd main dark area on wing vein 1 with 1 pale interruption; bases of hindtarsomeres 4 and 5 at most narrowly pale
103- A: Base of costa with 1 pale interruption, 3rd main dark area on costa and vein 1 much broader than subcostal pale spot, B: Base of costa with 2 pale interruptions, 3rd main dark area equal to or narrower than subcostal pale spot
104- A: Pale fringe spot present opposite wing vein 6, B: No pale fringe spot opposite vein 6
105- A: Apices of hindtarsomeres 3 and 4 dark or at most with a few pale scales, B: Apices of hindtarsomeres 1 to 3 and sometimes 4, distinctly pale banded
106- A: Base of costa with 2 pale interruptions, B: Base of costa with 1 or no pale interruption
107- A: Wing vein 6 either with pale fringe spot or with pale scales at apex of vein, B: Wing vein 6 without pale fringe spot and no pale scales at apex
108- A: Scutal scales fairly broad, extending over whole scutum and onto scutellum, B: Scutal scales variable, but decumbent scales confined to at most anterior 0.66 of scutum
109- A: Very small species, wing length 2.8 mm or less, B: Small or moderate species, wing length 2.9 mm or more
110- A: Hindtarsomeres entirely dark; preaccessory dark spot on wing vein 1 usually absent, B: Hindtarsomeres 1 and 2 narrowly but distinctly pale apically; preaccessory dark spot present on wing vein 1
111- A: 3rd main dark area much longer than subapical pale spot, B: 3rd main dark area of costa equal to or shorter than subapical pale spot
112- A: Scutal scales broadish and white, only slightly less dense on posterior 0.33 of scutum than anteriorly, and extending onto scutellum, B: Scutal scales on posterior 0.33 of scutum scanty, narrow and yellowish-brown
113- A: Moderate-sized species, wing length more than 3.2 mm, B: Small species, wing length 3.0 mm or less
114- A: Foretarsomere 4 with well-marked apical pale band; wing with fringe spot opposite vein 6, B: Foretarsomere 4 dark or indistinctly pale at apex; wing usually without pale fringe spot opposite vein 6
115- A: 3rd main dark area of costa equal to or shorter than subapical pale spot, B: 3rd main dark area of costa much longer than subapical pale spot
116- A: Wing with fork of vein 5 pale, B: Wing with fork of vein 5 dark
117- A: Base of costa with two pale interruptions, B: Base of costa with 1 or no pale interruption
118- A: Small species, wing length about 2.4-3.3 mm, B: Small or moderate-sized species, wing length 2.9ñ4.2 mm
119- A: Maxillary palpus with only apex pale, B: Maxillary palpus with 3 pale bands
120- A: Base of costa with large (presector) pale spot, base of vein 1 pale, B: Base of costa dark or with small pale spot, base of vein 1 dark
121- A: Lower branch of wing vein 2 and upper branch of vein 4 with distinct pale spots, B: These veins dark
122- A: Subapical pale spot on costa and wing vein 1 about as long as apical dark spot, fringe spots present opposite veins 3, lower branch of 4 and both branches of 5, B: Subapical pale spot shorter, usually much shorter, than apical dark spot, no pale fringe spot opposite upper branch of vein 5
123- A: Hindtarsomeres 1 to 4 with pale bands overlapping the joints, at least hindtarsomere 5 pale basally, B: Pale banding on hindtarsomeres narrow and apical only
124- A: Preaccessory dark spot on wing vein 1 about twice as long as pale spot on either side of it, B: Preaccessory dark spot absent or, if present, shorter or only slightly longer than adjoining pale spots
125- A: Basal area of wing vein 1 proximal to 1st main dark area, pale with a broad dark spot, B: Basal area of wing vein 1 entirely pale
126- A: Subapical pale band on maxillary palpus longer than or equal to apical dark band AND 3rd main dark area of costa and vein 1 equal to or shorter than subapical pale spot, B: Subapical pale band on maxillary palpus much shorter than apical dark band, OR 3rd main dark area longer than subapical pale spot
127- A: Moderate-sized species, wing length more than 3.3 mm, B: Small species, wing length 3.2 mm or less
128- A: Tip of wing vein 6 dark with no fringe spot, B: Tip of wing vein 6 with a few pale scales, sometimes with fringe spot present

### Example input for a single feature:
'Legs sparsely speckled'

### Expected reasoning for that feature:
Comparing that statement to the features, we see that speckled legs are mentioned in feature 3:
3- A: Legs speckled, sometimes sparsely, B: Legs not speckled
The input matches statement 3 A, and doesn't match 3B, so position 3 in the final vector should be 'A'.

Notice that feature 18 (A: Legs speckled, B: Legs not speckled) should also be 'A'.

### Example input for multiple features:
'Abdominal segments with laterally projecting tufts of scales on segments II-VII. Wing with abundant pale areas, costa with at least 4 pale spots. Hindtarsomeres 1 to 4, at least, with apical pale bands. Hindtarsomeres 1 and 2 with pale bands at apices only. Hindtarsomeres 3 and 4 not all white nor narrowly dark basally, hindtarsomere 5  not all dark nor with basal 0.5 dark. Hindtarsomere 5 and about apical 0.5 of 4 pale.'

### Expected Output for multiple features:
[A, nan, nan, nan, nan, nan, nan, nan, nan, nan, B, B, B, B, nan, nan, A, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan]

### Additional context:
- area: a broad, less defined region of color or texture. For example, a "dark area" on the wing could mean a large portion covered by dark scales, without a sharp boundary.
- band: a continuous stripe that runs across a segment, usually transverse. For example, a "pale band on the tarsus" means a light-colored ring that encircles the segment.
- spot: a relatively small, discrete patch of scales that is clearly localized, not coninuous.
- patch: similar to a spot but usually larger and less regularly shaped, often referring to a cluster of scales.
- ring: specifically circular or encircling markings, often used on leg segments.
- interruption: when a marking (often a band or ring) is broken or incomplete.
- tarsus: most distal portion of the leg
- tarsomere: segment of the last portion of the leg
- When something is described as "dark at apex", it means the apex is predominantly dark, but it may still have a few scattered pale scales, as long as there isn't a strong pale annulus interrupting. For example, palps with a dark base but with 1 to 2 pale interruptions can still be considered dark at base.
- "apex" refers to the terminal portion of the segment, not just the extreme tip. It can be anywhere between the last half and the last quarter.
- consider "white" and "pale" as synonyms. Occasionally, "white" might be used to show a sharper contrast, but consider them synonyms for the most part.
- consider "dark" and "black" as synonyms
- the term "apical" might be described as "distal"
- the wing contains veins that, from the top down are named: costa, sub-costa or subcosta, vein 1, vein 2, vein 3, vein 4, vein 5 and vein 6
- "wing vein 1 without usual main dark areas" generally implies that they are missing entirely, rather than one being absent or the set of bands being replaced by a different set.
- veins 5 and 6 might be described as "posterior veins"
- something "without distinct bands" may not be uniform in color; it just means it has no clearly defined, crisp regions that encircle the segment and stand out as bands.
- the costa can be called the "top vein" or "leading edge".
- Vein 1 can be called the radius 1, "R1", or the "first branch of the radius".
- vein 2 can be called Radius 2+3, "r2+3", or the "second branch of the radius".
- vein 3 can be called Radius 4+5, "r4+5", or the "third branch of the radius".
- vein 4 can be called Media, "M", or "medial vein".
- vein 5 can be called Cubitus, "Cu" or "cubital vein".
- vein 6 can be called Anal, "A", or "anal vein".
- The spots on the wing can be called "humeral spot" (at the base of the wing, near the costa, or "basal costal spot"); "presector spot" (just before sector vein along costa, or "costal pre-sector spot"); "median spot" (mid-wing on radial veins, or "central spot"); "preaccessory spot" (before accessory vein along costa, or "costal pre-accessory spot"); "preapical spot" (near wing tip, not at apex, or "subapical"); "subapical spot" (just before apex along main veins, or "distal costal spot"). They can also be described relative to the costa or specific veins.
- the feature "3rd main dark area of wing vein 1 with a pale interruption, sometimes fused with preceding pale spot" can be described as a "gambiae gap"
- Decumbent scales: scales that lie flat or nearly flat against the surface they cover, rather than sticking out (erect scales) or lying completely appressed. They can be on various body parts-  commonly the thorax, scutum, head and legs, depending on the species. They lay along the surface, often forming background coloration rather than highlighting a structure.
- Usually, a band would be described as "narrow" if it covered roughly a quarter or less of the segment's length or width, unless otherwise stated.
- usually, a band would be described as "broad" if it covered  roughly ahalf or more of the segment's length or width-
- intermediate" or "moderate" bands are anything in between narrow and broad.
- If the user or the key specifies a different percentage, let that take precedence over the definitions for "narrow", "broad" and "intermediate".
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

