from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import pandas as pd
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ZomatoData = pd.read_csv('zomato.csv')
ZomatoData = ZomatoData.drop_duplicates().reset_index(drop=True)
WeOperate = list(ZomatoData["City"].str.lower().unique())
Cuisines = ["north indian", "south indian", "american", "chinese", "italian", "mexican"]

def RestaurantSearch(City,Cuisine,Price):
	print(City, Cuisine, Price)
	zomato_data = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower()))]
	if(Price == "low"):
		TEMP = zomato_data[ZomatoData["Average Cost for two"] <= 300]
	elif(Price == "mid"):
		TEMP = zomato_data[(ZomatoData["Average Cost for two"] > 300) & (ZomatoData["Average Cost for two"] <= 700)]
	elif(Price == "high"):
		TEMP = zomato_data[(ZomatoData["Average Cost for two"] > 700)]
	else:
		return pd.DataFrame()
	return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']].sort_values('Aggregate rating', ascending = False)[:10]

def get_price_range(price):
	if(price == "low"):
		return "less than Rs. 300"
	elif(price=="mid"):
		return "between Rs 300 to 700"
	elif(price=="high"):
		return "greater than 700"

def CitySearch(City):
	if(City.lower() in WeOperate):
		return '1'
	else:
		return '0'

class ActionValEmail(Action):	
	def name(self):
		return 'action_val_email'

	def run(self, dispatcher, tracker, domain):
		to_user = tracker.get_slot('email')
		print("validating email")
		print(to_user)
		if re.search(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', to_user, re.I):
			return [SlotSet('invalid_email', 'no')]
		else:
			dispatcher.utter_message("The email ID is invalid.")
			return [SlotSet('invalid_email', 'yes')]

class ActionSearchRestaurants(Action):	
	def name(self):
		return 'action_search_restaurants'

	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')
		price_range = get_price_range(price)
		dispatcher.utter_message("Searching restaurants in {0} restaurants at {1}, in price range {2}.......\n".format(cuisine, loc, price_range));
		results = RestaurantSearch(City=loc,Cuisine=cuisine,Price=price)
		response=""
		count = 0
		bot_response_header = "Showing top 5 restaurants \n===========================================\n"
		email_response_header = "Top 10 restaurants \n===========================================\n"
		if results.shape[0] == 0 or (cuisine.lower() not in Cuisines):
				dispatcher.utter_message("Sorry, no restaurant(s) found for your criteria")
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


class ActionSearchCity(Action):	
	def name(self):
		return 'action_search_city'

	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		result = CitySearch(City=loc)
		print(result)
		if result == '0':
			dispatcher.utter_message("Sorry, we don’t operate in this city. Can you please specify some other location?")
			return [SlotSet('no_restaurant_found', 'yes')]
		else:
			return [SlotSet('no_restaurant_found', 'no')]

class ActionSendEmail(Action):
	
	def name(self):
		return 'action_send_email'

	def run(self, dispatcher, tracker, domain):
			try:
				from_user = 'upgrad.sriks@gmail.com' # replace email with your own
				to_user = tracker.get_slot('email')
				print('sending email to ' + to_user)
				password = 'password' # replace password with your own
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