## Sample bank

HEX content:

```
Unknown         | Mode | Unknown | Step | Unknown | Tone | Dup | Channel name ASCII (22 to 54)  | Unknown fixed? | Unknown variable (dstar?)
25 0D020320 28 8    0       00      80      E4      1     8     49523355582020202020202020202020 0087461D18745020 4081020408102040810204081020
25 0D020320 20 A    0       00      80      E4      3     8     4952335558205453514C202020202020 0087461D18745020 4081020408102040810204081020
24 5AD60060 20 8    0       00      80      E4      0     0     415249204D4E202D2056202020202020 0087461D18745020 4081020408102040810204081020
00 5C620000 20 8    3       00      20      E4      0     0     56656E657A6961205457523220202020 0087461D18745020 4081020408102040810204081020
24 5A8A00A0 20 8    5       00      80      E4      0     8     49523355472043472020202020202020 0087461D18745020 93499D58E8104393499D58E81047
24 5AFA0060 20 8    5       00      80      E4      0     4     4952344D4F2043472020202020202020 0087461D18745020 9349A4D9E810439349A4D9E81047
```

CSV content:
```
05; 430,412500; DUP+;   5,000000;   25kHz;  FM; IR3UX;          SKIP;   TONE;  94,8Hz; 88,5Hz; 023; BOTH N; OFF;    0;  CQCQCQ;         ;
06; 430,412500; DUP+;   5,000000;   25kHz;  FM; IR3UX TSQL;     OFF;    TSQL;  88,5Hz; 94,8Hz; 023; BOTH N; OFF;    0;  CQCQCQ;         ;
00; 145,337500; OFF;    0,600000;   25kHz;  FM; ARI MN - V;     OFF;    OFF;   88,5Hz; 88,5Hz; 023; BOTH N; OFF;    0;  CQCQCQ;         ;
88; 118,250000; OFF;    0,000000;   8,33kHz;AM; Venezia TWR2;   OFF;    OFF;   88,5Hz; 88,5Hz; 023; BOTH N; OFF;    0;  CQCQCQ;         ;
92; 144,862500; DUP+;   1,000000;   25kHz;  DV; IR3UG CG;       OFF;    OFF;   88,5Hz; 88,5Hz; 023; BOTH N; OFF;    0;  CQCQCQ; IR3UG  C;   IR3UG  G
94; 145,562500; DUP-;   0,600000;   25kHz;  DV; IR4MO CG;       OFF;    OFF;   88,5Hz; 88,5Hz; 023; BOTH N; OFF;    0;  CQCQCQ; IR4MO  C;   IR4MO  G

```

### Channel name

Channel naming follows the same convention we already got for the IC-2820, in this case from 22 to 54

### Channel mode

Channel mode is the 13th byte in the HEX string