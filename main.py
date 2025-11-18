from flask import Flask, request, jsonify, render_template_string
from pay import PayClass
import time
import os

app = Flask(__name__)

# -----------------------------------------------------------
# Mobile UI Page – Phone + Name
# -----------------------------------------------------------
HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>MoMo Laundry Payment</title>

<style>
    body {
        margin: 0;
        padding: 0;
        font-family: Arial;
        background-image: url('/static/laundry.jpg');
        background-size: cover;
        background-position: center;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .container {
        background: rgba(0,0,0,0.55);
        backdrop-filter: blur(3px);
        padding: 25px;
        width: 90%;
        max-width: 400px;
        border-radius: 12px;
        text-align: center;
        color: white;
    }

    input, button {
        width: 100%;
        padding: 15px;
        margin-top: 12px;
        border-radius: 10px;
        border: none;
        font-size: 18px;
    }
    button {
        background: #FFCC00;
        color: black;
        font-weight: bold;
    }
</style>

</head>
<body>

<div class="container">
    <h2>💳 MTN MoMo Laundry Payment</h2>
    <p>Amount: <b>540 XOF</b></p>

    <form action="/loading" method="get">
        <input name="phone" placeholder="Phone Number" required>
        <input name="payer" placeholder="Your Name" required>

        <button type="submit">Pay 540 XOF</button>
    </form>
</div>

</body>
</html>
"""


# -----------------------------------------------------------
# Loading Animation Page
# -----------------------------------------------------------
LOADING_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Processing Payment…</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
    body {
        margin: 0;
        padding: 0;
        background-color: black;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        flex-direction: column;
        color: white;
        font-family: Arial;
    }

    .loader {
        border: 12px solid #f3f3f3;
        border-top: 12px solid #FFCC00;
        border-radius: 50%;
        width: 70px;
        height: 70px;
        animation: spin 1s linear infinite;
        margin-bottom: 25px;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    p { font-size: 22px; margin-top: 0; }
</style>

<script>
    setTimeout(function(){
        window.location.href =
          "/process?phone={{phone}}&payer={{payer}}";
    }, 2500);
</script>

</head>
<body>

<div class="loader"></div>
<p>Processing Payment…</p>

</body>
</html>
"""


# -----------------------------------------------------------
# Status Checking Screen (new)
# -----------------------------------------------------------
STATUS_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Checking Payment Status…</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
    body {
        margin: 0; padding: 0;
        background-color: #111;
        color: white;
        font-family: Arial;
        height: 100vh;
        display: flex; justify-content: center; align-items: center;
        flex-direction: column; text-align: center;
    }

    .circle {
        border: 10px solid #444;
        border-top: 10px solid #FFCC00;
        border-radius: 50%;
        width: 90px; height: 90px;
        animation: spin 0.9s linear infinite;
        margin-bottom: 20px;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    p { font-size: 22px; }

</style>

<script>
function checkStatus() {
    fetch("/status?ref={{ref}}")
    .then(res => res.json())
    .then(data => {
        if (data.status === "SUCCESSFUL") {
            window.location.href = "/success";
        } else if (data.status === "FAILED" || data.status === "REJECTED") {
            window.location.href = "/failed";
        } else {
            setTimeout(checkStatus, 2500);
        }
    });
}

setTimeout(checkStatus, 2000);
</script>

</head>
<body>

<div class="circle"></div>
<p>Waiting for your confirmation…</p>

</body>
</html>
"""


# -----------------------------------------------------------
# Success Screen (updated)
# -----------------------------------------------------------
SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Payment Successful</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
    body {
        margin: 0; padding: 0; background-color: #0A9310;
        color: white; height: 100vh; display: flex;
        justify-content: center; align-items: center;
        font-family: Arial; text-align: center;
    }

    .check {
        font-size: 90px;
        animation: pop 0.5s ease;
    }

    @keyframes pop {
        0% { transform: scale(0.5); opacity: 0; }
        100% { transform: scale(1.1); opacity: 1; }
    }

    h1 { font-size: 32px; }
</style>

</head>
<body>

<div>
    <div class="check">✔</div>
    <h1>Payment Confirmed!</h1>
    <p>Thank you. Enjoy your laundry service.</p>
</div>

</body>
</html>
"""


# -----------------------------------------------------------
# Failed Payment Screen
# -----------------------------------------------------------
FAILED_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Payment Failed</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
    body {
        margin: 0; padding: 0; background-color: #8B0000;
        color: white; height: 100vh; display: flex;
        justify-content: center; align-items: center;
        font-family: Arial; text-align: center;
    }

    .fail {
        font-size: 90px;
        animation: pop 0.5s ease;
    }

    @keyframes pop {
        0% { transform: scale(0.5); opacity: 0; }
        100% { transform: scale(1.1); opacity: 1; }
    }

    h1 { font-size: 32px; }
</style>

</head>
<body>

<div>
    <div class="fail">✘</div>
    <h1>Payment Failed</h1>
    <p>Please try again or contact support.</p>
</div>

</body>
</html>
"""


# -----------------------------------------------------------
# ROUTES
# -----------------------------------------------------------

@app.route("/")
def home_screen():
    return render_template_string(HOME_PAGE)


@app.route("/loading")
def loading():
    phone = request.args.get("phone")
    payer = request.args.get("payer")
    return render_template_string(LOADING_PAGE, phone=phone, payer=payer)


@app.route("/process")
def process_payment():
    amount = "530"
    phone = request.args.get("phone")
    payer = request.args.get("payer")
    message = "Laundry Payment"

    result = PayClass.momopay(amount, "XOF", message, phone, payer)

    reference = result["reference"]

    return render_template_string(STATUS_PAGE, ref=reference)


@app.route("/status")
def check_status():
    ref = request.args.get("ref")
    status = PayClass.check_status(ref)
    return jsonify({"status": status})


@app.route("/success")
def success_screen():
    return render_template_string(SUCCESS_PAGE)


@app.route("/failed")
def failed_screen():
    return render_template_string(FAILED_PAGE)


# -----------------------------------------------------------
# RUN SERVER
# -----------------------------------------------------------
if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


