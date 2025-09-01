import os
import phonenumbers
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from phonenumbers import geocoder, carrier, timezone

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")
CORS(app)

# Serve frontend
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_info", methods=["POST"])
def get_info():
    try:
        data = request.get_json()
        number = data.get("number")

        if not number:
            return jsonify({"error": "No number provided"}), 400

        parsed_number = phonenumbers.parse(number, None)

        country = geocoder.description_for_number(parsed_number, "en")
        region = phonenumbers.region_code_for_number(parsed_number)
        carrier_name = carrier.name_for_number(parsed_number, "en")
        timezones = timezone.time_zones_for_number(parsed_number)
        valid = phonenumbers.is_valid_number(parsed_number)
        formatted_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        line_type = phonenumbers.number_type(parsed_number)

        latitude, longitude = "", ""
        try:
            token = os.environ.get("IPINFO_TOKEN", "")  # safer: use env variable
            if token:
                resp = requests.get(f"https://ipinfo.io/{region}?token={token}")
                if resp.status_code == 200:
                    loc = resp.json().get("loc")
                    if loc:
                        latitude, longitude = loc.split(",")
        except Exception:
            pass

        return jsonify({
            "Country": country,
            "Region/Area": region,
            "Carrier": carrier_name,
            "Line Type": str(line_type),
            "Timezone": timezones,
            "Formatted Number": formatted_number,
            "Country Code": str(parsed_number.country_code),
            "Validity": "Valid" if valid else "Invalid",
            "Coordinates": f"{latitude},{longitude}" if latitude and longitude else ""
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
