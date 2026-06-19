# Auto-generated Nepal location seed data with correct ward counts from official PDF
# All names are stored in English for display; Nepali names are kept in nepali_name columns.

import re
from typing import Dict, Tuple

COUNTRIES = [
    {"id": 1, "name": "Nepal", "code": "NP"},
]

# ── PROVINCES with English and Nepali names ────────────────────
PROVINCES = [
    {"id": 1, "name": "Koshi", "nepali_name": "कोशी", "country_id": 1},
    {"id": 2, "name": "Madhesh", "nepali_name": "मधेश", "country_id": 1},
    {"id": 3, "name": "Bagmati", "nepali_name": "बागमती", "country_id": 1},
    {"id": 4, "name": "Gandaki", "nepali_name": "गण्डकी", "country_id": 1},
    {"id": 5, "name": "Lumbini", "nepali_name": "लुम्बिनी", "country_id": 1},
    {"id": 6, "name": "Karnali", "nepali_name": "कर्णाली", "country_id": 1},
    {"id": 7, "name": "Sudurpashchim", "nepali_name": "सुदूरपश्चिम", "country_id": 1},
]

# ── DISTRICTS (name = English, nepali_name = Nepali) ──────────
DISTRICTS = [
    {"id": 1, "name": "Taplejung", "nepali_name": "ताप्लेजुङ", "province_id": 1},
    {"id": 2, "name": "Panchthar", "nepali_name": "पाँचथर", "province_id": 1},
    {"id": 3, "name": "Ilam", "nepali_name": "ईलाम", "province_id": 1},
    {"id": 4, "name": "Jhapa", "nepali_name": "झापा", "province_id": 1},
    {"id": 5, "name": "Morang", "nepali_name": "मोरंग", "province_id": 1},
    {"id": 6, "name": "Sunsari", "nepali_name": "सुनसरी", "province_id": 1},
    {"id": 7, "name": "Dhankuta", "nepali_name": "धनकुटा", "province_id": 1},
    {"id": 8, "name": "Terhathum", "nepali_name": "तेहथुम", "province_id": 1},
    {"id": 9, "name": "Sankhuwasabha", "nepali_name": "संखुवासभा", "province_id": 1},
    {"id": 10, "name": "Bhojpur", "nepali_name": "भोजपुर", "province_id": 1},
    {"id": 11, "name": "Solukhumbu", "nepali_name": "सोलुखुम्बु", "province_id": 1},
    {"id": 12, "name": "Okhaldhunga", "nepali_name": "ओखलढुंगा", "province_id": 1},
    {"id": 13, "name": "Khotang", "nepali_name": "खोटाङ", "province_id": 1},
    {"id": 14, "name": "Udayapur", "nepali_name": "उदयपुर", "province_id": 1},
    {"id": 15, "name": "Saptari", "nepali_name": "सप्तरी", "province_id": 2},
    {"id": 16, "name": "Siraha", "nepali_name": "सिराहा", "province_id": 2},
    {"id": 17, "name": "Dhanusa", "nepali_name": "धनुषा", "province_id": 2},
    {"id": 18, "name": "Mahottari", "nepali_name": "महोत्तरी", "province_id": 2},
    {"id": 19, "name": "Sarlahi", "nepali_name": "सर्लाही", "province_id": 2},
    {"id": 20, "name": "Rautahat", "nepali_name": "रौतहट", "province_id": 2},
    {"id": 21, "name": "Bara", "nepali_name": "बारा", "province_id": 2},
    {"id": 22, "name": "Parsa", "nepali_name": "पर्सा", "province_id": 2},
    {"id": 23, "name": "Sindhuli", "nepali_name": "सिन्धुली", "province_id": 3},
    {"id": 24, "name": "Ramechhap", "nepali_name": "रामेछाप", "province_id": 3},
    {"id": 25, "name": "Dolakha", "nepali_name": "दोलखा", "province_id": 3},
    {"id": 26, "name": "Sindhupalchok", "nepali_name": "सिन्धुपाल्चोक", "province_id": 3},
    {"id": 27, "name": "Kavrepalanchok", "nepali_name": "काभ्रेपलान्चोक", "province_id": 3},
    {"id": 28, "name": "Lalitpur", "nepali_name": "ललितपुर", "province_id": 3},
    {"id": 29, "name": "Bhaktapur", "nepali_name": "भक्तपुर", "province_id": 3},
    {"id": 30, "name": "Kathmandu", "nepali_name": "काठमाण्डौ", "province_id": 3},
    {"id": 31, "name": "Nuwakot", "nepali_name": "नुवाकोट", "province_id": 3},
    {"id": 32, "name": "Rasuwa", "nepali_name": "रसुवा", "province_id": 3},
    {"id": 33, "name": "Dhading", "nepali_name": "धादिङ", "province_id": 3},
    {"id": 34, "name": "Makwanpur", "nepali_name": "मकवानपुर", "province_id": 3},
    {"id": 35, "name": "Chitwan", "nepali_name": "चितवन", "province_id": 3},
    {"id": 36, "name": "Gorkha", "nepali_name": "गोरखा", "province_id": 4},
    {"id": 37, "name": "Lamjung", "nepali_name": "लमजुङ", "province_id": 4},
    {"id": 38, "name": "Tanahu", "nepali_name": "तनहुँ", "province_id": 4},
    {"id": 39, "name": "Syangja", "nepali_name": "स्याङजा", "province_id": 4},
    {"id": 40, "name": "Kaski", "nepali_name": "कास्की", "province_id": 4},
    {"id": 41, "name": "Manang", "nepali_name": "मनाङ", "province_id": 4},
    {"id": 42, "name": "Mustang", "nepali_name": "मुस्ताङ", "province_id": 4},
    {"id": 43, "name": "Myagdi", "nepali_name": "म्याग्दी", "province_id": 4},
    {"id": 44, "name": "Parbat", "nepali_name": "पर्वत", "province_id": 4},
    {"id": 45, "name": "Baglung", "nepali_name": "बाग्लुङ", "province_id": 4},
    {"id": 46, "name": "Nawalpur", "nepali_name": "नवलपरासी (बर्दघाट सुस्ता पूर्व)", "province_id": 4},
    {"id": 47, "name": "Gulmi", "nepali_name": "गुल्मी", "province_id": 5},
    {"id": 48, "name": "Palpa", "nepali_name": "पाल्पा", "province_id": 5},
    {"id": 49, "name": "Rupandehi", "nepali_name": "रुपन्देही", "province_id": 5},
    {"id": 50, "name": "Kapilbastu", "nepali_name": "कपिलबस्तु", "province_id": 5},
    {"id": 51, "name": "Arghakhanchi", "nepali_name": "अर्घाखाँची", "province_id": 5},
    {"id": 52, "name": "Pyuthan", "nepali_name": "प्यूठान", "province_id": 5},
    {"id": 53, "name": "Rolpa", "nepali_name": "रोल्पा", "province_id": 5},
    {"id": 54, "name": "Rukum East", "nepali_name": "रुकुम (पूर्वी भाग)", "province_id": 5},
    {"id": 55, "name": "Dang", "nepali_name": "दाङ", "province_id": 5},
    {"id": 56, "name": "Banke", "nepali_name": "बाँके", "province_id": 5},
    {"id": 57, "name": "Bardiya", "nepali_name": "बर्दिया", "province_id": 5},
    {"id": 58, "name": "Parasi", "nepali_name": "नवलपरासी (बर्दघाट सुस्ता पश्चिम)", "province_id": 5},
    {"id": 59, "name": "Rukum West", "nepali_name": "रुकुम (पश्चिम भाग)", "province_id": 6},
    {"id": 60, "name": "Salyan", "nepali_name": "सल्यान", "province_id": 6},
    {"id": 61, "name": "Surkhet", "nepali_name": "सुर्खेत", "province_id": 6},
    {"id": 62, "name": "Dailekh", "nepali_name": "दैलेख", "province_id": 6},
    {"id": 63, "name": "Jajarkot", "nepali_name": "जाजरकोट", "province_id": 6},
    {"id": 64, "name": "Dolpa", "nepali_name": "डोल्पा", "province_id": 6},
    {"id": 65, "name": "Jumla", "nepali_name": "जुम्ला", "province_id": 6},
    {"id": 66, "name": "Kalikot", "nepali_name": "कालिकोट", "province_id": 6},
    {"id": 67, "name": "Mugu", "nepali_name": "मुगु", "province_id": 6},
    {"id": 68, "name": "Humla", "nepali_name": "हुम्ला", "province_id": 6},
    {"id": 69, "name": "Bajura", "nepali_name": "बाजुरा", "province_id": 7},
    {"id": 70, "name": "Bajhang", "nepali_name": "बझाङ", "province_id": 7},
    {"id": 71, "name": "Achham", "nepali_name": "अछाम", "province_id": 7},
    {"id": 72, "name": "Doti", "nepali_name": "डोटी", "province_id": 7},
    {"id": 73, "name": "Kailali", "nepali_name": "कैलाली", "province_id": 7},
    {"id": 74, "name": "Kanchanpur", "nepali_name": "कञ्चनपुर", "province_id": 7},
    {"id": 75, "name": "Dadeldhura", "nepali_name": "डडेलधुरा", "province_id": 7},
    {"id": 76, "name": "Baitadi", "nepali_name": "बैतडी", "province_id": 7},
    {"id": 77, "name": "Darchula", "nepali_name": "दार्चुला", "province_id": 7},
]

# ── FULL PDF WARD DATA ────────────────────────────────────────
PDF_DATA = """
1 Koshi|Bhojpur|Shadananda Municipality|14
2 Koshi|Bhojpur|Bhojpur Municipality|12
3 Koshi|Bhojpur|Aamchowk Gaunpalika|10
4 Koshi|Bhojpur|Hatuwagadhi Gaunpalika|9
5 Koshi|Bhojpur|Temkemaiyum Gaunpalika|9
6 Koshi|Bhojpur|Ramprasad Rai Gaunpalika|8
7 Koshi|Bhojpur|Arun Gaunpalika|7
8 Koshi|Bhojpur|Pauwa Dunma Gaunpalika|6
9 Koshi|Bhojpur|Salpa Silichho Gaunpalika|6
10 Koshi|Dhankuta|Dhankuta Municipality|10
11 Koshi|Dhankuta|Pakhribas Municipality|10
12 Koshi|Dhankuta|Sangurigadhi Gaunpalika|10
13 Koshi|Dhankuta|Mahalaxmi Municipality|9
14 Koshi|Dhankuta|Chaubise Gaunpalika|8
15 Koshi|Dhankuta|Shahidbhumi Gaunpalika|7
16 Koshi|Dhankuta|Chhathar Jorpati Gaunpalika|6
17 Koshi|Ilam|Suryodaya Municipality|14
18 Koshi|Ilam|Illam Municipality|12
19 Koshi|Ilam|Mai Municipality|10
20 Koshi|Ilam|Deumai Municipality|9
21 Koshi|Ilam|Fakfokathum Gaunpalika|7
22 Koshi|Ilam|Chulachuli Gaunpalika|6
23 Koshi|Ilam|Mai Jogmai Gaunpalika|6
24 Koshi|Ilam|Mangsebung Gaunpalika|6
25 Koshi|Ilam|Rong Gaunpalika|6
26 Koshi|Ilam|Sandakpur Gaunpalika|5
27 Koshi|Jhapa|Mechinagar Municipality|15
28 Koshi|Jhapa|Arjundhara Municipality|11
29 Koshi|Jhapa|Shivasatakshi Municipality|11
30 Koshi|Jhapa|Bhadrapur Municipality|10
31 Koshi|Jhapa|Birtamod Municipality|10
32 Koshi|Jhapa|Damak Municipality|10
33 Koshi|Jhapa|Gauradaha Municipality|9
34 Koshi|Jhapa|Kankai Municipality|9
35 Koshi|Jhapa|Barhadashi Gaunpalika|7
36 Koshi|Jhapa|Buddhashanti Gaunpalika|7
37 Koshi|Jhapa|Jhapa Gaunpalika|7
38 Koshi|Jhapa|Kachanakawal Gaunpalika|7
39 Koshi|Jhapa|Kamal Gaunpalika|7
40 Koshi|Jhapa|Gauriganj Gaunpalika|6
41 Koshi|Jhapa|Haldibari Gaunpalika|5
42 Koshi|Khotang|Diktel Rupakot Majhuwagadhi Municipality|15
43 Koshi|Khotang|Halesi Tuwachung Municipality|11
44 Koshi|Khotang|Khotehang Gaunpalika|9
45 Koshi|Khotang|Aiselukharka Gaunpalika|7
46 Koshi|Khotang|Diprung Chuichumma Gaunpalika|7
47 Koshi|Khotang|Kepilasgadhi Gaunpalika|7
48 Koshi|Khotang|Baraha Pokhari Gaunpalika|6
49 Koshi|Khotang|Jante Dhunga Gaunpalika|6
50 Koshi|Khotang|Rawa Besi Gaunpalika|6
51 Koshi|Khotang|Sakela Gaunpalika|5
52 Koshi|Morang|Biratnagar Metropolitan City|19
53 Koshi|Morang|Sundarharaicha Municipality|12
54 Koshi|Morang|Belbari Municipality|11
55 Koshi|Morang|Kerabari Gaunpalika|10
56 Koshi|Morang|Pathari Shanishchare Municipality|10
57 Koshi|Morang|Ratuwamai Municipality|10
58 Koshi|Morang|Letang Municipality|9
59 Koshi|Morang|Miklajung Gaunpalika|9
60 Koshi|Morang|Rangeli Municipality|9
61 Koshi|Morang|Sunwarshi Municipality|9
62 Koshi|Morang|Urlabari Municipality|9
63 Koshi|Morang|Budhiganga Gaunpalika|7
64 Koshi|Morang|Dhanapalthan Gaunpalika|7
65 Koshi|Morang|Gramthan Gaunpalika|7
66 Koshi|Morang|Jahada Gaunpalika|7
67 Koshi|Morang|Kanepokhari Gaunpalika|7
68 Koshi|Morang|Katahari Gaunpalika|7
69 Koshi|Okhaldhunga|Siddhicharan Municipality|12
70 Koshi|Okhaldhunga|Champadevi Gaunpalika|10
71 Koshi|Okhaldhunga|Sunkoshi Gaunpalika|10
72 Koshi|Okhaldhunga|Khiji Demba Gaunpalika|9
73 Koshi|Okhaldhunga|Likhu Gaunpalika|9
74 Koshi|Okhaldhunga|Manebhanjyang Gaunpalika|9
75 Koshi|Okhaldhunga|Chishankhu Gadhi Gaunpalika|8
76 Koshi|Okhaldhunga|Molung Gaunpalika|8
77 Koshi|Panchthar|Phidim Municipality|14
78 Koshi|Panchthar|Falelung Gaunpalika|8
79 Koshi|Panchthar|Miklajung Gaunpalika|8
80 Koshi|Panchthar|Falgunanda Gaunpalika|7
81 Koshi|Panchthar|Hilihan Gaunpalika|7
82 Koshi|Panchthar|Yangbarak Gaunpalika|6
83 Koshi|Panchthar|Kummayak Gaunpalika|5
84 Koshi|Panchthar|Tumbewa Gaunpalika|5
85 Koshi|Sankhuwasabha|Chainapur Municipality|11
86 Koshi|Sankhuwasabha|Khandabari Municipality|11
87 Koshi|Sankhuwasabha|Dharmadevi Municipality|9
88 Koshi|Sankhuwasabha|Madi Municipality|9
89 Koshi|Sankhuwasabha|Panchakhapan Municipality|9
90 Koshi|Sankhuwasabha|Makalu Gaunpalika|6
91 Koshi|Sankhuwasabha|Sabhapokhari Gaunpalika|6
92 Koshi|Sankhuwasabha|Bhotkhola Gaunpalika|5
93 Koshi|Sankhuwasabha|Chichila Gaunpalika|5
94 Koshi|Sankhuwasabha|Silichong Gaunpalika|5
95 Koshi|Solukhumbu|Solu Dhudhakunda Municipality|11
96 Koshi|Solukhumbu|Thulung Dudhkoshi Gaunpalika|9
97 Koshi|Solukhumbu|Mapya Dudhkoshi Gaunpalika|7
98 Koshi|Solukhumbu|Khumbu Pasanglhamu Gaunpalika|5
99 Koshi|Solukhumbu|Likhu Pike Gaunpalika|5
100 Koshi|Solukhumbu|Mahakulung Gaunpalika|5
101 Koshi|Solukhumbu|Necha Salyan Gaunpalika|5
102 Koshi|Solukhumbu|Sotang Gaunpalika|5
103 Koshi|Sunsari|Dharan Sub-Metropolitan City|20
104 Koshi|Sunsari|Itahari Sub-Metropolitan City|20
105 Koshi|Sunsari|Duhabi Municipality|12
106 Koshi|Sunsari|Barahachhetra Municipality|11
107 Koshi|Sunsari|Inaruwa Municipality|10
108 Koshi|Sunsari|Ramdhuni Municipality|9
109 Koshi|Sunsari|Bhokraha Narsingh Gaunpalika|8
110 Koshi|Sunsari|Koshi Gaunpalika|8
111 Koshi|Sunsari|Dewangunj Gaunpalika|7
112 Koshi|Sunsari|Harinagar Gaunpalika|7
113 Koshi|Sunsari|Barju Gaunpalika|6
114 Koshi|Sunsari|Gadhi Gaunpalika|6
115 Koshi|Taplejung|Phungling Municipality|11
116 Koshi|Taplejung|Sirijanga Gaunpalika|8
117 Koshi|Taplejung|Phaktanlung Gaunpalika|7
118 Koshi|Taplejung|Sidingba Gaunpalika|7
119 Koshi|Taplejung|Maiwakhola Gaunpalika|6
120 Koshi|Taplejung|Meringden Gaunpalika|6
121 Koshi|Taplejung|Pathivara Yangwarak Gaunpalika|6
122 Koshi|Taplejung|Aatharai Tribeni Gaunpalika|5
123 Koshi|Taplejung|Mikwakhola Gaunpalika|5
124 Koshi|Terhathum|Myanglung Municipality|10
125 Koshi|Terhathum|Laligurans Municipality|9
126 Koshi|Terhathum|Aatharai Gaunpalika|7
127 Koshi|Terhathum|Chhathar Gaunpalika|6
128 Koshi|Terhathum|Menchhayayem Gaunpalika|6
129 Koshi|Terhathum|Phedap Gaunpalika|5
130 Koshi|Udayapur|Triyuga Municipality|16
131 Koshi|Udayapur|Katari Municipality|14
132 Koshi|Udayapur|Chaudandigadhi Municipality|10
133 Koshi|Udayapur|Belaka Municipality|9
134 Koshi|Udayapur|Rautamai Gaunpalika|8
135 Koshi|Udayapur|Udayapurgadhi Gaunpalika|8
136 Koshi|Udayapur|Limchunbung Gaunpalika|5
137 Koshi|Udayapur|Tapli Gaunpalika|5
138 Madhesh|Bara|Kalaiya Sub-Metropolitan City|27
139 Madhesh|Bara|Jitpur Simara Sub-Metropolitan City|24
140 Madhesh|Bara|Nijagadh Municipality|13
141 Madhesh|Bara|Kolhabi Municipality|11
142 Madhesh|Bara|Mahagadhimai Municipality|11
143 Madhesh|Bara|Simroungadh Municipality|11
144 Madhesh|Bara|Pacharauta Municipality|9
145 Madhesh|Bara|Aadarsha Kotwal Gaunpalika|8
146 Madhesh|Bara|Karaiyamai Gaunpalika|8
147 Madhesh|Bara|Subarna Gaunpalika|8
148 Madhesh|Bara|Devtal Gaunpalika|7
149 Madhesh|Bara|Pheta Gaunpalika|7
150 Madhesh|Bara|Prasauni Gaunpalika|7
151 Madhesh|Bara|Baragadhi Gaunpalika|6
152 Madhesh|Bara|Bishrampur Gaunpalika|5
153 Madhesh|Bara|Parawanipur Gaunpalika|5
154 Madhesh|Dhanusa|Janakpurdham Sub-Metropolitan City|25
155 Madhesh|Dhanusa|Sabaila Municipality|13
156 Madhesh|Dhanusa|Ganeshman Charnath Municipality|11
157 Madhesh|Dhanusa|Mithila Municipality|11
158 Madhesh|Dhanusa|Chhireshwornath Municipality|10
159 Madhesh|Dhanusa|Mithila Bihari Municipality|10
160 Madhesh|Dhanusa|Bideha Municipality|9
161 Madhesh|Dhanusa|Dhanushadham Municipality|9
162 Madhesh|Dhanusa|Hansapur Municipality|9
163 Madhesh|Dhanusa|Kamala Municipality|9
164 Madhesh|Dhanusa|Nagarain Municipality|9
165 Madhesh|Dhanusa|Shahidnagar Municipality|9
166 Madhesh|Dhanusa|Laxminiya Gaunpalika|7
167 Madhesh|Dhanusa|Aurahi Gaunpalika|6
168 Madhesh|Dhanusa|Janak Nandini Gaunpalika|6
169 Madhesh|Dhanusa|Mukhiyapatti Musaharmiya Gaunpalika|6
170 Madhesh|Dhanusa|Bateshwor Gaunpalika|5
171 Madhesh|Dhanusa|Dhanauji Gaunpalika|5
172 Madhesh|Mahottari|Bardibas Municipality|14
173 Madhesh|Mahottari|Gaushala Municipality|12
174 Madhesh|Mahottari|Jaleshwor Municipality|12
175 Madhesh|Mahottari|Balawa Municipality|11
176 Madhesh|Mahottari|Manara Shisawa Municipality|10
177 Madhesh|Mahottari|Aurahi Municipality|9
178 Madhesh|Mahottari|Bhangaha Municipality|9
179 Madhesh|Mahottari|Loharpatti Municipality|9
180 Madhesh|Mahottari|Matihani Municipality|9
181 Madhesh|Mahottari|Ram Gopalpur Municipality|9
182 Madhesh|Mahottari|Sonama Gaunpalika|8
183 Madhesh|Mahottari|Pipara Gaunpalika|7
184 Madhesh|Mahottari|Samsi Gaunpalika|7
185 Madhesh|Mahottari|Ekadara Gaunpalika|6
186 Madhesh|Mahottari|Mahottari Gaunpalika|6
187 Madhesh|Parsa|Birgunj Metropolitan City|32
188 Madhesh|Parsa|Pokhariya Municipality|10
189 Madhesh|Parsa|Bahudarmai Municipality|9
190 Madhesh|Parsa|Parsagadhi Municipality|9
191 Madhesh|Parsa|Jagarnathpur Gaunpalika|6
192 Madhesh|Parsa|Sakhuwa Prasauni Gaunpalika|6
193 Madhesh|Parsa|Bindabasini Gaunpalika|5
194 Madhesh|Parsa|Chhipaharmai Gaunpalika|5
195 Madhesh|Parsa|Dhobini Gaunpalika|5
196 Madhesh|Parsa|Jirabhawani Gaunpalika|5
197 Madhesh|Parsa|Kalikamai Gaunpalika|5
198 Madhesh|Parsa|Pakaha Mainpur Gaunpalika|5
199 Madhesh|Parsa|Paterwa Sugauli Gaunpalika|5
200 Madhesh|Parsa|Thori Gaunpalika|5
201 Madhesh|Rautahat|Phatuwa Bijayapur Municipality|11
202 Madhesh|Rautahat|Chandrapur Municipality|10
203 Madhesh|Rautahat|Boudhimai Municipality|9
204 Madhesh|Rautahat|Brindaban Municipality|9
205 Madhesh|Rautahat|Dewahi Gonahi Municipality|9
206 Madhesh|Rautahat|Gadhimai Municipality|9
207 Madhesh|Rautahat|Garuda Municipality|9
208 Madhesh|Rautahat|Gaur Municipality|9
209 Madhesh|Rautahat|Gujara Municipality|9
210 Madhesh|Rautahat|Ishanath Municipality|9
211 Madhesh|Rautahat|Katahariya Municipality|9
212 Madhesh|Rautahat|Madhav Narayan Municipality|9
213 Madhesh|Rautahat|Maulapur Municipality|9
214 Madhesh|Rautahat|Paroha Municipality|9
215 Madhesh|Rautahat|Rajdevi Municipality|9
216 Madhesh|Rautahat|Rajpur Municipality|9
217 Madhesh|Rautahat|Durga Bhagawati Gaunpalika|5
218 Madhesh|Rautahat|Yamunamai Gaunpalika|5
219 Madhesh|Saptari|Rajbiraj Municipality|16
220 Madhesh|Saptari|Hanumannagar Kankalini Municipality|14
221 Madhesh|Saptari|Kanchanrup Municipality|12
222 Madhesh|Saptari|Shambhunath Municipality|12
223 Madhesh|Saptari|Khadak Municipality|11
224 Madhesh|Saptari|Saptakoshi Municipality|11
225 Madhesh|Saptari|Surunga Municipality|11
226 Madhesh|Saptari|Bode Barsain Municipality|10
227 Madhesh|Saptari|Dakneshwori Municipality|10
228 Madhesh|Saptari|Tilathi Koiladi Gaunpalika|8
229 Madhesh|Saptari|Bishnupur Gaunpalika|7
230 Madhesh|Saptari|Chhinnamasta Gaunpalika|7
231 Madhesh|Saptari|Agnisair Krishna Sabaran Gaunpalika|6
232 Madhesh|Saptari|Balan-Bihul Gaunpalika|6
233 Madhesh|Saptari|Mahadewa Gaunpalika|6
234 Madhesh|Saptari|Rajgadh Gaunpalika|6
235 Madhesh|Saptari|Rupani Gaunpalika|6
236 Madhesh|Saptari|Tirahut Gaunpalika|5
237 Madhesh|Sarlahi|Barahathawa Municipality|18
238 Madhesh|Sarlahi|Lalbandi Municipality|17
239 Madhesh|Sarlahi|Ishworpur Municipality|15
240 Madhesh|Sarlahi|Bagmati Municipality|12
241 Madhesh|Sarlahi|Godaita Municipality|12
242 Madhesh|Sarlahi|Malangawa Municipality|12
243 Madhesh|Sarlahi|Balara Municipality|11
244 Madhesh|Sarlahi|Hariwan Municipality|11
245 Madhesh|Sarlahi|Kabilashi Municipality|10
246 Madhesh|Sarlahi|Chakraghatta Gaunpalika|9
247 Madhesh|Sarlahi|Haripur Municipality|9
248 Madhesh|Sarlahi|Haripurwa Municipality|9
249 Madhesh|Sarlahi|Bishnu Gaunpalika|8
250 Madhesh|Sarlahi|Brahmapuri Gaunpalika|7
251 Madhesh|Sarlahi|Chandranagar Gaunpalika|7
252 Madhesh|Sarlahi|Dhanakaul Gaunpalika|7
253 Madhesh|Sarlahi|Kaudena Gaunpalika|7
254 Madhesh|Sarlahi|Ramnagar Gaunpalika|7
255 Madhesh|Sarlahi|Basbariya Gaunpalika|6
256 Madhesh|Sarlahi|Parsa Gaunpalika|6
257 Madhesh|Siraha|Lahan Municipality|24
258 Madhesh|Siraha|Siraha Municipality|22
259 Madhesh|Siraha|Dhangadhimai Municipality|14
260 Madhesh|Siraha|Golbazar Municipality|13
261 Madhesh|Siraha|Kalyanpur Municipality|12
262 Madhesh|Siraha|Mirchaiya Municipality|12
263 Madhesh|Siraha|Karjanha Municipality|11
264 Madhesh|Siraha|Sukhipur Municipality|10
265 Madhesh|Siraha|Laxmipur Patari Gaunpalika|6
266 Madhesh|Siraha|Arnama Gaunpalika|5
267 Madhesh|Siraha|Aurahi Gaunpalika|5
268 Madhesh|Siraha|Bariyarpatti Gaunpalika|5
269 Madhesh|Siraha|Bhagawanpur Gaunpalika|5
270 Madhesh|Siraha|Bishnupur Gaunpalika|5
271 Madhesh|Siraha|Naraha Gaunpalika|5
272 Madhesh|Siraha|Nawarajpur Gaunpalika|5
273 Madhesh|Siraha|Sakhuwa Nankarkatti Gaunpalika|5
274 Bagmati|Bhaktapur|Bhaktapur Municipality|10
275 Bagmati|Bhaktapur|Suryabinayak Municipality|10
276 Bagmati|Bhaktapur|Changunarayan Municipality|9
277 Bagmati|Bhaktapur|Madhyapur Thimi Municipality|9
278 Bagmati|Chitawan|Bharatpur Metropolitan City|29
279 Bagmati|Chitawan|Ratnanagar Municipality|16
280 Bagmati|Chitawan|Khairahani Municipality|13
281 Bagmati|Chitawan|Rapti Municipality|13
282 Bagmati|Chitawan|Kalika Municipality|11
283 Bagmati|Chitawan|Madi Municipality|9
284 Bagmati|Chitawan|Ichchha Kamana Gaunpalika|7
285 Bagmati|Dhading|Nilkhantha Municipality|14
286 Bagmati|Dhading|Thakre Gaunpalika|11
287 Bagmati|Dhading|Benighat Rorang Gaunpalika|10
288 Bagmati|Dhading|Dhunibenshi Municipality|9
289 Bagmati|Dhading|Gajuri Gaunpalika|8
290 Bagmati|Dhading|Galchhi Gaunpalika|8
291 Bagmati|Dhading|Ganga Jamuna Gaunpalika|7
292 Bagmati|Dhading|Jwalamukhi Gaunpalika|7
293 Bagmati|Dhading|Siddhalek Gaunpalika|7
294 Bagmati|Dhading|Tripurasundari Gaunpalika|7
295 Bagmati|Dhading|Rubi Valley Gaunpalika|6
296 Bagmati|Dhading|Khaniyabas Gaunpalika|5
297 Bagmati|Dhading|Netrawati Dabjong Gaunpalika|5
298 Bagmati|Dolakha|Bhimeshwor Municipality|9
299 Bagmati|Dolakha|Gaurishankar Gaunpalika|9
300 Bagmati|Dolakha|Jiri Municipality|9
301 Bagmati|Dolakha|Kalinchowk Gaunpalika|9
302 Bagmati|Dolakha|Baiteshwor Gaunpalika|8
303 Bagmati|Dolakha|Bigu Gaunpalika|8
304 Bagmati|Dolakha|Shailung Gaunpalika|8
305 Bagmati|Dolakha|Melung Gaunpalika|7
306 Bagmati|Dolakha|Tamakoshi Gaunpalika|7
307 Bagmati|Kathmandu|Kathmandu Metropolitan City|32
308 Bagmati|Kathmandu|Chandragiri Municipality|15
309 Bagmati|Kathmandu|Budhanilkhantha Municipality|13
310 Bagmati|Kathmandu|Tarakeshwor Municipality|11
311 Bagmati|Kathmandu|Tokha Municipality|11
312 Bagmati|Kathmandu|Kirtipur Municipality|10
313 Bagmati|Kathmandu|Nagarjun Municipality|10
314 Bagmati|Kathmandu|Dakshinkali Municipality|9
315 Bagmati|Kathmandu|Gokarneshwor Municipality|9
316 Bagmati|Kathmandu|Kageshwori Manahara Municipality|9
317 Bagmati|Kathmandu|Shankharapur Municipality|9
318 Bagmati|Kavrepalanchok|Banepa Municipality|14
319 Bagmati|Kavrepalanchok|Panchkhal Municipality|13
320 Bagmati|Kavrepalanchok|Dhulikhel Municipality|12
321 Bagmati|Kavrepalanchok|Mandan Deupur Municipality|12
322 Bagmati|Kavrepalanchok|Panauti Municipality|12
323 Bagmati|Kavrepalanchok|Roshi Gaunpalika|12
324 Bagmati|Kavrepalanchok|Namobuddha Municipality|11
325 Bagmati|Kavrepalanchok|Bhumlu Gaunpalika|10
326 Bagmati|Kavrepalanchok|Chauri Deurali Gaunpalika|9
327 Bagmati|Kavrepalanchok|Temal Gaunpalika|9
328 Bagmati|Kavrepalanchok|Mahabharat Gaunpalika|8
329 Bagmati|Kavrepalanchok|Khanikhola Gaunpalika|7
330 Bagmati|Kavrepalanchok|Bethanchowk Gaunpalika|6
331 Bagmati|Lalitpur|Lalitpur Metropolitan City|29
332 Bagmati|Lalitpur|Godawari Municipality|14
333 Bagmati|Lalitpur|Mahalaxmi Municipality|10
334 Bagmati|Lalitpur|Bagmati Gaunpalika|7
335 Bagmati|Lalitpur|Mahankal Gaunpalika|6
336 Bagmati|Lalitpur|Konjyosom Gaunpalika|5
337 Bagmati|Makwanpur|Hetauda Sub-Metropolitan City|19
338 Bagmati|Makwanpur|Bakaiya Gaunpalika|12
339 Bagmati|Makwanpur|Thaha Municipality|12
340 Bagmati|Makwanpur|Kailash Gaunpalika|10
341 Bagmati|Makwanpur|Bagmati Gaunpalika|9
342 Bagmati|Makwanpur|Bhimphedi Gaunpalika|9
343 Bagmati|Makwanpur|Manahari Gaunpalika|9
344 Bagmati|Makwanpur|Raksirang Gaunpalika|9
345 Bagmati|Makwanpur|Makawanpurgadhi Gaunpalika|8
346 Bagmati|Makwanpur|Indrasarowar Gaunpalika|5
347 Bagmati|Nuwakot|Belkotgadhi Municipality|13
348 Bagmati|Nuwakot|Bidur Municipality|13
349 Bagmati|Nuwakot|Kakani Gaunpalika|8
350 Bagmati|Nuwakot|Shivapuri Gaunpalika|8
351 Bagmati|Nuwakot|Dupcheshwor Gaunpalika|7
352 Bagmati|Nuwakot|Likhu Gaunpalika|6
353 Bagmati|Nuwakot|Myagang Gaunpalika|6
354 Bagmati|Nuwakot|Tadi Gaunpalika|6
355 Bagmati|Nuwakot|Tarakeshwor Gaunpalika|6
356 Bagmati|Nuwakot|Kispang Gaunpalika|5
357 Bagmati|Nuwakot|Panchakanya Gaunpalika|5
358 Bagmati|Nuwakot|Suryagadhi Gaunpalika|5
359 Bagmati|Ramechhap|Manthali Municipality|14
360 Bagmati|Ramechhap|Khandadevi Gaunpalika|9
361 Bagmati|Ramechhap|Ramechhap Municipality|9
362 Bagmati|Ramechhap|Doramba Gaunpalika|7
363 Bagmati|Ramechhap|Likhu Tamakoshi Gaunpalika|7
364 Bagmati|Ramechhap|Umakunda Gaunpalika|7
365 Bagmati|Ramechhap|Gokulganga Gaunpalika|6
366 Bagmati|Ramechhap|Sunapati Gaunpalika|5
367 Bagmati|Rasuwa|Gosaikunda Gaunpalika|6
368 Bagmati|Rasuwa|Naukunda Gaunpalika|6
369 Bagmati|Rasuwa|Aamachhodingmo Gaunpalika|5
370 Bagmati|Rasuwa|Kalika Gaunpalika|5
371 Bagmati|Rasuwa|Uttargaya Gaunpalika|5
372 Bagmati|Sindhuli|Dudhouli Municipality|14
373 Bagmati|Sindhuli|Kamalamai Municipality|14
374 Bagmati|Sindhuli|Tinpatan Gaunpalika|11
375 Bagmati|Sindhuli|Hariharpurgaghi Gaunpalika|8
376 Bagmati|Sindhuli|Golanjor Gaunpalika|7
377 Bagmati|Sindhuli|Marin Gaunpalika|7
378 Bagmati|Sindhuli|Sunkoshi Gaunpalika|7
379 Bagmati|Sindhuli|Phikkal Gaunpalika|6
380 Bagmati|Sindhuli|Ghyanglekha Gaunpalika|5
381 Bagmati|Sindhupalchok|Choutara Sangachowkgadhi Municipality|14
382 Bagmati|Sindhupalchok|Melanchi Municipality|13
383 Bagmati|Sindhupalchok|Indrawoti Gaunpalika|12
384 Bagmati|Sindhupalchok|Bahrabise Municipality|9
385 Bagmati|Sindhupalchok|Balephi Gaunpalika|8
386 Bagmati|Sindhupalchok|Panchpokhari Thangpal Gaunpalika|8
387 Bagmati|Sindhupalchok|Helambu Gaunpalika|7
388 Bagmati|Sindhupalchok|Jugal Gaunpalika|7
389 Bagmati|Sindhupalchok|Lisankhu Pakhar Gaunpalika|7
390 Bagmati|Sindhupalchok|Sunkoshi Gaunpalika|7
391 Bagmati|Sindhupalchok|Tripurasundari Gaunpalika|6
392 Bagmati|Sindhupalchok|Bhotekoshi Gaunpalika|5
393 Gandaki|Baglung|Baglung Municipality|14
394 Gandaki|Baglung|Galkot Municipality|11
395 Gandaki|Baglung|Badigad Gaunpalika|10
396 Gandaki|Baglung|Jaimuni Municipality|10
397 Gandaki|Baglung|Dhorpatan Municipality|9
398 Gandaki|Baglung|Kathekhola Gaunpalika|8
399 Gandaki|Baglung|Nisikhola Gaunpalika|7
400 Gandaki|Baglung|Tamankhola Gaunpalika|6
401 Gandaki|Baglung|Bareng Gaunpalika|5
402 Gandaki|Baglung|Tarakhola Gaunpalika|5
403 Gandaki|Gorkha|Gorkha Municipality|14
404 Gandaki|Gorkha|Aarughat Gaunpalika|10
405 Gandaki|Gorkha|Palungtar Municipality|10
406 Gandaki|Gorkha|Shahid Lakhan Gaunpalika|9
407 Gandaki|Gorkha|Barpak Sulikot Gaunpalika|8
408 Gandaki|Gorkha|Bhimsenthapa Gaunpalika|8
409 Gandaki|Gorkha|Gandaki Gaunpalika|8
410 Gandaki|Gorkha|Siranchowk Gaunpalika|8
411 Gandaki|Gorkha|Chumanubri Gaunpalika|7
412 Gandaki|Gorkha|Dharche Gaunpalika|7
413 Gandaki|Gorkha|Ajirkot Gaunpalika|5
414 Gandaki|Kaski|Pokhara Metropolitan City|33
415 Gandaki|Kaski|Madi Gaunpalika|12
416 Gandaki|Kaski|Annapurna Gaunpalika|11
417 Gandaki|Kaski|Machhapuchchhre Gaunpalika|9
418 Gandaki|Kaski|Rupa Gaunpalika|7
419 Gandaki|Lamjung|Bensishahar Municipality|11
420 Gandaki|Lamjung|Sundarbazar Municipality|11
421 Gandaki|Lamjung|Madhya Nepal Municipality|10
422 Gandaki|Lamjung|Rainas Municipality|10
423 Gandaki|Lamjung|Dordi Gaunpalika|9
424 Gandaki|Lamjung|Kwhola Sothar Gaunpalika|9
425 Gandaki|Lamjung|Marshyangdi Gaunpalika|9
426 Gandaki|Lamjung|Dudhapokhari Gaunpalika|6
427 Gandaki|Manang|Manang Ngisyang Gaunpalika|9
428 Gandaki|Manang|Nason Gaunpalika|9
429 Gandaki|Manang|Chame Gaunpalika|5
430 Gandaki|Manang|Narpa Bhumi Gaunpalika|5
431 Gandaki|Mustang|Gharpajhong Gaunpalika|5
432 Gandaki|Mustang|Lo Ghekar Damodarkunda Gaunpalika|5
433 Gandaki|Mustang|Lomanthang Gaunpalika|5
434 Gandaki|Mustang|Thasang Gaunpalika|5
435 Gandaki|Mustang|Varagung Muktichhetra Gaunpalika|5
436 Gandaki|Myagdi|Beni Municipality|10
437 Gandaki|Myagdi|Annapurna Gaunpalika|8
438 Gandaki|Myagdi|Raghuganga Gaunpalika|8
439 Gandaki|Myagdi|Dhawalagiri Gaunpalika|7
440 Gandaki|Myagdi|Malika Gaunpalika|7
441 Gandaki|Myagdi|Mangala Gaunpalika|5
442 Gandaki|Nawalpur|Gaidakot Municipality|18
443 Gandaki|Nawalpur|Devchuli Municipality|17
444 Gandaki|Nawalpur|Kawasoti Municipality|17
445 Gandaki|Nawalpur|Madhya Bindu Municipality|15
446 Gandaki|Nawalpur|Binayi Tribeni Gaunpalika|7
447 Gandaki|Nawalpur|Baudikali Gaunpalika|6
448 Gandaki|Nawalpur|Bulingtar Gaunpalika|6
449 Gandaki|Nawalpur|Hupsekot Gaunpalika|6
450 Gandaki|Parbat|Kushma Municipality|14
451 Gandaki|Parbat|Phalebas Municipality|11
452 Gandaki|Parbat|Jaljala Gaunpalika|9
453 Gandaki|Parbat|Modi Gaunpalika|8
454 Gandaki|Parbat|Paiyu Gaunpalika|7
455 Gandaki|Parbat|Bihadi Gaunpalika|6
456 Gandaki|Parbat|Mahashila Gaunpalika|6
457 Gandaki|Syangja|Putalibazar Municipality|14
458 Gandaki|Syangja|Walling Municipality|14
459 Gandaki|Syangja|Galyang Municipality|11
460 Gandaki|Syangja|Chapakot Municipality|10
461 Gandaki|Syangja|Bhirkot Municipality|9
462 Gandaki|Syangja|Biruwa Gaunpalika|8
463 Gandaki|Syangja|Harinas Gaunpalika|7
464 Gandaki|Syangja|Kaligandaki Gaunpalika|7
465 Gandaki|Syangja|Aandhikhola Gaunpalika|6
466 Gandaki|Syangja|Arjun Choupari Gaunpalika|6
467 Gandaki|Syangja|Phedikhola Gaunpalika|5
468 Gandaki|Tanahu|Byas Municipality|14
469 Gandaki|Tanahu|Bhanu Municipality|13
470 Gandaki|Tanahu|Shuklagandaki Municipality|12
471 Gandaki|Tanahu|Bhimad Municipality|9
472 Gandaki|Tanahu|Rhishing Gaunpalika|8
473 Gandaki|Tanahu|Myagde Gaunpalika|7
474 Gandaki|Tanahu|Aanbu Khaireni Gaunpalika|6
475 Gandaki|Tanahu|Bandipur Gaunpalika|6
476 Gandaki|Tanahu|Devghat Gaunpalika|5
477 Gandaki|Tanahu|Ghiring Gaunpalika|5
478 Lumbini|Arghakhanchi|Shitaganga Municipality|14
479 Lumbini|Arghakhanchi|Sandhikharka Municipality|12
480 Lumbini|Arghakhanchi|Bhumikasthan Municipality|10
481 Lumbini|Arghakhanchi|Malarani Gaunpalika|9
482 Lumbini|Arghakhanchi|Chhatradev Gaunpalika|8
483 Lumbini|Arghakhanchi|Panini Gaunpalika|8
484 Lumbini|Banke|Nepalganj Sub-Metropolitan City|23
485 Lumbini|Banke|Kohalpur Municipality|15
486 Lumbini|Banke|Rapti Sonari Gaunpalika|9
487 Lumbini|Banke|Baijanath Gaunpalika|8
488 Lumbini|Banke|Khajura Gaunpalika|8
489 Lumbini|Banke|Duduwa Gaunpalika|6
490 Lumbini|Banke|Janaki Gaunpalika|6
491 Lumbini|Banke|Narainapur Gaunpalika|6
492 Lumbini|Bardiya|Gulariya Municipality|12
493 Lumbini|Bardiya|Barbardiya Municipality|11
494 Lumbini|Bardiya|Rajapur Municipality|10
495 Lumbini|Bardiya|Badhaiyatal Gaunpalika|9
496 Lumbini|Bardiya|Bansgadhi Municipality|9
497 Lumbini|Bardiya|Madhuwan Municipality|9
498 Lumbini|Bardiya|Thakurbaba Municipality|9
499 Lumbini|Bardiya|Geruwa Gaunpalika|6
500 Lumbini|Dang|Ghorahi Sub-Metropolitan City|19
501 Lumbini|Dang|Tulsipur Sub-Metropolitan City|19
502 Lumbini|Dang|Lamahi Municipality|9
503 Lumbini|Dang|Rapti Gaunpalika|9
504 Lumbini|Dang|Bangalachuli Gaunpalika|8
505 Lumbini|Dang|Gadhawa Gaunpalika|8
506 Lumbini|Dang|Babai Gaunpalika|7
507 Lumbini|Dang|Dangisharan Gaunpalika|7
508 Lumbini|Dang|Rajpur Gaunpalika|7
509 Lumbini|Dang|Shantinagar Gaunpalika|7
510 Lumbini|Gulmi|Resunga Municipality|14
511 Lumbini|Gulmi|Musikot Municipality|9
512 Lumbini|Gulmi|Chandrakot Gaunpalika|8
513 Lumbini|Gulmi|Malika Gaunpalika|8
514 Lumbini|Gulmi|Satyawoti Gaunpalika|8
515 Lumbini|Gulmi|Dhurkot Gaunpalika|7
516 Lumbini|Gulmi|Gulmi Durbar Gaunpalika|7
517 Lumbini|Gulmi|Kali Gandaki Gaunpalika|7
518 Lumbini|Gulmi|Madane Gaunpalika|7
519 Lumbini|Gulmi|Chhatrakot Gaunpalika|6
520 Lumbini|Gulmi|Isma Gaunpalika|6
521 Lumbini|Gulmi|Ruruchhetra Gaunpalika|6
522 Lumbini|Kapilbastu|Kapilbastu Municipality|12
523 Lumbini|Kapilbastu|Krishnanagar Municipality|12
524 Lumbini|Kapilbastu|Banganga Municipality|11
525 Lumbini|Kapilbastu|Maharajganj Municipality|11
526 Lumbini|Kapilbastu|Shivaraj Municipality|11
527 Lumbini|Kapilbastu|Buddhabhumi Municipality|10
528 Lumbini|Kapilbastu|Mayadevi Gaunpalika|8
529 Lumbini|Kapilbastu|Yasodhara Gaunpalika|8
530 Lumbini|Kapilbastu|Bijayanagar Gaunpalika|7
531 Lumbini|Kapilbastu|Shuddhodhan Gaunpalika|6
532 Lumbini|Palpa|Tansen Municipality|14
533 Lumbini|Palpa|Rampur Municipality|10
534 Lumbini|Palpa|Baganaskali Gaunpalika|9
535 Lumbini|Palpa|Mathagadhi Gaunpalika|8
536 Lumbini|Palpa|Rainadevi Chhahara Gaunpalika|8
537 Lumbini|Palpa|Ribdikot Gaunpalika|8
538 Lumbini|Palpa|Nisdi Gaunpalika|7
539 Lumbini|Palpa|Purbakhola Gaunpalika|6
540 Lumbini|Palpa|Tinau Gaunpalika|6
541 Lumbini|Palpa|Rambha Gaunpalika|5
542 Lumbini|Parasi|Ramgram Municipality|18
543 Lumbini|Parasi|Bardaghat Municipality|16
544 Lumbini|Parasi|Sunawal Municipality|13
545 Lumbini|Parasi|Pratapapur Gaunpalika|9
546 Lumbini|Parasi|Sarawal Gaunpalika|7
547 Lumbini|Parasi|Palhinandan Gaunpalika|6
548 Lumbini|Parasi|Susta Gaunpalika|5
549 Lumbini|Pyuthan|Pyuthan Municipality|10
550 Lumbini|Pyuthan|Sworgadwari Municipality|9
551 Lumbini|Pyuthan|Jhimaruk Gaunpalika|8
552 Lumbini|Pyuthan|Naubahini Gaunpalika|8
553 Lumbini|Pyuthan|Gaumukhi Gaunpalika|7
554 Lumbini|Pyuthan|Aairawati Gaunpalika|6
555 Lumbini|Pyuthan|Sarumarani Gaunpalika|6
556 Lumbini|Pyuthan|Mallarani Gaunpalika|5
557 Lumbini|Pyuthan|Mandavi Gaunpalika|5
558 Lumbini|Rolpa|Rolpa Municipality|10
559 Lumbini|Rolpa|Runtigadhi Gaunpalika|9
560 Lumbini|Rolpa|Sunil Smriti Gaunpalika|8
561 Lumbini|Rolpa|Gangadev Gaunpalika|7
562 Lumbini|Rolpa|Lungri Gaunpalika|7
563 Lumbini|Rolpa|Sunchhahari Gaunpalika|7
564 Lumbini|Rolpa|Tribeni Gaunpalika|7
565 Lumbini|Rolpa|Madi Gaunpalika|6
566 Lumbini|Rolpa|Pariwartan Gaunpalika|6
567 Lumbini|Rolpa|Thawang Gaunpalika|5
568 Lumbini|Rukum (East)|Putha Uttanganga Gaunpalika|14
569 Lumbini|Rukum (East)|Bhoome Gaunpalika|9
570 Lumbini|Rukum (East)|Sisne Gaunpalika|8
571 Lumbini|Rupandehi|Butwal Sub-Metropolitan City|19
572 Lumbini|Rupandehi|Tilottama Municipality|17
573 Lumbini|Rupandehi|Lumbini Sanskritik Municipality|13
574 Lumbini|Rupandehi|Siddharthanagar Municipality|13
575 Lumbini|Rupandehi|Devdaha Municipality|12
576 Lumbini|Rupandehi|Sainamaina Municipality|11
577 Lumbini|Rupandehi|Gaidahawa Gaunpalika|9
578 Lumbini|Rupandehi|Mayadevi Gaunpalika|8
579 Lumbini|Rupandehi|Kotahimai Gaunpalika|7
580 Lumbini|Rupandehi|Marchawari Gaunpalika|7
581 Lumbini|Rupandehi|Rohini Gaunpalika|7
582 Lumbini|Rupandehi|Sammarimai Gaunpalika|7
583 Lumbini|Rupandehi|Siyari Gaunpalika|7
584 Lumbini|Rupandehi|Suddhodhan Gaunpalika|7
585 Lumbini|Rupandehi|Om Satiya Gaunpalika|6
586 Lumbini|Rupandehi|Kanchan Gaunpalika|5
587 Karnali|Dailekh|Dullu Municipality|13
588 Karnali|Dailekh|Narayan Municipality|11
589 Karnali|Dailekh|Aathbis Municipality|9
590 Karnali|Dailekh|Chamunda Bindrasaini Municipality|9
591 Karnali|Dailekh|Gurans Gaunpalika|8
592 Karnali|Dailekh|Naumule Gaunpalika|8
593 Karnali|Dailekh|Bhagawatimai Gaunpalika|7
594 Karnali|Dailekh|Bhairabi Gaunpalika|7
595 Karnali|Dailekh|Dungeshwor Gaunpalika|6
596 Karnali|Dailekh|Mahabu Gaunpalika|6
597 Karnali|Dailekh|Thantikandh Gaunpalika|6
598 Karnali|Dolpa|Thulibheri Municipality|11
599 Karnali|Dolpa|Tripurasundari Municipality|11
600 Karnali|Dolpa|Mudkechula Gaunpalika|9
601 Karnali|Dolpa|Shey Phoksundo Gaunpalika|9
602 Karnali|Dolpa|Kaike Gaunpalika|7
603 Karnali|Dolpa|Chharka Tangsong Gaunpalika|6
604 Karnali|Dolpa|Dolpo Buddha Gaunpalika|6
605 Karnali|Dolpa|Jagadulla Gaunpalika|6
606 Karnali|Humla|Sarkegad Gaunpalika|8
607 Karnali|Humla|Simkot Gaunpalika|8
608 Karnali|Humla|Adanchuli Gaunpalika|6
609 Karnali|Humla|Chankheli Gaunpalika|6
610 Karnali|Humla|Namkha Gaunpalika|6
611 Karnali|Humla|Kharpunath Gaunpalika|5
612 Karnali|Humla|Tanjakot Gaunpalika|5
613 Karnali|Jajarkot|Bheri Malika Municipality|13
614 Karnali|Jajarkot|Chhedagad Municipality|13
615 Karnali|Jajarkot|Nalgad Municipality|13
616 Karnali|Jajarkot|Junichande Gaunpalika|11
617 Karnali|Jajarkot|Barekot Gaunpalika|9
618 Karnali|Jajarkot|Kuse Gaunpalika|9
619 Karnali|Jajarkot|Shivalaya Gaunpalika|9
620 Karnali|Jumla|Chandannath Municipality|10
621 Karnali|Jumla|Tila Gaunpalika|9
622 Karnali|Jumla|Kanaka Sundari Gaunpalika|8
623 Karnali|Jumla|Tatopani Gaunpalika|8
624 Karnali|Jumla|Hima Gaunpalika|7
625 Karnali|Jumla|Patarasi Gaunpalika|7
626 Karnali|Jumla|Sinja Gaunpalika|6
627 Karnali|Jumla|Guthichaur Gaunpalika|5
628 Karnali|Kalikot|Khandachakra Municipality|11
629 Karnali|Kalikot|Tilagupha Municipality|11
630 Karnali|Kalikot|Naraharinath Gaunpalika|9
631 Karnali|Kalikot|Pachal Jharana Gaunpalika|9
632 Karnali|Kalikot|Palata Gaunpalika|9
633 Karnali|Kalikot|Raskot Municipality|9
634 Karnali|Kalikot|Sanni Tribeni Gaunpalika|9
635 Karnali|Kalikot|Shuva Kalika Gaunpalika|8
636 Karnali|Kalikot|Mahawai Gaunpalika|7
637 Karnali|Mugu|Chhayanath Rara Municipality|14
638 Karnali|Mugu|Khatyad Gaunpalika|11
639 Karnali|Mugu|Soru Gaunpalika|11
640 Karnali|Mugu|Mugumakarmarog Gaunpalika|9
641 Karnali|Rukum (West)|Aathabisakot Municipality|14
642 Karnali|Rukum (West)|Chaurjahari Municipality|14
643 Karnali|Rukum (West)|Musikot Municipality|14
644 Karnali|Rukum (West)|Sanibheri Gaunpalika|11
645 Karnali|Rukum (West)|Banphikot Gaunpalika|10
646 Karnali|Rukum (West)|Tribeni Gaunpalika|10
647 Karnali|Salyan|Sharada Municipality|15
648 Karnali|Salyan|Bagachour Municipality|12
649 Karnali|Salyan|Banagad Kupinde Municipality|12
650 Karnali|Salyan|Chhatreshwori Gaunpalika|7
651 Karnali|Salyan|Kalimati Gaunpalika|7
652 Karnali|Salyan|Kumakh Gaunpalika|7
653 Karnali|Salyan|Darma Gaunpalika|6
654 Karnali|Salyan|Kapurkot Gaunpalika|6
655 Karnali|Salyan|Tribeni Gaunpalika|6
656 Karnali|Salyan|Siddha Kumakh Gaunpalika|5
657 Karnali|Surkhet|Birendranagar Municipality|16
658 Karnali|Surkhet|Bheriganga Municipality|13
659 Karnali|Surkhet|Gurtu Gaunpalika|10
660 Karnali|Surkhet|Lekbeshi Municipality|10
661 Karnali|Surkhet|Chaukune Gaunpalika|9
662 Karnali|Surkhet|Chingad Gaunpalika|9
663 Karnali|Surkhet|Panchapuri Municipality|9
664 Karnali|Surkhet|Simta Gaunpalika|9
665 Karnali|Surkhet|Barakot Gaunpalika|8
666 Karnali|Surkhet|Uttarganga Municipality|8
667 Sudurpashchim|Achham|Mangalsen Municipality|11
668 Sudurpashchim|Achham|Sanphebagar Municipality|9
669 Sudurpashchim|Achham|Chaurpati Gaunpalika|10
670 Sudurpashchim|Achham|Dhakari Gaunpalika|8
671 Sudurpashchim|Achham|Bannigadhi Jayagadh Gaunpalika|8
672 Sudurpashchim|Achham|Mellekh Gaunpalika|8
673 Sudurpashchim|Achham|Turmakhand Gaunpalika|8
674 Sudurpashchim|Achham|Kahankanda Gaunpalika|7
675 Sudurpashchim|Achham|Kedarstan Gaunpalika|7
676 Sudurpashchim|Achham|Ramaroshan Gaunpalika|7
677 Sudurpashchim|Achham|Panchadeval Binayak Municipality|8
678 Sudurpashchim|Baitadi|Dasharathchand Municipality|11
679 Sudurpashchim|Baitadi|Patan Municipality|10
680 Sudurpashchim|Baitadi|Purchaudi Municipality|10
681 Sudurpashchim|Baitadi|Dogadakedar Gaunpalika|9
682 Sudurpashchim|Baitadi|Dilasaini Gaunpalika|8
683 Sudurpashchim|Baitadi|Pancheshwar Gaunpalika|8
684 Sudurpashchim|Baitadi|Surnaya Gaunpalika|8
685 Sudurpashchim|Baitadi|Sigas Gaunpalika|7
686 Sudurpashchim|Baitadi|Shivnath Gaunpalika|7
687 Sudurpashchim|Baitadi|Melauli Municipality|5
688 Sudurpashchim|Bajhang|Jayaprithvi Municipality|11
689 Sudurpashchim|Bajhang|Bungal Municipality|10
690 Sudurpashchim|Bajhang|Talkot Municipality|9
691 Sudurpashchim|Bajhang|Durgathali Gaunpalika|9
692 Sudurpashchim|Bajhang|Khaptad Chhanna Gaunpalika|9
693 Sudurpashchim|Bajhang|Masta Gaunpalika|9
694 Sudurpashchim|Bajhang|Saipal Gaunpalika|9
695 Sudurpashchim|Bajhang|Surma Gaunpalika|9
696 Sudurpashchim|Bajhang|Kedarsyu Gaunpalika|8
697 Sudurpashchim|Bajhang|Bithadchir Gaunpalika|7
698 Sudurpashchim|Bajhang|Chhapali Gaunpalika|7
699 Sudurpashchim|Bajura|Budhinanda Municipality|8
700 Sudurpashchim|Bajura|Triveni Municipality|8
701 Sudurpashchim|Bajura|Gaumul Gaunpalika|9
702 Sudurpashchim|Bajura|Himali Gaunpalika|9
703 Sudurpashchim|Bajura|Jagannath Gaunpalika|9
704 Sudurpashchim|Bajura|Swamikartik Khapar Gaunpalika|9
705 Sudurpashchim|Bajura|Badimalika Municipality|9
706 Sudurpashchim|Bajura|Budhiganga Municipality|9
707 Sudurpashchim|Bajura|Khaptad Chhanna Gaunpalika|8
708 Sudurpashchim|Dadeldhura|Amargadhi Municipality|11
709 Sudurpashchim|Dadeldhura|Parashuram Municipality|9
710 Sudurpashchim|Dadeldhura|Aalital Gaunpalika|8
711 Sudurpashchim|Dadeldhura|Ajaymeru Gaunpalika|8
712 Sudurpashchim|Dadeldhura|Nawadurga Gaunpalika|8
713 Sudurpashchim|Dadeldhura|Ganyapdhura Gaunpalika|8
714 Sudurpashchim|Darchula|Shailyashikhar Municipality|10
715 Sudurpashchim|Darchula|Mahakali Municipality|9
716 Sudurpashchim|Darchula|Malikaarjun Gaunpalika|9
717 Sudurpashchim|Darchula|Apihimal Gaunpalika|8
718 Sudurpashchim|Darchula|Byans Gaunpalika|8
719 Sudurpashchim|Darchula|Dunhu Gaunpalika|8
720 Sudurpashchim|Darchula|Lekam Gaunpalika|8
721 Sudurpashchim|Darchula|Naugad Gaunpalika|6
722 Sudurpashchim|Darchula|Marma Gaunpalika|5
723 Sudurpashchim|Doti|Dipayal Silgadhi Municipality|11
724 Sudurpashchim|Doti|Shikhar Municipality|9
725 Sudurpashchim|Doti|Aadarsh Mahadevsthan Gaunpalika|9
726 Sudurpashchim|Doti|Badikedar Gaunpalika|9
727 Sudurpashchim|Doti|Bogtan Fudsil Gaunpalika|9
728 Sudurpashchim|Doti|Jorayal Gaunpalika|9
729 Sudurpashchim|Doti|K.I. Singh Gaunpalika|9
730 Sudurpashchim|Doti|Purbichauki Gaunpalika|5
731 Sudurpashchim|Kailali|Dhangadhi Sub-Metropolitan City|19
732 Sudurpashchim|Kailali|Tikapur Municipality|10
733 Sudurpashchim|Kailali|Bhajani Municipality|10
734 Sudurpashchim|Kailali|Ghodaghodi Municipality|15
735 Sudurpashchim|Kailali|Godawari Municipality|12
736 Sudurpashchim|Kailali|Janaki Rural Municipality|10
737 Sudurpashchim|Kailali|Kailari Gaunpalika|10
738 Sudurpashchim|Kailali|Bardagoriya Gaunpalika|9
739 Sudurpashchim|Kailali|Chure Gaunpalika|9
740 Sudurpashchim|Kailali|Joshipur Gaunpalika|6
741 Sudurpashchim|Kailali|Lamki Chuha Municipality|9
742 Sudurpashchim|Kailali|Mohanyal Gaunpalika|7
743 Sudurpashchim|Kanchanpur|Mahendranagar Municipality|12
744 Sudurpashchim|Kanchanpur|Belauri Municipality|9
745 Sudurpashchim|Kanchanpur|Bedkot Municipality|9
746 Sudurpashchim|Kanchanpur|Bhimdatta Municipality|15
747 Sudurpashchim|Kanchanpur|Krishnapur Municipality|9
748 Sudurpashchim|Kanchanpur|Laljhadi Gaunpalika|7
749 Sudurpashchim|Kanchanpur|Punarbas Municipality|9
750 Sudurpashchim|Kanchanpur|Shuklaphanta Municipality|11
751 Sudurpashchim|Kanchanpur|Beldandi Gaunpalika|6
752 Sudurpashchim|Kanchanpur|Dodhara Chandani Municipality|7
"""
# ────────────────────────────────────────────────────────────────────────────

# ----------------------------------------------------------------------
# Parse PDF data to build a mapping: (district_english, local_english) -> ward_count
def _parse_pdf() -> Dict[Tuple[str, str], int]:
    mapping = {}
    lines = PDF_DATA.strip().splitlines()
    for line in lines:
        if '|' not in line:
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) == 4:
            province, district, local, ward = parts
            try:
                ward_int = int(ward)
                mapping[(district, local)] = ward_int
            except ValueError:
                continue
    return mapping

WARD_MAPPING = _parse_pdf()

# ── Build district name -> ID mapping (using English names) ──
DISTRICT_ENGLISH_TO_ID = {d["name"]: d["id"] for d in DISTRICTS}
# Fix for mismatched names from PDF
DISTRICT_ENGLISH_TO_ID["Bhatkapur"] = 29  # Bhaktapur
DISTRICT_ENGLISH_TO_ID["Rukum (East)"] = 54
DISTRICT_ENGLISH_TO_ID["Rukum (West)"] = 59
DISTRICT_ENGLISH_TO_ID["Chitawan"] = 35   # Chitwan
DISTRICT_ENGLISH_TO_ID["Kavrepalanchok"] = 27
DISTRICT_ENGLISH_TO_ID["Sindhupalchok"] = 26

LOCAL_LEVEL_TYPES = {
    0: "Rural Municipality",
    1: "Municipality",
    2: "Sub Metropolitan City",
    3: "Metropolitan City",
}

def _determine_type(name: str) -> int:
    """Determine local level type based on English name."""
    name_lower = name.lower()
    if "metropolitan city" in name_lower:
        return 3
    elif "sub-metropolitan city" in name_lower:
        return 2
    elif "municipality" in name_lower:
        return 1
    else:
        return 0

# ── Generate LOCAL_LEVELS with English names and correct ward counts ──
LOCAL_LEVELS = []
WARD_COUNTS_BY_ID = {}

local_id = 1
for line in PDF_DATA.strip().splitlines():
    if '|' not in line:
        continue
    parts = [p.strip() for p in line.split('|')]
    if len(parts) == 4:
        province, district_eng, local_eng, ward_str = parts
        try:
            ward_count = int(ward_str)
        except ValueError:
            continue
        district_id = DISTRICT_ENGLISH_TO_ID.get(district_eng)
        if district_id is None:
            # fallback corrections
            if district_eng == "Bhatkapur":
                district_id = 29
            elif district_eng == "Rukum (East)":
                district_id = 54
            elif district_eng == "Rukum (West)":
                district_id = 59
            elif district_eng == "Chitawan":
                district_id = 35
            else:
                print(f"Warning: District '{district_eng}' not found; skipping.")
                continue
        level_type = _determine_type(local_eng)
        type_name = LOCAL_LEVEL_TYPES[level_type]
        LOCAL_LEVELS.append({
            "id": local_id,
            "district_id": district_id,
            "name": local_eng,
            "nepali_name": local_eng,  # fallback; we don't have Nepali names for all
            "type": level_type,
            "type_name": type_name,
        })
        WARD_COUNTS_BY_ID[local_id] = ward_count
        local_id += 1

# ────────────────────────────────────────────────────────────────────────────
def seed_locations(db):
    """Insert or replace location data with English names and correct ward counts."""

# ── PostgreSQL-compatible seed_locations ─────────────────────────────────────
def seed_locations(conn):
    """Create location tables and insert seed data. conn is a psycopg2 connection."""
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id   INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT
        );
        CREATE TABLE IF NOT EXISTS provinces (
            id          INTEGER PRIMARY KEY,
            country_id  INTEGER NOT NULL,
            name        TEXT NOT NULL,
            code        TEXT,
            nepali_name TEXT,
            FOREIGN KEY(country_id) REFERENCES countries(id)
        );
        CREATE TABLE IF NOT EXISTS districts (
            id          INTEGER PRIMARY KEY,
            province_id INTEGER NOT NULL,
            name        TEXT NOT NULL,
            nepali_name TEXT,
            FOREIGN KEY(province_id) REFERENCES provinces(id)
        );
        CREATE TABLE IF NOT EXISTS local_levels (
            id          INTEGER PRIMARY KEY,
            district_id INTEGER NOT NULL,
            name        TEXT NOT NULL,
            nepali_name TEXT,
            level_type  INTEGER NOT NULL,
            type_name   TEXT NOT NULL,
            ward_count  INTEGER DEFAULT 35,
            FOREIGN KEY(district_id) REFERENCES districts(id)
        );
        CREATE TABLE IF NOT EXISTS wards (
            id             SERIAL PRIMARY KEY,
            local_level_id INTEGER NOT NULL,
            ward_number    INTEGER NOT NULL,
            UNIQUE(local_level_id, ward_number),
            FOREIGN KEY(local_level_id) REFERENCES local_levels(id)
        );
        CREATE TABLE IF NOT EXISTS areas (
            id      SERIAL PRIMARY KEY,
            ward_id INTEGER NOT NULL,
            name    TEXT NOT NULL,
            FOREIGN KEY(ward_id) REFERENCES wards(id)
        );
        CREATE TABLE IF NOT EXISTS admin_locations (
            id             SERIAL PRIMARY KEY,
            user_id        TEXT NOT NULL,
            country_id     INTEGER,
            province_id    INTEGER,
            district_id    INTEGER,
            local_level_id INTEGER,
            ward_id        INTEGER,
            area_id        INTEGER,
            created_at     TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS news_approvals (
            id         TEXT PRIMARY KEY,
            news_id    TEXT NOT NULL,
            admin_id   TEXT NOT NULL,
            action     TEXT NOT NULL,
            comment    TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(news_id, admin_id)
        );
        """)

        # Insert countries
        for row in COUNTRIES:
            cur.execute(
                "INSERT INTO countries (id,name,code) VALUES (%s,%s,%s) ON CONFLICT (id) DO NOTHING",
                (row["id"], row["name"], row["code"])
            )

        # Insert provinces
        for p in PROVINCES:
            cur.execute(
                "INSERT INTO provinces (id,country_id,name,nepali_name) VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, nepali_name=EXCLUDED.nepali_name",
                (p["id"], p["country_id"], p["name"], p["nepali_name"])
            )

        # Insert districts
        for d in DISTRICTS:
            cur.execute(
                "INSERT INTO districts (id,province_id,name,nepali_name) VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, nepali_name=EXCLUDED.nepali_name",
                (d["id"], d["province_id"], d["name"], d["nepali_name"])
            )

        # Insert local levels
        for ll in LOCAL_LEVELS:
            ward_count = WARD_COUNTS_BY_ID.get(ll["id"], 35)
            cur.execute(
                "INSERT INTO local_levels (id,district_id,name,nepali_name,level_type,type_name,ward_count) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, ward_count=EXCLUDED.ward_count",
                (ll["id"], ll["district_id"], ll["name"], ll["nepali_name"], ll["type"], ll["type_name"], ward_count)
            )

        # Pre-seed wards
        for ll in LOCAL_LEVELS:
            ward_count = WARD_COUNTS_BY_ID.get(ll["id"], 35)
            for ward_num in range(1, ward_count + 1):
                cur.execute(
                    "INSERT INTO wards (local_level_id, ward_number) VALUES (%s,%s) ON CONFLICT (local_level_id, ward_number) DO NOTHING",
                    (ll["id"], ward_num)
                )

    conn.commit()


# ── Helpers (psycopg2 RealDictCursor compatible) ─────────────────────────────

def build_location_label(conn, country_id=None, province_id=None, district_id=None,
                         local_level_id=None, ward_id=None, area_id=None, fallback=None):
    """Build a human-readable location label from IDs."""
    parts = []

    def get_one(table, _id, col="name"):
        if not _id:
            return None
        with conn.cursor() as cur:
            cur.execute(f"SELECT {col} FROM {table} WHERE id=%s", (_id,))
            row = cur.fetchone()
        return row[col] if row else None

    area = None
    if area_id:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM areas WHERE id=%s", (area_id,))
            row = cur.fetchone()
            area = row["name"] if row else None

    ward = None
    if ward_id:
        with conn.cursor() as cur:
            cur.execute("SELECT ward_number, local_level_id FROM wards WHERE id=%s", (ward_id,))
            row = cur.fetchone()
        if row:
            ward = f"Ward {row['ward_number']}"
            if not local_level_id:
                local_level_id = row["local_level_id"]

    local_level = get_one("local_levels", local_level_id)
    district = get_one("districts", district_id)
    province = get_one("provinces", province_id)
    country = get_one("countries", country_id) or "Nepal"

    if area: parts.append(area)
    if ward: parts.append(ward)
    if local_level: parts.append(local_level)
    if district: parts.append(district)
    if province: parts.append(province)
    if country: parts.append(country)
    if not parts and fallback:
        return fallback
    return ", ".join(parts)


def location_scope_from_ids(country_id=None, province_id=None, district_id=None,
                            local_level_id=None, ward_id=None, area_id=None):
    """Determine the deepest location scope level and ID."""
    if area_id:       return ("area", area_id)
    if ward_id:       return ("ward", ward_id)
    if local_level_id: return ("local_level", local_level_id)
    if district_id:   return ("district", district_id)
    if province_id:   return ("province", province_id)
    if country_id:    return ("country", country_id)
    return (None, None)


def get_ward_count(local_level_id, local_level_type):
    return WARD_COUNTS_BY_ID.get(local_level_id, 35)
