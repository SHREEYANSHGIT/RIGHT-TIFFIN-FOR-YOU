import streamlit as st
import pandas as pd
import altair as alt
from firebase_config import db
from auth import register_user, login_user
from gemini_ai import (
    analyze_review, 
    generate_one_line_reason, 
    generate_short_summary, 
    generate_pros_cons_simple
)

# ================= PAGE CONFIG =================
st.set_page_config(page_title="RIGHT TIFFIN FOR YOU", layout="wide", initial_sidebar_state="expanded")

# ================= THEME (light/dark) and CUSTOM CSS =================
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

if st.session_state.get("theme", "light") == "light":
    bg_image = "https://images.unsplash.com/photo-1604908177522-2d5a6b3b0c4d?auto=format&fit=crop&w=1600&q=80"
    overlay_bg = "rgba(255,255,255,0.92)"
    card_bg = "linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(250,248,247,0.9) 100%)"
    header_shadow = "rgba(247,129,38,0.12)"
    text_color = "#111"
else:
    bg_image = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1600&q=80"
    overlay_bg = "rgba(18,18,18,0.88)"
    card_bg = "linear-gradient(180deg, rgba(26,26,26,0.9) 0%, rgba(36,36,36,0.9) 100%)"
    header_shadow = "rgba(0,0,0,0.4)"
    text_color = "#EEE"

css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"]  {{
        font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
        color: {text_color};
    }}

    .reportview-container, .main, body {{
        background-image: url('{bg_image}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .app-overlay {{
        background: {overlay_bg};
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(10,10,10,0.12);
    }}

    .tiffin-card {{
        border: none;
        border-radius: 14px;
        padding: 18px;
        margin: 14px 0;
        background: {card_bg};
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        transition: transform 0.22s ease, box-shadow 0.22s ease;
    }}
    .tiffin-card:hover {{ transform: translateY(-6px); box-shadow: 0 16px 40px rgba(0,0,0,0.12); }}

    .header-main {{
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        padding: 28px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 22px;
        box-shadow: 0 8px 24px {header_shadow};
    }}

    div.stButton > button, button[kind="primary"] {{
        background: linear-gradient(90deg,#FF6B35,#F7931E) !important;
        color: white !important;
        border: none !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
        box-shadow: 0 6px 18px rgba(255,107,53,0.18) !important;
    }}

    .metric-box {{
        background: rgba(255,255,255,0.95);
        padding: 14px;
        border-radius: 10px;
        border-left: 4px solid #FF6B35;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        min-height: 200px;
        
    }}

    .block-container {{
        padding-top: 18px;
        padding-left: 20px;
        padding-right: 20px;
        padding-bottom: 40px;
    }}

    textarea, input[type="text"], input[type="number"] {{
        border-radius: 8px !important;
        padding: 10px !important;
        border: 1px solid #e6e6e6 !important;
    }}

    .stMarkdown div[style*="scroll-snap-type"] img {{ border-radius: 10px; }}
    .theme-badge {{ position: fixed; left: 12px; top: 8px; z-index: 9999; }}
    
    .pros-item {{
        background: linear-gradient(90deg, #f0fdf4, #dcfce7);
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px 0;
        border-left: 3px solid #22c55e;
        font-weight: 500;
        color: #166534;
    }}
    
    .cons-item {{
        background: linear-gradient(90deg, #fef2f2, #fee2e2);
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px 0;
        border-left: 3px solid #ef4444;
        font-weight: 500;
        color: #991b1b;
    }}
    
    .suggestion-box {{
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        padding: 16px;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin-top: 12px;
    }}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

st.markdown('<div class="app-overlay">', unsafe_allow_html=True)

st.markdown(
    '<div class="header-main">'
    '<h1>🍱 RIGHT TIFFIN FOR YOU</h1>'
    '<p style="font-size:18px; margin:6px 0 8px 0;">Find Your Perfect Meal Delivery</p>'
    '<p style="font-size:14px; margin:0; background: rgba(255,255,255,0.08); display:inline-block; padding:6px 10px; border-radius:8px;">Now only available in <strong>RGPV Campus</strong> and nearby areas</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ================= AUTH =================
if "role" not in st.session_state:
    st.markdown(
        """
        <div style="background-image: url('https://images.unsplash.com/photo-1559056199-6415a6a2f3c2?auto=format&fit=crop&w=1350&q=80'); background-size:cover; background-position:center; border-radius:12px; padding:28px; color:white; text-align:center; box-shadow:0 6px 18px rgba(0,0,0,0.25); margin-bottom:18px;">
            <div style="background:rgba(0,0,0,0.38); padding:18px; border-radius:10px; display:inline-block; min-width:320px;">
                <h2 style="margin:0 0 6px 0; font-weight:700;">🍱 RIGHT TIFFIN FOR YOU — Sign In / Register</h2>
                <p style="margin:0; font-size:15px;">Fresh meals delivered with care. Now only available in <strong>RGPV Campus</strong> and nearby areas.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Welcome! Please Choose Your Role")
        option = st.selectbox("Select", ["👨‍🍳 Register", "🔐 Login"], label_visibility="collapsed")
        if "Register" in option:
            register_user()
        else:
            login_user()
    st.stop()

role = st.session_state["role"]
user_id = st.session_state["user_id"]

user_ref = db.collection("users").document(user_id)
user_snap = user_ref.get()
user_data = user_snap.to_dict() if user_snap.exists else {}


def generate_category_positive_summary(category_key, tiffin_name, reviews_text, monthly_price, avg_rating, avg_ai):
    """
    Generate a positive one-line summary for a specific category based on student reviews using Gemini AI.
    """
    if not reviews_text or not reviews_text.strip():
        return None
    
    # Limit review text to prevent token overflow
    limited_reviews = reviews_text[:800] if len(reviews_text) > 800 else reviews_text
    
    # Category-specific prompts
    category_prompts = {
        "budget": f"""Based on these student reviews about '{tiffin_name}' (Monthly price: ₹{monthly_price}:
Reviews: "{limited_reviews}"

Write ONE enthusiastic positive sentence (10-15 words max) explaining why students find this the BEST BUDGET-FRIENDLY tiffin. Focus on value for money and affordability.""",
        
        "taste": f"""Based on these student reviews about '{tiffin_name}' :
Reviews: "{limited_reviews}"

Write ONE enthusiastic positive sentence (10-15 words max) explaining why students say this has the BEST TASTE. Focus on deliciousness and food quality.""",
        
        "overall": f"""Based on these student reviews about '{tiffin_name}' :
Reviews: "{limited_reviews}"

Write ONE enthusiastic positive sentence (10-15 words max) explaining why students rate this as the BEST OVERALL tiffin. Consider taste, service, and value.""",
        
        "veg": f"""Based on these student reviews about '{tiffin_name}' :
Reviews: "{limited_reviews}"

Write ONE enthusiastic positive sentence (10-15 words max) explaining why students love this as the BEST VEGETARIAN option. Focus on veg food quality and variety.""",
        
        "nonveg": f"""Based on these student reviews about '{tiffin_name}' :
Reviews: "{limited_reviews}"

Write ONE enthusiastic positive sentence (10-15 words max) explaining why students love this as the BEST NON-VEG option. Focus on meat quality and flavors."""
    }
    
    prompt = category_prompts.get(category_key, category_prompts["overall"])
    
    full_prompt = f"""{prompt}

RULES:
1. Write ONLY one positive sentence
2. Maximum 15 words
3. Be enthusiastic and student-friendly
4. NO negative points
5. Start directly with the praise (don't say "Based on reviews...")
6. Use emojis sparingly if appropriate

Examples of good responses:
- "Amazing homestyle taste at pocket-friendly prices students absolutely love!"
- "Delicious fresh meals with generous portions that keep students coming back!"
- "Perfect blend of taste, quantity and timely delivery every single day!"
"""
    
    try:
        # Use the existing generate_one_line_reason function
        result = generate_one_line_reason(full_prompt)
        if result and len(result.strip()) > 5:
            # Clean up the result
            cleaned = result.strip().strip('"\'')
            # Ensure not too long
            words = cleaned.split()
            if len(words) > 18:
                cleaned = ' '.join(words[:16]) + '...'
            return cleaned
    except Exception as e:
        pass
    
    return None


def get_default_category_summary(category_key, entry):
    """Return a default positive summary if AI generation fails."""
    if not entry:
        return "No eligible tiffin found for this category."
    
    name = entry.get("name", "This tiffin")
    avg_rating = entry.get("avg_rating", 0)
    monthly = entry.get("monthly", "N/A")
    
    defaults = {
        "budget": f"Amazing value at ₹{monthly}/month - students love the quality!",
        "taste": f"Delicious homestyle cooking that students absolutely rave about!",
        "overall": f"Top-rated for taste, service & value - a student favorite!",
        "veg": f"Fresh, tasty vegetarian meals that students highly recommend!",
        "nonveg": f"Authentic non-veg flavors that students can't stop praising!"
    }
    return defaults.get(category_key, "Highly recommended by students!")


def render_top_rated_section():
    """Render the Top Rated Tiffins (AI Powered) section. Reusable for both Student and Provider tabs."""
    st.markdown("---")
    st.markdown("## 🏆 Top Rated Tiffins (AI Powered)")

    # Build combined ranking using ai_score (0-10), user rating (1-5), and price (lower is better)
    reviews = db.collection("reviews").stream()
    stats = {}
    review_texts = {}  # Store review texts for AI summary generation
    
    for r in reviews:
        d = r.to_dict()
        tid = d.get("tiffin_id")
        if tid not in stats:
            stats[tid] = {"ai_scores": [], "ratings": [], "prices": []}
            review_texts[tid] = []
        stats[tid]["ai_scores"].append(d.get("ai_score", 0) or 0)
        stats[tid]["ratings"].append(d.get("rating", 0) or 0)
        if d.get("price") is not None:
            stats[tid]["prices"].append(d.get("price"))
        # Collect review texts for AI summary
        if d.get("review"):
            review_texts[tid].append(str(d.get("review")))

    if stats:
        # gather price range
        prices = []
        for v in stats.values():
            prices.extend(v.get("prices", []))
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        combined = []
        for tid, v in stats.items():
            avg_ai = (sum(v["ai_scores"]) / len(v["ai_scores"])) if v["ai_scores"] else 0.0
            avg_rating = (sum(v["ratings"]) / len(v["ratings"])) if v["ratings"] else 0.0
            # scale rating 1-5 to 0-10
            rating_scaled = ((avg_rating - 1) / 4) * 10 if avg_rating else 0.0
            # price score: lower price gets higher score
            price_val = (sum(v["prices"]) / len(v["prices"])) if v["prices"] else None
            if price_val is None or min_price == max_price:
                price_score = 5.0
            else:
                price_score = ((max_price - price_val) / (max_price - min_price)) * 10

            combined_score = 0.5 * avg_ai + 0.3 * rating_scaled + 0.2 * price_score
            combined.append((tid, combined_score, avg_ai, avg_rating, price_val))

        combined_sorted = sorted(combined, key=lambda x: x[1], reverse=True)

        # Build detailed entries with tiffin metadata for category selection
        entries = []
        for tid, combined_score, avg_ai, avg_rating, price_val in combined:
            tdoc = db.collection("tiffins").document(tid).get()
            if not tdoc or not tdoc.exists:
                continue
            tdata = tdoc.to_dict()
            food_type = (tdata.get("food_type") or "").lower()
            # prefer monthly price for budget calculations; fallback to review price
            monthly = tdata.get("price_monthly") if tdata.get("price_monthly") is not None else price_val
            entries.append({
                "tid": tid,
                "name": tdata.get("name", "Unknown"),
                "combined": combined_score,
                "avg_ai": avg_ai,
                "avg_rating": avg_rating,
                "price": price_val,
                "monthly": monthly,
                "food_type": food_type,
                "reviews": review_texts.get(tid, []),  # Add review texts
            })

        # Compute winners for each category
        winner = {"budget": None, "taste": None, "overall": None, "veg": None, "nonveg": None}

        # Precompute min/max monthly price for budget normalization
        monthly_prices = [e["monthly"] for e in entries if e.get("monthly") is not None]
        min_month = min(monthly_prices) if monthly_prices else None
        max_month = max(monthly_prices) if monthly_prices else None

        def monthly_price_score(p):
            if p is None or min_month is None or max_month is None or min_month == max_month:
                return 5.0
            return ((max_month - p) / (max_month - min_month)) * 10

        # Best Budget: low monthly cost but good rating (use monthly prices)
        best_budget = None
        best_budget_score = -1
        for e in entries:
            ps = monthly_price_score(e.get("monthly")) if e.get("monthly") is not None else 5.0
            rating_scaled = ((e["avg_rating"] - 1) / 4) * 10 if e["avg_rating"] else 0.0
            # Budget preference: 80% monthly price importance, 20% rating
            bscore = 0.8 * ps + 0.2 * rating_scaled
            if bscore > best_budget_score:
                best_budget_score = bscore
                best_budget = e
        winner["budget"] = best_budget

        # Best Taste: select by AI taste score (prefer entries with strong taste scores)
        taste_candidates = [e for e in entries if (e.get("avg_ai") or 0) >= 7]
        if taste_candidates:
            winner["taste"] = max(taste_candidates, key=lambda x: x.get("avg_ai", 0))
        else:
            winner["taste"] = max(entries, key=lambda x: x.get("avg_ai", 0)) if entries else None

        # Best Overall: previously computed combined
        winner["overall"] = max(entries, key=lambda x: x["combined"]) if entries else None

        # Best Veg / Jain
        veg_entries = [e for e in entries if "veg" in (e.get("food_type") or "") and "non" not in (e.get("food_type") or "")]
        winner["veg"] = max(veg_entries, key=lambda x: x["combined"]) if veg_entries else None

        # Best Non-Veg
        nonveg_entries = [e for e in entries if "non" in (e.get("food_type") or "")]
        winner["nonveg"] = max(nonveg_entries, key=lambda x: x["combined"]) if nonveg_entries else None

        # Render the five recommendation boxes
        labels = [
            ("💰 Best Budget", "budget"), 
            ("😋 Best Taste", "taste"), 
            ("⭐ Best Overall", "overall"), 
            ("🥬 Best Veg / Jain", "veg"), 
            ("🍗 Best Non-Veg", "nonveg")
        ]

        cols5 = st.columns(5)
        for i, (label_text, key_cat) in enumerate(labels):
            e = winner.get(key_cat)
            with cols5[i]:
                if not e:
                    st.markdown(f"""
                    <div class="metric-box" style="text-align:center; display:flex; flex-direction:column; justify-content:center;">
                        <h4 style="margin:0 0 8px 0; color:#FF6B35; font-size:20px; font-weight:700;">{label_text}</h4>
                        <p style="color:#888;">No eligible tiffin found</p>
                    </div>
                    """, unsafe_allow_html=True)
                    continue
                
                # compute displayed metrics
                avg_user = e.get('avg_rating', 0.0)
                avg_ai = e.get('avg_ai', 0.0)
                overall = e.get('combined', 0.0)
                monthly_price = e.get('monthly', 'N/A')
                
                # Combine all reviews for this tiffin
                all_reviews = " ".join(e.get("reviews", []))

                # color coding for AI score: >7 green, 4-7 yellow, <4.5 red
                try:
                    aival = float(avg_ai)
                except Exception:
                    aival = 0.0
                if aival > 7:
                    ai_color = "#16a34a"
                elif aival >= 4:
                    ai_color = "#d97706"
                else:
                    ai_color = "#dc2626"

                # color coding for user avg: >3.5 green, 2.5-3.5 yellow, else red
                try:
                    uval = float(avg_user)
                except Exception:
                    uval = 0.0
                if uval > 3.5:
                    user_color = "#16a34a"
                elif uval >= 2.5:
                    user_color = "#d97706"
                else:
                    user_color = "#dc2626"

                # Generate AI-powered category-specific summary from student reviews
                ai_positive_summary = generate_category_positive_summary(
                    key_cat, 
                    e.get("name", "Unknown"),
                    all_reviews,
                    monthly_price,
                    avg_user,
                    avg_ai
                )
                
                # Fallback to default if AI fails
                if not ai_positive_summary:
                    ai_positive_summary = get_default_category_summary(key_cat, e)

                st.markdown(f"""
                <div class="metric-box">
                    <h4 style="margin:0 0 8px 0; color:#FF6B35; font-size:20px; font-weight:700; line-height:1.2;">{label_text}</h4>
                    <h3 style="margin:0 0 10px 0; font-size:18px; color:#222; font-weight:600;">{e['name']}</h3>
                    <p style="font-size:14px; margin:6px 0; color:#555;">
                        ⭐ <span style='color:{user_color}; font-weight:600'>{avg_user:.1f}/5</span> | 
                        🤖 <span style='color:{ai_color}; font-weight:600'>{avg_ai:.1f}/10</span>
                    </p>
                    <p style="font-size:14px; margin:6px 0; color:#555;">💰 ₹{monthly_price}/month</p>
                    <hr style="margin:12px 0; border:none; border-top:1px solid #eee;">
                    <p style="font-size:15px; color:#16a34a; font-weight:500; margin:0; line-height:1.5;">
                        ✨ {ai_positive_summary}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No ratings yet. Be the first to review!")

# ================= TIFFIN PROVIDER =================
if role == "Tiffin Provider":
    st.markdown(f"### 👨‍🍳 Welcome, {user_data.get('name', 'Provider')}!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Browse Tiffins", "📊 Dashboard", "🏆 Top Rated", "👤 Profile"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            selected_location = st.text_input("🔍 Search by Location", key="prov_search_loc", placeholder="e.g., Downtown")
            search_name = st.text_input("🔎 Search by Tiffin Name", key="prov_search_name", placeholder="e.g., Premium Lunch Box")
        with col2:
            selected_food = st.selectbox("🍽 Food Preference", ["All", "Veg", "Non-Veg", "Both"], key="prov_search_food")

        tiffins = db.collection("tiffins").stream()

        for t in tiffins:
            data = t.to_dict()

            if selected_location:
                delivery_locs = data.get("delivery_locations") or [data.get("location", "")]
                if not any(selected_location.lower() in (loc or "").lower() for loc in delivery_locs):
                    continue
            if search_name and search_name.lower() not in data.get("name", "").lower():
                continue
            if selected_food != "All" and data.get("food_type") != selected_food:
                continue

            with st.container():
                st.markdown('<div class="tiffin-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([2, 3])

                with c1:
                    image_list = [img for img in data.get("image_urls", []) if img]
                    if image_list:
                        imgs = []
                        for img in image_list:
                            imgs.append(f'<div style="flex:0 0 auto;scroll-snap-align:center;border-radius:12px;overflow:hidden;width:320px;height:420px;"><img src="{img}" style="width:320px;height:420px;object-fit:cover;border-radius:12px;display:block;"></div>')
                        imgs_html = '<div style="display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;padding:6px 0;">' + ''.join(imgs) + '</div>'
                        st.markdown(imgs_html, unsafe_allow_html=True)
                    else:
                        st.write("No images")

                with c2:
                    st.markdown(f"### {data.get('name', 'Unknown Tiffin')}")
                    desc = data.get('description', '')
                    if desc:
                        short_desc = desc if len(desc.split()) <= 50 else ' '.join(desc.split()[:50]) + '...'
                        st.markdown(f"**Description:** {short_desc}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"📍 **Location:** {data.get('location', 'N/A')}")
                        st.markdown(f"📞 **Phone:** {data.get('phone', 'N/A')}")
                        delivery_display = ', '.join(data.get('delivery_locations', [data.get('location', 'N/A')]))
                        st.markdown(f"🚚 **Delivery Areas:** {delivery_display}")
                    with col_b:
                        st.markdown(f"🍽 **Type:** {data.get('food_type', 'N/A')}")
                    
                    st.markdown("**Timings:**")
                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.markdown(f"⏰ Morning: {data.get('timing_morning', 'N/A')}")
                    with col_y:
                        st.markdown(f"🌙 Night: {data.get('timing_night', 'N/A')}")
                    
                    st.markdown(f"""
                    💰 **Pricing:**
                    - Monthly: ₹{data.get('price_monthly', 0)}
                    - Daily: ₹{data.get('price_daily', 0)}
                    - Per Tiffin: ₹{data.get('price_per_tiffin', 0)}
                    """)

                    with st.expander("📖 View Reviews"):
                        reviews = db.collection("reviews").where("tiffin_id", "==", t.id).stream()
                        found = False
                        for r in reviews:
                            rd = r.to_dict()
                            st.markdown(f"⭐ **{rd.get('rating', 0)}/5** – {rd.get('review', '')}")
                            if rd.get('ai_summary'):
                                st.info(f"🤖 AI Summary: {rd.get('ai_summary')}")
                            found = True
                        if not found:
                            st.write("No reviews yet")
                
                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("## 📊 Business Dashboard & Performance Analytics")

        t_docs = list(db.collection("tiffins").where("provider_id", "==", user_id).stream())
        if not t_docs:
            st.info("You haven't added any tiffins yet. Add tiffins to see analytics.")
        else:
            rows = []
            total_reviews = 0
            for t in t_docs:
                td = t.to_dict() or {}
                tid = t.id
                revs = list(db.collection("reviews").where("tiffin_id", "==", tid).stream())
                total_reviews += len(revs)
                ratings = []
                ai_scores = []
                texts = []
                for r in revs:
                    rd = r.to_dict() or {}
                    try:
                        if rd.get("rating") is not None:
                            ratings.append(float(rd.get("rating")))
                    except Exception:
                        pass
                    try:
                        if rd.get("ai_score") is not None:
                            ai_scores.append(float(rd.get("ai_score")))
                    except Exception:
                        pass
                    if rd.get("review"):
                        texts.append(str(rd.get("review")))

                avg_rating = round((sum(ratings) / len(ratings)) if ratings else 0.0, 2)
                avg_ai = round((sum(ai_scores) / len(ai_scores)) if ai_scores else 0.0, 2)
                
                context = " ".join(texts).strip()
                if context:
                    try:
                        pros, cons, suggestion = generate_pros_cons_simple(context, 5, 5)
                    except Exception:
                        pros = ["Error analyzing reviews"]
                        cons = ["Error analyzing reviews"]
                        suggestion = "Please try again later."
                else:
                    pros = ["No reviews yet."]
                    cons = ["No reviews yet."]
                    suggestion = "Collect student reviews to get insights."
                
                rows.append({
                    "tiffin_id": tid,
                    "name": td.get("name", "Unnamed"),
                    "food_type": td.get("food_type", "Unknown"),
                    "price_monthly": float(td.get("price_monthly") or 0),
                    "price_daily": float(td.get("price_daily") or 0),
                    "price_per_tiffin": float(td.get("price_per_tiffin") or 0),
                    "total_reviews": len(revs),
                    "avg_rating": avg_rating,
                    "avg_ai": avg_ai,
                    "pros": pros,
                    "cons": cons,
                    "suggestion": suggestion,
                })

            df = pd.DataFrame(rows)

            colk1, colk2, colk3 = st.columns(3)
            with colk1:
                st.metric("Tiffins", len(df))
            with colk2:
                st.metric("Total Reviews", int(total_reviews))
            with colk3:
                overall_avg = round((df['avg_rating'].mean()) if not df['avg_rating'].empty else 0.0, 2)
                st.metric("Avg Rating", f"{overall_avg}/5")

            st.markdown("---")

            c1, c2 = st.columns([1, 1])

            with c1:
                ft_counts = df['food_type'].value_counts().reset_index()
                ft_counts.columns = ['food_type', 'count']
                if not ft_counts.empty:
                    pie = alt.Chart(ft_counts).mark_arc().encode(
                        theta=alt.Theta(field="count", type="quantitative"),
                        color=alt.Color("food_type:N", legend=alt.Legend(title="Food Type")),
                        tooltip=[alt.Tooltip('food_type:N'), alt.Tooltip('count:Q')]
                    ).properties(width=380, height=320)
                    st.altair_chart(pie)
                else:
                    st.write("No data for food type distribution")

            with c2:
                if not df.empty:
                    bar = alt.Chart(df).mark_bar().encode(
                        x=alt.X('name:N', sort='-y', title='Tiffin'),
                        y=alt.Y('avg_rating:Q', title='Avg Rating (1-5)'),
                        color=alt.Color('avg_rating:Q', scale=alt.Scale(scheme='greens')),
                        tooltip=['name', 'total_reviews', 'avg_rating', 'avg_ai']
                    ).properties(width=520, height=320)
                    st.altair_chart(bar)
                else:
                    st.write("No rating data yet")

            st.markdown("---")

            st.subheader("Per-Tiffin Performance")
            display_df = df[['name', 'food_type', 'price_monthly', 'total_reviews', 'avg_rating', 'avg_ai']].rename(columns={
                'name': 'Tiffin', 'food_type': 'Food Type', 'price_monthly': 'Monthly ₹', 'total_reviews': 'Reviews', 'avg_rating': 'Avg Rating', 'avg_ai': 'Avg AI (0-10)'
            })
            st.dataframe(display_df.sort_values(by='Reviews', ascending=False))

            st.markdown("---")
            st.subheader("📋 Detailed Insights (AI-Powered)")
            st.markdown("*Pros, Cons, and Improvement Suggestions based on student reviews*")
            
            for _, row in df.iterrows():
                tiffin_name = row['name']
                pros_list = row.get('pros', [])
                cons_list = row.get('cons', [])
                suggestion = row.get('suggestion', '')
                review_count = row.get('total_reviews', 0)
                avg_rating = row.get('avg_rating', 0)
                avg_ai = row.get('avg_ai', 0)

                with st.expander(f"🔍 {tiffin_name} - Analysis ({review_count} reviews)"):
                    # Header with ratings
                    st.markdown(f"""
                    <div style="background: linear-gradient(90deg, #f8fafc, #f1f5f9); padding: 12px; border-radius: 8px; margin-bottom: 16px;">
                        <span style="font-size: 16px; color: #1e293b;">
                            ⭐ <strong>User Rating:</strong> {avg_rating}/5 | 
                            🤖 <strong>AI Score:</strong> {avg_ai}/10 |
                            📝 <strong>Reviews:</strong> {review_count}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_pros, col_cons = st.columns(2)
                    
                    with col_pros:
                        st.markdown("### ✅ Pros (What Students Love)")
                        if isinstance(pros_list, list):
                            for idx, pro in enumerate(pros_list[:5], 1):
                                st.markdown(f"""
                                <div class="pros-item">
                                    <span style="color: #16a34a; font-weight: 600;">{idx}.</span> {pro}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="pros-item">
                                <span style="color: #16a34a; font-weight: 600;">1.</span> {pros_list}
                            </div>
                            """, unsafe_allow_html=True)

                    with col_cons:
                        st.markdown("### ⚠️ Cons (Areas to Improve)")
                        if isinstance(cons_list, list):
                            for idx, con in enumerate(cons_list[:5], 1):
                                st.markdown(f"""
                                <div class="cons-item">
                                    <span style="color: #dc2626; font-weight: 600;">{idx}.</span> {con}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="cons-item">
                                <span style="color: #dc2626; font-weight: 600;">1.</span> {cons_list}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Improvement Suggestion
                    st.markdown("### 💡 AI Suggestion for Improvement")
                    st.markdown(f"""
                    <div class="suggestion-box">
                        <p style="margin: 0; color: #1e40af; font-size: 14px; line-height: 1.6;">
                            {suggestion}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

    with tab3:
        render_top_rated_section()

    with tab4:
        st.subheader("✏️ Edit Your Profile")
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name", value=user_data.get("name", ""), key="provider_name")
        with col2:
            new_phone = st.text_input("Phone Number", value=user_data.get("phone", ""), key="profile_phone")
        
        new_location = st.text_input("Location", value=user_data.get("location", ""), key="profile_location")
        
        if st.button("💾 Update Profile", use_container_width=True):
            user_ref.update({"name": new_name, "phone": new_phone, "location": new_location})
            st.success("✅ Profile Updated!")
            st.rerun()
        
        if st.button("🔓 Logout", use_container_width=True, key="provider_profile_logout"):
            st.session_state["force_register"] = True
            keep = {"theme", "force_register"}
            for k in list(st.session_state.keys()):
                if k not in keep:
                    st.session_state.pop(k, None)
            st.success("✅ Logged out")
            st.rerun()

        st.markdown("---")
        st.subheader("🍱 Manage Your Tiffins")
        
        sub_tab1, sub_tab2 = st.tabs(["➕ Add New Tiffin", "📋 My Tiffins"])
        
        with sub_tab1:
            st.markdown("### Fill in Tiffin Details")
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Tiffin Name", placeholder="e.g., Premium Lunch Box")
                phone = st.text_input("Contact Number", value=user_data.get("phone", ""), key="add_phone")
                location = st.text_input("Location", value=user_data.get("location", ""), key="add_loc")
                delivery_locations = st.text_input("Delivery Locations (comma-separated)", placeholder="e.g., RGPV Campus, Downtown", key="add_delivery")
                description = st.text_area("Short Description (max 50 words)", placeholder="Briefly describe this tiffin in up to 50 words", key="add_description", height=80)
                food_type = st.selectbox("Food Type", ["Veg", "Non-Veg", "Both"], key="add_food")
                timing_morning = st.text_input("Morning Timing", placeholder="e.g., 7:00 AM - 9:00 AM")
                timing_night = st.text_input("Night Timing", placeholder="e.g., 6:00 PM - 8:00 PM")

            with col2:
                price_monthly = st.number_input("Monthly Price ₹", min_value=0, step=100)
                price_daily = st.number_input("Daily Price ₹", min_value=0, step=10)
                price_per_tiffin = st.number_input("Per Tiffin Price ₹", min_value=0, step=10)
                img1 = st.text_input("Image URL 1")
                img2 = st.text_input("Image URL 2")
                img3 = st.text_input("Image URL 3")

                if st.button("✅ Add Tiffin", use_container_width=True):
                    if not name or not location:
                        st.error("❌ Tiffin name and location are required")
                    else:
                        desc_words = (description or "").split()
                        short_desc = " ".join(desc_words[:50])
                        db.collection("tiffins").add({
                            "provider_id": user_id,
                            "name": name,
                            "phone": phone,
                            "location": location,
                            "delivery_locations": [l.strip() for l in delivery_locations.split(",") if l.strip()],
                            "food_type": food_type,
                            "timing_morning": timing_morning,
                            "timing_night": timing_night,
                            "price_monthly": price_monthly,
                            "price_daily": price_daily,
                            "price_per_tiffin": price_per_tiffin,
                            "image_urls": [img1, img2, img3],
                            "description": short_desc,
                        })
                        st.success("✅ Tiffin added successfully!")
                        st.rerun()

        with sub_tab2:
            my_tiffins = db.collection("tiffins").where("provider_id", "==", user_id).stream()
            found_any = False
            for t in my_tiffins:
                found_any = True
                t_data = t.to_dict()
                t_id = t.id
                
                with st.expander(f"🍱 {t_data.get('name', 'Unnamed')} - {t_data.get('location', 'No Location')}"):
                    with st.form(key=f"edit_{t_id}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            e_name = st.text_input("Name", value=t_data.get("name", ""))
                            e_phone = st.text_input("Phone", value=t_data.get("phone", ""))
                            e_loc = st.text_input("Location", value=t_data.get("location", ""))
                            e_food = st.selectbox("Food Type", ["Veg", "Non-Veg", "Both"], index=["Veg", "Non-Veg", "Both"].index(t_data.get("food_type", "Veg")))
                            e_tm = st.text_input("Morning Time", value=t_data.get("timing_morning", ""))
                            e_tn = st.text_input("Night Time", value=t_data.get("timing_night", ""))
                        
                        with c2:
                            e_pm = st.number_input("Monthly ₹", value=int(t_data.get("price_monthly", 0)))
                            e_pd = st.number_input("Daily ₹", value=int(t_data.get("price_daily", 0)))
                            e_pt = st.number_input("Per Tiffin ₹", value=int(t_data.get("price_per_tiffin", 0)))
                            
                            imgs = t_data.get("image_urls", ["", "", ""])
                            while len(imgs) < 3: imgs.append("")
                            
                            e_img1 = st.text_input("Image 1", value=imgs[0])
                            e_img2 = st.text_input("Image 2", value=imgs[1])
                            e_img3 = st.text_input("Image 3", value=imgs[2])
                            e_delivery = st.text_input("Delivery Locations (comma-separated)", value=",".join(t_data.get("delivery_locations", [])))
                            e_description = st.text_area("Short Description (max 50 words)", value=t_data.get("description", ""))

                        col_update, col_delete = st.columns([1, 1])
                        with col_update:
                            if st.form_submit_button("💾 Update", use_container_width=True):
                                db.collection("tiffins").document(t_id).update({
                                    "name": e_name,
                                    "phone": e_phone,
                                    "location": e_loc,
                                    "food_type": e_food,
                                    "timing_morning": e_tm,
                                    "timing_night": e_tn,
                                    "price_monthly": e_pm,
                                    "price_daily": e_pd,
                                    "price_per_tiffin": e_pt,
                                    "image_urls": [e_img1, e_img2, e_img3],
                                    "delivery_locations": [x.strip() for x in e_delivery.split(",") if x.strip()],
                                    "description": " ".join((e_description or "").split()[:50])
                                })
                                st.success("✅ Updated!")
                                st.rerun()
                        
                        with col_delete:
                            if st.form_submit_button("🗑️ Delete", use_container_width=True):
                                db.collection("tiffins").document(t_id).delete()
                                st.success("✅ Deleted!")
                                st.rerun()

            if not found_any:
                st.info("📭 You haven't added any tiffins yet.")

# ================= STUDENT =================
elif role == "Student":
    st.markdown(f"### 🎓 Welcome, {user_data.get('name', 'Student')}!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Find Tiffin", "📊 Dashboard", "🏆 Top Rated", "👤 Profile"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            selected_location = st.text_input("🔍 Search by Location", placeholder="e.g., Downtown")
            search_name = st.text_input("🔎 Search by Tiffin Name", key="stud_search_name", placeholder="e.g., Premium Lunch Box")
           
        with col2:
            selected_food = st.selectbox("🍽 Food Preference", ["All", "Veg", "Non-Veg", "Both"])
            max_monthly = st.number_input("Max Monthly Price ₹ (0 = no filter)", min_value=0, value=0, step=100, key="stud_max_monthly")
        tiffins = db.collection("tiffins").stream()

        for t in tiffins:
            data = t.to_dict()

            if selected_location:
                delivery_locs = data.get("delivery_locations") or [data.get("location", "")]
                if not any(selected_location.lower() in (loc or "").lower() for loc in delivery_locs):
                    continue
            if search_name and search_name.lower() not in data.get("name", "").lower():
                continue
            if max_monthly and max_monthly > 0:
                try:
                    pm = float(data.get("price_monthly") or 0)
                except Exception:
                    pm = 0
                if pm > float(max_monthly):
                    continue
            if selected_food != "All" and data.get("food_type") != selected_food:
                continue

            with st.container():
                st.markdown('<div class="tiffin-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([2, 3])

                with c1:
                    image_list = [img for img in data.get("image_urls", []) if img]
                    if image_list:
                        imgs = []
                        for img in image_list:
                            imgs.append(f'<div style="flex:0 0 640px; scroll-snap-align:center; border-radius:12px; overflow:hidden; width:640px; height:360px;"><img src="{img}" style="width:100%; height:100%; object-fit:cover; border-radius:12px; display:block;"/></div>')
                        imgs_html = (
                            '<div style="display:flex; gap:12px; overflow-x:auto; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch; padding:6px 0;">'
                            + ''.join(imgs)
                            + '</div>'
                        )
                        st.markdown(imgs_html, unsafe_allow_html=True)
                    else:
                        st.write("No images")

                with c2:
                    st.markdown(f"### {data.get('name', 'Unknown Tiffin')}")
                    desc = data.get('description', '')
                    if desc:
                        short_desc = desc if len(desc.split()) <= 50 else ' '.join(desc.split()[:50]) + '...'
                        st.markdown(f"**Description:** {short_desc}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"📍 **Location:** {data.get('location', 'N/A')}")
                        st.markdown(f"📞 **Phone:** {data.get('phone', 'N/A')}")
                        delivery_display = ', '.join(data.get('delivery_locations', [data.get('location', 'N/A')]))
                        st.markdown(f"🚚 **Delivery Areas:** {delivery_display}")
                    with col_b:
                        st.markdown(f"🍽 **Type:** {data.get('food_type', 'N/A')}")
                    
                    st.markdown("**Timings:**")
                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.markdown(f"⏰ Morning: {data.get('timing_morning', 'N/A')}")
                    with col_y:
                        st.markdown(f"🌙 Night: {data.get('timing_night', 'N/A')}")
                    
                    st.markdown(f"""
                    💰 **Pricing:**
                    - Monthly: ₹{data.get('price_monthly', 0)}
                    - Daily: ₹{data.get('price_daily', 0)}
                    - Per Tiffin: ₹{data.get('price_per_tiffin', 0)}
                    """)

                    rev_docs = list(db.collection("reviews").where("tiffin_id", "==", t.id).stream())
                    avg_user = 0.0
                    avg_ai = 0.0
                    ai_one_line = "No reviews yet. Be the first to review!"
                    if rev_docs:
                        ratings = []
                        ai_scores = []
                        texts = []
                        for rr in rev_docs:
                            rd = rr.to_dict() or {}
                            if rd.get("rating") is not None:
                                try:
                                    ratings.append(float(rd.get("rating") or 0))
                                except Exception:
                                    pass
                            if rd.get("ai_score") is not None:
                                try:
                                    ai_scores.append(float(rd.get("ai_score") or 0))
                                except Exception:
                                    pass
                            if rd.get("review"):
                                texts.append(str(rd.get("review")))

                        if ratings:
                            avg_user = sum(ratings) / len(ratings)
                        if ai_scores:
                            avg_ai = sum(ai_scores) / len(ai_scores)

                        context = " ".join(texts)
                        if context:
                            try:
                                ai_one_line = generate_short_summary(context, min_words=5, max_words=15)
                            except Exception:
                                w = context.replace("\n", " ").split()
                                ai_one_line = " ".join(w[:15]) if w else "No reviews yet."

                    if avg_ai > 7:
                        ai_color = "#16a34a"
                    elif avg_ai >= 4:
                        ai_color = "#d97706"
                    else:
                        ai_color = "#dc2626"

                    if avg_user > 3.5:
                        user_color = "#16a34a"
                    elif avg_user >= 2.5:
                        user_color = "#d97706"
                    else:
                        user_color = "#dc2626"

                    st.markdown(
                        f"<p><strong>Avg user review:</strong> <span style='color:{user_color}; font-weight:600'>{avg_user:.1f}/5</span> • <strong>AI review:</strong> <span style='color:{ai_color}; font-weight:600'>{avg_ai:.1f}/10</span></p>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"*AI summary:* {ai_one_line}")

                    rating = st.slider("⭐ Rate (1–5)", 1, 5, key=f"rate_{t.id}")
                    review = st.text_area("💬 Write Review", key=f"rev_{t.id}", height=80)
                    if st.button("✅ Submit Review", key=f"btn_{t.id}", use_container_width=True):
                        price_val = data.get('price_per_tiffin', None)
                        ai_score, ai_summary = analyze_review(review, price_val)
                        existing_rev = None
                        for rr in db.collection("reviews").where("tiffin_id", "==", t.id).where("user_id", "==", user_id).stream():
                            existing_rev = rr
                            break

                        review_payload = {
                            "tiffin_id": t.id,
                            "user_id": user_id,
                            "rating": rating,
                            "review": review,
                            "ai_score": ai_score,
                            "ai_summary": ai_summary,
                            "price": price_val,
                        }

                        if existing_rev:
                            db.collection("reviews").document(existing_rev.id).update(review_payload)
                            st.success("✅ Review updated!")
                        else:
                            db.collection("reviews").add(review_payload)
                            st.success("✅ Review submitted!")

                        st.info(f"🤖 AI Score: {ai_score}/10\n\n📝 {ai_summary}")

                    with st.expander("📖 View Old Reviews"):
                        reviews = db.collection("reviews").where("tiffin_id", "==", t.id).stream()
                        found = False
                        for r in reviews:
                            rd = r.to_dict()
                            st.markdown(f"⭐ **{rd.get('rating', 0)}/5** – {rd.get('review', '')}")
                            if rd.get('ai_summary'):
                                st.info(f"🤖 AI: {rd.get('ai_summary')}")
                            found = True
                        if not found:
                            st.write("No reviews yet")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📊 Dashboard")
        t_docs = list(db.collection("tiffins").stream())
        if not t_docs:
            st.info("No tiffins available right now.")
        else:
            total_tiffins = len(t_docs)
            prices = []
            for t in t_docs:
                td = t.to_dict() or {}
                try:
                    p = float(td.get("price_monthly") or 0)
                except Exception:
                    p = 0
                if p:
                    prices.append(p)

            avg_monthly = round(sum(prices) / len(prices), 2) if prices else 0.0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Available Tiffins", total_tiffins)
            with col2:
                st.metric("Avg Monthly Price", f"₹{avg_monthly}")
            with col3:
                rev_count = len(list(db.collection("reviews").stream()))
                st.metric("Total Reviews", rev_count)

            st.markdown("---")
            st.markdown("### 🔝 Top AI-rated Tiffins")
            ai_map = {}
            for r in db.collection("reviews").stream():
                rd = r.to_dict() or {}
                tid = rd.get("tiffin_id")
                if tid:
                    ai_map.setdefault(tid, []).append(rd.get("ai_score", 0) or 0)

            scored = []
            for t in t_docs:
                td = t.to_dict() or {}
                tid = t.id
                avg_ai = round(sum(ai_map.get(tid, [])) / len(ai_map.get(tid, [])), 1) if ai_map.get(tid) else 0.0
                scored.append((tid, td.get("name", "Unknown"), avg_ai))

            scored_sorted = sorted(scored, key=lambda x: x[2], reverse=True)[:5]
            for tid, name, ai_score in scored_sorted:
                st.write(f"**{name}** — AI Score: {ai_score}/10")

    with tab3:
        render_top_rated_section()

    with tab4:
        st.subheader("✏️ Edit Your Profile")
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name", value=user_data.get("name", ""), key="student_name")
        with col2:
            new_phone = st.text_input("Phone Number", value=user_data.get("phone", ""), key="student_phone")
        
        new_location = st.text_input("Location", value=user_data.get("location", ""), key="student_location")
        
        if st.button("💾 Update Profile", use_container_width=True):
            user_ref.update({"name": new_name, "phone": new_phone, "location": new_location})
            st.success("✅ Profile Updated!")
            st.rerun()

        if st.button("🔓 Logout", use_container_width=True, key="student_profile_logout"):
            st.session_state["force_register"] = True
            keep = {"theme", "force_register"}
            for k in list(st.session_state.keys()):
                if k not in keep:
                    st.session_state.pop(k, None)
            st.success("✅ Logged out")
            st.rerun()

# Close the overlay div
st.markdown('</div>', unsafe_allow_html=True)
