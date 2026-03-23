import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from fuzzywuzzy import fuzz, process
import plotly.express as px

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediAssist AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1d2e;
        border-right: 1px solid #2d3561;
    }

    /* Chat input */
    [data-testid="stChatInput"] textarea {
        background-color: #1e2030 !important;
        border: 1px solid #3d5af1 !important;
        color: #e0e0e0 !important;
        border-radius: 12px !important;
    }

    /* Emergency banner */
    .emergency-banner {
        background: linear-gradient(135deg, #ff4444, #cc0000);
        color: white;
        padding: 20px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(255,68,68,0.4);
        animation: pulse 1s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 4px 15px rgba(255,68,68,0.4); }
        50% { box-shadow: 0 4px 25px rgba(255,68,68,0.8); }
        100% { box-shadow: 0 4px 15px rgba(255,68,68,0.4); }
    }

    /* Health tip card */
    .health-tip-card {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border-left: 4px solid #3d9be9;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        color: #e0e0e0;
    }

    /* Stats card */
    .stat-card {
        background: #1e2030;
        border: 1px solid #2d3561;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        color: #e0e0e0;
    }

    /* Metric number */
    .stat-number {
        font-size: 28px;
        font-weight: bold;
        color: #3d9be9;
    }

    .stat-label {
        font-size: 12px;
        color: #888;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Emergency Keywords ────────────────────────────────────────────────────────
EMERGENCY_KEYWORDS = [
    'chest pain', 'chest tightness', 'heart attack', 'cant breathe',
    "can't breathe", 'difficulty breathing', 'shortness of breath',
    'stroke', 'face drooping', 'arm weakness', 'sudden numbness',
    'unconscious', 'not breathing', 'stopped breathing',
    'severe bleeding', 'coughing blood', 'vomiting blood',
    'seizure', 'convulsion', 'overdose', 'poisoning',
    'severe allergic', 'anaphylaxis', 'throat swelling',
    'sudden severe headache', 'worst headache'
]

# ─── Health Tips Database ──────────────────────────────────────────────────────
HEALTH_TIPS = {
    'diabetes': [
        "🥗 Follow a low-glycemic diet — avoid white rice, sugary drinks, and processed foods",
        "🏃 Exercise at least 30 minutes daily — walking after meals helps control blood sugar",
        "💊 Take medications at the same time daily for consistent levels",
        "🩸 Monitor blood sugar regularly — keep a log to share with your doctor",
        "🦶 Check your feet daily for cuts or sores — diabetes slows healing",
        "💧 Stay well hydrated — aim for 8-10 glasses of water daily"
    ],
    'hypertension': [
        "🧂 Reduce salt intake — aim for less than 5g per day",
        "🏃 30 minutes of moderate exercise (walking, swimming) 5 days a week",
        "🚭 Quit smoking — nicotine raises blood pressure immediately",
        "🍌 Eat potassium-rich foods — bananas, sweet potatoes, spinach",
        "😴 Get 7-8 hours of sleep — poor sleep raises blood pressure",
        "🧘 Practice stress management — yoga, deep breathing, meditation"
    ],
    'fever': [
        "💧 Stay hydrated — drink plenty of water, coconut water, or ORS",
        "🌡️ Take paracetamol (not aspirin for children) to reduce fever",
        "🛏️ Rest as much as possible — your body needs energy to fight infection",
        "🧊 Use a cool damp cloth on forehead, armpits, and neck",
        "🚨 See a doctor if fever exceeds 103°F (39.4°C) or lasts more than 3 days",
        "👕 Wear light clothing — heavy blankets can trap heat"
    ],
    'headache': [
        "💧 Dehydration is a top cause — drink a full glass of water first",
        "😴 Ensure you're getting 7-9 hours of quality sleep",
        "📱 Reduce screen time — take a 20-20-20 break every 20 minutes",
        "🧘 Try relaxation techniques — tension headaches respond well to stretching",
        "☕ Caffeine can help or cause headaches — maintain consistent intake",
        "🚨 Seek immediate help for sudden severe headache — could indicate stroke"
    ],
    'cold': [
        "💧 Stay hydrated — hot soups and warm liquids soothe throat and clear congestion",
        "🍯 Honey with warm water or ginger tea can ease symptoms naturally",
        "🛏️ Rest is your best medicine — your immune system works harder when you sleep",
        "💨 Use steam inhalation to clear blocked nasal passages",
        "🤧 Wash hands frequently — colds spread easily through contact",
        "🚭 Avoid smoking — it irritates and delays healing of airways"
    ],
    'asthma': [
        "🚭 Avoid ALL smoke — even secondhand smoke is a major trigger",
        "💨 Keep rescue inhaler with you at ALL times",
        "🌿 Identify your triggers — dust, pollen, cold air, exercise, stress",
        "🏠 Use air purifiers at home and keep windows closed during high pollen days",
        "🧹 Clean regularly — dust mites in bedding are a common trigger",
        "🏃 Warm up before exercise — use prescribed preventer inhaler before physical activity"
    ],
    'malaria': [
        "🦟 Use mosquito nets while sleeping — especially between dusk and dawn",
        "🧴 Apply mosquito repellent containing DEET on exposed skin",
        "💊 Complete the FULL course of antimalarial medication even if feeling better",
        "🌡️ Monitor temperature regularly — malaria causes cyclical fevers",
        "💧 Stay hydrated — malaria causes significant fluid loss through sweating",
        "🚨 Return to doctor immediately if symptoms worsen despite medication"
    ],
    'typhoid': [
        "🍽️ Eat only well-cooked food — raw vegetables and salads are risky",
        "💧 Drink only boiled or bottled water during recovery",
        "💊 Complete the full antibiotic course — stopping early causes relapse",
        "🛏️ Rest completely — typhoid causes extreme fatigue",
        "🤲 Wash hands thoroughly before eating and after using the toilet",
        "🥣 Eat soft, easily digestible foods — khichdi, curd, bananas"
    ],
    'dengue': [
        "💧 Stay VERY well hydrated — drink ORS, coconut water, fruit juices",
        "🚫 NEVER take Aspirin or Ibuprofen — they increase bleeding risk",
        "✅ Paracetamol only for fever — under doctor supervision",
        "🩸 Monitor platelet count regularly as directed by doctor",
        "🦟 Prevent mosquito bites even during illness — protect others",
        "🚨 Seek emergency care for severe stomach pain, bleeding, or difficulty breathing"
    ],
    'anemia': [
        "🥩 Eat iron-rich foods — red meat, spinach, lentils, beans, tofu",
        "🍊 Pair iron with Vitamin C — lemon juice, oranges help absorb iron better",
        "☕ Avoid tea/coffee with meals — tannins block iron absorption",
        "💊 Take iron supplements as prescribed — don't skip doses",
        "🥛 Calcium and iron compete — take supplements at different times",
        "🛏️ Rest when tired — anemia reduces oxygen to muscles causing fatigue"
    ]
}

def get_health_tips(disease_name):
    """Return health tips for a disease if available."""
    disease_lower = disease_name.lower()
    for key, tips in HEALTH_TIPS.items():
        if key in disease_lower:
            return tips
    return None

def check_emergency(user_input):
    """Check if input contains emergency keywords."""
    user_lower = user_input.lower()
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in user_lower:
            return True
    return False

def find_matching_symptoms(user_input, symptoms_df):
    user_symptoms = [s.strip().lower() for s in user_input.split('and') if s.strip()]
    matches = []
    symptom_names = symptoms_df['name'].fillna('').str.lower().tolist()
    for user_sym in user_symptoms:
        fuzzy_matches = process.extractBests(user_sym, symptom_names, scorer=fuzz.partial_ratio, score_cutoff=70)
        for match, score in fuzzy_matches:
            original_name = symptoms_df[symptoms_df['name'].str.lower() == match]['name'].iloc[0]
            matches.append(original_name)
    return list(set(matches))

@st.cache_data
def load_data():
    base_path = Path(__file__).resolve().parent
    try:
        diseases = pd.read_csv(base_path / 'dia_3.csv')
        symptoms = pd.read_csv(base_path / 'symptoms2.csv')
        matrix = pd.read_csv(base_path / 'sym_dis_matrix.csv', index_col=0)
    except FileNotFoundError as e:
        st.error(f"File not found: {e}")
        return None, None, None, None

    disease_id_col = '_id' if '_id' in diseases.columns else 'id'
    symptom_id_col = '_id' if '_id' in symptoms.columns else 'id'

    diseases[disease_id_col] = pd.to_numeric(diseases[disease_id_col], errors='coerce')
    diseases = diseases.dropna(subset=[disease_id_col]).copy()
    diseases[disease_id_col] = diseases[disease_id_col].astype(int)
    diseases.set_index(disease_id_col, inplace=True)

    symptoms[symptom_id_col] = pd.to_numeric(symptoms[symptom_id_col], errors='coerce')
    symptoms = symptoms.dropna(subset=[symptom_id_col]).copy()
    symptoms[symptom_id_col] = symptoms[symptom_id_col].astype(int)
    symptoms.set_index(symptom_id_col, inplace=True)

    matrix.index = pd.to_numeric(matrix.index, errors='coerce')
    matrix = matrix.loc[~matrix.index.isna()].copy()
    matrix.index = matrix.index.astype(int)
    matrix.columns = pd.to_numeric(pd.Index(matrix.columns), errors='coerce')
    matrix = matrix.loc[:, ~pd.isna(matrix.columns)].copy()
    matrix.columns = matrix.columns.astype(int)

    medicines_path = base_path / 'medicines.csv'
    if medicines_path.exists():
        medicines = pd.read_csv(medicines_path)
    else:
        medicines = pd.DataFrame(columns=['medicine', 'uses', 'side_effects', 'dosage', 'interactions'])

    return diseases, symptoms, matrix, medicines

# ─── Drug Interactions ─────────────────────────────────────────────────────────
interactions = {
    ('Aspirin', 'Ibuprofen'): '🔴 HIGH RISK: Increased bleeding and stomach damage',
    ('Aspirin', 'Warfarin'): '🔴 CRITICAL: Dangerous bleeding risk - avoid combination',
    ('Ibuprofen', 'Naproxen'): '🟡 MEDIUM: Increased stomach bleeding risk',
    ('Paracetamol', 'Alcohol'): '🔴 HIGH RISK: Severe liver damage possible',
    ('Metformin', 'Alcohol'): '🟡 MEDIUM: Risk of lactic acidosis',
    ('Aspirin', 'Alcohol'): '🟡 MEDIUM: Increased stomach bleeding',
    ('Lisinopril', 'Potassium supplements'): '🔴 HIGH RISK: Dangerous potassium levels (hyperkalemia)',
    ('Amlodipine', 'Grapefruit'): '🟡 MEDIUM: Increases drug levels significantly',
    ('Atenolol', 'Insulin'): '🟡 MEDIUM: May mask low blood sugar symptoms',
    ('Metformin', 'Contrast dye'): '🔴 HIGH RISK: Kidney damage risk',
    ('Insulin', 'Alcohol'): '🔴 HIGH RISK: Dangerous low blood sugar',
    ('Glipizide', 'Aspirin'): '🟡 MEDIUM: Increased risk of low blood sugar',
    ('Amoxicillin', 'Birth control pills'): '🟡 MEDIUM: May reduce contraceptive effectiveness',
    ('Ciprofloxacin', 'Dairy products'): '🟡 MEDIUM: Reduces antibiotic absorption',
    ('Azithromycin', 'Antacids'): '🟡 MEDIUM: Take 1 hour apart',
    ('Omeprazole', 'Clopidogrel'): '🔴 HIGH RISK: Reduces blood thinner effectiveness',
    ('Ranitidine', 'Ketoconazole'): '🟡 MEDIUM: Reduces antifungal absorption',
    ('Warfarin', 'Vitamin K'): '🔴 HIGH RISK: Reduces anticoagulant effect',
    ('Warfarin', 'Green leafy vegetables'): '🟡 MEDIUM: Keep intake consistent',
    ('Clopidogrel', 'Omeprazole'): '🔴 HIGH RISK: Reduces effectiveness',
    ('Ibuprofen', 'Aspirin'): '🔴 HIGH RISK: Stomach bleeding risk',
    ('Acetaminophen', 'Warfarin'): '🟡 MEDIUM: May increase bleeding with high doses',
    ('Lisinopril', 'Ibuprofen'): '🟡 MEDIUM: Reduces blood pressure medication effectiveness',
    ('Prednisone', 'Ibuprofen'): '🔴 HIGH RISK: Severe stomach ulcer risk',
    ('Digoxin', 'Amoxicillin'): '🟡 MEDIUM: May increase digoxin levels',
    ('Warfarin', 'Fish oil'): '🟡 MEDIUM: Increased bleeding risk',
    ('Warfarin', 'Ginkgo biloba'): '🔴 HIGH RISK: Dangerous bleeding risk',
    ('Iron supplements', 'Calcium'): '🟡 MEDIUM: Take 2 hours apart for absorption',
    ('Metformin', 'Iodinated contrast'): '🔴 CRITICAL: Stop 48 hours before imaging',
    ('MAOIs', 'Tyramine foods'): '🔴 CRITICAL: Hypertensive crisis risk',
    ('Sildenafil', 'Nitrates'): '🔴 CRITICAL: Severe blood pressure drop - never combine',
}

# ─── Load Data ─────────────────────────────────────────────────────────────────
diseases, symptoms, matrix, medicines = load_data()
if diseases is None or symptoms is None or matrix is None:
    st.stop()

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MediAssist AI")
    st.markdown("*Your Personal Health Assistant*")
    st.divider()

    st.markdown("### 📊 Database Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{diseases.shape[0]}</div>
            <div class="stat-label">Diseases</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{symptoms.shape[0]}</div>
            <div class="stat-label">Symptoms</div>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(medicines) if not medicines.empty else 0}</div>
            <div class="stat-label">Medicines</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(interactions)}</div>
            <div class="stat-label">Interactions</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 💬 How to Use")
    st.markdown("""
    **🤒 Symptoms:**
    > "I have headache and fever"

    **💊 Medicine Info:**
    > "Aspirin info"

    **⚠️ Drug Interactions:**
    > "Aspirin and Warfarin"
    """)

    st.divider()

    st.markdown("### 🚨 Emergency Numbers")
    st.error("**108** — Ambulance (India)")
    st.warning("**112** — Police / Emergency")
    st.info("**104** — Health Helpline")

    st.divider()
    st.markdown("""
    <div style='text-align:center; color:#666; font-size:11px;'>
    ⚠️ Not a substitute for medical advice.<br>Always consult a qualified doctor.
    </div>
    """, unsafe_allow_html=True)

# ─── Main App ──────────────────────────────────────────────────────────────────
st.markdown("# 🏥 MediAssist AI — Health Chatbot")
st.markdown("*Describe symptoms, ask about medicines, or check drug interactions*")
st.divider()

# Init session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("type") == "emergency":
            st.markdown(message["content"], unsafe_allow_html=True)
        else:
            st.markdown(message["content"])
        if "chart" in message:
            st.plotly_chart(message["chart"], use_container_width=True)
        if "tips" in message:
            st.markdown(message["tips"], unsafe_allow_html=True)

# Chat input
prompt = st.chat_input("Describe symptoms, ask medicine info, or check interactions...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    user_input = prompt.lower()

    # ── 1. EMERGENCY DETECTION ──────────────────────────────────────────────────
    if check_emergency(user_input):
        emergency_content = """
        <div class="emergency-banner">
        🚨 EMERGENCY DETECTED — CALL 108 IMMEDIATELY! 🚨<br><br>
        📞 <strong>Ambulance: 108</strong> &nbsp;|&nbsp; 🆘 <strong>Emergency: 112</strong><br><br>
        Do NOT drive yourself. Stay calm and keep the patient still.<br>
        Stay on the line with the operator until help arrives.
        </div>
        """
        st.session_state.messages.append({
            "role": "assistant",
            "content": emergency_content,
            "type": "emergency"
        })
        with st.chat_message("assistant"):
            st.markdown(emergency_content, unsafe_allow_html=True)

    # ── 2. SYMPTOM PREDICTION ───────────────────────────────────────────────────
    else:
        matched_symptoms = find_matching_symptoms(user_input, symptoms)

        if matched_symptoms:
            sym_ids = symptoms[symptoms['name'].isin(matched_symptoms)].index.tolist()
            available_sym_ids = [sym_id for sym_id in sym_ids if sym_id in matrix.index]

            if available_sym_ids:
                scores = matrix.loc[available_sym_ids].sum(axis=0)
                top_diseases = scores.nlargest(3).index.tolist()

                response = f"**Symptoms detected:** {', '.join(matched_symptoms)}\n\n"
                response += "**Top 3 possible conditions:**\n\n"

                disease_names = []
                probabilities = []
                all_tips = None

                for i, dis_id in enumerate(top_diseases):
                    if dis_id not in diseases.index:
                        continue
                    dis_name = diseases.loc[dis_id, 'diagnose']
                    score = scores[dis_id]
                    prob = min((score / len(available_sym_ids)) * 100, 100)
                    emoji = ["🥇", "🥈", "🥉"][i]
                    response += f"{emoji} **{dis_name}** — {prob:.1f}% match\n\n"
                    disease_names.append(dis_name)
                    probabilities.append(prob)

                    # Get tips for the top disease
                    if i == 0 and all_tips is None:
                        tips = get_health_tips(dis_name)
                        if tips:
                            all_tips = tips
                            all_tips_disease = dis_name

                response += "\n⚠️ **Medical Disclaimer:** This is not medical advice. Please consult a qualified doctor for proper diagnosis and treatment."

                # Chart with fixed label display
                short_names = [name[:30] + "..." if len(name) > 30 else name for name in disease_names]
                fig = px.bar(
                    x=short_names,
                    y=probabilities,
                    labels={'x': 'Condition', 'y': 'Match %'},
                    title="🏥 Disease Prediction Analysis",
                    color=probabilities,
                    color_continuous_scale='Blues',
                    text=[f"{p:.1f}%" for p in probabilities]
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    yaxis_range=[0, 115],
                    showlegend=False,
                    height=380,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e0e0e0'),
                    xaxis=dict(tickangle=0),
                    coloraxis_showscale=False,
                    margin=dict(t=50, b=20)
                )

                # Build health tips HTML
                tips_html = ""
                if all_tips:
                    tips_html = f"""
                    <div class="health-tip-card">
                    <strong>💡 Health Tips for {all_tips_disease}:</strong><br><br>
                    {"<br>".join(all_tips)}
                    </div>
                    """

                msg = {
                    "role": "assistant",
                    "content": response,
                    "chart": fig
                }
                if tips_html:
                    msg["tips"] = tips_html

                st.session_state.messages.append(msg)
                with st.chat_message("assistant"):
                    st.markdown(response)
                    st.plotly_chart(fig, use_container_width=True)
                    if tips_html:
                        st.markdown(tips_html, unsafe_allow_html=True)

            else:
                response = "⚠️ Symptoms recognized but not found in database. Try different keywords."
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)

        # ── 3. MEDICINE INFO ────────────────────────────────────────────────────
        elif 'medicine' in medicines.columns and not medicines.empty and any(
            med.lower() in user_input for med in medicines['medicine'].dropna().astype(str)
        ):
            med_name = next(med for med in medicines['medicine'] if str(med).lower() in user_input)
            med_info = medicines[medicines['medicine'] == med_name].iloc[0]
            response = f"""### 💊 {med_name} Information

**Uses:** {med_info['uses']}

**Side Effects:** {med_info['side_effects']}

**Dosage:** {med_info['dosage']}

**Known Interactions:** {med_info['interactions']}

⚠️ *Always follow your doctor's prescription. Do not self-medicate.*"""
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

        # ── 4. DRUG INTERACTION CHECK ───────────────────────────────────────────
        elif 'and' in user_input and 'medicine' in medicines.columns and not medicines.empty:
            medicine_lookup = {str(med).lower(): str(med) for med in medicines['medicine'].dropna().astype(str)}
            meds = [medicine_lookup[m.strip()] for m in user_input.split('and') if m.strip() in medicine_lookup]

            if len(meds) >= 2:
                key = tuple(sorted(meds[:2]))
                warning = interactions.get(key, "✅ No known major interactions found – but always consult your pharmacist or doctor!")
                response = f"""### ⚠️ Drug Interaction Check

**Checking:** `{meds[0]}` + `{meds[1]}`

**Result:** {warning}

💡 *Always inform your doctor about ALL medications, supplements, and vitamins you are taking.*"""
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
            else:
                response = "Please specify two medicines to check (e.g., 'Aspirin and Warfarin')"
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)

        # ── 5. FALLBACK ─────────────────────────────────────────────────────────
        else:
            response = """I can help you with:

🤒 **Symptom Check** — *"I have headache and fever"*
💊 **Medicine Info** — *"Aspirin info"*
⚠️ **Drug Interactions** — *"Aspirin and Warfarin"*
🚨 **Emergency** — *"chest pain"* → Calls 108!

Please try one of the above formats."""
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
