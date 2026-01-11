import os
from dotenv import load_dotenv

load_dotenv()


def try_gemini(prompt: str):
    """Try Gemini safely (no hardcoding)."""
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
    """Fallback sentiment analysis using keyword matching."""
    text = review_text.lower()

    strong_positive = [
        "very tasty", "excellent", "awesome", "amazing", "delicious",
        "homemade", "fresh", "healthy", "perfect", "best", "love it",
        "superb", "mouth watering"
    ]

    mild_positive = [
        "good", "nice", "okay", "decent", "fine", "satisfactory",
        "soft roti", "good taste", "less oil", "balanced spice",
        "clean", "hygienic", "good quantity", "value for money"
    ]

    strong_negative = [
        "worst", "very bad", "pathetic", "disgusting", "spoiled",
        "smelly", "stale", "raw", "uncooked", "food poisoning"
    ]

    mild_negative = [
        "bad", "average", "oily", "too spicy", "bland", "cold food",
        "late", "delayed", "small quantity", "overpriced",
        "not fresh", "sometimes late", "inconsistent"
    ]

    score = 5

    for w in strong_positive:
        if w in text:
            score += 2

    for w in mild_positive:
        if w in text:
            score += 1

    for w in strong_negative:
        if w in text:
            score -= 2

    for w in mild_negative:
        if w in text:
            score -= 1

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

    score = max(0, min(score, 10))

    return score, "Rule-based review sentiment analysis (fallback)"


def analyze_review(review_text: str, price: float | None = None):
    """Analyze a review and return score and summary."""
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
                digits = "".join(filter(lambda c: c.isdigit() or c == ".", line))
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
            try:
                score_val = float(score)
                score_val = max(0.0, min(score_val, 10.0))
                return round(score_val), summary
            except Exception:
                pass

    return fallback_ai(review_text, price)


def generate_one_line_reason(context: str) -> str:
    """Return a concise one-line reason."""
    if not context or not context.strip():
        return "Recommended based on reviews and ratings."

    prompt = f"""
Given the following short context about a tiffin option, provide a single short sentence (one line) explaining why this is a good recommendation. Keep it under 25 words.

Context:
{context}
"""

    out = try_gemini(prompt)
    if out:
        for line in out.splitlines():
            line = line.strip()
            if line:
                return line if len(line) <= 220 else line[:217] + "..."

    txt = context.strip().replace("\n", " ")
    return (txt[:217] + "...") if len(txt) > 220 else txt


def generate_short_summary(context: str, min_words: int = 5, max_words: int = 7) -> str:
    """Generate a very short summary."""
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
            return line

    raw_words = context.replace("\n", " ").split()
    if not raw_words:
        return "No reviews yet."
    return " ".join(raw_words[:max_words])


def generate_pros_cons_simple(context: str, max_pros: int = 5, max_cons: int = 5) -> tuple:
    """
    Generate simple pros and cons lists from reviews.
    Returns: (pros_list, cons_list, improvement_suggestion)
    """
    if not context or not context.strip():
        return (
            ["No reviews available yet."],
            ["No reviews available yet."],
            "Collect more student reviews to get actionable insights."
        )

    prompt = f"""
Analyze these student reviews about a tiffin service and extract:

1. PROS: List {max_pros} positive points students mentioned (things they liked)
2. CONS: List {max_cons} negative points or complaints students mentioned
3. SUGGESTION: One short actionable suggestion for improvement (1-2 sentences)

Format your response EXACTLY like this:
PROS:
- [positive point 1]
- [positive point 2]
...

CONS:
- [negative point 1]
- [negative point 2]
...

SUGGESTION:
[Your improvement suggestion here]

Reviews:
{context[:1500]}
"""

    out = try_gemini(prompt)
    
    pros = []
    cons = []
    suggestion = "Focus on maintaining food quality and timely delivery based on student feedback."
    
    if out:
        current_section = None
        suggestion_lines = []
        
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            
            low = line.lower()
            
            if low.startswith("pros"):
                current_section = "pros"
                continue
            elif low.startswith("cons"):
                current_section = "cons"
                continue
            elif low.startswith("suggestion"):
                current_section = "suggestion"
                # Check if suggestion is on the same line
                if ":" in line:
                    rest = line.split(":", 1)[1].strip()
                    if rest:
                        suggestion_lines.append(rest)
                continue
            
            # Process items
            item = line.lstrip("-•*123456789.) ").strip()
            if not item:
                continue
            
            if current_section == "pros" and len(pros) < max_pros:
                pros.append(item)
            elif current_section == "cons" and len(cons) < max_cons:
                cons.append(item)
            elif current_section == "suggestion":
                suggestion_lines.append(item)
        
        if suggestion_lines:
            suggestion = " ".join(suggestion_lines)[:300]
    
    # Fallback extraction if AI didn't return proper format
    if not pros or not cons:
        pros, cons, suggestion = fallback_pros_cons(context, max_pros, max_cons)
    
    # Ensure at least one item in each list
    if not pros:
        pros = ["Students generally find the food acceptable."]
    if not cons:
        cons = ["No major complaints reported yet."]
    
    return pros, cons, suggestion


def fallback_pros_cons(context: str, max_pros: int = 5, max_cons: int = 5) -> tuple:
    """Fallback keyword-based extraction for pros and cons."""
    text = context.lower()
    
    positive_keywords = {
        "tasty": "Food is tasty and flavorful",
        "delicious": "Delicious meals appreciated by students",
        "fresh": "Fresh ingredients used",
        "homemade": "Homemade taste that students love",
        "good quality": "Good quality food",
        "clean": "Clean and hygienic preparation",
        "on time": "Timely delivery",
        "generous portion": "Generous portion sizes",
        "value for money": "Good value for money",
        "soft roti": "Soft and fresh rotis",
        "variety": "Good variety in menu",
        "healthy": "Healthy food options",
        "affordable": "Affordable pricing",
        "hot food": "Food served hot",
        "good taste": "Good taste overall"
    }
    
    negative_keywords = {
        "late": "Sometimes late delivery",
        "cold": "Food sometimes arrives cold",
        "oily": "Food can be oily",
        "spicy": "Sometimes too spicy",
        "bland": "Food can be bland at times",
        "small portion": "Portion sizes could be bigger",
        "expensive": "Pricing could be better",
        "inconsistent": "Inconsistent quality",
        "stale": "Freshness could improve",
        "delay": "Delivery delays reported",
        "less quantity": "Quantity could be more",
        "not fresh": "Freshness concerns",
        "overpriced": "Feels overpriced to some",
        "packaging": "Packaging needs improvement",
        "average": "Average quality"
    }
    
    pros = []
    cons = []
    
    for keyword, description in positive_keywords.items():
        if keyword in text and len(pros) < max_pros:
            # Check it's not negated
            idx = text.find(keyword)
            snippet = text[max(0, idx-20):idx]
            if not any(neg in snippet for neg in ["not ", "no ", "don't", "doesn't", "wasn't", "isn't"]):
                pros.append(description)
    
    for keyword, description in negative_keywords.items():
        if keyword in text and len(cons) < max_cons:
            cons.append(description)
    
    if not pros:
        pros = ["Food quality is generally acceptable"]
    if not cons:
        cons = ["No specific complaints identified"]
    
    # Generate suggestion based on cons
    if cons and cons[0] != "No specific complaints identified":
        suggestion = f"Consider addressing: {cons[0].lower()}. Regular feedback collection can help improve service."
    else:
        suggestion = "Continue maintaining current standards and collect more student feedback for improvements."
    
    return pros[:max_pros], cons[:max_cons], suggestion


def generate_pros_cons(context: str, max_items: int = 5) -> tuple:
    """
    Legacy function for backward compatibility.
    Returns (pros_list, cons_list) - simplified version.
    """
    pros, cons, _ = generate_pros_cons_simple(context, max_items, max_items)
    return pros, cons


def generate_improvement_suggestion(context: str) -> str:
    """Generate a short improvement suggestion based on reviews."""
    if not context or not context.strip():
        return "Collect more student reviews to identify areas for improvement."
    
    prompt = f"""
Based on these student reviews, provide ONE short, actionable suggestion (1-2 sentences) for how this tiffin service can improve:

Reviews:
{context[:1000]}

Suggestion:
"""
    
    out = try_gemini(prompt)
    if out:
        # Clean up the response
        suggestion = out.strip()
        # Remove any "Suggestion:" prefix if present
        if suggestion.lower().startswith("suggestion"):
            parts = suggestion.split(":", 1)
            if len(parts) > 1:
                suggestion = parts[1].strip()
        
        # Limit length
        if len(suggestion) > 300:
            suggestion = suggestion[:297] + "..."
        
        return suggestion
    
    return "Focus on consistency in food quality and timely delivery to improve student satisfaction."
