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


# Fallback AI (LOCAL – always works)
def fallback_ai(review_text: str, price: float | None = None):
    text = review_text.lower()

    positive = ["good", "tasty", "excellent", "awesome", "nice", "healthy", "fresh", "delicious"]
    negative = ["bad", "worst", "oily", "cold", "late", "poor", "smelly", "stale"]

    score = 5
    for w in positive:
        if w in text:
            score += 1
    for w in negative:
        if w in text:
            score -= 1

    # Simple price influence: cheaper perceived value increases score, expensive may lower expectation
    if price is not None:
        try:
            p = float(price)
            if p >= 200:
                score -= 2
            elif p >= 100:
                score -= 1
            elif p >= 50:
                score += 1
            else:
                score += 2
        except Exception:
            pass

    score = max(0, min(score, 10))

    return score, "AI-based taste analysis (fallback)" 


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
