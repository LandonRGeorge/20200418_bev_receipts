dict_county_map = ({
1: 'ANDERSON',
2: 'ANDREWS',
3: 'ANGELINA',
4: 'ARANSAS',
5: 'ARCHER',
6: 'ARMSTRONG',
7: 'ATASCOSA',
8: 'AUSTIN',
9: 'BAILEY',
10: 'BANDERA',
11: 'BASTROP',
12: 'BAYLOR',
13: 'BEE',
14: 'BELL',
15: 'BEXAR',
16: 'BLANCO',
17: 'BORDEN',
18: 'BOSQUE',
19: 'BOWIE',
20: 'BRAZORIA',
21: 'BRAZOS',
22: 'BREWSTER',
23: 'BRISCO',
24: 'BROOKS',
25: 'BROWN',
26: 'BURLESON',
27: 'BURNET',
28: 'CALDWELL',
29: 'CALHOUN',
30: 'CALLAHAN',
31: 'CAMERON',
32: 'CAMP',
33: 'CARSON',
34: 'CASS',
35: 'CASTRO',
36: 'CHAMBERS',
37: 'CHEROKEE',
38: 'CHILDRESS',
39: 'CLAY',
40: 'COCHRAN',
41: 'COKE',
42: 'COLEMAN',
43: 'COLLIN',
44: 'COLLINGSWORTH',
45: 'COLORADO',
46: 'COMAL',
47: 'COMANCHE',
48: 'CONCHO',
49: 'COOKE',
50: 'CORYELL',
51: 'COTTLE',
52: 'CRANE',
53: 'CROCKETT',
54: 'CROSBY',
55: 'CULBERSON',
56: 'DALLAM',
57: 'DALLAS',
58: 'DAWSON',
59: 'DEAF SMITH',
60: 'DELTA',
61: 'DENTON',
62: 'DE WITT',
63: 'DICKENS',
64: 'DIMMITT',
65: 'DONLEY',
66: 'DUVAL',
67: 'EASTLAND',
68: 'ECTOR',
69: 'EDWARDS',
70: 'ELLIS',
71: 'EL PASO',
72: 'ERATH',
73: 'FALLS',
74: 'FANNIN',
75: 'FAYETTE',
76: 'FISHER',
77: 'FLOYD',
78: 'FOARD',
79: 'FORT BEND',
80: 'FRANKLIN',
81: 'FREESTONE',
82: 'FRIO',
83: 'GAINES',
84: 'GALVESTON',
85: 'GARZA',
86: 'GILLESPIE',
87: 'GLASSCOCK',
88: 'GOLIAD',
89: 'GONZALES',
90: 'GRAY',
91: 'GRAYSON',
92: 'GREGG',
93: 'GRIMES',
94: 'GUADALUPE',
95: 'HALE',
96: 'HALL',
97: 'HAMILTON',
98: 'HANSFORD',
99: 'HARDEMAN',
100: 'HARDIN',
101: 'HARRIS',
102: 'HARRISON',
103: 'HARTLEY',
104: 'HASKELL',
105: 'HAYS',
106: 'HEMPHILL',
107: 'HENDERSON',
108: 'HIDALGO',
109: 'HILL',
110: 'HOCKLEY',
111: 'HOOD',
112: 'HOPKINS',
113: 'HOUSTON',
114: 'HOWARD',
115: 'HUDSPETH',
116: 'HUNT',
117: 'HUTCHINSON',
118: 'IRION',
119: 'JACK',
120: 'JACKSON',
121: 'JASPER',
122: 'JEFF DAVIS',
123: 'JEFFERSON',
124: 'JIM HOGG',
125: 'JIM WELLS',
126: 'JOHNSON',
127: 'JONES',
128: 'KARNES',
129: 'KAUFMAN',
130: 'KENDALL',
131: 'KENEDY',
132: 'KENT',
133: 'KERR',
134: 'KIMBLE',
135: 'KING',
136: 'KINNEY',
137: 'KLEBERG',
138: 'KNOX',
139: 'LAMAR',
140: 'LAMB',
141: 'LAMPASAS',
142: 'LA SALLE',
143: 'LAVACA',
144: 'LEE',
145: 'LEON',
146: 'LIBERTY',
147: 'LIMESTONE',
148: 'LIPSCOMB',
149: 'LIVE OAK',
150: 'LLANO',
151: 'LOVING',
152: 'LUBBOCK',
153: 'LYNN',
154: 'MADISON',
155: 'MARION',
156: 'MARTIN',
157: 'MASON',
158: 'MATAGORDA',
159: 'MAVERICK',
160: 'MCCULLOCH',
161: 'MCLENNAN',
162: 'MCMULLEN',
163: 'MEDINA',
164: 'MENARD',
165: 'MIDLAND',
166: 'MILAM',
167: 'MILLS',
168: 'MITCHELL',
169: 'MONTAGUE',
170: 'MONTGOMERY',
171: 'MOORE',
172: 'MORRIS',
173: 'MOTLEY',
174: 'NACOGDOCHES',
175: 'NAVARRO',
176: 'NEWTON',
177: 'NOLAN',
178: 'NUECES',
179: 'OCHILTREE',
180: 'OLDHAM',
181: 'ORANGE',
182: 'PALO PINTO',
183: 'PANOLA',
184: 'PARKER',
185: 'PARMER',
186: 'PECOS',
187: 'POLK',
188: 'POTTER',
189: 'PRESIDIO',
190: 'RAINS',
191: 'RANDALL',
192: 'REAGAN',
193: 'REAL',
194: 'RED RIVER',
195: 'REEVES',
196: 'REFUGIO',
197: 'ROBERTS',
198: 'ROBERTSON',
199: 'ROCKWALL',
200: 'RUNNELS',
201: 'RUSK',
202: 'SABINE',
203: 'SAN AUGUSTINE',
204: 'SAN JACINTO',
205: 'SAN PATRICIO',
206: 'SAN SABA',
207: 'SCHLEICHER',
208: 'SCURRY',
209: 'SHACKELFORD',
210: 'SHELBY',
211: 'SHERMAN',
212: 'SMITH',
213: 'SOMERVELL',
214: 'STARR',
215: 'STEPHENS',
216: 'STERLING',
217: 'STONEWALL',
218: 'SUTTON',
219: 'SWISHER',
220: 'TARRANT',
221: 'TAYLOR',
222: 'TERRELL',
223: 'TERRY',
224: 'THROCKMORTON',
225: 'TITUS',
226: 'TOM GREEN',
227: 'TRAVIS',
228: 'TRINITY',
229: 'TYLER',
230: 'UPSHUR',
231: 'UPTON',
232: 'UVALDE',
233: 'VAL VERDE',
234: 'VAN ZANDT',
235: 'VICTORIA',
236: 'WALKER',
237: 'WALLER',
238: 'WARD',
239: 'WASHINGTON',
240: 'WEBB',
241: 'WHARTON',
242: 'WHEELER',
243: 'WICHITA',
244: 'WILBARGER',
245: 'WILLACY',
246: 'WILLIAMSON',
247: 'WILSON',
248: 'WINKLER',
249: 'WISE',
250: 'WOOD',
251: 'YOAKUM',
252: 'YOUNG',
253: 'ZAPATA',
254: 'ZAVALA'
})