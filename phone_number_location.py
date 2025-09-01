from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import requests
import os

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/get_info", methods=["POST"])
def get_info():
    try:
        data = request.get_json()
        number = data.get("number")

        if not number:
            return jsonify({"error": "No number provided"}), 400

        parsed_number = phonenumbers.parse(number)

        # Basic details
        country = geocoder.country_name_for_number(parsed_number, "en")
        region = geocoder.description_for_number(parsed_number, "en")
        provider = carrier.name_for_number(parsed_number, "en")
        timezones = timezone.time_zones_for_number(parsed_number)
        valid = phonenumbers.is_valid_number(parsed_number)
        line_type = phonenumbers.number_type(parsed_number)
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        # Get coordinates (via external API)
        try:
            resp = requests.get(f"https://nominatim.openstreetmap.org/search?q={region}&format=json").json()
            coordinates = {
                "lat": resp[0]["lat"],
                "lon": resp[0]["lon"]
            } if resp else {}
        except Exception:
            coordinates = {}

        result = {
            "Country": country,
            "Region/Area": region,
            "City/Location": region,
            "Carrier": provider,
            "Line Type": str(line_type),
            "Timezone": timezones,
            "Formatted Number": formatted_number,
            "Country Code": parsed_number.country_code,
            "Validity": "Valid" if valid else "Invalid",
            "Coordinates": coordinates
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
