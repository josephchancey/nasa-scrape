from flask import Flask, render_template, redirect
import nasa_scrape
from flask_pymongo import PyMongo


app = Flask(__name__)

# Connect to MongoDB
mongo = PyMongo(app, uri="mongodb://localhost:27017/nasa_scrape_mars")


# Routes
@app.route('/')
@app.route('/home')
def home():

    mars_data = mongo.db.mars_scraped_data.find_one()

    return render_template('index.html', mars_data=mars_data)

@app.route('/scrape')
def scrape():

    mars_data = mongo.db.mars_scraped_data
    mars_scrape = nasa_scrape.scrape()
    mars_data.update({}, mars_scrape, upsert=True)

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
