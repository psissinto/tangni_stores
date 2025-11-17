from flask import Flask, request, jsonify, render_template_string
from pay import PayClass

app = Flask(__name__)

# -----------------------------------------------------------
# Mobile UI Page (Background Laundry Image)
# -----------------------------------------------------------
MOBILE_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>MoMo Payment</title>

<style>
    body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        background-image: url('/static/laundry.jpg');
        background-size: cover;
        background-position: center;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        text-shadow: 1px 1px 3px black;
    }

    .container {
        backdrop-filter: blur(3px);
        background: rgba(0, 0, 0, 0.45);
        padding: 25px;
        width: 90%;
        max-width: 400px;
        border-radius: 12px;
        text-align: center;
    }

    input, button {
        width: 100%;
        padding: 15px;
        margin-top: 12px;
        border-radius: 10px;
        border: none;
        font-size: 18px;
    }

    input {
        background: rgba(255, 255, 255, 0.9);
    }

    button {
        background: #FFCC00;
        color: #000;
        font-weight: bold;
    }

    button:active {
        background: #e6b800;
    }
</style>

</head>
<body>

<div class="container">
    <h2>💳 MTN MoMo Laundry Payment</h2>
    <p>Amount: <b>540 XOF</b></p>

    <form action="/momo/pay" method="get">

        <input type="text" name="phone" placeholder="Enter Phone Number (MSISDN)" required>

        <input type="text" name="payer" placeholder="Your Name" required>

        <button type="submit">Pay 540 XOF</button>
    </form>
</div>

</body>
</html>
"""

# -----------------------------------------------------------
# Home Page
# -----------------------------------------------------------
@app.route("/")
def home_screen():
    return render_template_string(MOBILE_PAGE)


# -----------------------------------------------------------
# MoMo Payment Endpoint (amount fixed to 540)
# -----------------------------------------------------------
@app.route("/momo/pay", methods=["GET"])
def momo_qr_pay():
    
    amount = "540"                                     # 🔒 FIXED AMOUNT
    phone  = request.args.get("phone")                 # REQUIRED
    payer  = request.args.get("payer")                 # REQUIRED
    message = "Laundry Payment"                        # optional fixed message

    if not phone or not payer:
        return jsonify({"status": "failed", "reason": "Phone and payer name required"}), 400

    result = PayClass.momopay(amount, "XOF", message, phone, payer)
    return jsonify(result)


# -----------------------------------------------------------
# Run Server
# -----------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

