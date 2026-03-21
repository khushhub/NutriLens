
"""
NutriLens - AI Nutrition Tracker
Food Recognition + Barcode Scanner + Groq AI Insights
"""

import streamlit as st
from PIL import Image
from datetime import datetime, date
import numpy as np
import json
import os

st.set_page_config(page_title="NutriLens", page_icon="🍽️", layout="wide")


# ======================
# LOAD MODEL
# ======================

@st.cache_resource
def load_food_model():
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model

        model_path = "saved_models/food_classifier.h5"
        labels_path = "saved_models/labels.json"

        if not os.path.exists(model_path) or not os.path.exists(labels_path):
            return None, None

        model = load_model(model_path)

        with open(labels_path, "r") as f:
            labels_dict = json.load(f)

        labels = {int(k): v for k, v in labels_dict.items()}
        return model, labels

    except Exception:
        return None, None


food_model, food_labels = load_food_model()
MODEL_AVAILABLE = food_model is not None


# ======================
# NUTRITION DATABASE
# ======================

NUTRITION_DB = {
    'biryani':        {'cal': 371, 'protein': 14.8, 'carbs': 67.8, 'fat':  7.1, 'portion': 285},
    'masala_dosa':    {'cal': 200, 'protein':  6.5, 'carbs': 38.2, 'fat':  2.8, 'portion': 120},
    'paneer_tikka':   {'cal': 240, 'protein': 14.5, 'carbs':  5.2, 'fat': 18.3, 'portion': 100},
    'dal_rice':       {'cal': 330, 'protein': 13.5, 'carbs': 64.5, 'fat':  3.6, 'portion': 300},
    'idli':           {'cal': 150, 'protein':  5.2, 'carbs': 28.5, 'fat':  1.5, 'portion': 160},
    'butter_chicken': {'cal': 360, 'protein': 25.6, 'carbs': 13.0, 'fat': 24.2, 'portion': 200},
    'samosa':         {'cal': 262, 'protein':  4.5, 'carbs': 28.5, 'fat': 14.8, 'portion': 100},
    'roti':           {'cal': 120, 'protein':  3.6, 'carbs': 22.0, 'fat':  2.5, 'portion':  40},
    'naan':           {'cal': 262, 'protein':  7.6, 'carbs': 44.0, 'fat':  6.2, 'portion':  90},
    'chole_bhature':  {'cal': 450, 'protein': 15.0, 'carbs': 60.0, 'fat': 18.0, 'portion': 250},
    'rajma_rice':     {'cal': 340, 'protein': 14.0, 'carbs': 62.0, 'fat':  4.0, 'portion': 300},
    'upma':           {'cal': 180, 'protein':  5.0, 'carbs': 32.0, 'fat':  4.5, 'portion': 200},
    'poha':           {'cal': 165, 'protein':  4.0, 'carbs': 32.0, 'fat':  3.5, 'portion': 180},
    'vada_pav':       {'cal': 290, 'protein':  7.0, 'carbs': 45.0, 'fat': 10.0, 'portion': 150},
    'pav_bhaji':      {'cal': 310, 'protein':  8.5, 'carbs': 52.0, 'fat':  9.5, 'portion': 250},
    'default':        {'cal': 200, 'protein':  8.0, 'carbs': 30.0, 'fat':  5.0, 'portion': 200},
}

DAILY_GOALS = {'cal': 2000, 'protein': 50, 'carbs': 275, 'fat': 65}


# ======================
# DAILY LOG PERSISTENCE
# ======================

LOG_FILE = "utils/daily_log.json"


def load_daily_log():
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
        required = {"name", "calories", "protein", "carbs", "fat", "time"}
        if isinstance(data, list):
            return [e for e in data if isinstance(e, dict) and required.issubset(e.keys())]
        return []
    except Exception:
        return []


def save_daily_log(logs):
    try:
        serializable = []
        for entry in logs:
            e = entry.copy()
            if isinstance(e.get("time"), datetime):
                e["time"] = e["time"].strftime("%Y-%m-%d %H:%M:%S")
            serializable.append(e)
        with open(LOG_FILE, "w") as f:
            json.dump(serializable, f, indent=2)
    except Exception as ex:
        st.error(f"Could not save log: {ex}")


# ======================
# BARCODE LOOKUP
# ======================

BARCODE_DEMO_DB = {
    "8901030868139": {"name": "Maggi Noodles",        "cal": 385, "protein": 10.0, "carbs": 63.0, "fat": 10.0, "portion": 100},
    "8906002940004": {"name": "Parle-G Biscuits",     "cal": 483, "protein":  6.7, "carbs": 76.5, "fat": 16.7, "portion": 100},
    "8901725181009": {"name": "Amul Butter",          "cal": 720, "protein":  0.5, "carbs":  1.4, "fat": 80.0, "portion": 100},
    "8901725130009": {"name": "Amul Full Cream Milk", "cal":  61, "protein":  3.2, "carbs":  4.4, "fat":  3.5, "portion": 100},
}


def lookup_barcode(barcode_data):
    try:
        import requests
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == 1:
                p = data["product"]
                n = p.get("nutriments", {})
                return {
                    "name":    p.get("product_name", "Unknown Product"),
                    "cal":     round(n.get("energy-kcal_100g", 0)),
                    "protein": round(n.get("proteins_100g", 0), 1),
                    "carbs":   round(n.get("carbohydrates_100g", 0), 1),
                    "fat":     round(n.get("fat_100g", 0), 1),
                    "portion": 100,
                }
    except Exception:
        pass
    return BARCODE_DEMO_DB.get(barcode_data, None)


# ======================
# BARCODE SCAN FROM IMAGE
# ======================

def scan_barcode_from_image(image):
    try:
        import cv2
        from pyzbar.pyzbar import decode as pyzbar_decode

        img_array = np.array(image.convert("RGB"))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        barcodes = pyzbar_decode(img_bgr)
        if barcodes:
            return barcodes[0].data.decode("utf-8")
    except ImportError:
        st.warning("pyzbar / opencv not installed. Use manual barcode entry below.")
    except Exception as e:
        st.error(f"Barcode scan error: {e}")
    return None


# ======================
# FOOD PREDICTION
# ======================

def predict_food(image):
    if MODEL_AVAILABLE:
        try:
            from tensorflow.keras.preprocessing.image import img_to_array
            from tensorflow.keras.applications.efficientnet import preprocess_input

            img = image.resize((224, 224)).convert("RGB")
            img_array = img_to_array(img)
            img_array = preprocess_input(img_array)
            img_array = np.expand_dims(img_array, axis=0)

            preds = food_model.predict(img_array)
            index = int(np.argmax(preds))
            confidence = float(preds[0][index])
            food_name = food_labels.get(index, "unknown")
            return food_name, confidence

        except Exception as e:
            st.error(f"Prediction error: {e}")

    demo_foods = [k for k in NUTRITION_DB if k != "default"]
    food_name = demo_foods[hash(image.tobytes()) % len(demo_foods)]
    return food_name, 0.87


def get_nutrition(food):
    name = food.lower().replace(" ", "_")
    return NUTRITION_DB.get(name, NUTRITION_DB["default"])


# ======================
# GROQ AI INSIGHTS
# ======================

def get_groq_insight(food_logs):
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("groq_insights", "groq_insights.py")
        groq_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(groq_mod)
        if hasattr(groq_mod, "get_insight"):
            return groq_mod.get_insight(food_logs)
    except Exception:
        pass

    try:
        from groq import Groq

        api_key = st.secrets.get("GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            return "💡 Add GROQ_API_KEY to Streamlit secrets to enable AI insights."
        client = Groq(api_key=api_key)

        today_str = date.today().strftime("%Y-%m-%d")
        today_logs = [l for l in food_logs if l.get("time", "")[:10] == today_str]

        total_cal     = round(sum(x["calories"] for x in today_logs), 1)
        total_protein = round(sum(x["protein"]  for x in today_logs), 1)
        total_carbs   = round(sum(x["carbs"]    for x in today_logs), 1)
        total_fat     = round(sum(x["fat"]      for x in today_logs), 1)
        meal_names    = ", ".join(x["name"] for x in today_logs) or "No meals yet"

        prompt = f"""You are a friendly Indian nutrition coach. Based on today's meals, give 2-3 short practical tips in plain English. Be specific to Indian cuisine.

Today's intake:
- Meals: {meal_names}
- Calories: {total_cal} / {DAILY_GOALS['cal']} kcal
- Protein: {total_protein}g / {DAILY_GOALS['protein']}g
- Carbs: {total_carbs}g / {DAILY_GOALS['carbs']}g
- Fat: {total_fat}g / {DAILY_GOALS['fat']}g

Keep it under 100 words. Use bullet points."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Add your GROQ_API_KEY to get personalized insights. ({e})"


# ======================
# SESSION STATE
# ======================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "food_logs" not in st.session_state:
    st.session_state.food_logs = load_daily_log()


# ======================
# SIDEBAR
# ======================

with st.sidebar:
    st.title("🍽️ NutriLens")
    st.markdown("AI Food & Nutrition Analyzer")
    st.markdown("---")

    if not MODEL_AVAILABLE:
        st.warning("⚠️ Demo Mode — model not found")

    page = st.radio(
        "Navigate",
        ["🏠 Home", "📊 Dashboard", "📜 History"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Daily Goals**")
    st.caption(f"🔥 Calories : {DAILY_GOALS['cal']} kcal")
    st.caption(f"💪 Protein  : {DAILY_GOALS['protein']} g")
    st.caption(f"🌾 Carbs    : {DAILY_GOALS['carbs']} g")
    st.caption(f"🫐 Fat      : {DAILY_GOALS['fat']} g")

    today_str = date.today().strftime("%Y-%m-%d")
    today_logs = [l for l in st.session_state.food_logs if l.get("time", "")[:10] == today_str]
    if today_logs:
        st.markdown("---")
        st.markdown("**Today so far**")
        total_cal = round(sum(x["calories"] for x in today_logs), 1)
        remaining = DAILY_GOALS['cal'] - total_cal
        st.caption(f"🔥 {total_cal} / {DAILY_GOALS['cal']} kcal")
        if remaining > 0:
            st.caption(f"➡️ {remaining} kcal remaining")
        else:
            st.caption(f"⚠️ {abs(remaining)} kcal over goal")


# ======================
# HOME PAGE
# ======================

if "Home" in page:

    st.title("🍽️ NutriLens")
    st.markdown("AI-powered nutrition tracking for Indian cuisine")
    st.markdown("---")

    col_food, col_barcode = st.columns(2)

    # LEFT: FOOD IMAGE
    with col_food:
        st.subheader("📸 Snap your meal")

        uploaded_file = st.file_uploader(
            "Upload a food photo",
            type=["jpg", "jpeg", "png"],
            key="food_uploader",
        )

        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Image", use_container_width=True)

            if st.button("🔍 Analyze Food", type="primary"):
                with st.spinner("Analyzing your meal..."):
                    food, conf = predict_food(image)
                    nutrition = get_nutrition(food)

                st.session_state.analysis_result = {
                    "source":        "image",
                    "name":          food.replace("_", " ").title(),
                    "confidence":    conf,
                    "image":         image,
                    "base_calories": nutrition["cal"],
                    "base_protein":  nutrition["protein"],
                    "base_carbs":    nutrition["carbs"],
                    "base_fat":      nutrition["fat"],
                    "base_portion":  nutrition["portion"],
                }
                st.rerun()

    # RIGHT: BARCODE SCANNER
    with col_barcode:
        st.subheader("📦 Barcode Scanner")

        # ── Option A: Live webcam scan ────────────────────────────────────
        st.markdown("**Option A — Scan with laptop camera**")
        st.caption("Point your camera at the barcode and click Capture")

        # Use streamlit-webrtc if available, else fall back to OpenCV snapshot
        try:
            from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
            import threading
            import av

            class BarcodeTransformer(VideoTransformerBase):
                def __init__(self):
                    self.barcode_data = None
                    self.lock = threading.Lock()

                def transform(self, frame):
                    try:
                        import cv2
                        from pyzbar.pyzbar import decode as pyzbar_decode

                        img = frame.to_ndarray(format="bgr24")
                        barcodes = pyzbar_decode(img)

                        for barcode in barcodes:
                            data = barcode.data.decode("utf-8")
                            with self.lock:
                                self.barcode_data = data
                            # Draw green box around barcode
                            x, y, w, h = barcode.rect
                            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
                            cv2.putText(img, data, (x, y - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    except Exception:
                        pass
                    return img

            ctx = webrtc_streamer(
                key="barcode-cam",
                video_transformer_factory=BarcodeTransformer,
                media_stream_constraints={"video": True, "audio": False},
                async_transform=True,
            )

            if ctx.video_transformer:
                if st.button("📸 Capture Barcode", type="primary"):
                    with ctx.video_transformer.lock:
                        code = ctx.video_transformer.barcode_data

                    if code:
                        st.success(f"✅ Barcode detected: `{code}`")
                        result = lookup_barcode(code)
                        if result:
                            st.session_state.analysis_result = {
                                "source":        "barcode",
                                "name":          result["name"],
                                "confidence":    1.0,
                                "image":         None,
                                "base_calories": result["cal"],
                                "base_protein":  result["protein"],
                                "base_carbs":    result["carbs"],
                                "base_fat":      result["fat"],
                                "base_portion":  result["portion"],
                            }
                            st.rerun()
                        else:
                            st.warning(f"Barcode `{code}` not found. Try manual entry below.")
                    else:
                        st.warning("No barcode detected yet. Hold the barcode steady in front of the camera.")

        except ImportError:
            # Fallback: OpenCV snapshot from webcam
            st.info("Install `streamlit-webrtc` for live camera. Using snapshot mode instead.")

            if st.button("📸 Capture from Webcam", type="primary"):
                try:
                    import cv2
                    from pyzbar.pyzbar import decode as pyzbar_decode

                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        st.error("❌ Could not open webcam.")
                    else:
                        code = None
                        with st.spinner("Scanning... hold barcode steady"):
                            for _ in range(60):           # try for ~2 seconds
                                ret, frame = cap.read()
                                if not ret:
                                    break
                                barcodes = pyzbar_decode(frame)
                                if barcodes:
                                    code = barcodes[0].data.decode("utf-8")
                                    break
                        cap.release()

                        if code:
                            st.success(f"✅ Barcode detected: `{code}`")
                            result = lookup_barcode(code)
                            if result:
                                st.session_state.analysis_result = {
                                    "source":        "barcode",
                                    "name":          result["name"],
                                    "confidence":    1.0,
                                    "image":         None,
                                    "base_calories": result["cal"],
                                    "base_protein":  result["protein"],
                                    "base_carbs":    result["carbs"],
                                    "base_fat":      result["fat"],
                                    "base_portion":  result["portion"],
                                }
                                st.rerun()
                            else:
                                st.warning(f"Barcode `{code}` not found. Try manual entry.")
                        else:
                            st.error("No barcode detected. Try again with better lighting.")

                except ImportError:
                    st.error("OpenCV not installed. Run: pip install opencv-python")

        st.markdown("---")
        st.markdown("**Option B — Enter barcode number manually**")

        manual_code = st.text_input("Barcode number", placeholder="e.g. 8901030868139")

        if st.button("🔍 Look Up Barcode") and manual_code.strip():
            with st.spinner("Looking up product..."):
                result = lookup_barcode(manual_code.strip())

            if result:
                st.session_state.analysis_result = {
                    "source":        "barcode",
                    "name":          result["name"],
                    "confidence":    1.0,
                    "image":         None,
                    "base_calories": result["cal"],
                    "base_protein":  result["protein"],
                    "base_carbs":    result["carbs"],
                    "base_fat":      result["fat"],
                    "base_portion":  result["portion"],
                }
                st.rerun()
            else:
                st.warning("Product not found. Check the barcode number or add it manually.")

    # ANALYSIS RESULT
    if st.session_state.analysis_result:
        r = st.session_state.analysis_result

        st.markdown("---")
        st.subheader("🧾 Meal Analysis")

        col1, col2 = st.columns([1, 2])

        with col1:
            if r.get("image"):
                st.image(r["image"], use_container_width=True)
            else:
                st.info("📦 Packaged product")

        with col2:
            st.markdown(f"### {r['name']}")
            if r["source"] == "image":
                st.caption(f"AI Confidence: {r['confidence'] * 100:.1f}%")
            else:
                st.caption("Source: Barcode scan")

            st.caption(f"Base values are per {r['base_portion']} g")

            grams = st.number_input(
                "Adjust grams consumed",
                min_value=1,
                max_value=2000,
                value=int(r["base_portion"]),
                step=5,
                help="Calories and macros recalculate automatically",
            )

            ratio       = grams / r["base_portion"] if r["base_portion"] > 0 else 1.0
            adj_cal     = round(r["base_calories"] * ratio, 1)
            adj_protein = round(r["base_protein"]  * ratio, 1)
            adj_carbs   = round(r["base_carbs"]    * ratio, 1)
            adj_fat     = round(r["base_fat"]      * ratio, 1)

        st.markdown(f"#### Nutrition Facts for **{grams} g**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔥 Calories", f"{adj_cal} kcal",  delta=f"{adj_cal - r['base_calories']:+.1f} vs base")
        c2.metric("💪 Protein",  f"{adj_protein} g", delta=f"{adj_protein - r['base_protein']:+.1f} vs base")
        c3.metric("🌾 Carbs",    f"{adj_carbs} g",   delta=f"{adj_carbs - r['base_carbs']:+.1f} vs base")
        c4.metric("🫐 Fat",      f"{adj_fat} g",     delta=f"{adj_fat - r['base_fat']:+.1f} vs base")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ Log Meal", type="primary"):
                entry = {
                    "name":     f"{r['name']} ({grams}g)",
                    "calories": adj_cal,
                    "protein":  adj_protein,
                    "carbs":    adj_carbs,
                    "fat":      adj_fat,
                    "time":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                st.session_state.food_logs.append(entry)
                save_daily_log(st.session_state.food_logs)
                st.session_state.analysis_result = None
                st.success(f"✅ Logged {r['name']} — {adj_cal} kcal for {grams}g!")
                st.rerun()
        with col_b:
            if st.button("❌ Discard"):
                st.session_state.analysis_result = None
                st.rerun()


# ======================
# DASHBOARD PAGE
# ======================

elif "Dashboard" in page:

    st.title("📊 Dashboard")

    today_str = date.today().strftime("%Y-%m-%d")
    today_logs = [l for l in st.session_state.food_logs if l.get("time", "")[:10] == today_str]

    if not today_logs:
        st.info("No meals logged today. Head to 🏠 Home to log your first meal!")
    else:
        st.markdown(f"### Today — {date.today().strftime('%d %B %Y')}")

        total_cal     = round(sum(x["calories"] for x in today_logs), 1)
        total_protein = round(sum(x["protein"]  for x in today_logs), 1)
        total_carbs   = round(sum(x["carbs"]    for x in today_logs), 1)
        total_fat     = round(sum(x["fat"]      for x in today_logs), 1)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔥 Calories", f"{total_cal} kcal",  delta=f"{total_cal - DAILY_GOALS['cal']:+.0f} vs goal",     delta_color="inverse")
        c2.metric("💪 Protein",  f"{total_protein} g", delta=f"{total_protein - DAILY_GOALS['protein']:+.0f} vs goal")
        c3.metric("🌾 Carbs",    f"{total_carbs} g",   delta=f"{total_carbs - DAILY_GOALS['carbs']:+.0f} vs goal",  delta_color="inverse")
        c4.metric("🫐 Fat",      f"{total_fat} g",     delta=f"{total_fat - DAILY_GOALS['fat']:+.0f} vs goal",      delta_color="inverse")

        st.markdown("#### Progress towards daily goals")

        def progress_bar(label, current, goal):
            pct = min(current / goal, 1.0) if goal > 0 else 0
            icon = "🟢" if pct <= 0.85 else ("🟡" if pct <= 1.0 else "🔴")
            st.write(f"{icon} **{label}** — {current} / {goal}  ({pct * 100:.0f}%)")
            st.progress(pct)

        progress_bar("Calories", total_cal,     DAILY_GOALS['cal'])
        progress_bar("Protein",  total_protein, DAILY_GOALS['protein'])
        progress_bar("Carbs",    total_carbs,   DAILY_GOALS['carbs'])
        progress_bar("Fat",      total_fat,     DAILY_GOALS['fat'])

        st.markdown("#### Meals logged today")
        for log in today_logs:
            t = datetime.strptime(log["time"], "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")
            st.markdown(
                f"🍽️ **{log['name']}** &nbsp;·&nbsp; {log['calories']} kcal &nbsp;·&nbsp; "
                f"P: {log['protein']}g &nbsp; C: {log['carbs']}g &nbsp; F: {log['fat']}g &nbsp;·&nbsp; _{t}_"
            )

        st.markdown("---")
        st.subheader("🤖 AI Nutrition Insights")
        if st.button("✨ Get Personalized Insights (Groq)"):
            with st.spinner("Asking Groq AI..."):
                insight = get_groq_insight(st.session_state.food_logs)
            st.info(insight)


# ======================
# HISTORY PAGE
# ======================

elif "History" in page:

    st.title("📜 Food History")

    all_logs = st.session_state.food_logs

    if not all_logs:
        st.info("No history yet. Start logging meals from 🏠 Home!")
    else:
        from itertools import groupby

        sorted_logs = sorted(all_logs, key=lambda x: x.get("time", ""), reverse=True)

        def date_key(log):
            return log.get("time", "")[:10]

        today_str = date.today().strftime("%Y-%m-%d")

        for day, entries in groupby(sorted_logs, key=date_key):
            entries = list(entries)
            day_cal = round(sum(x["calories"] for x in entries), 1)
            try:
                day_label = datetime.strptime(day, "%Y-%m-%d").strftime("%A, %d %B %Y")
            except ValueError:
                day_label = day

            with st.expander(
                f"📅 {day_label}  —  {day_cal} kcal  ({len(entries)} meals)",
                expanded=(day == today_str),
            ):
                for log in entries:
                    try:
                        t = datetime.strptime(log["time"], "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")
                    except ValueError:
                        t = log.get("time", "")
                    st.markdown(
                        f"🍽️ **{log['name']}** &nbsp;·&nbsp; {log['calories']} kcal &nbsp;·&nbsp; "
                        f"P: {log['protein']}g &nbsp; C: {log['carbs']}g &nbsp; F: {log['fat']}g &nbsp;·&nbsp; _{t}_"
                    )

        st.markdown("---")
        if st.button("🗑️ Clear All History", type="secondary"):
            st.session_state.food_logs = []
            save_daily_log([])
            st.success("History cleared.")
            st.rerun()