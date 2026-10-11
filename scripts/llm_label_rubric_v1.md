# Knee MRI report reading rubric, version 1 (LLM label-repair pilot, D-025)

You read knee MRI radiology reports and record, for twelve findings, **what the report states**. You are not
shown any image or any existing label, and you must not look for them: read only this rubric and your batch file.

## Scope

- Use the findings / results / impression text. Ignore the clinical history, the referral question
  (for example "?meniscal tear", "Klinische Inlichtingen", "Indicación"), technique and protocol.
- Reports may be in any language (English, German, Dutch, Spanish, Portuguese, French, Italian, Greek, Bulgarian,
  Turkish, Croatian, Russian, ...). Read the original language. Quote evidence verbatim in the original language.
- One report = one knee. Medial and lateral are distinct: a statement about one side does not answer the other.

## Status (one per finding)

- `present`: the report asserts the finding (including "small", "mild", "partial", "grade 1").
- `absent`: the report denies it, or describes the structure as normal / intact / preserved / unremarkable, or a
  global negative clearly covers it ("no other abnormality", "otherwise normal knee"). For a global negative,
  quote that sentence and set the qualifier to `global negative`.
- `uncertain`: hedged wording ("possible", "probable", "suspected", "cannot be excluded", "questionable",
  "likely"), or a description that does not clearly meet the definition (see the definitions).
- `not_mentioned`: the report says nothing that answers this finding.

## Probability `p` (that the report asserts the finding as defined)

- `present`, unqualified or moderate-severe: 0.90-1.00; `present` but minimal / small / mild / low grade: 0.75-0.90.
- `uncertain`: 0.30-0.65 (higher when the wording leans towards present).
- `absent`, explicit: 0.00-0.05; `absent` by a global negative only: 0.05-0.15.
- `not_mentioned`: 0.10.

## Definitions

| Finding | Counts as present | Does not count (or `uncertain`, with a qualifier) |
|---|---|---|
| ACL | tear of the anterior cruciate ligament: complete, partial, high-grade, sprain, rupture, avulsion; tear of an ACL graft | intact graft after reconstruction (`absent`, qualifier `reconstructed, intact graft`); mucoid degeneration or ganglion without tear (`uncertain`) |
| MCL | medial collateral ligament injury: sprain or tear of any grade, including grade 1 (periligamentous edema) | chronic thickening or old injury without active injury (`uncertain`) |
| Medial Meniscus | tear of the medial meniscus of any type (horizontal, oblique, radial, complex, bucket-handle, root, degenerative tear, re-tear) | intrasubstance degeneration / grade 1-2 signal without a tear (`absent`, qualifier `degeneration, no tear`); post-meniscectomy without a described re-tear (`uncertain`); extrusion alone (`uncertain`) |
| Lateral Meniscus | the same for the lateral meniscus | as above |
| Medial OA | osteoarthritis or cartilage damage of the medial femorotibial compartment: chondropathy / chondromalacia of any grade, chondral defect or thinning, osteophytes, joint space narrowing, subchondral sclerosis or cysts attributed to OA | patellar or trochlear cartilage (that is PF OA) |
| Lateral OA | the same for the lateral femorotibial compartment | as above |
| PF OA | cartilage damage or osteoarthritis of the patellofemoral joint: chondromalacia / chondropathy of the patella or trochlea, chondral defects there, patellofemoral osteophytes | - |
| Effusion | knee joint effusion of any size, including small or minimal, hemarthrosis, lipohemarthrosis | "physiological amount of fluid" (`uncertain`, qualifier `physiological fluid`); fluid only in a bursa or cyst (not effusion) |
| Synovitis | synovitis, synovial thickening or hypertrophy, Hoffa fat pad synovitis or inflammation, reactive synovitis | - |
| Baker's | popliteal (Baker's) cyst, gastrocnemius-semimembranosus bursal cyst, ruptured Baker's cyst | other cysts (parameniscal, ganglion) |
| Contusion | bone contusion, bone bruise, bone marrow edema from trauma or without a stated cause | marrow edema explicitly attributed to a non-traumatic cause (degenerative / subchondral OA edema, stress reaction, SONK, osteonecrosis): `uncertain`, qualifier naming the cause |
| Fracture | any fracture: traumatic, avulsion (including Segond), impaction, osteochondral, insufficiency or subchondral insufficiency fracture | old healed fracture: `present`, qualifier `old/healed`; stress reaction without a fracture line: `uncertain` |

## Output

For your batch file (a JSON list of `{"rid", "report"}`), write one JSON list, one object per report, to the
output path you are given:

```json
[
  {"rid": "pilot_0001",
   "findings": {
     "ACL": {"status": "absent", "p": 0.02, "evidence": "Ligamentum cruciatum anterius intakt.", "qualifier": ""},
     "MCL": {"status": "not_mentioned", "p": 0.10, "evidence": "", "qualifier": ""},
     "...": {}
   }}
]
```

- All twelve keys exactly as written: `ACL`, `MCL`, `Medial Meniscus`, `Lateral Meniscus`, `Medial OA`,
  `Lateral OA`, `PF OA`, `Effusion`, `Synovitis`, `Baker's`, `Contusion`, `Fracture`.
- `evidence`: a verbatim quote (at most about 200 characters) for `present`, `absent` and `uncertain`; empty for
  `not_mentioned`.
- `qualifier`: short English note when relevant (severity, grade, compartment detail, the reason for
  `uncertain`, `global negative`); otherwise empty.
- Valid JSON (UTF-8). Do not add commentary outside the JSON file.
