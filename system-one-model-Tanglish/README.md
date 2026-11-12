# Gemini Decisions API (`gemini-decision-1`)

Tea kadai example vechu, ungalukku crystal clear-ah puriyara maari Tanglish-la explain panren. Konjam kooda confuse aagaadheenga!

---

### First, Normal LLM-kum Decisions API-kum enna difference?

Oru real-life situation paapom:

* **Normal LLM (Gemini 1.5 / 2.0 / ChatGPT maari):**
  Neenga tea kadai anna kitta poi: *"Anna, kadaila tea irukka illaya?"* nu kekkareenga.
  Andha anna enna pannuvaaru: *"Thambi, namma kadaila 1990-la irundhu Nilgiri thela pottu, fresh pasumpaal kaachi super-ah tea podrom... tea irukku thambi!"* nu 2 minute oru periya essay pesuvaaru.
  * **Problem:** Namma ketadhu simple Yes/No dhaan. Aana avar vala vala-nu text generate pannadhunaala time waste (**high latency**), adhu mattum illama periya paragraph pesinadhukku extra kaasu bill (**output token cost**).

* **Decisions API (`gemini-decision-1`):**
  Neenga adhey tea kadai anna kitta *"Tea irukka illaya?"* nu kekkareenga.
  Avaru vaaye thorakka maataaru. Instant-ah **"YES" (99% confidence)** nu thalaya aattitu poite irupparu.
  * **Result:** Zero extra words, blink panra gap-la (150ms-la) answer, zero output token cost!

> **Short-ah sonna:** Decisions API is **NOT for generating text or essays**. Idhu **pure-ah decisions edukkuradhukku mattum design panna fast classification model!**

---

### Idhoda 3 Mukkiyamaana Question Types (Namma enna kekkalam?)

Namma oru input (text, photo, audio, video, illa PDF) kuduthu, 3 vidhamana kelvigal kekkalam:

#### 1. `noul` (Yes or No / Boolean)
* Idhu binary decision. True-ah illai False-ah nu mattum paakum.
* **Example:** *"Customer message-la kovama pesuraara illaya?"*
* **Output:** Probability value kodukkum (e.g., `0.95` na 95% chance he is angry).

#### 2. `choice` (Multiple Choice / Options)
* Namma options kudupom (upto 255 options kudukalam), adhu correct option-ah select pannum.
* **Example:** *"Indha customer ticket-ah endha department-ku anupalaam?"*
  * Option A: `billing` (Kaasu / refund issues)
  * Option B: `replacements` (Porul odanju pochu)
  * Option C: `general` (General doubts)
* **Output:** `replacements` nu choose pannitu, ovvoru option-kum evlo probability nu percentage-oda kuduthudum.

#### 3. `score` (Rating / Rubric)
* Oru criteria vechu rating podum (like 1 to 5 stars, illa 0 to 10 points).
* **Example:** *"Indha resume / code quality-ku 1 to 5-la evlo score kudukalam?"*
* **Output:** Weighted score calculation kudukkum.

---

### Yen idhu semma Game Changer? (Super Powers)

1. **Output Token Cost = $0.00 (Zero Kaasu!)**
   * Normal models-la output tokens-ku dhaan jaasthi charge pannuvaanga.
   * Decisions API-la text generation-e kedayadhu. Adhanala **output tokens are 100% FREE**! Input tokens-ku mattum dhaan romba cheap-ah ($0.10 per 1 Million tokens) charge pannuvanga.
2. **Rocket Speed (150ms - 250ms)**
   * Autoregressive generation (word-by-word typing) illadha nala, super fast-ah reply varum.
3. **Ore Shot-la 1,000 Questions!**
   * Neenga oru periya document (upto 256K tokens) illa video kuduthu, adhayey input-ah vechu **ore API call-la 1,000 questions** ketaalum, single pass-la instant-ah answer pannidum.
4. **Multimodal Support**
   * Text mattum illa — image, audio, video, PDF documents edhu venalum input-ah kudukalam.

---

### Simple Python Code (Idha epdi use panradhu?)

SDK install pannanum:
```bash
pip install --upgrade google-genai
```

Python code:
```python
from google import genai

# v1beta endpoint use pannanum
client = genai.Client(http_options={"api_version": "v1beta"})

# Decisions API call
result = client.decisions.create(
    model="gemini-decision-1",
    input="Naan order panna blue tea cup odanju pochu bro. Refund venum.",
    questions={
        # Question 1: Yes/No type
        "is_damaged": {
            "type": "noul",
            "instructions": "Porul damage aagirukka?",
        },
        # Question 2: Multiple Choice routing
        "department": {
            "type": "choice",
            "instructions": "Indha complaint-ah yaaru handle pannanum?",
            "criteria": {
                "billing": "Refund and payment issues.",
                "delivery": "Delay in courier.",
                "general": "General questions.",
            },
        },
    },
)

# Answers eduthu paapom
damaged = result.answers["is_damaged"]
dept = result.answers["department"]

print("Damaged ah?:", damaged.noul, "Confidence:", damaged.confidence)
print("Department:", dept.choice, "Confidence:", dept.confidence)
```

---

### Enga use panna super-ah irukkum? (Real Use-Cases)

1. **AI Agent Routing:** User kitta irundhu oru message varudhu. Adha direct-ah Coding bot-ku anupalaama, Weather bot-ku anupalaama, illa Database search-ku anupalaama nu instant-ah decide panna.
2. **Content Moderation / Safety:** Oru user post panra comment-la bad words irukka, spam irukka, privacy leak irukka nu 20 safety rules-ah ore fraction of second-la check panna.
3. **Fast Filter / Triage:** Heavy, costly LLM kitta poradhukku munnadi, idhuvachae basic classification panni anupalaam.

---

### Common Mistake (Enna panna koodadhu?)

> [!WARNING]
> Decisions API kitta poi *"Write a poem about rain"* nno, *"Explain quantum computing"* nno kekka koodadhu. Adhu text eludhadhu, code generate pannadhu. Idhu strictly **Decision maker / Classifier** mattum dhaan!

---

### Quick Recap

* **Normal Gemini:** Writer maari — vala vala-nu paragraph eludhum, cost jaasthi, konjam time edukkum.
* **Decisions API (`gemini-decision-1`):** Judge maari — Yes/No, A/B/C choice, score rating mattum instant-ah (150ms) thalayatti solli mudichidum. Output token billey kedayadhu ($0)!
