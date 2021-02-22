from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import pandas as pd
import json

ZomatoData = pd.read_csv('zomato.csv')
ZomatoData = ZomatoData.drop_duplicates().reset_index(drop=True)

def RestaurantSearch(City,Cuisine):
	TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower()))]
	return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_search_restaurants'

	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')
		results = RestaurantSearch(City=loc,Cuisine=cuisine)
		response=""
		if results.shape[0] == 0:
			response= "Sorry, we do not operate in that area yet."
		else:
			for restaurant in RestaurantSearch(loc,cuisine).iloc[:5].iterrows():
				restaurant = restaurant[1]
				response=response + F"Found {restaurant['Restaurant Name']} in {restaurant['Address']} rated {restaurant['Address']} with avg cost {restaurant['Average Cost for two']} \n\n"
				
		dispatcher.utter_message("-----"+response)
		return [SlotSet('location',loc)]

