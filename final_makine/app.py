import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import os
import csv
import streamlit.components.v1 as components
import sqlite3
import json


def patch_onehotencoder_check_unknown():
    """Work around a NumPy/Scikit-Learn compatibility issue for object categories."""
    try:
        import sklearn.preprocessing._encoders as encoders_module
        import sklearn.utils._encode as encode_module
    except Exception:
        return

    original_check_unknown = getattr(encoders_module, "_check_unknown", None)
    if original_check_unknown is None or getattr(original_check_unknown, "_safe_patch", False):
        return

    def safe_check_unknown(values, known_values, return_mask=False):
        try:
            return original_check_unknown(values, known_values, return_mask=return_mask)
        except TypeError:
            values_array = np.asarray(values, dtype=object)
            known_array = np.asarray(known_values, dtype=object)
            known_set = set(known_array.tolist())

            if return_mask:
                mask = np.array([value in known_set for value in values_array], dtype=bool)
                diff = np.unique(values_array[~mask])
                return diff, mask

            return np.unique([value for value in values_array if value not in known_set])

    safe_check_unknown._safe_patch = True
    encoders_module._check_unknown = safe_check_unknown
    encode_module._check_unknown = safe_check_unknown


patch_onehotencoder_check_unknown()

# --- DATABASE SETUP ---
DB_FOLDER = "analysis_history"
DB_PATH = os.path.join(DB_FOLDER, "predictions.db")

def init_db():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
            inputs TEXT,
            prediction INTEGER,
            probability_0 REAL,
            probability_1 REAL
        )
    ''')
    conn.commit()
    conn.close()

HISTORY_CSV_COLUMNS = [
    "Timestamp",
    "Administrative",
    "Administrative_Duration",
    "Informational",
    "Informational_Duration",
    "ProductRelated",
    "ProductRelated_Duration",
    "BounceRates",
    "ExitRates",
    "PageValues",
    "SpecialDay",
    "Month",
    "OperatingSystems",
    "Browser",
    "Region",
    "TrafficType",
    "VisitorType",
    "Weekend",
    "Total_Duration",
    "Engagement_Score",
    "Bounce_Exit_Ratio",
    "Returning_Visitor_Flag",
    "Prediction",
    "Probability_0",
    "Probability_1"
]


def load_prediction_history_csv(csv_path):
    """Load historical prediction rows dynamically supporting 17, 18, and 25 column schemas."""
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=HISTORY_CSV_COLUMNS)

    try:
        with open(csv_path, newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
    except Exception:
        return pd.DataFrame(columns=HISTORY_CSV_COLUMNS)

    if not rows or len(rows) <= 1:
        return pd.DataFrame(columns=HISTORY_CSV_COLUMNS)

    header = rows[0]
    data_rows = rows[1:]

    # Known historical layouts
    layout_17 = [
        "Administrative", "Administrative_Duration", "Informational", "Informational_Duration",
        "ProductRelated", "ProductRelated_Duration", "BounceRates", "ExitRates", "PageValues",
        "SpecialDay", "Month", "VisitorType", "Weekend", "Prediction", "Probability_0",
        "Probability_1", "Timestamp"
    ]
    layout_18 = [
        "Administrative", "Administrative_Duration", "Informational", "Informational_Duration",
        "ProductRelated", "ProductRelated_Duration", "BounceRates", "ExitRates", "PageValues",
        "SpecialDay", "Month", "VisitorType", "Weekend", "TrafficType", "Prediction", "Probability_0",
        "Probability_1", "Timestamp"
    ]

    normalized_rows = []
    for row in data_rows:
        if not row:
            continue
        row_dict = {}
        if len(row) == 17:
            row_dict = dict(zip(layout_17, row))
        elif len(row) == 18:
            row_dict = dict(zip(layout_18, row))
        elif len(row) == len(HISTORY_CSV_COLUMNS):
            row_dict = dict(zip(HISTORY_CSV_COLUMNS, row))
        else:
            # Fallback layout mapping
            if len(row) == len(header):
                row_dict = dict(zip(header, row))
            else:
                row_dict = dict(zip(HISTORY_CSV_COLUMNS, row))

        # Fill missing values with default or calculated metrics
        full_row = {}
        for col in HISTORY_CSV_COLUMNS:
            val = row_dict.get(col, "")
            if val == "" or val is None:
                if col == "Total_Duration":
                    try:
                        val = float(row_dict.get("Administrative_Duration", 0)) + \
                              float(row_dict.get("Informational_Duration", 0)) + \
                              float(row_dict.get("ProductRelated_Duration", 0))
                    except Exception:
                        val = ""
                elif col == "Engagement_Score":
                    try:
                        val = float(row_dict.get("PageValues", 0)) * float(row_dict.get("ProductRelated", 0))
                    except Exception:
                        val = ""
                elif col == "Bounce_Exit_Ratio":
                    try:
                        val = float(row_dict.get("BounceRates", 0)) / (float(row_dict.get("ExitRates", 0)) + 0.0001)
                    except Exception:
                        val = ""
                elif col == "Returning_Visitor_Flag":
                    try:
                        val = 1 if row_dict.get("VisitorType", "") == "Returning_Visitor" else 0
                    except Exception:
                        val = ""
                elif col in ["OperatingSystems", "Browser", "Region"]:
                    if col == "OperatingSystems":
                        val = "2"
                    elif col == "Browser":
                        val = "2"
                    elif col == "Region":
                        val = "1"
            full_row[col] = val
        normalized_rows.append(full_row)

    history_df = pd.DataFrame(normalized_rows, columns=HISTORY_CSV_COLUMNS)
    return history_df


def save_prediction_to_db(input_dict, prediction, probability):
    try:
        # SQLite Kaydı
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Ensure values are JSON serializable
        clean_inputs = {}
        for key, value in input_dict.items():
            if isinstance(value, list) and len(value) > 0:
                clean_inputs[key] = str(value[0])
            else:
                clean_inputs[key] = str(value)

        # Enforce default values for missing raw metrics
        if "OperatingSystems" not in clean_inputs:
            clean_inputs["OperatingSystems"] = "2"
        if "Browser" not in clean_inputs:
            clean_inputs["Browser"] = "2"
        if "Region" not in clean_inputs:
            clean_inputs["Region"] = "1"
            
        # Compute engineered features
        try:
            admin_dur = float(clean_inputs.get("Administrative_Duration", 0))
            info_dur = float(clean_inputs.get("Informational_Duration", 0))
            prod_dur = float(clean_inputs.get("ProductRelated_Duration", 0))
            clean_inputs["Total_Duration"] = str(admin_dur + info_dur + prod_dur)
        except Exception:
            clean_inputs["Total_Duration"] = "0.0"

        try:
            page_val = float(clean_inputs.get("PageValues", 0))
            prod_rel = float(clean_inputs.get("ProductRelated", 0))
            clean_inputs["Engagement_Score"] = str(page_val * prod_rel)
        except Exception:
            clean_inputs["Engagement_Score"] = "0.0"

        try:
            bounce = float(clean_inputs.get("BounceRates", 0))
            exit_r = float(clean_inputs.get("ExitRates", 0))
            clean_inputs["Bounce_Exit_Ratio"] = str(bounce / (exit_r + 0.0001))
        except Exception:
            clean_inputs["Bounce_Exit_Ratio"] = "0.0"

        clean_inputs["Returning_Visitor_Flag"] = "1" if clean_inputs.get("VisitorType", "") == "Returning_Visitor" else "0"

        inputs_json = json.dumps(clean_inputs)
        c.execute('''
            INSERT INTO history (inputs, prediction, probability_0, probability_1)
            VALUES (?, ?, ?, ?)
        ''', (inputs_json, int(prediction), float(probability[0]), float(probability[1])))
        conn.commit()
        conn.close()

        # CSV Kaydı
        csv_path = os.path.join(DB_FOLDER, "predictions.csv")
        import datetime
        flat_dict = clean_inputs.copy()
        flat_dict['Prediction'] = int(prediction)
        flat_dict['Probability_0'] = float(probability[0])
        flat_dict['Probability_1'] = float(probability[1])
        flat_dict['Timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # CSV'yi tek bir standart şema ile yeniden yazarak eski bozuk satırları da düzelt
        history_df = load_prediction_history_csv(csv_path)
        history_df = pd.concat([history_df, pd.DataFrame([flat_dict])], ignore_index=True, sort=False)
        history_df = history_df.reindex(columns=HISTORY_CSV_COLUMNS)
        history_df.to_csv(csv_path, index=False, encoding='utf-8')
            
    except Exception as e:
        print(f"Veriler kaydedilirken hata oluştu: {e}")

init_db()

# --- HCI & UI SETUP ---
st.set_page_config(
    page_title="Online Shoppers Revenue Prediction",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INJECT CUSTOM CSS ---
def inject_custom_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Poppins:wght@300;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif !important;
    }

    @keyframes glorious-glow {
        0% { box-shadow: 0 0 15px rgba(255, 215, 0, 0.4), 0 0 30px rgba(255, 105, 180, 0.2); border-color: rgba(255, 215, 0, 0.5); }
        50% { box-shadow: 0 0 25px rgba(255, 215, 0, 0.8), 0 0 50px rgba(255, 105, 180, 0.6); border-color: rgba(255, 105, 180, 0.8); }
        100% { box-shadow: 0 0 15px rgba(255, 215, 0, 0.4), 0 0 30px rgba(255, 105, 180, 0.2); border-color: rgba(255, 215, 0, 0.5); }
    }

    @keyframes text-breathe {
        0% { text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
        50% { text-shadow: 0 0 20px rgba(255, 215, 0, 0.8); }
        100% { text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
    }

    .breathing-title {
      animation: text-breathe 3s ease-in-out infinite;
      background: -webkit-linear-gradient(45deg, #FFD700, #FF69B4, #8A2BE2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-align: center;
      font-size: 3.5rem;
      font-weight: 800;
      margin-bottom: 1.5rem;
    }
    
    .story-text {
        font-size: 1.15rem;
        line-height: 1.7;
        padding: 25px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(49, 46, 129, 0.9));
        color: #F3F4F6 !important;
        border-left: 5px solid #FFD700;
        border-radius: 12px;
        animation: glorious-glow 4s infinite alternate;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
        color: #F9FAFB !important;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid rgba(255, 215, 0, 0.3);
        animation: glorious-glow 5s infinite alternate;
        text-align: center;
    }
    
    .metric-card h3, .metric-card h4, .metric-card h2 {
        color: #FFD700 !important;
    }

    .result-positive {
      background: linear-gradient(135deg, #14532D, #064E3B);
      color: #34D399;
      padding: 2.5rem;
      border-radius: 20px;
      text-align: center;
      border: 2px solid #34D399;
      animation: glorious-glow 3s infinite alternate;
    }
    
    .result-warning {
      background: linear-gradient(135deg, #F18F01, #E85D04);
      color: white;
      padding: 2rem;
      border-radius: 15px;
      text-align: center;
      border: 2px solid #F18F01;
      animation: glorious-glow 3s infinite alternate;
    }

    .result-danger {
      background: linear-gradient(135deg, #7F1D1D, #450A0A);
      color: #F87171;
      padding: 2.5rem;
      border-radius: 20px;
      text-align: center;
      border: 2px solid #F87171;
      animation: glorious-glow 3s infinite alternate;
    }

    @keyframes pulse-red-svg {
        0% { transform: scale(0.9); filter: drop-shadow(0 0 2px rgba(239, 68, 68, 0.7)); }
        70% { transform: scale(1.1); filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.9)); }
        100% { transform: scale(0.9); filter: drop-shadow(0 0 2px rgba(239, 68, 68, 0.7)); }
    }
    .red-warning-light-svg {
        display: inline-block;
        transform-origin: center;
        animation: pulse-red-svg 1.2s infinite;
        vertical-align: middle;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #FF69B4, #8A2BE2);
        color: white !important;
        font-weight: 800;
        border-radius: 10px;
        padding: 0.6rem 2.5rem;
        border: none;
        transition: all 0.3s ease;
        animation: glorious-glow 3s infinite alternate;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #8A2BE2, #FF69B4);
    }
    
    /* Vagonlar için Glorious Theme */
    .train-car {
        display: flex; 
        align-items: stretch; 
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); 
        border-radius: 12px; 
        overflow: hidden;
        border: 2px solid rgba(255, 105, 180, 0.4);
        animation: glorious-glow 4s infinite alternate;
        margin-bottom: 0px;
    }
    
    .train-car-content {
        padding: 20px; 
        color: #F3F4F6; 
        flex: 1;
    }
    
    .train-car h4 {
        color: #FFD700 !important; 
        font-size: 1.2rem;
        margin-top: 0;
        margin-bottom: 10px;
    }
    
    @keyframes siren-pulse {
        0% { box-shadow: inset 0 0 15px rgba(239, 68, 68, 0.1); }
        50% { box-shadow: inset 0 0 50px rgba(239, 68, 68, 0.65); }
        100% { box-shadow: inset 0 0 15px rgba(239, 68, 68, 0.1); }
    }
    .screen-warning-siren {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 999999;
        animation: siren-pulse 1.5s infinite ease-in-out;
    }
    
    @keyframes pulse-green {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
    }
    .live-pulse {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #34D399;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse-green 1.5s infinite;
        vertical-align: middle;
    }
    .live-stream-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 10px;
    }
    .live-visitor-card {
        flex: 1;
        min-width: 280px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.8));
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .live-visitor-card:hover {
        transform: translateY(-3px);
        border-color: rgba(52, 211, 153, 0.4);
        box-shadow: 0 6px 25px rgba(52, 211, 153, 0.15);
    }
    .live-visitor-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #34D399, #60A5FA);
    }
    .live-visitor-card.risk::before {
        background: linear-gradient(90deg, #F59E0B, #EF4444);
    }
    .live-visitor-card.danger::before {
        background: linear-gradient(90deg, #EF4444, #7F1D1D);
    }
    .visitor-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 10px;
        margin-bottom: 12px;
    }
    .visitor-id {
        font-family: 'Montserrat', sans-serif;
        font-weight: bold;
        color: #F3F4F6;
        font-size: 1.05rem;
    }
    .visitor-badge {
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 20px;
        font-weight: 600;
    }
    .badge-returning {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .badge-new {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .visitor-metrics {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        font-size: 0.9rem;
    }
    .metric-item {
        display: flex;
        flex-direction: column;
    }
    .metric-label {
        color: #9CA3AF;
        font-size: 0.75rem;
        margin-bottom: 2px;
    }
    .metric-val {
        color: #E5E7EB;
        font-weight: bold;
    }
    .visitor-prediction {
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px dashed rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .pred-status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }
    .step-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        transition: all 0.3s ease;
    }
    .step-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 215, 0, 0.5) !important;
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.1);
    }
    </style>
    
    <script>
    (function() {
      if (window.salescopeShortcutsInitialized) return;
      window.salescopeShortcutsInitialized = true;
      console.log("SaleScope Keyboard Shortcuts Initialized via Script Tag!");

      function clickRadio(keyword) {
        var labels = document.querySelectorAll('[data-testid="stSidebar"] [data-testid="stRadio"] label');
        for (var i = 0; i < labels.length; i++) {
          if (labels[i].innerText && labels[i].innerText.indexOf(keyword) > -1) {
              labels[i].click();
              break;
          }
        }
      }

      function doScroll(toBottom) {
        var mainContainer = document.querySelector('.main') || document.scrollingElement || window;
        if (toBottom) {
          if (mainContainer.scrollTo) mainContainer.scrollTo({ top: 99999, behavior: 'smooth' });
          else mainContainer.scrollTop = 99999;
        } else {
          if (mainContainer.scrollTo) mainContainer.scrollTo({ top: 0, behavior: 'smooth' });
          else mainContainer.scrollTop = 0;
        }
      }

      function handleKeydown(e) {
        var alt = e.altKey;
        var code = e.code; 

        if (alt && code === 'Digit1') { e.preventDefault(); e.stopPropagation(); clickRadio('Ana Sayfa'); }
        if (alt && code === 'Digit2') { e.preventDefault(); e.stopPropagation(); clickRadio('Tekil'); }
        if (alt && code === 'Digit3') { e.preventDefault(); e.stopPropagation(); clickRadio('Yönetici'); }

        if (alt && (code === 'Enter' || code === 'NumpadEnter')) {
          e.preventDefault(); e.stopPropagation();
          var btns = document.querySelectorAll('button[kind="primaryFormSubmit"], button[data-testid="baseButton-primaryFormSubmit"]');
          for (var i = 0; i < btns.length; i++) {
            if (btns[i].innerText && btns[i].innerText.indexOf('Analiz') > -1) { btns[i].click(); break; }
          }
        }

        if (alt && code === 'KeyR') {
          e.preventDefault(); e.stopPropagation();
          var btns = document.querySelectorAll('button');
          for (var i = 0; i < btns.length; i++) {
            if (btns[i].innerText && btns[i].innerText.indexOf('Temizle') > -1) { btns[i].click(); break; }
          }
        }

        if (alt && code === 'KeyT') {
          e.preventDefault(); e.stopPropagation();
          doScroll(false);
        }
        if (alt && code === 'KeyB') {
          e.preventDefault(); e.stopPropagation();
          doScroll(true);
        }
      }

      window.addEventListener('keydown', handleKeydown, true);
    })();
    </script>
    
    <img src="x" onerror="if(!window.salescopeShortcutsInitialized){
      window.salescopeShortcutsInitialized = true;
      console.log('SaleScope Keyboard Shortcuts Initialized via Image Tag!');
      var clickRadio = function(keyword) {
        var labels = document.querySelectorAll('[data-testid=&quot;stSidebar&quot;] [data-testid=&quot;stRadio&quot;] label');
        for (var i = 0; i < labels.length; i++) {
          if (labels[i].innerText && labels[i].innerText.indexOf(keyword) > -1) {
              labels[i].click();
              break;
          }
        }
      };
      var doScroll = function(toBottom) {
        var mainContainer = document.querySelector('.main') || document.scrollingElement || window;
        if (toBottom) {
          if (mainContainer.scrollTo) mainContainer.scrollTo({ top: 99999, behavior: 'smooth' });
          else mainContainer.scrollTop = 99999;
        } else {
          if (mainContainer.scrollTo) mainContainer.scrollTo({ top: 0, behavior: 'smooth' });
          else mainContainer.scrollTop = 0;
        }
      };
      var handleKeydown = function(e) {
        var alt = e.altKey;
        var code = e.code; 
        if (alt && code === 'Digit1') { e.preventDefault(); e.stopPropagation(); clickRadio('Ana Sayfa'); }
        if (alt && code === 'Digit2') { e.preventDefault(); e.stopPropagation(); clickRadio('Tekil'); }
        if (alt && code === 'Digit3') { e.preventDefault(); e.stopPropagation(); clickRadio('Yönetici'); }
        if (alt && (code === 'Enter' || code === 'NumpadEnter')) {
          e.preventDefault(); e.stopPropagation();
          var btns = document.querySelectorAll('button[kind=&quot;primaryFormSubmit&quot;], button[data-testid=&quot;baseButton-primaryFormSubmit&quot;]');
          for (var i = 0; i < btns.length; i++) {
            if (btns[i].innerText && btns[i].innerText.indexOf('Analiz') > -1) { btns[i].click(); break; }
          }
        }
        if (alt && code === 'KeyR') {
          e.preventDefault(); e.stopPropagation();
          var btns = document.querySelectorAll('button');
          for (var i = 0; i < btns.length; i++) {
            if (btns[i].innerText && btns[i].innerText.indexOf('Temizle') > -1) { btns[i].click(); break; }
          }
        }
        if (alt && code === 'KeyT') { e.preventDefault(); e.stopPropagation(); doScroll(false); }
        if (alt && code === 'KeyB') { e.preventDefault(); e.stopPropagation(); doScroll(true); }
      };
      window.addEventListener('keydown', handleKeydown, true);
    }" style="display:none;">
    """
    st.markdown(css, unsafe_allow_html=True)

inject_custom_css()



# --- MODEL LOADING & PIPELINE DEPENDENCIES ---
# Define this globally so joblib can find it!
month_map = {'Jan': 1, 'Feb':2, 'Mar':3, 'May':5, 'June':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
def encode_month(X_in):
    X_copy = X_in.copy()
    for c in X_copy.columns:
        X_copy[c] = X_copy[c].map(month_map).fillna(0)
    return X_copy

@st.cache_resource
def load_model_assets():
    model_path = Path("models/final_model.pkl")
    pipeline_path = Path("models/preprocessing_pipeline.pkl")
    threshold_path = Path("models/threshold_config.json")
    
    threshold = 0.50
    try:
        if threshold_path.exists():
            import json
            with open(threshold_path, 'r') as f:
                config = json.load(f)
                threshold = config.get("optimal_threshold", 0.50)
    except Exception:
        pass

    try:
        model = joblib.load(model_path)
        pipeline = joblib.load(pipeline_path)
        return model, pipeline, threshold
    except Exception as e:
        st.error(f"Model yüklenirken hata oluştu: {e}")
        return None, None, 0.50

model, pipeline, OPTIMAL_THRESHOLD = load_model_assets()

# --- HELPER FUNCTIONS ---
def prepare_input(df):
    """Applies phase 5 feature engineering before passing to pipeline."""
    df_new = df.copy()
    
    # Defaults for nominal variables missing from the prompt input list but needed by Pipeline
    if "OperatingSystems" not in df_new.columns: df_new["OperatingSystems"] = "2"
    if "Browser" not in df_new.columns: df_new["Browser"] = "2"
    if "Region" not in df_new.columns: df_new["Region"] = "1"
    if "TrafficType" not in df_new.columns: df_new["TrafficType"] = "2"

    for column in ["Month", "VisitorType", "OperatingSystems", "Browser", "Region", "TrafficType"]:
        if column in df_new.columns:
            df_new[column] = df_new[column].astype(str)
    
    # Feature Engineering logic from DATAPREP_HANDOFF_REPORT
    df_new["Total_Duration"] = df_new["Administrative_Duration"] + df_new["Informational_Duration"] + df_new["ProductRelated_Duration"]
    df_new["Engagement_Score"] = df_new["PageValues"] * df_new["ProductRelated"]
    df_new["Bounce_Exit_Ratio"] = df_new["BounceRates"] / (df_new["ExitRates"] + 0.0001)
    df_new["Returning_Visitor_Flag"] = (df_new["VisitorType"] == "Returning_Visitor").astype(int)
    
    # Drop columns that cause Multicollinearity
    if "BounceRates" in df_new.columns:
        df_new = df_new.drop(columns=["BounceRates"])
    if "ProductRelated_Duration" in df_new.columns:
        df_new = df_new.drop(columns=["ProductRelated_Duration"])
        
    return df_new

def render_prediction_card(prediction, probability=None):
    if probability is not None:
        confidence = float(np.max(probability)) * 100
    else:
        confidence = None

    if prediction == 1:
        pred_text = "Satın Alma Gerçekleşir (Revenue = True)"
        warning_light = ""
    else:
        pred_text = "Satın Alma Gerçekleşmez (Revenue = False)"
        warning_light = '<svg class="red-warning-light-svg" width="18" height="18" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="#EF4444" stroke="#FFFFFF" stroke-width="2" /></svg>'

    if confidence is None:
        card_class = "result-warning"
    elif prediction == 1 and confidence >= 75:
        card_class = "result-positive"
    elif prediction == 1:
        card_class = "result-positive"
    elif prediction == 0 and confidence < 70:
        card_class = "result-warning"
    else:
        card_class = "result-danger"

    st.markdown(
        f"""
        <div class="{card_class}">
            <h2 style="color: white; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; gap: 12px;">
                {warning_light} Tahmin: {pred_text} {warning_light}
            </h2>
            <h4 style="color: rgba(255,255,255,0.9);">Güven Skoru: %{confidence:.1f}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # HCI Principle: Bilgilendirici Geri Bildirim
    if prediction == 1:
        st.success(f"Bu kullanıcının satın alma profiline uygun davranışlar sergilediği tespit edilmiştir. Güven: %{confidence:.1f}")
    else:
        if confidence < 70:
            st.warning("Model kullanıcının satın alma yapmayacağını öngörüyor ancak kararsızlık payı var (False Negative riski olabilir).")
        else:
            st.error("Kullanıcının satın alma gerçekleştirmeden ayrılacağı tahmin ediliyor.")


# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 30px; margin-top: 10px;">
    <h1 style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 2.2rem; background: -webkit-linear-gradient(45deg, #FFD700, #FF69B4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;">SALESCOPE</h1>
    <p style="color: #A0AEC0; font-size: 0.95rem; font-family: 'Poppins', sans-serif; letter-spacing: 2px; margin-top: 0;">E-TİCARET ZEKASI</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<style>
/* Sidebar Radio Button Görkemli Yapı */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 12px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(15, 23, 42, 0.4) !important;
    padding: 12px 20px !important;
    border-radius: 12px !important;
    border-left: 4px solid transparent !important;
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(30, 41, 59, 0.9) !important;
    border-left: 4px solid #FF69B4 !important;
    transform: translateX(5px);
    box-shadow: 0 0 15px rgba(255, 105, 180, 0.3);
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radio"][aria-checked="true"] + div {
    color: #FFD700 !important;
    font-weight: 700 !important;
    font-family: 'Montserrat', sans-serif;
    font-size: 1.05rem !important;
}


</style>
""", unsafe_allow_html=True)

page_options = ["Ana Sayfa / Hikaye", "Tekil Tahmin", "Yönetici Özeti"]
page_icons = {
    "Ana Sayfa / Hikaye": "Ana Sayfa & Hikaye",
    "Tekil Tahmin": "Tekil Canlı Tahmin",
    "Yönetici Özeti": "Yönetici Özeti Paneli"
}
svg_nav = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px; margin-bottom: 4px; color: #8A2BE2;"><path d="M12 13v8"/><path d="M12 3v3"/><path d="M18.172 6a2 2 0 0 1 1.414.586l2.06 2.06a1.207 1.207 0 0 1 0 1.708l-2.06 2.06a2 2 0 0 1-1.414.586H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1z"/></svg>'
st.sidebar.markdown(f"<h3 style='color: #8A2BE2; font-family: Montserrat; font-size: 1.2rem; margin-bottom: -10px;'>{svg_nav} Navigasyon</h3>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigasyon Menüsü", page_options, format_func=lambda x: page_icons[x], label_visibility="collapsed")

st.sidebar.markdown("""
<style>
div[role="radiogroup"] label:nth-child(1) div[data-testid="stMarkdownContainer"] p::before {
    content: '';
    display: inline-block;
    width: 18px;
    height: 18px;
    margin-right: 6px;
    margin-bottom: -3px;
    background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNFMkU4RjAiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTUgMjF2LThhMSAxIDAgMCAwLTEtMWgtNGExIDEgMCAwIDAtMSAxdjgiLz48cGF0aCBkPSJNMyAxMGEyIDIgMCAwIDEgLjcwOS0xLjUyOGw3LTZhMiAyIDAgMCAxIDIuNTgyIDBsNyA2QTIgMiAwIDAgMSAyMSAxMHY5YTIgMiAwIDAgMS0yIDJINWEyIDIgMCAwIDEtMi0yeiIvPjwvc3ZnPg==') no-repeat center;
    background-size: contain;
}
div[role="radiogroup"] label:nth-child(2) div[data-testid="stMarkdownContainer"] p::before {
    content: '';
    display: inline-block;
    width: 18px;
    height: 18px;
    margin-right: 6px;
    margin-bottom: -3px;
    background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNFMkU4RjAiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTYuMjQ3IDcuNzYxYTYgNiAwIDAgMSAwIDguNDc4Ii8+PHBhdGggZD0iTTE5LjA3NSA0LjkzM2ExMCAxMCAwIDAgMSAwIDE0LjEzNCIvPjxwYXRoIGQ9Ik00LjkyNSAxOS4wNjdhMTAgMTAgMCAwIDEgMC0xNC4xMzQiLz48cGF0aCBkPSJNNy43NTMgMTYuMjM5YTYgNiAwIDAgMSAwLTguNDc4Ii8+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMiIvPjwvc3ZnPg==') no-repeat center;
    background-size: contain;
}
div[role="radiogroup"] label:nth-child(3) div[data-testid="stMarkdownContainer"] p::before {
    content: '';
    display: inline-block;
    width: 18px;
    height: 18px;
    margin-right: 6px;
    margin-bottom: -3px;
    background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNFMkU4RjAiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNNiAyMmEyIDIgMCAwIDEtMi0yVjRhMiAyIDAgMCAxIDItMmg4YTIuNCAyLjQgMCAwIDEgMS43MDQuNzA2bDMuNTg4IDMuNTg4QTIuNCAyLjQgMCAwIDEgMjAgOHYxMmEyIDIgMCAwIDEtMiAyeiIvPjxwYXRoIGQ9Ik0xNCAydjVhMSAxIDAgMCAwIDEgMWg1Ii8+PHBhdGggZD0iTTggMTh2LTIiLz48cGF0aCBkPSJNMTIgMTh2LTQiLz48cGF0aCBkPSJNMTYgMTh2LTYiLz48L3N2Zz4=') no-repeat center;
    background-size: contain;
}
</style>
""", unsafe_allow_html=True)



# Session State for prediction history/inputs
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None
if "last_probability" not in st.session_state:
    st.session_state.last_probability = None

# --- PAGE 1: ANA SAYFA ---
if page == "Ana Sayfa / Hikaye":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <h2 style="color: #FFD700; font-family: 'Montserrat', sans-serif; text-shadow: 0 0 10px rgba(255,215,0,0.4);">Neden SaleScope?</h2>
    </div>
    <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 35px;">
        <div style="flex: 1; min-width: 300px; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); padding: 25px; border-radius: 16px; border: 1px solid rgba(138, 43, 226, 0.4); box-shadow: 0 8px 32px rgba(0,0,0,0.2);">
            <h4 style="color: #FF69B4; font-family: 'Montserrat', sans-serif; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 5H3"/><path d="M10 12H3"/><path d="M10 19H3"/><circle cx="17" cy="15" r="3"/><path d="m21 19-1.9-1.9"/></svg>
                E-Ticaret Ziyaretçi Çıkmazı
            </h4>
            <p style="color: #E2E8F0; line-height: 1.65; font-size: 1rem; margin-bottom: 0;">
                Her gün binlerce kullanıcı e-ticaret sitenizi ziyaret ediyor. Bazıları sadece dolaşıyor, bazıları bilgi ediniyor, bazıları ise ürünleri dikkatlice inceliyor. Ancak günün sonunda asıl soru şu: <b style="color: #FFD700;">Kim sepetini onaylayıp satın alma yapacak?</b>
            </p>
        </div>
        <div style="flex: 1; min-width: 300px; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); padding: 25px; border-radius: 16px; border: 1px solid rgba(52, 211, 153, 0.4); box-shadow: 0 8px 32px rgba(0,0,0,0.2);">
            <h4 style="color: #34D399; font-family: 'Montserrat', sans-serif; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></svg>
                Makine Öğrenmesi ile Gelişmiş Tahmin
            </h4>
            <p style="color: #E2E8F0; line-height: 1.65; font-size: 1rem; margin-bottom: 0;">
                Bu proje, kullanıcıların oturum (session) içerisindeki dijital ayak izlerini analiz ederek, ziyaretin <b style="color: #34D399;">'Satın Alma' (Revenue)</b> ile sonuçlanıp sonuçlanmayacağını tahmin eden, Gradient Boosting Classifier mimarisi ile donatılmış gelişmiş bir yapay zeka asistanıdır.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    svg_album = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px; margin-bottom: 4px; color: #FFD700;"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><polyline points="11 3 11 11 14 8 17 11 17 3"/></svg>'
    st.markdown(f"### {svg_album} Kullanım Kılavuzu (How-to Guide)", unsafe_allow_html=True)
    st.markdown("""
<div style="display: flex; flex-direction: column; gap: 0;">
<!-- Vagon 1 -->
<div class="train-car">
<div style="padding: 20px; background: linear-gradient(135deg, #FF69B4, #8A2BE2); color: white; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: bold; width: 80px;">1</div>
<div class="train-car-content">
<h4>Uygulama Nasıl Kullanılır? (Adım Adım)</h4>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
    <!-- Step 1 -->
    <div class="step-card" style="border-top: 3px solid #FFD700;">
        <h5 style="color: #FFD700; margin-top: 0; margin-bottom: 8px; font-size: 1rem;">Adım 1: Navigasyon</h5>
        <p style="margin: 0; font-size: 0.85rem; line-height: 1.5; color: #E5E7EB;">Sol navigasyon menüsünü kullanarak <b>"Tekil Tahmin"</b> sayfasına geçiş yapın.</p>
    </div>
    <!-- Step 2 -->
    <div class="step-card" style="border-top: 3px solid #FF69B4;">
        <h5 style="color: #FF69B4; margin-top: 0; margin-bottom: 8px; font-size: 1rem;">Adım 2: Sayfa Verileri</h5>
        <p style="margin: 0; font-size: 0.85rem; line-height: 1.5; color: #E5E7EB;">Müşterinin hangi tür sayfalarda (Yönetim, Bilgi, Ürün) ne kadar süre geçirdiğini forma girin.</p>
    </div>
    <!-- Step 3 -->
    <div class="step-card" style="border-top: 3px solid #00BFFF;">
        <h5 style="color: #00BFFF; margin-top: 0; margin-bottom: 8px; font-size: 1rem;">Adım 3: Etkileşim</h5>
        <p style="margin: 0; font-size: 0.85rem; line-height: 1.5; color: #E5E7EB;">Google Analytics'ten alınan Çıkış Oranı (Exit Rate) ve Sayfa Değeri (Page Value) gibi metrikleri ekleyin.</p>
    </div>
    <!-- Step 4 -->
    <div class="step-card" style="border-top: 3px solid #8A2BE2;">
        <h5 style="color: #8A2BE2; margin-top: 0; margin-bottom: 8px; font-size: 1rem;">Adım 4: Ziyaret Bağlamı</h5>
        <p style="margin: 0; font-size: 0.85rem; line-height: 1.5; color: #E5E7EB;">Ziyaretçi tipi, ziyaretin hangi ayda olduğu ve özel günlere yakınlık gibi çevresel verileri seçin.</p>
    </div>
    <!-- Step 5 -->
    <div class="step-card" style="border-top: 3px solid #FF4500;">
        <h5 style="color: #FF4500; margin-top: 0; margin-bottom: 8px; font-size: 1rem;">Adım 5: YZ Analizi</h5>
        <p style="margin: 0; font-size: 0.85rem; line-height: 1.5; color: #E5E7EB;">Tüm formu doldurduktan sonra <b>"Analiz Et"</b> butonuna basarak gelişmiş modelimizi tetikleyin.</p>
    </div>
    <!-- Step 6 -->
    <div class="step-card" style="border-top: 3px solid #34D399;">
        <h5 style="color: #34D399; margin-top: 0; margin-bottom: 8px; font-size: 1rem;">Adım 6: Karar & Aksiyon</h5>
        <p style="margin: 0; font-size: 0.85rem; line-height: 1.5; color: #E5E7EB;">Satın alma tahminine ve güven skoruna göre o müşteriye anlık fırsat veya hatırlatıcı sunun.</p>
    </div>
</div>
</div>
</div>

<!-- Bağlantı -->
<div style="width: 6px; height: 25px; background: #FFD700; margin-left: 37px; box-shadow: 0 0 10px rgba(255,215,0,0.8);"></div>

<!-- Vagon 2 -->
<div class="train-car">
<div style="padding: 20px; background: linear-gradient(135deg, #8A2BE2, #FFD700); color: white; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: bold; width: 80px;">2</div>
<div class="train-car-content">
<h4>Metrikler Nereden Elde Edilir?</h4>
<p style="margin: 0; font-size: 0.95rem;">Formdaki tüm veriler, sitenizin arka planında çalışan <b>Google Analytics</b> vb. web izleme toollarından gerçek zamanlı oturum (session) datası olarak otomatik çekilerek uygulamaya beslenir.</p>
</div>
</div>
</div>
    """, unsafe_allow_html=True)
    



    
# --- PAGE 2: TEKİL TAHMİN ---
elif page == "Tekil Tahmin":
    st.markdown('<div class="breathing-title">Canlı Tahmin Paneli</div>', unsafe_allow_html=True)
    st.markdown("Lütfen kullanıcının davranışsal verilerini aşağıya giriniz. Model, anında *Satın Alma* ihtimalini hesaplayacaktır.")

    # ── Tek kaynak: base değerler ──────────────────────────────────────────────
    FORM_DEFAULTS = {
        "f_admin":     0,
        "f_admin_dur": 0.0,
        "f_info":      0,
        "f_info_dur":  0.0,
        "f_prod":      0,
        "f_prod_dur":  0.0,
        "f_bounce":    0.0,
        "f_exit":      0.0,
        "f_page":      0.0,
        "f_month":     None,
        "f_spec":      None,
        "f_vis":       None,
        "f_week":      None,
    }

    # İlk yüklemede session_state'i base değerlere ayarla
    for _k, _v in FORM_DEFAULTS.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    def clear_form_callback():
        for _k, _v in FORM_DEFAULTS.items():
            st.session_state[_k] = _v
        st.session_state.last_prediction = None
        st.session_state.last_probability = None
        st.session_state.last_update_time = None
        st.session_state.show_confetti = False
        st.toast("Tüm form verileri başarıyla temizlendi ve sıfırlandı!", icon="🧹")

    with st.form("prediction_form"):
        st.subheader("Kullanıcı Davranış Metrikleri")
        
        st.markdown('<h4 style="color: #FFD700; border-bottom: 1px solid rgba(255,215,0,0.3); padding-bottom: 5px; display: flex; align-items: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-text-search-icon lucide-text-search"><path d="M21 5H3"/><path d="M10 12H3"/><path d="M10 19H3"/><circle cx="17" cy="15" r="3"/><path d="m21 19-1.9-1.9"/></svg> Sayfa Gezinme İstatistikleri</h4>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            administrative = st.number_input("Yönetimsel Sayfalar (Administrative)", min_value=0, step=1, key="f_admin", help="Kullanıcının hesap yönetimi, sepet vb. sayfaları ziyaret sayısı")
            admin_duration = st.number_input("Yönetimsel Sayfada Geçen Süre (Administrative Duration)", min_value=0.0, key="f_admin_dur", help="Yönetimsel sayfalarda saniye cinsinden geçirilen süre")
        with c2:
            informational = st.number_input("Bilgilendirici Sayfalar (Informational)", min_value=0, step=1, key="f_info", help="İletişim, hakkımızda gibi bilgi veren sayfaları ziyaret sayısı")
            info_duration = st.number_input("Bilgi Sayfasında Geçen Süre (Informational Duration)", min_value=0.0, key="f_info_dur", help="Bilgilendirici sayfalarda saniye cinsinden geçirilen süre")
        with c3:
            product_related = st.number_input("Ürün İnceleme Sayfası (Product Related)", min_value=0, step=1, key="f_prod", help="Kullanıcının sitede incelediği toplam ürün sayısı")
            product_duration = st.number_input("Ürün Sayfasında Geçen Süre (Product Related Duration)", min_value=0.0, key="f_prod_dur", help="Ürün inceleme sayfalarında saniye cinsinden geçirilen toplam süre")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h4 style="color: #FF69B4; border-bottom: 1px solid rgba(255,105,180,0.3); padding-bottom: 5px; display: flex; align-items: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-no-axes-combined-icon lucide-chart-no-axes-combined"><path d="M12 16v5"/><path d="M16 14.639V21"/><path d="M20 10.656V21"/><path d="m22 3-8.646 8.646a.5.5 0 0 1-.708 0L9.354 8.354a.5.5 0 0 0-.707 0L2 15"/><path d="M4 18.463V21"/><path d="M8 14.656V21"/></svg> Etkileşim ve Analitik Metrikleri</h4>', unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4:
            bounce_rates = st.number_input("Hemen Çıkma Oranı (Bounce Rates)", min_value=0.0, max_value=0.2, step=0.01, key="f_bounce", help="Siteye girip hiçbir işlem yapmadan ayrılan kullanıcıların Google Analytics oranı")
        with c5:
            exit_rates = st.number_input("Siteden Çıkış Oranı (Exit Rates)", min_value=0.0, max_value=0.2, step=0.01, key="f_exit", help="Kullanıcıların bu sayfadan veya sayfa grubundan çıkış yapma oranı")
        with c6:
            page_values = st.number_input("Sayfa Değeri (Page Values)", min_value=0.0, key="f_page", help="Kullanıcının ziyaret ettiği sayfaların ortalama e-ticaret değeri")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h4 style="color: #8A2BE2; border-bottom: 1px solid rgba(138,43,226,0.3); padding-bottom: 5px; display: flex; align-items: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-eye-icon lucide-eye"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg> Ziyaret Bağlamı ve Özellikleri</h4>', unsafe_allow_html=True)
        
        tr_special_day = {0.0: "Standart Dönem (0)", 0.2: "Sezon Başlangıcı (0.2)", 0.4: "Kampanya Hazırlığı (0.4)", 0.6: "Aktif Kampanya Süreci (0.6)", 0.8: "Yoğun İndirim Süreci (0.8)", 1.0: "Özel Gün Trafiği (1)"}
        tr_months = {'Jan': 'Ocak', 'Feb': 'Şubat', 'Mar': 'Mart', 'May': 'Mayıs', 'June': 'Haziran', 'Jul': 'Temmuz', 'Aug': 'Ağustos', 'Sep': 'Eylül', 'Oct': 'Ekim', 'Nov': 'Kasım', 'Dec': 'Aralık'}
        tr_visitor = {"Returning_Visitor": "Geri Dönen Ziyaretçi", "New_Visitor": "Yeni Ziyaretçi", "Other": "Diğer"}
        tr_weekend = {True: "Evet", False: "Hayır"}
        tr_traffic = {1: "Organic (Google, Bing)", 2: "Direct (Doğrudan URL)", 3: "Referral (Diğer Sitelerden)", 4: "Social Media (Sosyal Ağlardan)", 5: "Paid Search (Ücretli Arama)"}
        
        c7, c8 = st.columns(2)
        with c7:
            month = st.selectbox("Ziyaret Ayı (Month)", options=list(tr_months.keys()), format_func=lambda x: tr_months[x], index=None, placeholder="Seçenek Seçin", key="f_month", help="Ziyaretin gerçekleştiği yılın ayı")
            special_day = st.selectbox("Özel Gün Yakınlığı (Special Day)", options=list(tr_special_day.keys()), format_func=lambda x: tr_special_day[x], index=None, placeholder="Seçenek Seçin", key="f_spec", help="Ziyaret tarihinin sevgililer günü, anneler günü gibi özel günlere yakınlığı")
            traffic_type = st.selectbox("Trafik Kaynağı (Traffic Type)", options=list(tr_traffic.keys()), format_func=lambda x: tr_traffic[x], index=None, placeholder="Seçenek Seçin", key="f_traffic", help="Kullanıcının siteden nereden geldiği bilgisi")
        with c8:
            visitor_type = st.selectbox("Ziyaretçi Tipi (Visitor Type)", options=list(tr_visitor.keys()), format_func=lambda x: tr_visitor[x], index=None, placeholder="Seçenek Seçin", key="f_vis", help="Kullanıcının siteye ilk kez mi yoksa daha önce de mi geldiği bilgisi")
            weekend = st.selectbox("Hafta Sonu (Weekend)", options=list(tr_weekend.keys()), format_func=lambda x: tr_weekend[x], index=None, placeholder="Seçenek Seçin", key="f_week", help="Ziyaretin hafta sonu mu yoksa hafta içi mi yapıldığı")
        
        # 🤖 Otomatik Hesaplanan Feature'lar
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h4 style="color: #34D399; border-bottom: 1px solid rgba(52,211,153,0.3); padding-bottom: 5px; display: flex; align-items: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-cpu"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="4" height="4" x="9" y="9" rx="1"/><path d="M7 6V4M7 20v-2M17 6V4M17 20v-2M4 13H2M4 7H2M20 13h2M20 7h2"/></svg> Yapay Zeka Tarafından Hesaplanan Özellikler</h4>', unsafe_allow_html=True)
        
        # Otomatik hesaplamaları gerçekleştir
        total_duration_auto = admin_duration + info_duration + product_duration
        engagement_score_auto = page_values * product_related if product_related > 0 else 0
        bounce_exit_ratio_auto = bounce_rates / (exit_rates + 0.0001) if exit_rates > 0 else bounce_rates
        
        ai_c1, ai_c2, ai_c3 = st.columns(3)
        with ai_c1:
            st.metric("Toplam Ziyaret Süresi", f"{total_duration_auto:.1f}s", help="Admin + Info + Ürün sayfası sürelerinin toplamı")
        with ai_c2:
            st.metric("Katılım Skoru", f"{engagement_score_auto:.2f}", help="Sayfa Değeri × Ürün Sayısı")
        with ai_c3:
            st.metric("Çıkış Dengesi", f"{bounce_exit_ratio_auto:.3f}", help="Hemen Çıkış / Site Çıkışı Oranı")
            
        st.markdown("<br>", unsafe_allow_html=True)
        btn_c1, _, btn_c2 = st.columns([3, 4, 3])
        with btn_c1:
            submit = st.form_submit_button("Analiz Et", use_container_width=True, type="primary")
        with btn_c2:
            clear_btn = st.form_submit_button("Formu Temizle", on_click=clear_form_callback, use_container_width=True, type="primary")


    if submit:
        # Selectbox'ların seçilip seçilmediğini kontrol et
        if month is None or special_day is None or visitor_type is None or weekend is None or traffic_type is None:
            st.error("⚠️ Lütfen tüm sayısal olmayan metrikleri (Ay, Özel Gün, Trafik Kaynağı, Ziyaretçi Tipi, Hafta Sonu) seçiniz!")
        elif model is None or pipeline is None:
            st.error("Model yüklenemediği için tahmin yapılamıyor!")
        else:
            import time
            st.toast("Yapay Zeka Modeli verileri işliyor...", icon="🧠")
            # Prepare Input DataFrame
            input_dict = {
                "Administrative": [administrative],
                "Administrative_Duration": [admin_duration],
                "Informational": [informational],
                "Informational_Duration": [info_duration],
                "ProductRelated": [product_related],
                "ProductRelated_Duration": [product_duration],
                "BounceRates": [bounce_rates],
                "ExitRates": [exit_rates],
                "PageValues": [page_values],
                "SpecialDay": [special_day],
                "Month": [month],
                "VisitorType": [visitor_type],
                "Weekend": [int(weekend)],
                "TrafficType": [traffic_type]
            }
            
            raw_df = pd.DataFrame(input_dict)
            
            with st.spinner('Derin Öğrenme Ağları ve Karar Ağaçları Sentezleniyor...'):
                time.sleep(0.7) # Simüle edilmiş gecikme ile UX/UI güven hissi oluşturulur
                processed_df = prepare_input(raw_df)
                
                try:
                    pipeline_out = pipeline.transform(processed_df)
                    probability = model.predict_proba(pipeline_out)[0]
                    prediction = 1 if probability[1] >= OPTIMAL_THRESHOLD else 0
                    
                    st.session_state.last_prediction = prediction
                    st.session_state.last_probability = probability
                    st.session_state.last_update_time = time.strftime('%H:%M:%S')
                    st.session_state.show_confetti = (prediction == 1)
                    st.toast("Model analizi tamamlandı! Sonuçlar ekrana yansıtılıyor...", icon="🎯")
                    
                    # Veritabanına analiz geçmişini kaydet
                    save_prediction_to_db(input_dict, prediction, probability)
                    
                except Exception as e:
                    st.error(f"Tahmin sırasında hata: {e}")
                    
    # Sonuç Gösterimi
    if st.session_state.last_prediction is not None:
        if st.session_state.get("show_confetti", False):
            import time
            unique_id = time.time()
            components.html(
                f"""
                <script>
                    // Benzersiz ID: {unique_id}
                    const parentWindow = window.parent;
                    const parentDoc = parentWindow.document;
                    if (!parentWindow.confetti) {{
                        let script = parentDoc.createElement('script');
                        script.src = "https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js";
                        script.onload = function() {{ fireConfetti(); }};
                        parentDoc.head.appendChild(script);
                    }} else {{
                        fireConfetti();
                    }}
                    function fireConfetti() {{
                        var duration = 3000;
                        var end = Date.now() + duration;
                        (function frame() {{
                          parentWindow.confetti({{ particleCount: 8, angle: 60, spread: 55, origin: {{ x: 0, y: 1 }}, colors: ['#FFD700', '#FF69B4', '#8A2BE2', '#34D399', '#60A5FA'], zIndex: 99999 }});
                          parentWindow.confetti({{ particleCount: 8, angle: 120, spread: 55, origin: {{ x: 1, y: 1 }}, colors: ['#FFD700', '#FF69B4', '#8A2BE2', '#34D399', '#60A5FA'], zIndex: 99999 }});
                          if (Date.now() < end) {{ requestAnimationFrame(frame); }}
                        }}());
                    }}
                </script>
                """,
                height=0, width=0,
            )
            st.session_state.show_confetti = False
            
        if st.session_state.last_prediction == 0:
            st.markdown(
                """
                <div class="screen-warning-siren"></div>
                """,
                unsafe_allow_html=True
            )
            
        st.markdown("---")
        chart_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-no-axes-combined-icon lucide-chart-no-axes-combined"><path d="M12 16v5"/><path d="M16 14.639V21"/><path d="M20 10.656V21"/><path d="m22 3-8.646 8.646a.5.5 0 0 1-.708 0L9.354 8.354a.5.5 0 0 0-.707 0L2 15"/><path d="M4 18.463V21"/><path d="M8 14.656V21"/></svg>'
        st.markdown(f'<h3 style="display: flex; align-items: center; gap: 8px;">{chart_svg} Analiz Sonucu</h3>', unsafe_allow_html=True)
        if "last_update_time" in st.session_state and st.session_state.last_update_time:
            clock_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clock-check-icon lucide-clock-check"><path d="M12 6v6l4 2"/><path d="M22 12a10 10 0 1 0-11 9.95"/><path d="m22 16-5.5 5.5L14 19"/></svg>'
            st.markdown(f'<div style="color: #A0AEC0; font-size: 0.875rem; display: flex; align-items: center; gap: 6px; margin-bottom: 1rem;">{clock_svg} <span><b>Son Güncelleme:</b> Model yeni metrikler ile <i>{st.session_state.last_update_time}</i> saatinde yeniden hesaplandı.</span></div>', unsafe_allow_html=True)
        render_prediction_card(st.session_state.last_prediction, st.session_state.last_probability)
        
        # Ek Açıklama Paneli (HCI: Bilişsel yükü azaltmak için genişletilebilir panel)
        import base64
        package_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFD700" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><polyline points="3.29 7 12 12 20.71 7"/><path d="m7.5 4.27 9 5.15"/></svg>'
        package_b64 = base64.b64encode(package_svg.encode('utf-8')).decode('utf-8')
        
        st.markdown(f"""
        <style>
        div[data-testid="stExpander"] summary p::before {{
            content: '';
            display: inline-block;
            width: 22px;
            height: 22px;
            margin-right: 8px;
            margin-bottom: -4px;
            background: url('data:image/svg+xml;base64,{package_b64}') no-repeat center;
            background-size: contain;
        }}
        </style>
        """ + """
        <style>
        div[data-testid="stExpander"] {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)) !important;
            border: 2px solid rgba(138, 43, 226, 0.5) !important;
            border-radius: 15px !important;
            box-shadow: 0 0 20px rgba(138, 43, 226, 0.2) !important;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        div[data-testid="stExpander"]:hover {
            border-color: rgba(255, 105, 180, 0.8) !important;
            box-shadow: 0 0 25px rgba(255, 105, 180, 0.4) !important;
        }
        div[data-testid="stExpander"] summary p {
            font-family: 'Montserrat', sans-serif !important;
            color: #FFD700 !important;
            font-size: 1.15rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="stExpander"] svg {
            color: #FFD700 !important;
        }
        .expander-box {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #8A2BE2;
            margin-bottom: 10px;
        }
        .expander-box h4 {
            color: #FF69B4;
            margin-top: 0;
            font-family: 'Montserrat', sans-serif;
            font-size: 1.1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 8px;
            margin-bottom: 12px;
        }
        .expander-box ul {
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }
        .expander-box li {
            margin-bottom: 12px;
            font-size: 0.95rem;
            color: #F3F4F6;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        .expander-val {
            color: #FFD700;
            font-weight: bold;
            font-family: monospace;
            font-size: 1.05rem;
            background: rgba(255,215,0,0.1);
            padding: 4px 10px;
            border-radius: 6px;
            text-align: right;
            flex-shrink: 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.expander("Model Bilgileri & Sistem Detayları"):
            m1, m2 = st.columns(2)
            with m1:
                decision = 'Satın Alır (1)' if st.session_state.last_prediction == 1 else 'Satın Almaz (0)'
                st.markdown(f"""
                <div class="expander-box">
                    <h4 style="display: flex; align-items: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-column-decreasing-icon lucide-chart-column-decreasing"><path d="M13 17V9"/><path d="M18 17v-3"/><path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M8 17V5"/></svg> Tahmin İstatistikleri</h4>
                    <ul>
                        <li>Sınıflandırma Kararı: <span class="expander-val">{decision}</span></li>
                        <li>Satın Alma İhtimali: <span class="expander-val">%{st.session_state.last_probability[1]*100:.2f}</span></li>
                        <li>Sayfayı Terk Etme İhtimali: <span class="expander-val">%{st.session_state.last_probability[0]*100:.2f}</span></li>
                        <li>Model Güven Skoru: <span class="expander-val">%{max(st.session_state.last_probability)*100:.2f}</span></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown("""
                <div class="expander-box" style="border-left-color: #FF69B4;">
                    <h4 style="color: #8A2BE2; display: flex; align-items: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-cog-icon lucide-cog"><path d="M11 10.27 7 3.34"/><path d="m11 13.73-4 6.93"/><path d="M12 22v-2"/><path d="M12 2v2"/><path d="M14 12h8"/><path d="m17 20.66-1-1.73"/><path d="m17 3.34-1 1.73"/><path d="M2 12h2"/><path d="m20.66 17-1.73-1"/><path d="m20.66 7-1.73 1"/><path d="m3.34 17 1.73-1"/><path d="m3.34 7 1.73 1"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="12" r="8"/></svg> Altyapı & Mimarisi</h4>
                    <ul>
                        <li>Seçilen Model: <span class="expander-val">Gradient Boosting</span></li>
                        <li>Veri Dönüşümü: <span class="expander-val">MinMax & Encoding</span></li>
                        <li>Sınıf Dengeleme: <span class="expander-val">SMOTE</span></li>
                        <li>Karar Sınırı (Threshold): <span class="expander-val">{0.35}</span></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        # Stratejik Öneriler Paneli
        def render_strategy_card(title, icon, desc, action, gradient, border_color):
            st.markdown(f"""
            <div style="
                background: {gradient};
                padding: 30px;
                border-radius: 15px;
                border: 2px solid {border_color};
                box-shadow: 0 0 25px {border_color}40;
                color: #FFFFFF;
                margin-top: 20px;
                margin-bottom: 25px;
                animation: glorious-glow 4s infinite alternate;
            ">
                <h3 style="color: {border_color}; margin-top:0; font-family: 'Montserrat', sans-serif; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 2rem;">{icon}</span> {title}
                </h3>
                <p style="font-size: 1.15rem; line-height: 1.6; margin-bottom: 20px;">{desc}</p>
                <div style="background: rgba(0,0,0,0.35); padding: 20px; border-radius: 10px; border-left: 5px solid {border_color};">
                    <strong style="font-size: 1.1rem; color: #FFD700; display: inline-flex; align-items: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-rocket-icon lucide-rocket"><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09"/><path d="M9 12a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.4 22.4 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 .05 5 .05"/></svg> TAVSİYE EDİLEN AKSİYON PLANLAMASI:</strong><br><br>
                    <span style="font-size: 1.05rem; letter-spacing: 0.5px;">{action}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        target_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-target-icon lucide-target"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
        st.markdown(f'<h3 style="color: #FFD700; display: flex; align-items: center; justify-content: center; gap: 10px; font-family: Montserrat; text-shadow: 0 0 10px rgba(255,215,0,0.4);">{target_svg} Kişiselleştirilmiş Stratejik Öneriler</h3>', unsafe_allow_html=True)
        
        if st.session_state.last_prediction == 1 and st.session_state.last_probability[1] < 0.7:
            render_strategy_card(
                "Risk Analizi (Sınırda Dönüşüm)", "⚠️",
                f"Sistem, kullanıcının satın alma ihtimalini eşiğe yakın bir değer olan <b>%{st.session_state.last_probability[1]*100:.1f}</b> ile pozitif değerlendirmiştir. Ancak güven skoru kritik sınırın altındadır. Kullanıcı sepeti terk etme eğiliminde olabilir.",
                "Kısa süreli bir 'Sepette %5 İndirim' veya 'Hızlı Teslimat' vurgusu barındıran dikkat çekici bir pop-up ile kullanıcıyı anında ödeme adımına teşvik edin.",
                "linear-gradient(135deg, rgba(245, 158, 11, 0.85), rgba(180, 83, 9, 0.95))",
                "#FCD34D"
            )
        elif st.session_state.last_prediction == 0 and st.session_state.last_probability[0] < 0.7:
            render_strategy_card(
                "Geri Kazanım Stratejisi (Kaçan Fırsat)", "💡",
                f"Kullanıcının satın alma ihtimali <b>%{st.session_state.last_probability[1]*100:.1f}</b> gibi sınırda bir değerle reddedilmiştir. Bu müşteri, kaybedilmek üzere olan çok sıcak bir potansiyeldir.",
                "Kullanıcının çıkış niyetini (exit intent) algılayan bir pop-up tetikleyin. Özel bir indirim kodu veya 'Kargo Bedava' fırsatı sunarak müşteriyi derhal satın alma döngüsüne geri çekin.",
                "linear-gradient(135deg, rgba(59, 130, 246, 0.85), rgba(30, 58, 138, 0.95))",
                "#93C5FD"
            )
        elif st.session_state.last_prediction == 1 and st.session_state.last_probability[1] >= 0.7:
            render_strategy_card(
                "Yüksek Dönüşüm Potansiyeli", "✅",
                f"Kullanıcının profili çok güçlü ve satın alma ihtimali oldukça yüksek (<b>%{st.session_state.last_probability[1]*100:.1f}</b>). Herhangi bir dış müdahaleye ihtiyaç duymadan ödemeye gitmesi bekleniyor.",
                "Dikkat dağıtıcı hiçbir kampanya, pop-up veya çapraz satış göstermeyin. Yalnızca ödeme adımının pürüzsüz olduğundan emin olun. İşlem sonrasında sadakat (Loyalty) programına davet edebilirsiniz.",
                "linear-gradient(135deg, rgba(16, 185, 129, 0.85), rgba(6, 78, 59, 0.95))",
                "#6EE7B7"
            )
        else:
            chart_network_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chart-network-icon lucide-chart-network"><path d="m13.11 7.664 1.78 2.672"/><path d="m14.162 12.788-3.324 1.424"/><path d="m20 4-6.06 1.515"/><path d="M3 3v16a2 2 0 0 0 2 2h16"/><circle cx="12" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="9" cy="15" r="2"/></svg>'
            render_strategy_card(
                "Düşük İlgi Seviyesi (Soğuk Trafik)", chart_network_svg,
                f"Kullanıcının satın alma niyeti çok zayıf (İhtimal: <b>%{st.session_state.last_probability[1]*100:.1f}</b>). Ziyaretçi yüksek ihtimalle sadece bilgi arıyor veya fiyat karşılaştırıyor.",
                "Ziyaretçiyi agresif bir şekilde satın almaya zorlamak yerine markaya alıştırın. Bülten aboneliğine (newsletter) yönlendirin veya 'İlginizi Çekebilecek Diğer Ürünler' gibi keşif (exploration) içeriklerine kanalize edin.",
                "linear-gradient(135deg, rgba(239, 68, 68, 0.85), rgba(153, 27, 27, 0.95))",
                "#FCA5A5"
            )

# --- PAGE 3: YÖNETİCİ ÖZETİ ---
elif page == "Yönetici Özeti":
    st.markdown('<div class="breathing-title">Yönetici Özeti</div>', unsafe_allow_html=True)
    
    # ⚡ Canlı Oturum Akışı (Real-time Session Feed)
    st.markdown("""
    <div class="dash-card" style="margin-bottom: 0px; padding-bottom: 5px;">
        <h3><span class="live-pulse"></span> Canlı Oturum Akışı</h3>
        <p style="color: #A0AEC0; margin-bottom: 10px; font-size: 0.95rem;">
            E-ticaret platformuna şu anda giren aktif ziyaretçilerin gerçek zamanlı oturum metrikleri. Veriler dinamik olarak akmaktadır.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    live_feed_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Poppins:wght@300;500;700&display=swap');
            
            body {
                margin: 0;
                padding: 0 10px;
                background: transparent;
                font-family: 'Poppins', sans-serif;
                color: #F9FAFB;
                overflow: hidden;
            }
            
            .stream-container {
                display: flex;
                flex-direction: column;
                gap: 12px;
                max-height: 480px;
                overflow: hidden;
                padding-top: 5px;
            }
            
            .live-visitor-card {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px 20px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                position: relative;
                overflow: hidden;
                opacity: 1;
                transform: translateY(0) scale(1);
            }
            
            .live-visitor-card.new-item {
                opacity: 0;
                transform: translateY(-30px) scale(0.95);
                max-height: 0;
                padding-top: 0;
                padding-bottom: 0;
                margin-bottom: -12px;
                border-color: rgba(52, 211, 153, 0.6);
            }
            
            .live-visitor-card:hover {
                transform: translateY(-2px);
                border-color: rgba(255, 215, 0, 0.4);
                box-shadow: 0 6px 25px rgba(255, 215, 0, 0.1);
            }
            
            .live-visitor-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: linear-gradient(90deg, #FFD700, #8A2BE2);
            }
            
            .visitor-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                padding-bottom: 8px;
                margin-bottom: 10px;
            }
            
            .visitor-id {
                font-family: 'Montserrat', sans-serif;
                font-weight: 700;
                color: #F3F4F6;
                font-size: 1rem;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .visitor-badge {
                font-size: 0.75rem;
                padding: 3px 10px;
                border-radius: 20px;
                font-weight: 600;
            }
            
            .badge-returning {
                background-color: rgba(59, 130, 246, 0.15);
                color: #60A5FA;
                border: 1px solid rgba(59, 130, 246, 0.3);
            }
            
            .badge-new {
                background-color: rgba(16, 185, 129, 0.15);
                color: #34D399;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }
            
            .visitor-metrics {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 15px;
                font-size: 0.9rem;
                flex-wrap: nowrap;
            }
            
            .metric-item {
                display: flex;
                flex-direction: column;
                flex: 1;
                min-width: 80px;
            }
            
            .metric-label {
                color: #A0AEC0;
                font-size: 0.75rem;
                margin-bottom: 3px;
                white-space: nowrap;
            }
            
            .metric-val {
                color: #E2E8F0;
                font-weight: 600;
                font-family: 'Montserrat', sans-serif;
            }
            
            .stream-time {
                color: #A0AEC0;
                font-size: 0.75rem;
            }
        </style>
    </head>
    <body>
        <div class="stream-container" id="stream-container"></div>
        
        <script>
            const visitorTypes = ["Geri Dönen Ziyaretçi", "Yeni Ziyaretçi"];
            const months = ["Ocak", "Şubat", "Mart", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
            const specialDays = ["Hayır", "Hayır", "Hayır", "Hayır", "Evet"];
            
            function generateRandomVisitor() {
                const id = Math.floor(1000 + Math.random() * 9000);
                const type = visitorTypes[Math.random() < 0.75 ? 0 : 1];
                const pageVal = (Math.random() < 0.3 ? 0.00 : (Math.random() * 110).toFixed(2));
                const exitRate = (Math.random() * 0.05).toFixed(3);
                const prodDuration = Math.floor(Math.random() * 500);
                const month = months[Math.floor(Math.random() * months.length)];
                const specDay = specialDays[Math.floor(Math.random() * specialDays.length)];
                
                const now = new Date();
                const timeStr = now.toTimeString().split(' ')[0];
                
                return {
                    id, type, pageVal, exitRate: (exitRate * 100).toFixed(1), prodDuration, month, specDay, timeStr
                };
            }
            
            function addVisitorToFeed(isInitial = false) {
                const v = generateRandomVisitor();
                const container = document.getElementById("stream-container");
                
                const card = document.createElement("div");
                card.className = "live-visitor-card" + (isInitial ? "" : " new-item");
                
                const badgeClass = v.type === "Geri Dönen Ziyaretçi" ? "badge-returning" : "badge-new";
                
                card.innerHTML = `
                    <div class="visitor-header">
                        <span class="visitor-id">👤 Oturum #${v.id} <span class="visitor-badge ${badgeClass}">${v.type}</span></span>
                        <span class="stream-time">⏱️ ${v.timeStr}</span>
                    </div>
                    <div class="visitor-metrics">
                        <div class="metric-item">
                            <span class="metric-label">Sayfa Değeri</span>
                            <span class="metric-val">${v.pageVal}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Çıkış Oranı</span>
                            <span class="metric-val">%${v.exitRate}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Ürün Süresi</span>
                            <span class="metric-val">${v.prodDuration} sn</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Ziyaret Ayı</span>
                            <span class="metric-val">${v.month}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Özel Gün</span>
                            <span class="metric-val">${v.specDay}</span>
                        </div>
                    </div>
                `;
                
                container.insertBefore(card, container.firstChild);
                
                if (!isInitial) {
                    // Trigger expansion/fade-in
                    setTimeout(() => {
                        card.classList.remove("new-item");
                    }, 50);
                }
                
                // Keep only last 3 items to fit comfortably
                if (container.children.length > 3) {
                    container.removeChild(container.lastChild);
                }
            }
            
            // Populate initially
            for (let i = 0; i < 3; i++) {
                addVisitorToFeed(true);
            }
            
            // Stream new visitors every 4 seconds
            setInterval(() => {
                addVisitorToFeed(false);
            }, 4000);
        </script>
    </body>
    </html>
    """
    components.html(live_feed_html, height=430, scrolling=False)
    
    st.markdown("""
    <style>
    .dash-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
        color: #F9FAFB;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .dash-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(255, 215, 0, 0.5);
    }
    .dash-card h3 {
        color: #FFD700 !important;
        margin-top: 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 10px;
        margin-bottom: 15px;
        font-size: 1.5rem;
    }
    .dash-card p, .dash-card ul {
        font-size: 1rem;
        line-height: 1.6;
    }
    .dash-card ul {
        padding-left: 20px;
    }
    .dash-card li {
        margin-bottom: 10px;
    }
    .metric-highlight {
        font-size: 1.2rem;
        font-weight: bold;
        color: #34D399;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="dash-card">
        <h3 style="display: flex; align-items: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-up-narrow-wide-icon lucide-arrow-up-narrow-wide"><path d="m3 8 4-4 4 4"/><path d="M7 4v16"/><path d="M11 12h4"/><path d="M11 16h7"/><path d="M11 20h10"/></svg> Uygulamamızın Amacı</h3>
        <p>E-ticaret platformumuzdaki ziyaretçilerin session (oturum) sırasındaki dijital ayak izlerini takip ederek,
        oturumun sonunda <b>"satın alma yapıp yapmayacaklarını (Revenue)"</b> gerçek zamanlı olarak tahmin etmektir. 
        Bu tahminleme sayesinde yüksek potansiyelli müşterilere özel fırsatlar sunulabilir veya sepet terk etme olasılığı yüksek
        olan müşteriler önceden tespit edilerek kampanya veya hatırlatıcılarla hedeflenebilir.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="dash-card" style="height: auto;">
        <h3 style="margin-bottom: 20px; display: flex; align-items: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-box-icon lucide-file-box"><path d="M14.5 22H18a2 2 0 0 0 2-2V8a2.4 2.4 0 0 0-.706-1.706l-3.588-3.588A2.4 2.4 0 0 0 14 2H6a2 2 0 0 0-2 2v3.8"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M11.7 14.2 7 17l-4.7-2.8"/><path d="M3 13.1a2 2 0 0 0-.999 1.76v3.24a2 2 0 0 0 .969 1.78L6 21.7a2 2 0 0 0 2.03.01L11 19.9a2 2 0 0 0 1-1.76V14.9a2 2 0 0 0-.97-1.78L8 11.3a2 2 0 0 0-2.03-.01z"/><path d="M7 17v5"/></svg> Model & Performans</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 25px;">
            <!-- Box 1: Recall -->
            <div style="flex: 1; min-width: 150px; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2); transition: transform 0.3s ease;">
                <div style="font-size: 0.85rem; color: #A0AEC0; font-family: 'Poppins', sans-serif; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; gap: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-open-check-icon lucide-book-open-check"><path d="M12 21V7"/><path d="m16 12 2 2 4-4"/><path d="M22 6V4a1 1 0 0 0-1-1h-5a4 4 0 0 0-4 4 4 4 0 0 0-4-4H3a1 1 0 0 0-1 1v13a1 1 0 0 0 1 1h6a3 3 0 0 1 3 3 3 3 0 0 1 3-3h6a1 1 0 0 0 1-1v-1.3"/></svg> Recall</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #F59E0B; font-family: 'Montserrat', sans-serif;">%88.3</div>
            </div>
            <!-- Box 2: ROC-AUC -->
            <div style="flex: 1; min-width: 150px; background: rgba(52, 211, 153, 0.15); border: 1px solid rgba(52, 211, 153, 0.4); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(52, 211, 153, 0.2); transition: transform 0.3s ease;">
                <div style="font-size: 0.85rem; color: #A0AEC0; font-family: 'Poppins', sans-serif; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; gap: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-axis3d-icon lucide-axis-3d"><path d="M13.5 10.5 15 9"/><path d="M4 4v15a1 1 0 0 0 1 1h15"/><path d="M4.293 19.707 6 18"/><path d="m9 15 1.5-1.5"/></svg> ROC-AUC Skor</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #34D399; font-family: 'Montserrat', sans-serif;">%92.6</div>
            </div>
            <!-- Box 3: F1 Score -->
            <div style="flex: 1; min-width: 150px; background: rgba(255, 105, 180, 0.15); border: 1px solid rgba(255, 105, 180, 0.4); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(255, 105, 180, 0.2); transition: transform 0.3s ease;">
                <div style="font-size: 0.85rem; color: #A0AEC0; font-family: 'Poppins', sans-serif; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; gap: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bow-arrow-icon lucide-bow-arrow"><path d="M17 3h4v4"/><path d="M18.575 11.082a13 13 0 0 1 1.048 9.027 1.17 1.17 0 0 1-1.914.597L14 17"/><path d="M7 10 3.29 6.29a1.17 1.17 0 0 1 .6-1.91 13 13 0 0 1 9.03 1.05"/><path d="M7 14a1.7 1.7 0 0 0-1.207.5l-2.646 2.646A.5.5 0 0 0 3.5 18H5a1 1 0 0 1 1 1v1.5a.5.5 0 0 0 .854.354L9.5 18.207A1.7 1.7 0 0 0 10 17v-2a1 1 0 0 0-1-1z"/><path d="M9.707 14.293 21 3"/></svg> F1 Score</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #FF69B4; font-family: 'Montserrat', sans-serif;">%89.5</div>
            </div>
            <!-- Box 4: Accuracy -->
            <div style="flex: 1; min-width: 150px; background: rgba(96, 165, 250, 0.15); border: 1px solid rgba(96, 165, 250, 0.4); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(96, 165, 250, 0.2); transition: transform 0.3s ease;">
                <div style="font-size: 0.85rem; color: #A0AEC0; font-family: 'Poppins', sans-serif; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; gap: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-target-icon lucide-target"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg> Accuracy</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: #60A5FA; font-family: 'Montserrat', sans-serif;">%94.1</div>
            </div>
            <!-- Box 5: Model Name -->
            <div style="flex: 1; min-width: 200px; background: rgba(138, 43, 226, 0.15); border: 1px solid rgba(138, 43, 226, 0.4); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(138, 43, 226, 0.2); transition: transform 0.3s ease;">
                <div style="font-size: 0.85rem; color: #A0AEC0; font-family: 'Poppins', sans-serif; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; gap: 6px;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trophy-icon lucide-trophy"><path d="M10 14.66v1.626a2 2 0 0 1-.976 1.696A5 5 0 0 0 7 21.978"/><path d="M14 14.66v1.626a2 2 0 0 0 .976 1.696A5 5 0 0 1 17 21.978"/><path d="M18 9h1.5a1 1 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M6 9a6 6 0 0 0 12 0V3a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1z"/><path d="M6 9H4.5a1 1 0 0 1 0-5H6"/></svg> Seçilen Model</div>
                <div style="font-size: 1.4rem; font-weight: bold; color: #FFD700; font-family: 'Montserrat', sans-serif;">Gradient Boosting</div>
            </div>
        </div>
        <div style="background: rgba(0, 0, 0, 0.2); padding: 18px; border-left: 4px solid #FFD700; border-radius: 8px;">
            <p style="margin: 0; font-size: 0.95rem; color: #E2E8F0; line-height: 1.6; font-family: 'Poppins', sans-serif;"><b><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-lightbulb-icon lucide-lightbulb" style="vertical-align: middle; margin-bottom: 4px; color: #FFD700;"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></svg> Neden Bu Model?</b> Test edilen 12 farklı yapay zeka algoritması arasından, en düşük ezberleme (overfit) riski (%0.02 gap) ve yüksek kararlılık sunduğu için lider seçilmiştir.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- GEÇMİŞ ANALİZ SONUÇLARI ---
    svg_history = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px; margin-bottom: 4px; color: #FFD700;"><path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M8 18v-2"/><path d="M12 18v-4"/><path d="M16 18v-6"/></svg>'
    st.markdown(f"### {svg_history} Geçmiş Analiz Kayıtları", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 215, 0, 0.2); margin-bottom: 20px;">
        <p style="margin: 0; color: #E2E8F0; font-size: 0.95rem; font-family: 'Poppins', sans-serif;">Bu tablo, <b>Tekil Tahmin</b> sayfasından yapılan analizlerin kayıtlarını anlık olarak gösterir. Zaman, tahmin sonucu (1: Alacak, 0: Almayacak) ve ihtimal oranları tablonun başında yer alır.</p>
    </div>
    """, unsafe_allow_html=True)
    
    csv_path = os.path.join(DB_FOLDER, "predictions.csv")
    if os.path.exists(csv_path):
        try:
            history_df = load_prediction_history_csv(csv_path)
            # Reorder columns to show the most important ones first
            cols = history_df.columns.tolist()
            important_cols = ['Timestamp', 'Prediction', 'Probability_1', 'Probability_0']
            for col in important_cols:
                if col in cols:
                    cols.remove(col)
            final_cols = important_cols + cols
            history_df = history_df[final_cols]
            
            st.dataframe(
                history_df,
                use_container_width=True,
                height=300
            )
            
            # CSV İndirme Butonu
            csv_data = history_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tabloyu İndir (CSV)",
                data=csv_data,
                file_name="salescope_predictions_history.csv",
                mime="text/csv",
                type="primary"
            )
        except Exception as e:
            st.error(f"Geçmiş veriler okunurken hata oluştu: {e}")
    else:
        st.info("Henüz kaydedilmiş bir analiz geçmişi bulunmuyor. Lütfen 'Tekil Tahmin' sekmesinden form doldurup analiz yapın.")
        
    st.markdown("<br>", unsafe_allow_html=True)

    svg_db = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px; margin-bottom: 4px; color: #FFD700;"><path d="M21 11.693V5"/><path d="m22 22-1.875-1.875"/><path d="M3 12a9 3 0 0 0 8.697 2.998"/><path d="M3 5v14a9 3 0 0 0 9.28 2.999"/><circle cx="18" cy="18" r="3"/><ellipse cx="12" cy="5" rx="9" ry="3"/></svg>'
    st.markdown(f"### {svg_db} Veri Sözlüğü", unsafe_allow_html=True)
    
    # Vagon 3 with Interactive Dropdown (using components.html to allow JS inside the same styled box)
    vagon3_html = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Poppins:wght@300;500;700&display=swap');
    html, body {
        margin: 0;
        padding: 0;
        font-family: 'Poppins', sans-serif;
        background: transparent;
        color: #F3F4F6;
    }
    .train-car {
        display: flex; 
        align-items: stretch; 
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); 
        border-radius: 12px; 
        overflow: hidden;
        border: 2px solid rgba(255, 105, 180, 0.4);
    }

    .train-car-content {
        padding: 20px; 
        color: #F3F4F6; 
        flex: 1;
    }
    .train-car-content h4 {
        color: #FFD700;
        font-family: 'Montserrat', sans-serif;
        font-size: 1.2rem;
        margin-top: 0;
        margin-bottom: 15px;
    }
    .dropdown-container {
        display: flex;
        gap: 20px;
        align-items: stretch;
    }
    select.metric-select {
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        background: rgba(15, 23, 42, 0.9);
        color: white;
        border: 1px solid #FFD700;
        font-family: 'Poppins', sans-serif;
        font-size: 1rem;
        cursor: pointer;
        outline: none;
    }
    select.metric-select option {
        background: #0F172A;
        color: white;
    }
    .metric-desc {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        border-left: 4px solid #FFD700;
        padding: 15px;
        flex: 1;
        font-size: 0.95rem;
        line-height: 1.6;
        height: 140px;
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: rgba(255, 215, 0, 0.4) rgba(255, 255, 255, 0.05);
    }
    .metric-desc::-webkit-scrollbar {
        width: 6px;
    }
    .metric-desc::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 4px;
    }
    .metric-desc::-webkit-scrollbar-thumb {
        background: rgba(255, 215, 0, 0.4);
        border-radius: 4px;
    }
    .metric-desc::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 215, 0, 0.7);
    }
    </style>
    <div class="train-car">
        <div class="train-car-content">
            <h4>Metrikler Neyi İfade Eder?</h4>
            <div class="dropdown-container">
                <div style="flex: 1; max-width: 320px;">
                    <select class="metric-select" onchange="document.getElementById('descText').innerHTML = this.value">
                        <option value="<b>Administrative (Yönetimsel Sayfalar):</b> Kullanıcının profil, üyelik, sepet veya ödeme gibi operasyonel sayfaları ziyaret sayısıdır.<br><br><b>Ne İşe Yarar?</b> Kullanıcının site altyapısıyla etkileşime girip girmediğini ve satın alma işlemlerini başlatma isteğini gösterir.">Administrative</option>
                        <option value="<b>Administrative Duration (Yönetimsel Süre):</b> Yönetimsel veya işlemsel sayfalarda geçirilen toplam süredir (saniye).<br><br><b>Ne İşe Yarar?</b> Kullanıcının üyelik veya sepet işlemlerinde ne kadar zaman harcadığını ve işlemlerini tamamlama kararlılığını ölçer.">Administrative Duration</option>
                        <option value="<b>Informational (Bilgilendirici Sayfalar):</b> İletişim, hakkımızda, gizlilik politikası, kargo ve iade koşulları gibi bilgi sayfalarının ziyaret sayısıdır.<br><br><b>Ne İşe Yarar?</b> Ziyaretçinin siteye ve markaya karşı duyduğu güven arayışını ve kurumsal bilgileri sorgulama eğilimini analiz eder.">Informational</option>
                        <option value="<b>Informational Duration (Bilgilendirici Süre):</b> Bilgilendirici sayfalarda geçirilen saniye cinsinden süredir.<br><br><b>Ne İşe Yarar?</b> Ziyaretçinin bilgi edinme sürecinde ne kadar derinlemesine araştırma yaptığını ve güven tesis etmeye çalışıp çalışmadığını ölçer.">Informational Duration</option>
                        <option value="<b>Product Related (Ürün İnceleme Sayfaları):</b> Ziyaretçinin incelediği toplam ürün detay veya ürün kategori sayfası sayısıdır.<br><br><b>Ne İşe Yarar?</b> Kullanıcının ürün kataloğuna olan ilgisini ve alışveriş niyetiyle yaptığı ürün arama yoğunluğunu yansıtan en temel metriklerdendir.">Product Related</option>
                        <option value="<b>Product Related Duration (Ürün İnceleme Süresi):</b> Ürün detay ve listeleme sayfalarında geçirilen toplam süredir (saniye).<br><br><b>Ne İşe Yarar?</b> Kullanıcının ürünleri ne kadar odaklanarak incelediğini, satın alma karar süresinin uzunluğunu ve ürünlere olan ilgi düzeyini belirler.">Product Related Duration</option>
                        <option value="<b>Bounce Rates (Hemen Çıkma Oranı):</b> Ziyaretçinin siteye girdiği ilk sayfadan başka hiçbir sayfaya geçmeden ve etkileşim kurmadan siteden ayrılma oranıdır.<br><br><b>Ne İşe Yarar?</b> Ziyaretçinin siteden memnun kalma düzeyini ve sunulan ilk sayfa içeriğinin hedeflenen kitleyle uyumunu denetler.">Bounce Rates</option>
                        <option value="<b>Exit Rates (Siteden Çıkış Oranı):</b> Belirli bir sayfa veya sayfa grubu ziyaret edildikten sonra kullanıcının siteyi terk etme olasılığıdır.<br><br><b>Ne İşe Yarar?</b> Kullanıcının siteyi terk etmesine neden olan sorunlu/odaksız sayfaları veya sepeti tamamlama aşamasındaki olası engelleri tespit etmeyi sağlar.">Exit Rates</option>
                        <option value="<b>Page Values (Sayfa Değeri):</b> Ziyaretçinin oturum süresince gezindiği sayfaların ortalama finansal/e-ticaret değeridir.<br><br><b>Ne İşe Yarar?</b> Ziyaret edilen sayfaların satın almaya ne kadar katkı sağladığını gösteren en güçlü metrik olup, dönüşüm olasılığını doğrudan yansıtır.">Page Values</option>
                        <option value="<b>Special Day (Özel Gün Yakınlığı):</b> Ziyaret tarihinin sevgililer günü, anneler günü, yılbaşı veya özel indirim dönemlerine olan takvimsel yakınlığıdır.<br><br><b>Ne İşe Yarar?</b> Alışveriş trafiğinin ve satın alma kararlarının özel kampanyalardan ve dönemsel heyecanlardan ne kadar etkilendiğini ortaya koyar.">Special Day</option>
                        <option value="<b>Month (Ziyaret Ayı):</b> Ziyaretin yılın hangi ayında yapıldığı bilgisidir.<br><br><b>Ne İşe Yarar?</b> E-ticaretteki aylık satış trendlerini, sezonsallık etkilerini ve belirli aylara özel tüketim davranışlarını yakalamayı sağlar.">Month</option>
                        <option value="<b>Visitor Type (Ziyaretçi Tipi):</b> Kullanıcının siteye daha önce gelmiş bir müşteri mi (Returning Visitor) yoksa ilk kez gelen yeni bir ziyaretçi mi (New Visitor) olduğudur.<br><br><b>Ne İşe Yarar?</b> Müşteri sadakatinin, aşinalığının ve kazanım modellerinin satın alma kararlarının üzerindeki etkisini inceler.">Visitor Type</option>
                        <option value="<b>Weekend (Hafta Sonu):</b> Oturumun cumartesi veya pazar günleri gerçekleşip gerçekleşmediğini belirtir.<br><br><b>Ne İşe Yarar?</b> Tüketicilerin hafta içi (iş/okul günleri) ile hafta sonu (serbest zaman) alışveriş eğilimleri ve sepet alışkanlıkları arasındaki farkı gösterir.">Weekend</option>
                        <option value="<b>Traffic Type (Trafik Kaynağı):</b> Ziyaretçinin e-ticaret sitesine hangi kanaldan ulaştığı bilgisidir (örneğin Google Organik Arama, Doğrudan URL, Sosyal Medya, Ücretli Reklamlar).<br><br><b>Ne İşe Yarar?</b> Çeşitli reklam ve pazarlama kanallarının dönüşüm kalitesini ve hangi kaynaklardan gelen kullanıcıların satın almaya daha meyilli olduğunu belirlemeyi sağlar.">Traffic Type</option>
                    </select>
                </div>
                <div class="metric-desc">
                    <span id="descText"><b>Administrative (Yönetimsel Sayfalar):</b> Kullanıcının profil, üyelik, sepet veya ödeme gibi operasyonel sayfaları ziyaret sayısıdır.<br><br><b>Ne İşe Yarar?</b> Kullanıcının site altyapısıyla etkileşime girip girmediğini ve satın alma işlemlerini başlatma isteğini gösterir.</span>
                </div>
            </div>
        </div>
    </div>
    """
    components.html(vagon3_html, height=310)

    # ── KİLAVYE KISAYOLLARI REFERANS KARTI ────────────────────────────────
    ks_html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Montserrat:wght@700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;font-family:"Poppins",sans-serif;padding:4px}
.ks-wrapper{
  background:linear-gradient(135deg,rgba(30,41,59,0.95),rgba(15,23,42,0.95));
  border:1px solid rgba(255,215,0,0.2);
  border-radius:16px;
  padding:28px 32px;
  max-height:340px;
  overflow-y:scroll;
  scrollbar-width:thin;
  scrollbar-color:rgba(255,215,0,0.4) rgba(255,255,255,0.05);
}
.ks-wrapper::-webkit-scrollbar{width:6px}
.ks-wrapper::-webkit-scrollbar-track{background:rgba(255,255,255,0.04);border-radius:4px}
.ks-wrapper::-webkit-scrollbar-thumb{background:rgba(255,215,0,0.4);border-radius:4px}
.ks-wrapper::-webkit-scrollbar-thumb:hover{background:rgba(255,215,0,0.7)}
.ks-title{
  font-family:"Montserrat",sans-serif;
  font-size:1.05rem;font-weight:700;color:#FFD700;
  margin-bottom:18px;padding-bottom:10px;
  border-bottom:1px solid rgba(255,215,0,0.15);
}
.ks-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
  gap:10px;
}
.ks-row{
  display:flex;align-items:center;gap:12px;
  padding:10px 14px;
  background:rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.06);
  border-radius:10px;
  transition:background 0.2s;
}
.ks-row:hover{background:rgba(255,215,0,0.05)}
.ks-keys{display:flex;gap:4px;flex-shrink:0;align-items:center}
.kbd{
  display:inline-block;
  background:rgba(255,255,255,0.08);
  border:1px solid rgba(255,255,255,0.18);
  border-bottom:2px solid rgba(255,255,255,0.25);
  border-radius:6px;padding:3px 9px;
  font-size:0.76rem;font-family:"Montserrat",sans-serif;
  font-weight:700;color:#FFD700;white-space:nowrap;
}
.ks-sep{color:#475569;font-size:0.8rem;line-height:1}
.ks-desc{font-size:0.80rem;color:#94A3B8;line-height:1.4}
.ks-desc strong{color:#E2E8F0;display:block;margin-bottom:2px}
.ks-badge{
  font-size:0.68rem;
  background:rgba(138,43,226,0.2);
  border:1px solid rgba(138,43,226,0.4);
  border-radius:20px;padding:2px 8px;
  color:#A78BFA;margin-left:auto;flex-shrink:0;
}
</style>
</head>
<body>
<div class="ks-wrapper">
  <div class="ks-title" style="display: flex; align-items: center; justify-content: center; gap: 8px;"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-keyboard-icon lucide-keyboard"><path d="M10 8h.01"/><path d="M12 12h.01"/><path d="M14 8h.01"/><path d="M16 12h.01"/><path d="M18 8h.01"/><path d="M6 8h.01"/><path d="M7 16h10"/><path d="M8 12h.01"/><rect width="20" height="16" x="2" y="4" rx="2"/></svg> Klavye Kısayolları</div>
  <div class="ks-grid">

    <div class="ks-row">
      <div class="ks-keys"><span class="kbd">Alt / ⌥ Opt</span><span class="ks-sep">+</span><span class="kbd">1</span></div>
      <div class="ks-desc"><strong style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-house-icon lucide-house"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg> Ana Sayfa &amp; Hikaye</strong>Ana sayfaya geçiş yapar</div>
      <span class="ks-badge">Navigasyon</span>
    </div>

    <div class="ks-row">
      <div class="ks-keys"><span class="kbd">Alt / ⌥ Opt</span><span class="ks-sep">+</span><span class="kbd">2</span></div>
      <div class="ks-desc"><strong style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-radio-icon lucide-radio"><path d="M16.247 7.761a6 6 0 0 1 0 8.478"/><path d="M19.075 4.933a10 10 0 0 1 0 14.134"/><path d="M4.925 19.067a10 10 0 0 1 0-14.134"/><path d="M7.753 16.239a6 6 0 0 1 0-8.478"/><circle cx="12" cy="12" r="2"/></svg> Tekil Canlı Tahmin</strong>Tahmin formuna geçiş yapar</div>
      <span class="ks-badge">Navigasyon</span>
    </div>

    <div class="ks-row">
      <div class="ks-keys"><span class="kbd">Alt / ⌥ Opt</span><span class="ks-sep">+</span><span class="kbd">3</span></div>
      <div class="ks-desc"><strong style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-chart-column-increasing-icon lucide-file-chart-column-increasing"><path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M8 18v-2"/><path d="M12 18v-4"/><path d="M16 18v-6"/></svg> Yönetici Özeti Paneli</strong>Dashboard sayfasına geçiş yapar</div>
      <span class="ks-badge">Navigasyon</span>
    </div>

    <div class="ks-row">
      <div class="ks-keys"><span class="kbd">Alt / ⌥ Opt</span><span class="ks-sep">+</span><span class="kbd">&#8629; Enter</span></div>
      <div class="ks-desc"><strong>Analiz Et</strong>Tahmin formunu gönderir ve modeli tetikler</div>
      <span class="ks-badge">Form</span>
    </div>

    <div class="ks-row">
      <div class="ks-keys"><span class="kbd">Alt / ⌥ Opt</span><span class="ks-sep">+</span><span class="kbd">R</span></div>
      <div class="ks-desc"><strong>Formu Sıfırla</strong>Tüm form alanlarını temizler</div>
      <span class="ks-badge">Form</span>
    </div>

    <div class="ks-row">
      <div class="ks-keys"><span class="kbd">Alt / ⌥ Opt</span><span class="ks-sep">+</span><span class="kbd">T</span></div>
      <div class="ks-desc"><strong>Başa Dön (Top)</strong>Sayfanın en üstüne kaydırır</div>
      <span class="ks-badge">Kaydirma</span>
    </div>

    <div class="ks-row">
      <div class="ks-keys"><span class="kbd">Alt / ⌥ Opt</span><span class="ks-sep">+</span><span class="kbd">B</span></div>
      <div class="ks-desc"><strong>Sona Git (Bottom)</strong>Sayfanın en altına kaydırır</div>
      <span class="ks-badge">Kaydirma</span>
    </div>

  </div>
</div>
</body>
</html>"""
    components.html(ks_html, height=380, scrolling=False)



# --- GLOBAL FOOTER ---
footer_html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Montserrat:wght@700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;font-family:"Poppins",sans-serif;color:#94A3B8;overflow:hidden}
.gf-wrapper{border-top:1px solid rgba(255,255,255,0.10);padding-top:10px}
.gf-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:40px;padding:30px 20px 24px}
.gf-logo{font-family:"Montserrat",sans-serif;font-size:1.05rem;font-weight:700;color:#F1F5F9;display:block;margin-bottom:10px}
.gf-brand p{font-size:.82rem;line-height:1.7;color:#94A3B8}
h6{font-family:"Montserrat",sans-serif;font-size:.75rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#FFD700;margin-bottom:14px}
ul{list-style:none;padding:0;margin:0}li{margin-bottom:9px}
a{font-size:.83rem;color:#94A3B8;text-decoration:none;transition:color .2s,padding-left .2s;display:inline-block;cursor:pointer}
a:hover{color:#FFD700;padding-left:4px}
.gf-bottom{border-top:1px solid rgba(255,255,255,0.06);padding:14px 20px;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px}
.copy{font-size:.75rem;color:#64748B}
.gf-badges{display:flex;gap:6px;flex-wrap:wrap}
.badge{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.10);border-radius:6px;padding:2px 10px;font-size:.72rem;color:#94A3B8}
/* OVERLAY */
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:9000;align-items:center;justify-content:center}
.overlay.show{display:flex}
.modal{background:#fff;border-radius:14px;width:90%;max-width:540px;max-height:75vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.3);animation:fadeIn .2s ease}
@keyframes fadeIn{from{opacity:0;transform:scale(.93)}to{opacity:1;transform:scale(1)}}
.modal::-webkit-scrollbar{width:4px}.modal::-webkit-scrollbar-thumb{background:#D1D5DB;border-radius:4px}
.mhead{display:flex;align-items:center;justify-content:space-between;padding:18px 22px 14px;border-bottom:1px solid #E5E7EB}
.mtitle{font-family:"Montserrat",sans-serif;font-size:.95rem;font-weight:700;color:#111827}
.mclose{background:none;border:none;font-size:1.2rem;color:#9CA3AF;cursor:pointer;transition:color .2s}
.mclose:hover{color:#111827}
.mbody{padding:18px 22px 22px}
.msec{margin-bottom:14px}.msec:last-child{margin-bottom:0}
.msec h4{font-family:"Montserrat",sans-serif;font-size:.7rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#374151;margin-bottom:5px}
.msec p,.msec li{font-size:.82rem;line-height:1.75;color:#6B7280}
.msec ul{list-style:disc;padding-left:16px}.msec ul li{margin-bottom:3px}
.mtag{display:inline-block;background:#F3E8FF;border:1px solid #D8B4FE;border-radius:20px;padding:2px 12px;font-size:.7rem;color:#7C3AED;margin-bottom:12px}
</style>
<script>
var FOOTER_H = 220;
var MODAL_H  = 520;

function setH(h){
  window.frameElement.style.height = h + "px";
  window.frameElement.style.minHeight = h + "px";
}
function goToPage(kw){
  var ls=window.parent.document.querySelectorAll('[data-testid="stSidebar"] [data-testid="stRadio"] label');
  for(var i=0;i<ls.length;i++){if(ls[i].innerText&&ls[i].innerText.indexOf(kw)>-1){ls[i].click();window.parent.scrollTo({top:0,behavior:"smooth"});break;}}
}
function openModal(id){
  setH(MODAL_H);
  document.body.style.overflow="hidden";
  document.getElementById(id).classList.add("show");
}
function closeModal(id){
  document.getElementById(id).classList.remove("show");
  document.body.style.overflow="hidden";
  setH(FOOTER_H);
}
document.addEventListener("click",function(e){
  if(e.target&&e.target.classList.contains("overlay")){
    e.target.classList.remove("show");
    setH(FOOTER_H);
  }
});
window.addEventListener("load",function(){
  setH(FOOTER_H);
  
  // ── KEYBOARD SHORTCUTS INJECTED TO BOTH PARENT & IFRAME ──
  function handleKeydown(e) {
    var alt = e.altKey;
    var code = e.code; 

    function clickRadio(keyword) {
      var labels = window.parent.document.querySelectorAll('[data-testid="stSidebar"] [data-testid="stRadio"] label');
      for (var i = 0; i < labels.length; i++) {
        if (labels[i].innerText && labels[i].innerText.indexOf(keyword) > -1) {
            labels[i].click();
            break;
        }
      }
    }

    function doScroll(toBottom) {
      var mainContainer = window.parent.document.querySelector('.main') || window.parent.document.scrollingElement || window.parent;
      if (toBottom) {
        if (mainContainer.scrollTo) mainContainer.scrollTo({ top: 99999, behavior: 'smooth' });
        else mainContainer.scrollTop = 99999;
      } else {
        if (mainContainer.scrollTo) mainContainer.scrollTo({ top: 0, behavior: 'smooth' });
        else mainContainer.scrollTop = 0;
      }
    }
    
    // Alt + 1, 2, 3
    if (alt && code === 'Digit1') { e.preventDefault(); e.stopPropagation(); clickRadio('Ana Sayfa'); }
    if (alt && code === 'Digit2') { e.preventDefault(); e.stopPropagation(); clickRadio('Tekil'); }
    if (alt && code === 'Digit3') { e.preventDefault(); e.stopPropagation(); clickRadio('Yönetici'); }

    // Alt + Enter
    if (alt && (code === 'Enter' || code === 'NumpadEnter')) {
      e.preventDefault(); e.stopPropagation();
      var btns = window.parent.document.querySelectorAll('button[kind="primaryFormSubmit"], button[data-testid="baseButton-primaryFormSubmit"]');
      for (var i = 0; i < btns.length; i++) {
        if (btns[i].innerText && btns[i].innerText.indexOf('Analiz') > -1) { btns[i].click(); break; }
      }
    }

    // Alt + R
    if (alt && code === 'KeyR') {
      e.preventDefault(); e.stopPropagation();
      var btns = window.parent.document.querySelectorAll('button');
      for (var i = 0; i < btns.length; i++) {
        if (btns[i].innerText && btns[i].innerText.indexOf('Temizle') > -1) { btns[i].click(); break; }
      }
    }

    // Alt + T (Top) / Alt + B (Bottom)
    if (alt && code === 'KeyT') {
      e.preventDefault(); e.stopPropagation();
      doScroll(false);
    }
    if (alt && code === 'KeyB') {
      e.preventDefault(); e.stopPropagation();
      doScroll(true);
    }
  }

  // Bind to iframe
  window.addEventListener('keydown', handleKeydown, true);
  // Bind to parent
  if (window.parent && window.parent.document) {
    window.parent.document.addEventListener('keydown', handleKeydown, true);
  }
});
</script>
</head>
<body>

<div class="gf-wrapper">
  <div class="gf-grid">
    <div class="gf-brand">
      <span class="gf-logo">SALESCOPE</span>
      <h6>E-Ticaret Zekas&#305;</h6>
      <p>M&#252;&#351;teri oturum verilerini makine &#246;&#287;renmesiyle analiz ederek sat&#305;n alma d&#246;n&#252;&#351;&#252;m&#252;n&#252; saniyeler i&#231;inde tahminleyen karar destek platformu.</p>
    </div>
    <div>
      <h6>Uygulama</h6>
      <ul>
        <li><a onclick="goToPage('Ana Sayfa')" style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-house-icon lucide-house"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg> Ana Sayfa &amp; Hikaye</a></li>
        <li><a onclick="goToPage('Tekil')" style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-radio-icon lucide-radio"><path d="M16.247 7.761a6 6 0 0 1 0 8.478"/><path d="M19.075 4.933a10 10 0 0 1 0 14.134"/><path d="M4.925 19.067a10 10 0 0 1 0-14.134"/><path d="M7.753 16.239a6 6 0 0 1 0-8.478"/><circle cx="12" cy="12" r="2"/></svg> Tekil Canl&#305; Tahmin</a></li>
        <li><a onclick="goToPage('Y&#246;netici')" style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-chart-column-increasing-icon lucide-file-chart-column-increasing"><path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M8 18v-2"/><path d="M12 18v-4"/><path d="M16 18v-6"/></svg> Y&#246;netici &#214;zeti Paneli</a></li>
        <li><a onclick="openModal('m-kilavuz')" style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-notebook-tabs-icon lucide-notebook-tabs"><path d="M2 6h4"/><path d="M2 10h4"/><path d="M2 14h4"/><path d="M2 18h4"/><rect width="16" height="20" x="4" y="2" rx="2"/><path d="M15 2v20"/><path d="M15 7h5"/><path d="M15 12h5"/><path d="M15 17h5"/></svg> Kullan&#305;m K&#305;lavuzu</a></li>
      </ul>
    </div>
    <div>
      <h6>Yasal</h6>
      <ul>
        <li><a onclick="openModal('m-gizlilik')" style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-square-asterisk-icon lucide-square-asterisk"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M12 8v8"/><path d="m8.5 14 7-4"/><path d="m8.5 10 7 4"/></svg> Gizlilik Politikas&#305;</a></li>
        <li><a onclick="openModal('m-kullanim')" style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-receipt-text-icon lucide-receipt-text"><path d="M13 16H8"/><path d="M14 8H8"/><path d="M16 12H8"/><path d="M4 3a1 1 0 0 1 1-1 1.3 1.3 0 0 1 .7.2l.933.6a1.3 1.3 0 0 0 1.4 0l.934-.6a1.3 1.3 0 0 1 1.4 0l.933.6a1.3 1.3 0 0 0 1.4 0l.933-.6a1.3 1.3 0 0 1 1.4 0l.934.6a1.3 1.3 0 0 0 1.4 0l.933-.6A1.3 1.3 0 0 1 19 2a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1 1.3 1.3 0 0 1-.7-.2l-.933-.6a1.3 1.3 0 0 0-1.4 0l-.934.6a1.3 1.3 0 0 1-1.4 0l-.933-.6a1.3 1.3 0 0 0-1.4 0l-.933.6a1.3 1.3 0 0 1-1.4 0l-.934-.6a1.3 1.3 0 0 0-1.4 0l-.933.6a1.3 1.3 0 0 1-.7.2 1 1 0 0 1-1-1z"/></svg> Kullan&#305;m &#350;artlar&#305;</a></li>
        <li><a onclick="openModal('m-kvkk')" style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-book-open-check-icon lucide-book-open-check"><path d="M12 21V7"/><path d="m16 12 2 2 4-4"/><path d="M22 6V4a1 1 0 0 0-1-1h-5a4 4 0 0 0-4 4 4 4 0 0 0-4-4H3a1 1 0 0 0-1 1v13a1 1 0 0 0 1 1h6a3 3 0 0 1 3 3 3 3 0 0 1 3-3h6a1 1 0 0 0 1-1v-1.3"/></svg> KVKK Ayd&#305;nlatma Metni</a></li>
        <li><a onclick="openModal('m-cerez')" style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-lock-keyhole-open-icon lucide-lock-keyhole-open"><circle cx="12" cy="16" r="1"/><rect width="18" height="12" x="3" y="10" rx="2"/><path d="M7 10V7a5 5 0 0 1 9.33-2.5"/></svg> &#199;erez Politikas&#305;</a></li>
      </ul>
    </div>
  </div>
  <div class="gf-bottom">
    <span class="copy">&#169; 2026 SALESCOPE &middot; T&#252;m haklar&#305; sakl&#305;d&#305;r.</span>
    <div class="gf-badges">
      <span class="badge">GBC Model</span><span class="badge">ROC-AUC %92.6</span>
      <span class="badge">F1 %89.5</span><span class="badge">v1.4.2</span>
    </div>
  </div>
</div>

<!-- MODAL: Gizlilik -->
<div id="m-gizlilik" class="overlay">
  <div class="modal">
    <div class="mhead"><span class="mtitle">&#128274; Gizlilik Politikas&#305;</span><button class="mclose" onclick="closeModal('m-gizlilik')">&#10005;</button></div>
    <div class="mbody">
      <span class="mtag">Ocak 2026</span>
      <div class="msec"><h4>Toplanan Veriler</h4><p>Platform hi&#231;bir ki&#351;isel tan&#305;mlay&#305;c&#305; bilgi toplamaz. Oturum metrikleri yaln&#305;zca taray&#305;c&#305;n&#305;zda anl&#305;k olarak i&#351;lenir.</p></div>
      <div class="msec"><h4>Veri &#304;&#351;leme Amac&#305;</h4><p>Girilen veriler YZ modelinin tahmin &#252;retmesi i&#231;in kullan&#305;l&#305;r. Hi&#231;bir veri uzak sunucuya g&#246;nderilmez veya saklanmaz.</p></div>
      <div class="msec"><h4>Veri G&#252;venli&#287;i</h4><p>T&#252;m i&#351;lemler istemci taraf&#305;nda ger&#231;ekle&#351;tirilir. Platform HTTPS ve Streamlit altyap&#305;s&#305;n&#305;n g&#252;venlik standartlar&#305;na uymaktad&#305;r.</p></div>
      <div class="msec"><h4>&#220;&#231;&#252;nc&#252; Taraf</h4><p>Yaln&#305;zca Google Fonts CDN kullan&#305;lmaktad&#305;r. Ba&#351;ka analitik veya reklam arac&#305; yoktur.</p></div>
    </div>
  </div>
</div>

<!-- MODAL: Kullanim -->
<div id="m-kullanim" class="overlay">
  <div class="modal">
    <div class="mhead"><span class="mtitle">&#128196; Kullan&#305;m &#350;artlar&#305;</span><button class="mclose" onclick="closeModal('m-kullanim')">&#10005;</button></div>
    <div class="mbody">
      <span class="mtag">Ocak 2026</span>
      <div class="msec"><h4>Hizmet Kapsam&#305;</h4><p>E-ticaret sekt&#246;r&#252;ne y&#246;nelik karar destek ve makine &#246;&#287;renmesi e&#287;itim platformudur. Ticari kararlarda tek ba&#351;&#305;na esas al&#305;nmamal&#305;d&#305;r.</p></div>
      <div class="msec"><h4>Kullan&#305;c&#305; Y&#252;k&#252;ml&#252;l&#252;kleri</h4><ul><li>Yanl&#305;&#351; veri giri&#351;i yapmamak</li><li>K&#246;t&#252; ama&#231;l&#305; kullan&#305;m yapmamak</li><li>&#199;&#305;kt&#305;lar&#305; do&#287;rulanmam&#305;&#351; ger&#231;ek olarak sunmamak</li></ul></div>
      <div class="msec"><h4>Sorumluluk S&#305;n&#305;rlamas&#305;</h4><p>Model &#231;&#305;kt&#305;lar&#305; istatistiksel olas&#305;l&#305;klara dayanmakta olup uzman g&#246;r&#252;&#351;&#252;yle birlikte de&#287;erlendirilmelidir.</p></div>
      <div class="msec"><h4>Fikri M&#252;lkiyet</h4><p>Platform kodu ve model mimarisi telif hakk&#305; kapsam&#305;ndad&#305;r. &#304;zinsiz kopyalanmas&#305; yasakt&#305;r.</p></div>
    </div>
  </div>
</div>

<!-- MODAL: KVKK -->
<div id="m-kvkk" class="overlay">
  <div class="modal">
    <div class="mhead"><span class="mtitle">&#128737; KVKK Ayd&#305;nlatma Metni</span><button class="mclose" onclick="closeModal('m-kvkk')">&#10005;</button></div>
    <div class="mbody">
      <span class="mtag">6698 Say&#305;l&#305; KVKK</span>
      <div class="msec"><h4>Veri Sorumlusu</h4><p>Platform hi&#231;bir ki&#351;isel veri i&#351;lemedi&#287;inden KVKK kapsam&#305;nda veri sorumlusu s&#305;fat&#305; ta&#351;&#305;mamaktad&#305;r.</p></div>
      <div class="msec"><h4>&#304;&#351;lenmeyen Veriler</h4><ul><li>Ad, soyad, e-posta, telefon</li><li>IP adresi, konum, cihaz kimli&#287;i</li><li>Finansal veya &#246;zel nitelikli veriler</li></ul></div>
      <div class="msec"><h4>&#304;&#351;lenen Veriler</h4><p>Forma girilen anonim oturum metrikleri ki&#351;iyle ili&#351;kilendirilemez, yaln&#305;zca taray&#305;c&#305;da anl&#305;k i&#351;lenir.</p></div>
      <div class="msec"><h4>Haklar&#305;n&#305;z</h4><p>Ki&#351;isel veri i&#351;lenmedi&#287;inden KVKK&#39;n&#305;n 11. maddesi haklar&#305;n&#305; kullanman&#305;z&#305; gerektiren bir durum bulunmamaktad&#305;r.</p></div>
    </div>
  </div>
</div>

<!-- MODAL: Cerez -->
<div id="m-cerez" class="overlay">
  <div class="modal">
    <div class="mhead"><span class="mtitle">&#127850; &#199;erez Politikas&#305;</span><button class="mclose" onclick="closeModal('m-cerez')">&#10005;</button></div>
    <div class="mbody">
      <span class="mtag">Ocak 2026</span>
      <div class="msec"><h4>Kullan&#305;lan &#199;erezler</h4><p>Yaln&#305;zca Streamlit altyap&#305;s&#305;n&#305;n teknik i&#351;leyi&#351;i i&#231;in zorunlu oturum &#231;erezleri kullan&#305;l&#305;r.</p></div>
      <div class="msec"><h4>Kullan&#305;lmayanlar</h4><ul><li>Analitik &#231;erezler</li><li>Pazarlama &#231;erezleri</li><li>&#220;&#231;&#252;nc&#252; taraf izleme &#231;erezleri</li></ul></div>
      <div class="msec"><h4>Kontrol</h4><p>Taray&#305;c&#305; ayarlar&#305;ndan &#231;erezleri devre d&#305;&#351;&#305; b&#305;rakabilirsiniz; ancak oturum y&#246;netimi bozulabilir.</p></div>
    </div>
  </div>
</div>

<!-- MODAL: Kilavuz -->
<div id="m-kilavuz" class="overlay">
  <div class="modal">
    <div class="mhead"><span class="mtitle">&#128214; Kullan&#305;m K&#305;lavuzu</span><button class="mclose" onclick="closeModal('m-kilavuz')">&#10005;</button></div>
    <div class="mbody">
      <span class="mtag">Ad&#305;m Ad&#305;m Rehber</span>
      <div class="msec"><h4>Ad&#305;m 1 &#8212; Navigasyon</h4><p>Sol paneldeki men&#252;den <b>Tekil Canl&#305; Tahmin</b> sayfas&#305;na ge&#231;i&#351; yap&#305;n.</p></div>
      <div class="msec"><h4>Ad&#305;m 2 &#8212; Sayfa Verileri</h4><p>Y&#246;netim, Bilgi ve &#220;r&#252;n sayfalar&#305;nda ge&#231;irilen s&#252;re ve ziyaret say&#305;s&#305;n&#305; girin.</p></div>
      <div class="msec"><h4>Ad&#305;m 3 &#8212; Etkile&#351;im</h4><p>&#199;&#305;k&#305;&#351; Oran&#305;, Bounce Rate ve Sayfa De&#287;eri metriklerini Google Analytics vb. ara&#231;lardan ekleyin.</p></div>
      <div class="msec"><h4>Ad&#305;m 4 &#8212; Ziyaret Ba&#287;lam&#305;</h4><p>Ziyaret&#231;i tipi, ay, hafta sonu ve &#246;zel g&#252;n yak&#305;nl&#305;&#287;&#305; bilgisini se&#231;in.</p></div>
      <div class="msec"><h4>Ad&#305;m 5 &#8212; YZ Analizi</h4><p>T&#252;m formu doldurup <b>Analiz Et</b> butonuna basarak modeli tetikleyin.</p></div>
      <div class="msec"><h4>Ad&#305;m 6 &#8212; Aksiyon</h4><p>Tahmin sonucuna g&#246;re m&#252;&#351;teriye anl&#305;k f&#305;rsat veya hat&#305;rlat&#305;c&#305; y&#246;nlendirin.</p></div>
    </div>
  </div>
</div>

</body>
</html>"""
components.html(footer_html, height=220, scrolling=False)






