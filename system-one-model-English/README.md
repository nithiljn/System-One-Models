# Gemini Decisions API (`gemini-decision-1`)

Using a simple tea shop analogy to explain everything with crystal clarity so you never get confused!

---

### First, What is the Difference Between a Normal LLM and the Decisions API?

Let's look at a real-life situation:

* **Normal LLM (Like Gemini 1.5 / 2.0 / ChatGPT):**
  You go to a tea shop and ask the counter attendant: *"Do you have tea right now?"*
  The attendant starts answering: *"Sir, since 1990 our shop has been sourcing handpicked Nilgiri tea leaves, boiling fresh farm milk, and making extraordinary aromatic tea... yes sir, tea is available!"* He gives you a whole 2-minute speech.
  * **Problem:** You only asked a simple Yes/No question. But because he generated a massive paragraph of text, you wasted time (**high latency**), and you got billed heavily for every word spoken (**high output token costs**).

* **Decisions API (`gemini-decision-1`):**
  You go to the same tea shop and ask: *"Do you have tea right now?"*
  The attendant doesn't utter unnecessary sentences. He instantly nods **"YES" (99% confidence)** within a fraction of a second.
  * **Result:** Zero chit-chat, instant answer in a blink (150ms), and zero output token bill!

> **In Short:** The Decisions API is **NOT designed for generating prose, essays, or conversational text**. It is a purpose-built model optimized exclusively for **rapid, calibrated decision-making and classification**.

---

### The 3 Core Question Types (What Can You Ask?)

You pass a shared input (text, photo, audio, video, or PDF), and you can ask 3 types of structured questions:

#### 1. `noul` (Yes or No / Boolean)
* A binary condition evaluator that checks whether a statement is True or False.
* **Example:** *"Is the customer expressing anger in this message?"*
* **Output:** A calibrated probability score (e.g., `0.95` means a 95% probability of True) with a confidence level.

#### 2. `choice` (Multiple Choice / Categorization)
* Evaluates input against discrete options (up to 255 candidate choices) and picks the best match.
* **Example:** *"Which department should resolve this customer support ticket?"*
  * Option A: `billing` (Payment and refund questions)
  * Option B: `replacements` (Damaged or missing items)
  * Option C: `general` (General product inquiries)
* **Output:** Returns the selected choice (`replacements`) along with normalized probability percentages for all candidates.

#### 3. `score` (Rating / Rubric Evaluation)
* Evaluates input across ordered rubric tiers (e.g., a scale from 1 to 5, or 0 to 10).
* **Example:** *"Rate the quality of this code snippet from 1 to 5."*
* **Output:** A continuous, probability-weighted score along with individual level probabilities.

---

### Key Superpowers (Why Is This a Game Changer?)

1. **Zero Output Token Billing ($0.00)**
   * In traditional LLMs, output tokens are usually the most expensive part of your bill.
   * Because the Decisions API evaluates inputs in a single forward pass without autoregressive token generation, **output token usage is completely free ($0.00)**. You only pay for input tokens at a very low rate ($0.10 per 1 million tokens).
2. **Lightning Speed (150ms - 250ms)**
   * Without having to stream text word-by-word, the end-to-end response time is typically under a quarter of a second.
3. **Up to 1,000 Questions in a Single Pass!**
   * You can supply a massive input (up to 256K tokens of context, including long documents or videos) and ask **up to 1,000 independent questions simultaneously** in one single API request.
4. **Multimodal Inputs**
   * Accepts text, high-res images, audio recordings, video clips, and PDFs natively.

---

### Python Code Example (How to Use It)

Install the latest Google Gen AI SDK:
```bash
pip install --upgrade google-genai
```

Python implementation:
```python
from google import genai

# Must target the v1beta endpoint where the Decisions API is available
client = genai.Client(http_options={"api_version": "v1beta"})

# Call the Decisions API
result = client.decisions.create(
    model="gemini-decision-1",
    input="The blue mug I ordered on Monday arrived cracked on Wednesday. I need a refund.",
    questions={
        # Question 1: Yes/No type
        "is_damaged": {
            "type": "noul",
            "instructions": "Did the customer receive a damaged item?",
        },
        # Question 2: Categorization / Routing
        "department": {
            "type": "choice",
            "instructions": "Which department should handle this request?",
            "criteria": {
                "billing": "Refund, invoice, or payment queries.",
                "replacements": "Damaged, broken, or missing products.",
                "general": "General questions and account inquiries.",
            },
        },
    },
)

# Extract answers
damaged = result.answers["is_damaged"]
dept = result.answers["department"]

print("Damaged?:", damaged.noul, "Confidence:", damaged.confidence)
print("Assigned Department:", dept.choice, "Confidence:", dept.confidence)
```

---

### Where Should You Use This? (Practical Use-Cases)

1. **AI Agent Routing:** When a user message arrives, immediately decide which specialized sub-agent or tool should take action (e.g., Code Agent vs. Database Agent vs. Search Tool).
2. **Policy Compliance & Safety Moderation:** Run content against 50 different safety and moderation guidelines simultaneously in a fraction of a second.
3. **High-Throughput Triage & Filtering:** Screen thousands of items, resumes, support tickets, or media files before routing only necessary candidates to heavier, more expensive reasoning models.

---

### Common Pitfall (What NOT to Do)

> [!WARNING]
> Do NOT ask the Decisions API to *"Write an essay about artificial intelligence"* or *"Generate a Python script for a web scraper"*. It cannot write open-ended creative text. It is purely an ultra-fast **Decision Maker and Classifier**.

---

### Summary Recap

* **Standard Gemini:** Like an articulate writer — generates elaborate paragraphs, takes longer, costs more per output word.
* **Decisions API (`gemini-decision-1`):** Like a decisive judge — answers Yes/No, picks from choices, or scores items in milliseconds with zero output token fees ($0.00)!
