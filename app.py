import streamlit as st
from firebase_config import db
from auth import register_user, login_user
from gemini_ai import analyze_review

# ================= PAGE CONFIG =================
st.set_page_config(page_title="RIGHT TIFFIN FOR YOU", layout="wide", initial_sidebar_state="expanded")

# ================= THEME (light/dark) and CUSTOM CSS =================
# Initialize theme state
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"


# Build CSS based on theme
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
        background: rgba(0,0,0);
        padding: 14px;
        border-radius: 10px;
        border-left: 4px solid #FF6B35;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
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
    /* small floating theme badge */
    .theme-badge {{ position: fixed; left: 12px; top: 8px; z-index: 9999; }}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# wrap main content in a light overlay so background image shows through around cards
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
    # Attractive banner for auth page with background image and availability note
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

# ================= TIFFIN PROVIDER =================
if role == "Tiffin Provider":
    st.markdown(f"### 👨‍🍳 Welcome, {user_data.get('name', 'Provider')}!")
    
    tab1, tab2 = st.tabs(["🔍 Browse Tiffins", "👤 Profile"])

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
                    # Display images in a horizontal, swipeable container (works with mouse drag and touch swipe)
                    image_list = [img for img in data.get("image_urls", []) if img]
                    if image_list:
                        imgs = []
                        for img in image_list:
                            imgs.append(f'<div style="flex:0 0 auto;scroll-snap-align:center;border-radius:12px;overflow:hidden;height:420px;"><img src="{img}" style="height3:20px;object-fit:cover;display:block;"></div>')
                        imgs_html = '<div style="display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;padding:6px 0;">' + ''.join(imgs) + '</div>'
                        st.markdown(imgs_html, unsafe_allow_html=True)
                    else:
                        st.write("No images")

                with c2:
                    st.markdown(f"### {data.get('name', 'Unknown Tiffin')}")
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
        
        # Logout button inside Student profile to return to registration/login
        if st.button("🔓 Logout", use_container_width=True, key="student_profile_logout"):
            # preserve theme and force_register flag so UI remains consistent
            st.session_state["force_register"] = True
            keep = {"theme", "force_register"}
            for k in list(st.session_state.keys()):
                if k not in keep:
                    st.session_state.pop(k, None)
            st.success("✅ Logged out")
            st.rerun()

        # if st.button("🔓 Logout", use_container_width=True, key="student_logout"):
        #     for k in list(st.session_state.keys()):
        #         st.session_state.pop(k, None)
        #     st.success("Logged out")
        #     st.rerun()


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
                        "image_urls": [img1, img2, img3]
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
                                    "delivery_locations": [x.strip() for x in e_delivery.split(",") if x.strip()]
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
    
    tab1, tab2 = st.tabs(["🔍 Find Tiffin", "👤 Profile"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            selected_location = st.text_input("🔍 Search by Location", placeholder="e.g., Downtown")
            search_name = st.text_input("🔎 Search by Tiffin Name", key="stud_search_name", placeholder="e.g., Premium Lunch Box")
        with col2:
            selected_food = st.selectbox("🍽 Food Preference", ["All", "Veg", "Non-Veg", "Both"])

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
                    # Horizontal swipeable image carousel for students
                    image_list = [img for img in data.get("image_urls", []) if img]
                    if image_list:
                        imgs = []
                        for img in image_list:
                            imgs.append(f'<div style="flex:0 0 auto;scroll-snap-align:center;border-radius:12px;overflow:hidden;height:220px;"><img src="{img}" style="height:220px;object-fit:cover;display:block;"></div>')
                        imgs_html = '<div style="display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;padding:6px 0;">' + ''.join(imgs) + '</div>'
                        st.markdown(imgs_html, unsafe_allow_html=True)
                    else:
                        st.write("No images")

                with c2:
                    st.markdown(f"### {data.get('name', 'Unknown Tiffin')}")
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

                    col_review = st.columns(1)[0]
                    rating = st.slider("⭐ Rate (1–5)", 1, 5, key=f"rate_{t.id}")
                    review = st.text_area("💬 Write Review", key=f"rev_{t.id}", height=80)

                    if st.button("✅ Submit Review", key=f"btn_{t.id}", use_container_width=True):
                        price_val = data.get('price_per_tiffin', None)
                        ai_score, ai_summary = analyze_review(review, price_val)
                        db.collection("reviews").add({
                            "tiffin_id": t.id,
                            "user_id": user_id,
                            "rating": rating,
                            "review": review,
                            "ai_score": ai_score,
                            "ai_summary": ai_summary,
                            "price": price_val,
                        })
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

        st.markdown("---")
        st.markdown("## 🏆 Top Rated Tiffins (AI Powered)")

        # Build combined ranking using ai_score (0-10), user rating (1-5), and price (lower is better)
        reviews = db.collection("reviews").stream()
        stats = {}
        for r in reviews:
            d = r.to_dict()
            tid = d.get("tiffin_id")
            if tid not in stats:
                stats[tid] = {"ai_scores": [], "ratings": [], "prices": []}
            stats[tid]["ai_scores"].append(d.get("ai_score", 0) or 0)
            stats[tid]["ratings"].append(d.get("rating", 0) or 0)
            if d.get("price") is not None:
                stats[tid]["prices"].append(d.get("price"))

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
            col1, col2, col3 = st.columns(3)
            medals = ["🥇", "🥈", "🥉"]
            for idx, (tid, score_val, ai_v, rat_v, p_v) in enumerate(combined_sorted[:3]):
                tiffin_doc = db.collection("tiffins").document(tid).get()
                if tiffin_doc.exists:
                    tiffin = tiffin_doc.to_dict()

                    # derive a one-line reason: prefer an AI summary from reviews or a short review excerpt
                    reason = "Top choice based on combined AI score, user ratings and price."
                    revs = db.collection("reviews").where("tiffin_id", "==", tid).stream()
                    for rr in revs:
                        rdata = rr.to_dict()
                        if rdata.get("ai_summary"):
                            reason = rdata.get("ai_summary")
                            break
                        if rdata.get("review"):
                            txt = rdata.get("review").strip()
                            if txt:
                                reason = (txt[:120] + "...") if len(txt) > 120 else txt
                                break

                    with [col1, col2, col3][idx]:
                        st.markdown(f"""
                        <div class="metric-box">
                            <h3>{medals[idx]} {tiffin.get('name', 'Unknown')}</h3>
                            <p style="font-size: 18px; color: #FF6B35;">Combined Score: {score_val:.2f}/10</p>
                            <p>AI Avg: {ai_v:.1f}/10 • Rating Avg: {rat_v:.1f}/5</p>
                            <p>Price: ₹{p_v if p_v is not None else 'N/A'}</p>
                            <p style="margin-top:6px; font-style:italic;">Why: {reason}</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No ratings yet. Be the first to review!")
    
    with tab2:
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
            # Logout button inside Student profile to return to registration/login

        if st.button("🔓 Logout", use_container_width=True, key="student_profile_logout"):
            # preserve theme and force_register flag so UI remains consistent
            st.session_state["force_register"] = True
            keep = {"theme", "force_register"}
            for k in list(st.session_state.keys()):
                if k not in keep:
                    st.session_state.pop(k, None)
            st.success("✅ Logged out")
            st.rerun()
