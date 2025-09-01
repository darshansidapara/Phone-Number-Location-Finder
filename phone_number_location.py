import os
import phonenumbers
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from phonenumbers import geocoder, carrier, timezone

app = Flask(__name__)
CORS(app)

@app.route("/get_info", methods=["POST"])
def get_info():
    try:
        data = request.get_json()
        number = data.get("number")

        if not number:
            return jsonify({"error": "No number provided"}), 400

        # Parse number
        parsed_number = phonenumbers.parse(number, None)

        # Details from phonenumbers
        country = geocoder.description_for_number(parsed_number, "en")
        region = phonenumbers.region_code_for_number(parsed_number)
        carrier_name = carrier.name_for_number(parsed_number, "en")
        timezones = timezone.time_zones_for_number(parsed_number)
        valid = phonenumbers.is_valid_number(parsed_number)
        formatted_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        line_type = phonenumbers.number_type(parsed_number)

        # Default coordinates empty
        latitude, longitude = "", ""

        # Try external API for coords (ipinfo)
        try:
            resp = requests.get(f"https://ipinfo.io/{region}?token=YOUR_TOKEN_HERE")
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
