from flask import Flask, render_template, request
import csv
import os

app = Flask(__name__)

CSV_FILE = 'prices.csv'

@app.route('/', methods=['GET', 'POST'])
def home():
    price_data = None
    search_url = ""

    if request.method == 'POST':
        # 1. Get the link the user pasted
        search_url = request.form.get('link')
        
        # 2. Search our CSV "Database" for this link
        history = []
        found_name = "Unknown Product"
        
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # If the link in the file matches the link the user pasted
                    if row['Link'] == search_url:
                        found_name = row['Name']
                        # Save the date and price for the graph
                        history.append({
                            "date": row['Date'],
                            "price": row['Price']
                        })
        
        # 3. Prepare data for the website
        if history:
            price_data = {
                "name": found_name,
                "history": history,
                "current_price": history[-1]['price'] # The last price added
            }

    return render_template('index.html', data=price_data)

if __name__ == '__main__':
    app.run(debug=True)
