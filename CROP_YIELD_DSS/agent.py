from openai import OpenAI
from ml_api.gemma_tools import predict_yield_simple
import difflib

# -----------------------------
# LLM CLIENT (LM Studio)
# -----------------------------
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

# -----------------------------
# ALLOWED COUNTIES (TRAIN DOMAIN)
# -----------------------------
ALLOWED_COUNTIES = {
    "nakuru": {"lat": -0.3031, "lon": 36.0800},
    "nyandarua": {"lat": -0.1800, "lon": 36.5220},
    "trans nzoia": {"lat": 1.0567, "lon": 34.9500}
}

# -----------------------------
# INTENT DETECTION (LLM)
# -----------------------------
def detect_intent(user_input):
    try:
        response = client.chat.completions.create(
            model="google/gemma-4-e4b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify the user's intent.\n"
                        "Return ONLY one word:\n"
                        "- PREDICT_YIELD (if user wants yield prediction)\n"
                        "- GENERAL (for everything else)"
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "GENERAL"


# -----------------------------
# COUNTY EXTRACTION (RULE-BASED)
# -----------------------------

def normalize_text(text):
    return text.lower().replace("-", " ").replace("_", " ").strip()


def extract_county(user_input):
    text = normalize_text(user_input)

    # direct match
    for county in ALLOWED_COUNTIES:
        if county in text:
            return county

    # fuzzy match (handles typos like "transnzoia")
    words = text.split()

    for word in words:
        matches = difflib.get_close_matches(word, ALLOWED_COUNTIES.keys(), n=1, cutoff=0.7)
        if matches:
            return matches[0]

    # phrase-level fuzzy match (for "transnzoia" as one word)
    matches = difflib.get_close_matches(text, ALLOWED_COUNTIES.keys(), n=1, cutoff=0.6)
    if matches:
        return matches[0]

    return None
# -----------------------------
# MAIN HANDLER
# -----------------------------
def handle_query(user_input):

    intent = detect_intent(user_input)

    # -----------------------------------
    # PREDICTION FLOW
    # -----------------------------------
    if intent == "PREDICT_YIELD":

        county = extract_county(user_input)

        # ❌ No valid county
        if not county:
            return (
                "⚠️ Please specify a supported county.\n\n"
                "Supported counties:\n"
                "- Nakuru\n"
                "- Nyandarua\n"
                "- Trans Nzoia\n\n"
                "Example:\n"
                "'Predict maize yield in Nakuru'"
            )

        coords = ALLOWED_COUNTIES[county]

        # Baseline features (next upgrade = dynamic extraction)
        features = {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "precip_total": 650,
            "temp_mean": 23,
            "fertilizer": 120
        }

        try:
            result = predict_yield_simple(features)

            return (
                f"🌽 Predicted maize yield in {county.title()}: {result['predicted_yield']} tons/ha\n"
                f"• RF Model: {result['rf']}\n"
                f"• DSSAT Model: {result['dssat']}"
            )

        except Exception as e:
            return f"❌ Prediction failed: {str(e)}"

    # -----------------------------------
    # GENERAL LLM RESPONSE
    # -----------------------------------
    try:
        response = client.chat.completions.create(
            model="google/gemma-4-e4b",
            messages=[
                {"role": "system", "content": "You are an agricultural AI assistant."},
                {"role": "user", "content": user_input}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ LLM error: {str(e)}"


# -----------------------------
# CLI LOOP
# -----------------------------
if __name__ == "__main__":
    while True:
        user_input = input("\nAsk something: ")
        print("\nGemma says:\n")
        print(handle_query(user_input))