import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from PIL import Image
import matplotlib.pyplot as plt
import pytz
from datetime import datetime

st.set_page_config(page_title="Parking Monitor Application", page_icon='🅿️')

def get_current_hour_in_est():
    utc_now = datetime.now(pytz.utc)  
    est = pytz.timezone('US/Eastern')  
    est_now = utc_now.astimezone(est)  
    return est_now.hour

daily_data = []
current_hour_est = get_current_hour_in_est()

if not firebase_admin._apps:
    cred = credentials.Certificate("./serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

st.markdown("""
    <style>
        .flex-container {
            display: flex;
        }
        
        .image-container{
            display: flex;
            width: 50%; 
            align-items: center; 
            justify-content: center; 
        }
        
        .text-container{
            width: 50%;
            
        }
        
        .image-container img{
            max-width: 100%;
            height: auto;
            aspect-ratio: 1/1;
        }
        
        .flex-container h1 {
            margin: 0;
        }
        
        .direction_button{
            border: 1px solid black;
            border-radius: 3px;
            padding: 10px;
            transition-duration: 0.4s;
            text-decoration: none;
            border-shadow: none;
            
        }
        
        .direction_button:hover{
            background-color: black;
            color: white;
            text-decoration: none;
        }
        
    </style>
    """, unsafe_allow_html=True)

db = firestore.client()
parking_lots_ref = db.collection('UNCC')

st.image("banner.png")
selected_location = st.selectbox("**Please select the Surrounding where you are looking for parking**", ["UNCC", "UPTOWN", "Wake Forest University"])
locations = []
if selected_location == "UNCC":
    locations = ["CRI Deck", "Cone Deck", "East Deck 1", "East Deck 2", "East Deck 3", "Lot 11", "North Deck", "Union Deck", "West Deck"]
elif selected_location == "UPTOWN":
    locations = ["124 S Poplar St", "7th Street Station"]
else:
    locations = ["Wake Forest University Charlotte Center Garage"]

select_parking_space = st.selectbox(f"**Please select a parking space in {selected_location}**", locations)

cri_deck_ref = parking_lots_ref.document(f'{select_parking_space}')
cri_deck = cri_deck_ref.get()

cri_deck_1 = parking_lots_ref.document("CRI Deck")
cri_deck_2 = cri_deck_1.get()
cri_deck_dict = cri_deck_2 .to_dict()
    
if cri_deck.exists:
    with st.spinner("Loading...."):
        deck_dict = cri_deck.to_dict()
        total_lots = deck_dict.get("totalLots")
        available_spaces = deck_dict.get("availableLots")

        st.markdown(f"""
        <div class="flex-container">
            <div class="text-container">
                <h1>{deck_dict.get('parkingLotName')}</h1>
                <h4>Lot Type: {deck_dict.get("lotType")}</h4>
                <h4>Total Lots: {deck_dict.get("totalLots")}</h4>
                <h4>ADA Car Lots: {deck_dict.get("adaCarsLots")}</h4>
            </div>
            <div class="image-container">
                <img src="{deck_dict.get('parkingLotImage')}" alt="Parking Lot Image" />
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<h4>Address: {deck_dict.get("address")}</h4>', unsafe_allow_html=True)
        link = deck_dict.get("direction")
        st.markdown(f'<a href="{link}" target="_blank" class="direction_button">Direction</a>', unsafe_allow_html=True) 
        
        # total_percentage = int((total_lots - available_spaces)/total_lots * 100)
        trend = cri_deck_dict.get("weeklyData")[0]
        sorted_data = {k: trend[k] for k in sorted(trend, key=int)}
        
        daily_data = []
        hours = []

        for key, item in sorted_data.items():
            percentage_calculate = int((total_lots - item)/total_lots * 100)
            daily_data.append(percentage_calculate)
            hours.append(f"{key}:0")
        
        current_hour = current_hour_est
        st.markdown(f'<h4>Live Occupancy Percentage: {daily_data[current_hour]}% </h4>', unsafe_allow_html=True)
        st.progress(daily_data[current_hour], "")
        
        st.markdown(f'<h4>Occupancy Trend (Today))</h4>', unsafe_allow_html=True)

        plt.figure(figsize=(12,6))
        bars = plt.bar(hours, daily_data, color='lightgray')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.ylim(0, 100) 
        
        bars[current_hour].set_color('salmon')

        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)

        st.pyplot(plt)
        
        if daily_data[current_hour]  > 90:
            st.markdown(f'<h4 style="text-align: center; color: salmon;">Low availability here. Try other deck.</h4>', unsafe_allow_html=True)
        with st.expander("Other Locations", expanded=True):
            st.markdown(f'<h4>Other Parking Locations Near:  {deck_dict.get("nearLocation")}</h4>', unsafe_allow_html=True)

else:
    st.write("No document found with the name 'CRI Deck'")


  

