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
	zomato_data = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower()))]
	if(Price == "low"):
		TEMP = zomato_data[ZomatoData["Average Cost for two"] <= 300]
	elif(Price == "mid"):
		TEMP = zomato_data[(ZomatoData["Average Cost for two"] > 300) & (ZomatoData["Average Cost for two"] <= 700)]
	elif(Price == "high"):
		TEMP = zomato_data[(ZomatoData["Average Cost for two"] > 700)]
	return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']].sort_values('Aggregate rating', ascending = False)[:10]

class ActionSearchRestaurants(Action):	
	def name(self):
		return 'action_search_restaurants'

	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')
		results = RestaurantSearch(City=loc,Cuisine=cuisine,Price=price)
		response=""
		count = 0
		bot_response_header = "Showing top 5 restaurants \n===========================================\n"
		email_response_header = "Top 10 restaurants \n===========================================\n"
		if results.shape[0] == 0:
				dispatcher.utter_message("Sorry, no restaurant found for your criteria. you might what to start over?")
				return [SlotSet('no_restaurant_found', 'yes')]
		else:
			for restaurant in results.iterrows():
				count = count + 1
				restaurant = restaurant[1]
				response = response + F"Found {restaurant['Restaurant Name']} in {restaurant['Address']} has been rated {restaurant['Aggregate rating']}, average cost for two is {restaurant['Average Cost for two']}\n\n"
				if (count == 5):
					dispatcher.utter_message(bot_response_header + response) # dispatch the message to caller
			if(count<5 and count >0):
					dispatcher.utter_message(bot_response_header + response)
			print(response)
			SlotSet('no_restaurant_found', 'no')
			return [SlotSet('email_body', email_response_header + response)]

class ActionSendEmail(Action):
	
	def name(self):
		return 'action_send_email'

	def run(self, dispatcher, tracker, domain):
			try:
				from_user = 'replace-with-your-own' # replace email with your own
				to_user = tracker.get_slot('email')
				password = 'replace-with-your-own' # replace password with your own
				server = smtplib.SMTP('smtp.gmail.com',587)
				server.starttls()
				server.login(from_user, password)
				subject = 'Your list of restaurants from Foodie'
				msg = MIMEMultipart()
				msg['From'] = from_user
				msg['TO'] = to_user
				msg['Subject'] = subject
				body = tracker.get_slot('email_body')
				msg.attach(MIMEText(body,'plain'))
				text = msg.as_string()
				server.sendmail(from_user,to_user,text)
				server.close()
			except: 
				dispatcher.utter_message("Something went wrong, we could not send you the email. Please try again later.")