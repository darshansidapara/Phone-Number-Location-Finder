import os
import phonenumbers
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from phonenumbers import geocoder, carrier, timezone

# --- Path Configuration (The Robust Fix) ---
# Get the absolute path of the directory where this script is located.
base_dir = os.path.abspath(os.path.dirname(__file__))
# Define the paths to the templates and static folders relative to the script's location.
template_folder = os.path.join(base_dir, 'app', 'templates')
static_folder = os.path.join(base_dir, 'app', 'static')

# Initialize the Flask app with the correct folder paths
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
CORS(app)

# --- Routes ---

# Route to serve the main HTML page (your frontend)
@app.route("/")
def home():
    return render_template("index.html")

# Route for the API to process the phone number
@app.route("/get_info", methods=["POST"])
def get_info():
    try:
        # Ensure the request has JSON data
        if not request.is_json:
            return jsonify({"error": "Invalid request: Content-Type must be application/json"}), 415

        data = request.get_json()
        number = data.get("number")

        if not number:
            return jsonify({"error": "No phone number provided"}), 400

        # Parse the phone number
        parsed_number = phonenumbers.parse(number, None)

        # Check if the number is valid before proceeding
        if not phonenumbers.is_valid_number(parsed_number):
            return jsonify({"error": "The provided phone number is not valid"}), 400

        # Gather all information
        country = geocoder.description_for_number(parsed_number, "en")
        region = phonenumbers.region_code_for_number(parsed_number)
        carrier_name = carrier.name_for_number(parsed_number, "en") or "Not Available"
        timezones = timezone.time_zones_for_number(parsed_number)
        formatted_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        
        # Return a clean JSON response
        return jsonify({
            "Country": country,
            "Region": region,
            "Carrier": carrier_name,
            "Timezone": timezones[0] if timezones else "Not Available",
            "Formatted Number": formatted_number,
            "Country Code": str(parsed_number.country_code),
            "Validity": "Valid"
        })

    except phonenumbers.phonenumberutil.NumberParseException as e:
        return jsonify({"error": f"Error parsing number: {e}"}), 400
    except Exception as e:
        # Generic error handler for unexpected issues
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# This part is for local development and is ignored by Gunicorn on Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
