import os
import phonenumbers
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from phonenumbers import geocoder, carrier, timezone

# Ensure templates folder is used
app = Flask(__name__, template_folder="templates")
CORS(app)

def build_response_from_number(raw_number: str):
    """
    Parse phone number and build normalized JSON response.
    Returns (payload_dict, http_status_code)
    """
    if not raw_number:
        return {"error": "No number provided"}, 400

    try:
        # Parse number (let libphonenumber infer region from the E.164 input)
        parsed_number = phonenumbers.parse(raw_number, None)
    except Exception:
        return {"error": "Invalid phone number format"}, 400

    # Validate number
    is_valid = phonenumbers.is_valid_number(parsed_number)

    # Basic fields (safe to compute even if invalid; library still returns formats)
    country_or_description = geocoder.description_for_number(parsed_number, "en") or ""
    region_code = phonenumbers.region_code_for_number(parsed_number) or ""
    carrier_name = carrier.name_for_number(parsed_number, "en") or ""
    timezones = list(timezone.time_zones_for_number(parsed_number) or [])
    formatted_number = phonenumbers.format_number(
        parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
    ) or ""
    line_type = phonenumbers.number_type(parsed_number)  # int enum

    # Optional coordinates via ipinfo (country-level), requires token
    latitude, longitude = "", ""
    ipinfo_token = os.environ.get("IPINFO_TOKEN", "").strip()
    if ipinfo_token and region_code:
        try:
            # ipinfo.io/{COUNTRY_CODE}?token=TOKEN returns e.g. { "country": "IN", "loc": "20.5937,78.9629", ... }
            resp = requests.get(
                f"https://ipinfo.io/{region_code}?token={ipinfo_token}",
                timeout=5
            )
            if resp.status_code == 200:
                loc = resp.json().get("loc")
                if loc and "," in loc:
                    latitude, longitude = loc.split(",", 1)
        except Exception:
            # Silently ignore external API errors; coordinates remain blank
            pass

    payload = {
        "Country": country_or_description,             # as in your original UI
        "Region/Area": region_code,
        "Carrier": carrier_name,
        "Line Type": str(line_type),                   # keep original field type (stringified enum)
        "Timezone": timezones,                         # array; UI joins safely
        "Formatted Number": formatted_number,
        "Country Code": str(parsed_number.country_code),
        "Validity": bool(is_valid),                    # BOOLEAN for your frontend ternary
        "Coordinates": f"{latitude},{longitude}" if latitude and longitude else ""
    }

    return payload, 200

@app.route("/", methods=["GET"])
def home():
    # Serve the UI
    return render_template("index.html")

# Frontend expects POST /lookup with { phone }
@app.route("/lookup", methods=["POST"])
def lookup():
    try:
        data = request.get_json(silent=True) or {}
        number = data.get("phone") or data.get("number")  # accept either
        payload, code = build_response_from_number(number)
        return jsonify(payload), code
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

# Backward-compat endpoint kept intact
@app.route("/get_info", methods=["POST"])
def get_info():
    try:
        data = request.get_json(silent=True) or {}
        number = data.get("number") or data.get("phone")  # accept either
        payload, code = build_response_from_number(number)
        return jsonify(payload), code
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Bind on all interfaces for Render
    app.run(host="0.0.0.0", port=port)
