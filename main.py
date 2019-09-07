import os
import json
from pandas.io.json import json_normalize
import pycountry
import requests
import ast

from flask import Flask
from flask import send_file
from flask import Flask, render_template, request , redirect, url_for



app = Flask(__name__,template_folder='template')

"""

For deployment :
source env/bin/activate
python3.6 main.py

"""


from pandas.io.json import json_normalize
import requests




def write_file(file_name,data):
	with open(file_name , 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=4)

def read_file(file_name):
	with open(file_name) as f:
		data = json.load(f)
		return data










class Utils(object):
	def __init__(self):
		self.city_file = "city.json"
		self.state_file = "states.json"
		self.countries_file = "countries.json"
		self.area_file = "area.json"
		self.list_amenity = [
		    "university",
		    "bbq",
		    "biergarten",
		    "cafe",
		    "drinking_water",
		    "fast_food",
		    "food_court",
		    "ice_cream",
		    "hospital",
		    "restaurant",
		    "college",
		    "kindergarten",
		    "library",
		    "public_bookcase",
		    "school",
		    "fire_station",
		    "fountain",
		    "place_of_worship",
		    "fuel",
		    "pharmacy",
		    "arts_centre",
		    "police"
		]


	def get_countries(self):

		try:
			data = read_file(self.countries_file )
		except Exception as e:
			print("Error @get_countries",e)

			data = []
			pass

		if len(data) == 0:

			url2 = 'http://overpass-api.de/api/interpreter'  # Overpass API URL
			query2 = f"""[out:csv("name:en")];relation["admin_level"="2"];out;"""
			r2 = requests.get(url2, params={'data': query2})
			data2 = r2  # read response as JSON and get the data
			list_cnt = [ _  for _ in data2.text.split("\n") if _ != "" ]

			cnt_list = []
			list_cnt

			for co in list_cnt :
				try:
				    iso_name = pycountry.countries.search_fuzzy(co)

				except Exception as e:
				    #print("Error",e)
				    iso_name = None
				    pass
				try:
				    iso_code = (iso_name[0] ).alpha_2
				    #print(co, "||" ,  ( iso_code   ) )
				    cnt_list.append({ "co" : co , "iso" : iso_code })

				except:
				    pass


			write_file(self.countries_file, cnt_list )
			return cnt_list
		else:
			return data


	def get_states(self, cnt , init_flag ):
		data = []

		if init_flag == 0:
			url = 'http://overpass-api.de/api/interpreter'  # Overpass API URL
			query = f"""
			[out:json];
			area["ISO3166-1"="%s"][admin_level=2];
			node ["place"="state"](area);
			out;
			"""%(cnt)
			r = requests.get(url, params={'data': query})
			data = r.json()['elements']  # read response as JSON and get the data

			list_dat = []
			for _ in data:
				try:
					name, state_code = (_["tags"]["name"],_["tags"]["state_code"] )
				except Exception as e:
					name, state_code = (_["tags"]["name"]) , "none"
					pass
				list_dat.append({ "name": name, "state_code": state_code})

			write_file(self.state_file, list_dat )

			return list_dat

		elif init_flag == 1:
			try:
				data = read_file(self.state_file )
			except Exception as e:
				print("Error @get_states",e)

				data = []
				pass
		else:
			data = []

		return data

	def get_cities(self, state, init_flag ):

		if init_flag == 0:

			url2 = 'http://overpass-api.de/api/interpreter'  # Overpass API URL
			query5 = f"""
			[out:json][timeout:50];
			area[name="%s"];(node[place="city"](area););out;

			"""%(state)


			r5 = requests.get(url2, params={'data': query5})
			#print(r5.text)
			data5 = r5.json()['elements']  # read response as JSON and get the data
			list_name = [ { "name" : _["tags"]["name"] , "lat" :_["lat"] , "lon" : _["lon"] }  for _ in data5 ]
			write_file(self.city_file, list_name )

			return list_name
		elif init_flag == 1:
			try:
				data = read_file(self.city_file )
			except Exception as e:
				print("Error @get_states",e)

				data = []
				pass
		else:
			data = []

		return data



	def query(self, lat , lon, query_term):

		try:
			from pandas.io.json import json_normalize
			import requests

			url2 = 'http://overpass-api.de/api/interpreter'  # Overpass API URL
			query5 = f"""
			[out:json][timeout:50];
			nwr(around:10000,%s,%s)["amenity"="%s"];
			out center;
			"""%(lat,lon,query_term)


			r5 = requests.get(url2, params={'data': query5})
			print("-"*20)
			print(lat,lon,query_term)
			print(r5.text)
			data5 = r5.json()['elements']  # read response as JSON and get the data
			df5 = json_normalize(data5)  # create a DataFrame from the data

			df5.to_csv('file.csv')
			return True
		except Exception as e:
			return False
			pass



utils_tool = Utils()





@app.route('/download/<query>') # this is a job for GET, not POST
def download_file():


	return send_file('file.csv',mimetype='text/csv',attachment_filename='file.csv',as_attachment=True)



@app.route('/cities/<state>', methods= ["GET"])
def get_city(state):
	utils_tool.get_cities(state,0)
	return redirect(url_for('index'))

@app.route('/states/<country>', methods= ["GET"])
def get_state(country):
	country_code = country
	utils_tool.get_states(country_code,0)
	cnt = []
	states = []
	cities = []
	areas = []
	cnt = utils_tool.get_countries()
	states = utils_tool.get_states( "s", 1)
	return redirect(url_for('index'))


@app.route('/city/<city>', methods= ["GET"])
def get_places(city):

	data = read_file(utils_tool.city_file)
	print(city)
	city,query = city.split("||")
	if query != "none":
		for _ in data :
			if _["name"] == city:
				lat = _["lat"]
				lon = _["lon"]
		utils_tool.query(lat,lon, query)
		return send_file('file.csv',mimetype='text/csv',attachment_filename='file.csv',as_attachment=True)
	else:
		return redirect(url_for('index'))



@app.route('/')
def index():
	cnt = []
	states = []
	cities = []
	areas = []
	cnt = utils_tool.get_countries()
	states = utils_tool.get_states( "s", 1)
	cities = utils_tool.get_cities( "s", 1)
	amenities = utils_tool.list_amenity
	return render_template("index2.html", cnt = cnt , states =states , cities = cities, areas = areas ,amenities= amenities )

if __name__ == '__main__':
	utils_tool.get_countries()
	app.run(debug=True)
