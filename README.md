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

## 🧩 Technology Stack

Talk Shop is designed as a modular, service-oriented system. Each core capability (voice, reasoning, retrieval) is handled by a best-in-class provider.

### Web & Product Discovery

* **you.com** — used for web search and product discovery

  * Retrieves up-to-date product pages, images, and metadata
  * Acts as the external knowledge and discovery layer

### Voice Recognition

* **Plivo** — handles voice input and speech-to-text

  * Low-latency voice capture
  * Optimized for conversational, short-utterance interactions (e.g. “next”, “too flashy”)

### Core Reasoning & Preference Learning

* **Gemini** — serves as the core large language model

  * Interprets user intent and conversational feedback
  * Translates natural language into structured preference signals
  * Maintains and updates session-level and long-term user profiles

### Internal Components (Conceptual)

* **Preference Engine** — weights, scopes, and reconciles inferred preferences
* **Ranking Engine** — scores and selects the next best product to show
* **UI Layer** — image-first product cards with voice-driven interaction

This separation allows Talk Shop to evolve individual components independently as the product scales.

### Data & Backend

* **Supabase** — local-first backend for development and (optionally) production

  * Postgres database, Auth, Storage, and Realtime run locally via Docker
  * Same config and migrations for everyone who clones the repo
  * See [Development setup](#-development-setup) below.

---

## 🛠 Development setup

Anyone who clones the repo can run Supabase locally with the same setup.

### Prerequisites

* **Docker** (or a Docker-compatible runtime: Docker Desktop, OrbStack, Rancher Desktop, Podman, colima)
* **Node.js 20+** (for running the Supabase CLI via `npx`; no global install required)

### 1. Start and stop local Supabase

From the project root, use the helper script (recommended):

```bash
./scripts/supabase.sh start    # start Supabase
./scripts/supabase.sh status   # show URLs and keys
./scripts/supabase.sh stop     # stop Supabase (keeps data)
```

The first `start` downloads Docker images and can take a few minutes. When it finishes, the script prints your local credentials (API URL, anon key, service role key, database URL, etc.). Run `./scripts/supabase.sh status` anytime to see them again.

Alternatively, you can run the Supabase CLI directly: `npx supabase start`, `npx supabase status`, `npx supabase stop`.

### 2. Use the credentials in your app

* Copy `.env.example` to `.env`.
* Fill in the values from the `supabase start` output (or run `./scripts/supabase.sh status` anytime to see them again).

| What you need | Where to get it |
|---------------|-----------------|
| **Supabase Studio** (DB UI, Auth, etc.) | http://127.0.0.1:54323 |
| **API URL** | `./scripts/supabase.sh start` or `./scripts/supabase.sh status` |
| **anon key** / **service_role key** | same as above |
| **Postgres connection** | `postgresql://postgres:postgres@127.0.0.1:54322/postgres` |

### 3. Stop when you’re done

Run `./scripts/supabase.sh stop`. This stops the containers but keeps your local data. Use `npx supabase db reset` to apply migrations from scratch and re-run seeds.

### Adding migrations and seed data

* **Migrations:** Add SQL files under `supabase/migrations/` (with a timestamped name, e.g. `20240206120000_initial_schema.sql`). They run automatically on the next `supabase start` or `supabase db reset`.
* **Seeds:** Edit `supabase/seed.sql`; it runs after migrations on `supabase db reset`.

---

## 📌 Product Philosophy

> People are good at reacting, not specifying.

Talk Shop is designed around reactions — what users notice, like, dislike, or skip — and turns those reactions into better recommendations over time.
