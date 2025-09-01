from flask import Flask, request, jsonify
import phonenumbers
from phonenumbers import timezone, geocoder, carrier
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Allow frontend to access backend

# Replace with your OpenCage API key (get free from https://opencagedata.com/api)
OPENCAGE_API_KEY = "YOUR_OPENCAGE_API_KEY"

@app.route("/api/phone", methods=["POST"])
def phone_lookup():
    data = request.get_json()
    number = data.get("phone")

    try:
        phoneNumber = phonenumbers.parse(number)

        # Location name from phonenumbers
        location_name = geocoder.description_for_number(phoneNumber, "en")

        # Default empty coordinates
        coordinates = {"lat": "", "lng": ""}

        # Fetch coordinates if location available
        if location_name:
            geo_url = f"https://api.opencagedata.com/geocode/v1/json?q={location_name}&key={OPENCAGE_API_KEY}"
            geo_res = requests.get(geo_url).json()
            if geo_res.get("results"):
                coords = geo_res["results"][0]["geometry"]
                coordinates = {"lat": coords["lat"], "lng": coords["lng"]}

        response = {
            "country": geocoder.country_name_for_number(phoneNumber, "en"),
            "region": phonenumbers.region_code_for_number(phoneNumber),
            "carrier": carrier.name_for_number(phoneNumber, "en"),
            "line_type": str(phonenumbers.number_type(phoneNumber)),
            "timezone": str(timezone.time_zones_for_number(phoneNumber)),
            "formatted_number": phonenumbers.format_number(phoneNumber, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "country_code": str(phoneNumber.country_code),
            "validity": "Valid" if phonenumbers.is_valid_number(phoneNumber) else "Not Valid",
            "coordinates": coordinates
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
