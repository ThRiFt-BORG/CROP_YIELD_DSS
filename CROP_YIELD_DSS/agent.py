from openai import OpenAI
from ml_api.gemma_tools import predict_yield_simple
from feature_extractor import extract_features, extract_county, COUNTY_GEO

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

# -----------------------------
# COUNTY PROFILES
# -----------------------------
COUNTY_PROFILES = {
    "nakuru": {
        "avg_precip": 650,
        "avg_yield": 4.1,
        "avg_fertilizer": 120,
        "description": "Rift Valley highlands"
    },
    "nyandarua": {
        "avg_precip": 900,
        "avg_yield": 4.8,
        "avg_fertilizer": 130,
        "description": "Cooler highland zone"
    },
    "trans nzoia": {
        "avg_precip": 1100,
        "avg_yield": 5.3,
        "avg_fertilizer": 140,
        "description": "High potential maize zone"
    }
}

# -----------------------------
# INTENT DETECTION
# -----------------------------
def detect_intent(user_input: str) -> str:
    try:
        response = client.chat.completions.create(
            model="google/gemma-4-e4b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify intent. Return ONLY one word:\n"
                        "- PREDICT_YIELD if user is asking for maize yield prediction "
                        "(including implicit ones like 'yield in Nakuru', 'how much maize...', 'expected production')\n"
                        "- GENERAL for other questions."
                    )
                },
                {"role": "user", "content": user_input}
            ],
            temperature=0.0,
            max_tokens=10
        )
        intent = response.choices[0].message.content.strip().upper()
        return "PREDICT_YIELD" if "PREDICT" in intent or "YIELD" in intent else "GENERAL"
    except Exception:
        text = user_input.lower()
        if any(k in text for k in ["yield", "predict maize", "maize in", "expected yield", "tons"]):
            return "PREDICT_YIELD"
        return "GENERAL"


# -----------------------------
# FEATURE VALIDATION
# -----------------------------
def validate_features(features: dict) -> dict:
    """Clamp unrealistic values"""
    f = features.copy()
    if f.get("precip_total") is not None:
        f["precip_total"] = max(300, min(2000, f["precip_total"]))
    if f.get("fertilizer") is not None:
        f["fertilizer"] = max(0, min(300, f["fertilizer"]))
    if f.get("temp_mean") is not None:
        f["temp_mean"] = max(15, min(32, f["temp_mean"]))
    return f


# -----------------------------
# PEST RISK ASSESSMENT
# -----------------------------
def calculate_pest_risks(features: dict) -> dict:
    temp = features.get("temp_mean", 23.0)
    precip = features.get("precip_total", 650.0)
    
    risks = {}
    
    # Fall Armyworm
    temp_score = max(0, min(1.0, (temp - 15) / 15))
    precip_score = max(0, min(1.0, precip / 900))
    faw_risk = min(1.0, 0.6 * temp_score + 0.4 * precip_score)
    
    risks["faw"] = {
        "risk_index": round(faw_risk, 2),
        "risk_level": "HIGH" if faw_risk > 0.75 else "MEDIUM" if faw_risk > 0.45 else "LOW",
        "name": "Fall Armyworm"
    }
    
    # Maize Stemborer
    stemborer_risk = min(1.0, 0.7 * temp_score + 0.3 * (precip / 1100))
    risks["stemborer"] = {
        "risk_index": round(stemborer_risk, 2),
        "risk_level": "HIGH" if stemborer_risk > 0.70 else "MEDIUM" if stemborer_risk > 0.40 else "LOW",
        "name": "Maize Stemborer"
    }
    
    return risks


def get_pest_summary(risks: dict) -> str:
    summary = [f"• {pest['name']}: {pest['risk_level']} risk" for pest in risks.values()]
    return "\n".join(summary)


# -----------------------------
# AGRONOMIC INSIGHTS (FIXED)
# -----------------------------
def generate_agronomic_insights(result: dict, features: dict, county: str, used: list) -> str:
    """Generate contextual agronomic insights"""
    profile = COUNTY_PROFILES.get(county, {})
    
    context = f"""
County: {county.title()}
Predicted Yield: {result['predicted_yield']} tons/ha
RF Contribution: {result['rf']} t/ha
DSSAT Contribution: {result['dssat']} t/ha
Rainfall: {features.get('precip_total')} mm
Temperature: {features.get('temp_mean')} °C
Fertilizer: {features.get('fertilizer')} kg/ha
County average yield: ~{profile.get('avg_yield', '4.0')} t/ha
"""

    system_prompt = (
        "You are an experienced Kenyan agronomist specializing in maize farming in the Rift Valley. "
        "Give short, practical, and honest insights in simple language that a farmer can understand. "
        "Highlight whether the yield is good/average/low, mention the main limiting factor, "
        "and give one clear actionable recommendation."
    )

    try:
        response = client.chat.completions.create(
            model="google/gemma-4-e4b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this maize yield prediction and give insights:\n{context}"}
            ],
            temperature=0.7,
            max_tokens=180
        )
        insight = response.choices[0].message.content.strip()
        return insight if insight else "No additional insights available."
    
    except Exception as e:
        print(f"[Debug] Insights generation failed: {e}")  # Helpful for debugging
        return "Insights generation is temporarily unavailable."


# -----------------------------
# MAIN HANDLER
# -----------------------------
def handle_query(user_input: str):
    intent = detect_intent(user_input)

    if intent == "PREDICT_YIELD":
        extracted = extract_features(user_input)
        county = extracted.get("county") or extract_county(user_input)

        if not county or county not in COUNTY_GEO:
            return (
                "⚠️ Please specify a supported county (Nakuru, Nyandarua, or Trans Nzoia).\n"
                "Example: Predict maize yield in Nakuru with 800mm rainfall and 150 fertilizer"
            )

        geo = COUNTY_GEO[county]

        # Build features
        features = {
            "year": 2024,
            "lat": geo["lat"],
            "lon": geo["lon"],
            "ndvi_mean": 0.55,
            "precip_total": extracted.get("precip_total") or 650,
            "gdd_total": 1400,
            "elevation": geo["elevation"],
            "soil_texture": geo["soil_texture"],
            "fertilizer": extracted.get("fertilizer") or 120,
            "temp_mean": extracted.get("temp_mean") or 23,
        }

        features = validate_features(features)

        # Track user inputs
        used = []
        if extracted.get("precip_total") is not None:
            used.append(f"{extracted['precip_total']}mm rainfall")
        if extracted.get("fertilizer") is not None:
            used.append(f"{extracted['fertilizer']} kg/ha fertilizer")
        if extracted.get("temp_mean") is not None:
            used.append(f"{extracted['temp_mean']}°C")

        try:
            result = predict_yield_simple(features)
            pests = calculate_pest_risks(features)
            insights = generate_agronomic_insights(result, features, county, used)

            response = f"🌽 **Predicted maize yield in {county.title()}**: {result['predicted_yield']} tons/ha\n\n"
            response += f"• Random Forest : {result['rf']} tons/ha\n"
            response += f"• DSSAT simulation : {result['dssat']} tons/ha\n\n"
            
            response += "🐛 **Pest Risk Assessment**:\n"
            response += get_pest_summary(pests) + "\n\n"
            
            response += "💡 **Agronomist Insights**:\n"
            response += insights + "\n"

            if used:
                response += f"\n📊 Used your inputs: {', '.join(used)}"
            else:
                response += f"\n📊 Using {county.title()} average seasonal conditions."

            return response

        except Exception as e:
            return f"❌ Prediction failed: {str(e)}"

    # General conversation
    try:
        response = client.chat.completions.create(
            model="google/gemma-4-e4b",
            messages=[
                {"role": "system", "content": "You are a helpful agricultural AI assistant for Kenyan maize farmers."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"


# -----------------------------
# CLI
# -----------------------------
if __name__ == "__main__":
    print("🌾 GeoAI Crop Yield + Pest Risk + Insights Agent (Kenya) Ready\n")
    while True:
        user_input = input("Ask something: ").strip()
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye 👋")
            break
        if user_input:
            print("\nGemma says:\n")
            print(handle_query(user_input))