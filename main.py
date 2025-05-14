import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, request, jsonify, make_response
import json
import requests # Added for Airtable integration

app = Flask(__name__, template_folder="templates", static_folder="static")

# User-provided Airtable API Key
AIRTABLE_API_KEY = "patPlaukIFlDNaeIU.e3b3f3c274a745298437bbe62529d459bc2b5a4da50bb1842e6df73e3bbda0c3"
# User-provided Airtable Table Name
AIRTABLE_TABLE_NAME = "customers"
# User-provided Airtable Base ID
AIRTABLE_BASE_ID = "appykIGCgr5PfBQMp"

@app.route("/")
def roi_calculator_page():
    return render_template("roi_calculator.html")

@app.route("/submit_roi_data", methods=["POST"])
def submit_roi_data():
    try:
        data = request.get_json()
        print("Received data for submission:", json.dumps(data, indent=2, ensure_ascii=False))
        
        # Airtable Integration
        if not AIRTABLE_BASE_ID:
            print("Airtable Base ID not configured. Skipping Airtable submission.")
            return jsonify({"message": "Data received. Airtable integration pending Base ID on server."}), 200 # Still acknowledge data receipt

        if not AIRTABLE_API_KEY or not AIRTABLE_TABLE_NAME:
            print("Airtable API Key or Table Name is missing. Skipping Airtable submission.")
            return jsonify({"message": "Airtable configuration incomplete on server side."}), 500

        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        
        # Field names as previously suggested, user confirmed names are not critical.
        # Ensure these fields exist in the Airtable base or that Airtable can create them.
        airtable_payload = {
            "records": [
                {
                    "fields": {
                        "Email": data.get("email"),
                        "Тип бизнеса": data.get("businessType"),
                        "Размер компании": int(data.get("companySize", 0)) if data.get("companySize") else None,
                        "Годовой оборот": float(data.get("annualRevenue", 0)) if data.get("annualRevenue") else None,
                        "Средняя ЗП": float(data.get("avgSalary", 0)) if data.get("avgSalary") else None,
                        "Автоматизация Маркетинга (%)": int(data.get("marketingAutomation", 0)) if data.get("marketingAutomation") else None,
                        "Автоматизация Поддержки (%)": int(data.get("customerServiceAutomation", 0)) if data.get("customerServiceAutomation") else None,
                        "Автоматизация Операций (%)": int(data.get("operationsAutomation", 0)) if data.get("operationsAutomation") else None,
                        "Автоматизация HR (%)": int(data.get("hrAutomation", 0)) if data.get("hrAutomation") else None,
                        "Автоматизация Финансов (%)": int(data.get("financeAutomation", 0)) if data.get("financeAutomation") else None,
                        "Инвестиции в AI (RUB)": float(data.get("aiInvestment", 0)) if data.get("aiInvestment") else None,
                        "Время внедрения (мес)": int(data.get("implementationTime", 0)) if data.get("implementationTime") else None,
                        "Экономия времени (час/год)": data.get("timeSaved"),
                        "Экономия затрат (RUB/год)": data.get("costSavings"),
                        "Рост выручки (RUB/год)": data.get("revenueIncrease"),
                        "ROI (%)": data.get("roiValue"),
                        "Срок окупаемости (мес)": data.get("paybackPeriod")
                    }
                }
            ]
        }
        
        print(f"Attempting to send data to Airtable: {airtable_url}")
        print(f"Payload: {json.dumps(airtable_payload, indent=2, ensure_ascii=False)}")

        response = requests.post(airtable_url, headers=headers, json=airtable_payload)
        
        if response.status_code == 200:
            print("Data successfully sent to Airtable.")
            print(f"Airtable response: {response.json()}")
            return jsonify({"message": "Data received and successfully sent to Airtable."}), 200
        else:
            print(f"Error sending data to Airtable: {response.status_code} - {response.text}")
            return jsonify({"message": "Error saving data to Airtable", "details": response.text, "status_code": response.status_code}), 500

    except Exception as e:
        print(f"Error processing request in /submit_roi_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Error processing request", "error": str(e)}), 500

if __name__ == "__main__":
    if not AIRTABLE_BASE_ID:
        print("Warning: AIRTABLE_BASE_ID is not set. Airtable integration will be skipped if not provided by user.")
    app.run(debug=True, host="0.0.0.0", port=5000)

