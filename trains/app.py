from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Replace these values with your registered credentials
CLIENT_ID = "b46118f0-fbde-4b16-a4b1-6ae6ad718b27"
CLIENT_SECRET = "XOyo10RPasKWODAN"
AUTH_URL = "http://20.244.56.144/train/auth"
TRAINS_URL = "http://20.244.56.144/train/trains"

# Get authorization token
def get_authorization_token():
    payload = {
        "companyName": "Train Central",
        "clientID": CLIENT_ID,
        "ownerName": "Rahul",
        "ownerEmail": "rahul@abc.edu",
        "rollNo": "1",
        "clientSecret": CLIENT_SECRET
    }
    response = requests.post(AUTH_URL, json=payload)
    token = response.json().get("access_token")
    return token

# Get train data from John Doe Railway Server
def get_train_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(TRAINS_URL, headers=headers)
    train_data = response.json()
    return train_data

# Filter and format train data
def format_train_data(trains):
    now = datetime.now()
    twelve_hours_later = now + timedelta(hours=12)
    formatted_trains = []

    for train in trains:
        departure_time = datetime(
            now.year, now.month, now.day,
            train["departureTime"]["Hours"],
            train["departureTime"]["Minutes"],
            train["departureTime"]["Seconds"]
        )
        delay = timedelta(minutes=train["delayedBy"])
        departure_time += delay

        if now < departure_time < twelve_hours_later and delay.total_seconds() <= 1800:
            formatted_train = {
                "trainName": train["trainName"],
                "trainNumber": train["trainNumber"],
                "departureTime": departure_time.strftime("%Y-%m-%d %H:%M:%S"),
                "seatsAvailable": train["seatsAvailable"],
                "price": train["price"],
                "totalPrice": train["price"]["sleeper"] + train["price"]["AC"]
            }
            formatted_trains.append(formatted_train)

    # Sort trains based on price, available seats, and departure time
    formatted_trains.sort(key=lambda x: (x["totalPrice"], -x["seatsAvailable"]["sleeper"], -x["departureTime"]))

    return formatted_trains

@app.route("/trains", methods=["GET"])
def get_next_12_hours_trains():
    token = get_authorization_token()
    train_data = get_train_data(token)
    formatted_trains = format_train_data(train_data)

    return jsonify(formatted_trains)

if __name__ == "__main__":
    app.run(debug=True)
