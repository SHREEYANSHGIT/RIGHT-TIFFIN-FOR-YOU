import os
from dotenv import load_dotenv

load_dotenv()

# Try Gemini safely (no hardcoding)
def try_gemini(prompt: str):
    try:
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # Dynamically find a usable model
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                model = genai.GenerativeModel(m.name)
                response = model.generate_content(prompt)
                return response.text.strip()

        return None
    except Exception:
        return None


def fallback_ai(review_text: str, price: float | None = None):
    text = review_text.lower()

    # Strong positive signals (high impact)
    strong_positive = [
        "very tasty", "excellent", "awesome", "amazing", "delicious",
        "homemade", "fresh", "healthy", "perfect", "best", "love it",
        "superb", "mouth watering"
    ]

    # Mild positive signals (low impact)
    mild_positive = [
        "good", "nice", "okay", "decent", "fine", "satisfactory",
        "soft roti", "good taste", "less oil", "balanced spice",
        "clean", "hygienic", "good quantity", "value for money"
    ]

    # Strong negative signals (high impact)
    strong_negative = [
        "worst", "very bad", "pathetic", "disgusting", "spoiled",
        "smelly", "stale", "raw", "uncooked", "food poisoning"
    ]

    # Mild negative signals (low impact)
    mild_negative = [
        "bad", "average", "oily", "too spicy", "bland", "cold food",
        "late", "delayed", "small quantity", "overpriced",
        "not fresh", "sometimes late", "inconsistent"
    ]

    score = 5  # neutral baseline

    # Apply strong positives
    for w in strong_positive:
        if w in text:
            score += 2

    # Apply mild positives
    for w in mild_positive:
        if w in text:
            score += 1

    # Apply strong negatives
    for w in strong_negative:
        if w in text:
            score -= 2

    # Apply mild negatives
    for w in mild_negative:
        if w in text:
            score -= 1

    # 🔹 Price perception logic (value-for-money bias)
    if price is not None:
        try:
            p = float(price)
            if p >= 3500:
                score -= 2
            elif p >= 2500:
                score -= 1
            elif p <= 2000:
                score += 1
        except Exception:
            pass

    # Clamp score to 0–10
    score = max(0, min(score, 10))

    return score, "Rule-based review sentiment analysis (fallback)"


def analyze_review(review_text: str, price: float | None = None):
    if not review_text.strip():
        return 0, "No review provided"

    prompt = f"""
Analyze this food review and the price of the meal.

Return exactly two lines:
Score: <number out of 10>
Summary: <one line summary>

Review:
{review_text}

Price: {price if price is not None else 'N/A'}
"""

    gemini_output = try_gemini(prompt)

    if gemini_output:
        score = None
        summary = "AI analysis completed"

        for line in gemini_output.splitlines():
            if line.lower().startswith("score"):
                digits = "".join(filter(lambda c: c.isdigit() or c==".", line))
                try:
                    if digits:
                        score = float(digits)
                except Exception:
                    pass
            if line.lower().startswith("summary"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    summary = parts[1].strip()

        if score is not None:
            # normalize to 0-10 and round
            try:
                score_val = float(score)
                score_val = max(0.0, min(score_val, 10.0))
                return round(score_val), summary
            except Exception:
                pass

    # 🔁 Fallback (guaranteed)
    return fallback_ai(review_text, price)


def generate_one_line_reason(context: str) -> str:
    """Return a concise one-line reason (prefer AI via Gemini, otherwise fallback to trimmed context)."""
    if not context or not context.strip():
        return "Recommended based on reviews and ratings."

    prompt = f"""
Given the following short context about a tiffin option, provide a single short sentence (one line) explaining why this is a good recommendation. Keep it under 25 words.

Context:
{context}
"""

    out = try_gemini(prompt)
    if out:
        # take the first non-empty line
        for line in out.splitlines():
            line = line.strip()
            if line:
                return line if len(line) <= 220 else line[:217] + "..."

    # fallback: return a trimmed version of the context
    txt = context.strip().replace("\n", " ")
    return (txt[:217] + "...") if len(txt) > 220 else txt


def generate_short_summary(context: str, min_words: int = 5, max_words: int = 7) -> str:
    """Generate a very short summary (preferably between min_words and max_words).
    Uses Gemini when available; falls back to taking the first max_words from the context.
    """
    if not context or not context.strip():
        return "No reviews yet."

    prompt = f"""
Given the following user reviews, produce a concise summary phrase of {min_words} to {max_words} words capturing the main taste/quality points. Output only the phrase (no extra explanation).

Reviews:
{context}
"""

    out = try_gemini(prompt)
    if out:
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            words = line.split()
            if len(words) <= max_words and len(words) >= min_words:
                return line
            if len(words) > max_words:
                return " ".join(words[:max_words])
            # if shorter than min_words, still return it (it's better than nothing)
            return line

    # fallback: take first max_words from the raw context
    raw_words = context.replace("\n", " ").split()
    if not raw_words:
        return "No reviews yet."
    return " ".join(raw_words[:max_words])


def generate_pros_cons(context: str, max_items: int = 5) -> tuple[dict, dict]:
    """Return (pros_by_category, cons_by_category) derived from the context.
    Each return value is a dict mapping 4 categories to a list of short items.
    Categories: Taste & Quality, Satisfaction, Delivery & Timeliness, Packaging & Value.
    Prefer Gemini; fall back to keyword extraction per category.
    """
    categories = [
        "Taste & Quality",
        "Satisfaction",
        "Delivery & Timeliness",
        "Packaging & Value",
    ]

    empty_pros = {c: [] for c in categories}
    empty_cons = {c: [] for c in categories}

    if not context or not context.strip():
        # provide an explicit no-reviews structure
        for c in categories:
            empty_pros[c] = ["No reviews yet."]
            empty_cons[c] = ["No reviews yet."]
        return empty_pros, empty_cons

    prompt = f"""
From the following user reviews, produce pros and cons grouped under these categories: {', '.join(categories)}.
For each category produce up to {max_items} concise bullet items (start each item with '-' or '•').
Keep items short (under 12 words). Output clearly labeled sections, for example:
Pros - Taste & Quality:
- ...
Pros - Satisfaction:
- ...
Cons - Delivery & Timeliness:
- ...

Reviews:
{context}
"""

    out = try_gemini(prompt)
    if out:
        pros = {c: [] for c in categories}
        cons = {c: [] for c in categories}
        lines = [l.rstrip() for l in out.splitlines()]
        current_side = None
        current_cat = None

        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            low = line.lower()
            # detect headers like 'pros - taste & quality:' or 'pros: taste & quality'
            if low.startswith("pros") or low.startswith("cons"):
                # determine side and optional category
                side = "pros" if low.startswith("pros") else "cons"
                # attempt to extract category name after '-' or ':'
                if "-" in line:
                    parts = line.split("-", 1)
                    cat = parts[1].strip().rstrip(":").strip()
                elif ":" in line:
                    parts = line.split(":", 1)
                    cat = parts[1].strip()
                else:
                    cat = None

                # normalize category search
                matched_cat = None
                if cat:
                    for c in categories:
                        if cat.lower() in c.lower() or c.lower() in cat.lower():
                            matched_cat = c
                            break

                current_side = side
                current_cat = matched_cat
                continue

            # strip leading bullets
            item = line.lstrip("-•* ").strip()
            if not item:
                continue

            # If we have a current category, assign there; otherwise try to guess by keywords
            target_cat = current_cat
            if not target_cat:
                # naive mapping by keywords
                low_item = item.lower()
                if any(k in low_item for k in ["taste", "spicy", "delicious", "fresh", "quality", "tasty", "homemade"]):
                    target_cat = "Taste & Quality"
                elif any(k in low_item for k in ["satisf", "portion", "quantity", "value", "price", "cost", "recommend"]):
                    target_cat = "Satisfaction"
                elif any(k in low_item for k in ["deliver", "late", "time", "delay", "pickup"]):
                    target_cat = "Delivery & Timeliness"
                else:
                    target_cat = "Packaging & Value"

            if current_side == "pros":
                if len(pros[target_cat]) < max_items:
                    pros[target_cat].append(item)
            elif current_side == "cons":
                if len(cons[target_cat]) < max_items:
                    cons[target_cat].append(item)

        # If any category empty in both pros/cons, leave empty lists for fallback to fill
        return pros, cons

    # Fallback extraction per category
    text = context.lower()
    # keyword banks per category
    kp = {
        "Taste & Quality": ["tasty", "delicious", "fresh", "spicy", "bland", "quality", "homemade", "roti", "curry"],
        "Satisfaction": ["satisf", "recommend", "value", "portion", "quantity", "price", "worth"],
        "Delivery & Timeliness": ["late", "delay", "deliver", "time", "pickup", "on time", "early"],
        "Packaging & Value": ["packag", "hygien", "clean", "presentation", "container", "leak"]
    }

    pros = {c: [] for c in categories}
    cons = {c: [] for c in categories}

    # Find hits per category
    for c in categories:
        pos_hits = []
        neg_hits = []
        for k in kp[c]:
            if k in text:
                # classify as positive or negative by nearby sentiment words
                # simple heuristic: check for negation words within 30 chars before keyword
                idx = text.find(k)
                snippet = text[max(0, idx-30): idx+len(k)+30]
                if any(neg in snippet for neg in ["not ", "no ", "never", "n't", "poor", "bad", "worst"]):
                    neg_hits.append(k)
                else:
                    pos_hits.append(k)

        # create readable items
        for p in pos_hits[:max_items]:
            pros[c].append(p.replace("packag", "packaging").capitalize())
        for n in neg_hits[:max_items]:
            cons[c].append(n.replace("packag", "packaging").capitalize())

    # ensure at least one item per category where nothing found
    for c in categories:
        if not pros[c]:
            pros[c].append("No clear pros identified")
        if not cons[c]:
            cons[c].append("No clear cons identified")

    return pros, cons
