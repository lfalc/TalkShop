# Talk Shop

**Talk Shop** is a voice-first shopping assistant that helps users discover products through natural conversation.
Instead of filters, forms, and endless scrolling, users simply talk about what they want — and what they like or dislike — while the app learns their preferences over time.

> *You don’t search. You talk shop.*

---

## ✨ What Talk Shop Does

* Lets users **shop by speaking naturally**
* Shows **one product at a time**, anchored by images
* Learns preferences implicitly from likes, dislikes, questions, and skips
* Builds a **long-term preference profile** that works across categories
* Improves recommendations without forcing users to configure settings

---

## 🗣️ Core Interaction Model

### 1. Start with intent

Users begin with a natural prompt:

> “I want to buy shoes that match the color scheme of the Brazilian soccer team.”

Talk Shop interprets this and visually confirms it (e.g. green/yellow/blue color cues), then immediately shows a product.

---

### 2. React to a product

Users mostly respond by commenting on what they see:

* “The design is too flashy”
* “I like the brand”
* “What material are these made of?”
* “Next”

These responses are treated as **signals**, not commands.

---

### 3. Implicit preference learning

Talk Shop infers preferences based on context:

* Saying *“too flashy”* → preference for subtler designs
* Asking about materials → interest in composition
* Hearing *“PU leather”* followed by *“next”* → likely avoidance of faux leather
* Saying *“I like the brand”* → brand affinity

Preferences are:

* Weighted (soft vs hard)
* Scoped (session-only vs long-term)
* Reversible (users can correct the system)

---

### 4. Iterate

Each interaction refines the next recommendation.
The assistant may ask a clarification **only when necessary**.

---

## 🧠 Preference Profile

Talk Shop maintains a continuously evolving profile built from user behavior.

### Preference types

* **Hard constraints**
  (e.g. “under $150”, “no faux leather”)
* **Soft preferences**
  (e.g. subtle design, preferred brands, natural materials)
* **Visual/style signals**
  (learned from liked vs skipped products)

### Cross-category learning

Preferences can transfer across categories when appropriate.

Example:

* User avoids synthetic leather when shopping for shoes
* Later, when shopping for sweaters, Talk Shop prioritizes natural fabrics

This happens **silently and conservatively**, with low confidence until reinforced.

---

## 🖼️ UI Principles

* **One product at a time** (no grids)
* Large image as the primary focus
* Clear attribute chips (brand, material, style, color, price)
* Voice-first, touch-optional
* Minimal confirmations — behavior proves understanding

---

## 🔍 Transparency & Trust

To avoid “black box” behavior:

* Visual cues reflect what the system is learning
* Preferences can be viewed and edited in a dedicated drawer
* Explanations are provided *only when asked*

---

## 🚫 What Talk Shop Is Not

* Not a voice command interface
* Not a chatbot that asks constant follow-ups
* Not a static recommender based only on past purchases

Talk Shop behaves like a **good salesperson**:

* Attentive
* Quietly adaptive
* Willing to be corrected

---

## 🧪 MVP Scope (Suggested)

* Single category (e.g. shoes)
* Fixed attribute schema
* Voice input + image output
* Like / dislike / next / questions
* Session-based preference learning

---

## 📌 Product Philosophy

> People are good at reacting, not specifying.

Talk Shop is designed around reactions — what users notice, like, dislike, or skip — and turns those reactions into better recommendations over time.
