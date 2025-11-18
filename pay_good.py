import requests
import base64
import json
import uuid


class PayClass:
    # ----------------------------------------------------------
    # 🔧 FILL THESE WITH YOUR REAL MTN MOMO CREDENTIALS
    # ----------------------------------------------------------
    subscriptionKey = "4bfc7b16eda84b099329dd273c82a304"
    apiUser = "d83b5778-06aa-44d1-941d-251b248cade8"           # X-Reference-Id used when API user was created
    apiKey = "d4078f2c56594c6cb77377a0a4ec4abc"             # API Key returned when generating API key

    # ----------------------------------------------------------
    # Generate Basic Auth token (Base64 encoding)
    # ----------------------------------------------------------
    @staticmethod
    def get_basic_auth():
        text = f"{PayClass.apiUser}:{PayClass.apiKey}"
        encoded = base64.b64encode(text.encode()).decode()
        return f"Basic {encoded}"

    # ----------------------------------------------------------
    # Obtain access token from MoMo API
    # ----------------------------------------------------------
    @staticmethod
    def momotoken():
        try:
            url = "https://proxy.momoapi.mtn.com/collection/token/"

            headers = {
                "Ocp-Apim-Subscription-Key": PayClass.subscriptionKey,
                "Authorization": PayClass.get_basic_auth()
            }

            response = requests.post(url, headers=headers)

            print("TOKEN RAW RESPONSE:", response.text)

            if response.status_code != 200:
                print("❌ Token Error:", response.status_code, response.text)
                return None

            return response.json()

        except Exception as e:
            print("❌ Exception in momotoken():", e)
            return None

    # ----------------------------------------------------------
    # Trigger a request to pay (Collections API)
    # ----------------------------------------------------------
    @staticmethod
    def momopay(amount, currency, message, phone, payerName):
        # 1. Get Access Token
        token_data = PayClass.momotoken()

        if token_data is None:
            return {"status": "failed", "reason": "Token generation failed"}

        access_token = token_data["access_token"]

        # 2. Prepare RequestToPay URL
        url = "https://proxy.momoapi.mtn.com/collection/v1_0/requesttopay"

        # 3. Unique transaction reference
        reference = str(uuid.uuid4())

        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Reference-Id": reference,
            "X-Target-Environment": "mtnbenin",
            "Ocp-Apim-Subscription-Key": PayClass.subscriptionKey,
            "Content-Type": "application/json"
        }

        body = {
            "amount": str(amount),
            "currency": currency,
            "externalId": "123456",
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone
            },
            "payerMessage": message,
            "payeeNote": payerName
        }

        print("PAY BODY:", body)

        try:
            response = requests.post(url, headers=headers, json=body)

            print("PAY RAW RESPONSE:", response.text)

            if response.status_code in [200, 202]:
                return {
                    "status": "success",
                    "transaction_ref": reference,
                    "detail": response.text
                }

            return {
                "status": "failed",
                "http_code": response.status_code,
                "response": response.text
            }

        except Exception as e:
            print("❌ Exception in momopay():", e)
            return {"status": "error", "reason": str(e)}

