from flask import Flask, jsonify, redirect, render_template, request
from markupsafe import Markup
import numpy as np
import pandas as pd
from fertilizer import fertilizer_dic
import requests
import config
import pickle
import io
import torch
from torchvision import transforms
from PIL import Image
from model import ResNet9

# Import Azure deployment module
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.web.models import SiteConfig
from azure.mgmt.web.models import NameValuePair
from azure.mgmt.web.models import ConnStringValueTypePair

#==========================================================================================
# Creating instance
app = Flask(__name__)

model = pickle.load(open('RandomForest.pkl', 'rb'))
model_pro = pickle.load(open('model.pkl', 'rb'))

# Define the list of features in the same order as during training
model_features = ['Crop', 'District_Name', 'State_Name', 'Area', 'Season']

# Loading plant disease classification model
disease_classes = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy']

#===================================================================================================
# Custom functions for calculations

def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None

#===================================================================================================

# =========================================================================================
# Custom functions for Azure deployment

def deploy_to_azure():
    # Azure authentication details
    credentials = ServicePrincipalCredentials(
        client_id='your-client-id',
        secret='your-client-secret',
        tenant='your-tenant-id'
    )
    
    # Initialize Azure WebSiteManagementClient
    client = WebSiteManagementClient(credentials, 'your-subscription-id')
    
    # Define your app name
    app_name = 'your-app-name'
    
    # Set up configuration
    config = SiteConfig(app_command_line='your-startup-command')
    
    # Deploy the app
    client.web_apps.create_or_update('your-resource-group', app_name, config)
    print("App deployed successfully!")

#===================================================================================================
# Define routes

@app.route('/')
def home():
    title = 'Agropro- Home'
    return render_template('index.html', title=title)

@app.route('/crop-recommend')
def crop_recommend():
    title = 'Agropro- Crop Recommendation'
    return render_template('crop.html', title=title)

@app.route('/fertilizer')
def fertilizer_recommendation():
    title = 'Agropro - Fertilizer Suggestion'
    return render_template('fertilizer.html', title=title)

@app.route('/crop_production')
def crop_production():
    title = 'Agropro - Crop Production Prediction'
    return render_template('crop_production.html', title=title)

#==================================================================================================
# Run the app

if __name__ == '__main__':
    app.run(debug=True)

    # Uncomment the following line to deploy to Azure
    # deploy_to_azure()
