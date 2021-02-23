from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import pandas as pd
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ZomatoData = pd.read_csv('zomato.csv')
ZomatoData = ZomatoData.drop_duplicates().reset_index(drop=True)

def RestaurantSearch(City,Cuisine,Price):
	if(Price == "low"):
		TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) \
		& (ZomatoData['City'].apply(lambda x: City.lower() in x.lower())) & \
		(ZomatoData["Average Cost for two"] <= 300)]
	elif(Price == "mid"):
		TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) \
		& (ZomatoData['City'].apply(lambda x: City.lower() in x.lower())) & \
		((ZomatoData["Average Cost for two"] > 300) & (ZomatoData["Average Cost for two"] <= 700))]
	return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]

class ActionSearchRestaurants(Action):	
	def name(self):
		return 'action_search_restaurants'

	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')
		results = RestaurantSearch(City=loc,Cuisine=cuisine,Price=price)
		response=""
		if results.shape[0] == 0:
			response= "Sorry, we do not operate in that area yet."
		else:
			for restaurant in RestaurantSearch(loc,cuisine).iloc[:5].iterrows():
				restaurant = restaurant[1]
				response=response + F"Found {restaurant['Restaurant Name']} in {restaurant['Address']} rated {restaurant['Address']} with avg cost {restaurant['Average Cost for two']} \n\n"
				
		dispatcher.utter_message("-----"+response)
		return [SlotSet('location',loc)]

class ActionSendEmail(Action):
    
    def name(self):
        return 'action_send_email'

    def run(self, dispatcher, tracker, domain):
        from_user = 'sriks@gmail.com'
        to_user = tracker.get_slot('email')
        password = 'password'
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(from_user, password)
        subject = 'Your list of restaurants from Foodie'
        msg = MIMEMultipart()
        msg['From'] = from_user
        msg['TO'] = to_user
        msg['Subject'] = subject
        body = tracker.get_slot('emailbody')
        msg.attach(MIMEText(body,'plain'))
        text = msg.as_string()
        server.sendmail(from_user,to_user,text)
        server.close()