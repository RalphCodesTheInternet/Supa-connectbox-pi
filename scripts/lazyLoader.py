#  Loads content from USB and creates the JSON / file structure for enhanced media interface


print ("lazyLoader: Starting...")

import json
import os
import pathlib
import sys


# Defaults for Connectbox / TheWell
contentDirectory = "/var/www/enhanced/content/www/assets/content/"

# First Download the URL and unzip it
url = sys.argv[1]
print ("Handling File: " + url)
os.system("wget '" + url + "' -O /tmp/openwell.zip")
os.system("unzip -o /tmp/openwell.zip -d /var/www/enhanced/content/www/assets/")



# Go through all the language folders in the package
for language in next(os.walk(contentDirectory))[1]:
	print ("Found Possible Language Folder: " + language)
	if os.path.exists(contentDirectory + language + "/data/main.json"):
		print ("Confirmed Language: " + language + " main.json exists")
		# Load main.json to process
		f = open (contentDirectory + language + "/data/main.json")
		thisMain = json.load(f)
		for content in thisMain["content"]:
			print (" Processing: " + content["title"])
			f = open (contentDirectory + language + "/data/" + content["slug"] + ".json")
			details = json.load(f)
			#print (json.dumps(details))
			items = []
			try:	
				items = details["episodes"]
				print ("	Loading Multi-Episodic Content: " + details["title"] )
			except: 
				items = [details]
				print ("	Single Episodic Content: " + details["title"])
			#print (json.dumps(items))
			for item in items:
				print ("	Checking Media Content: " + item["filename"])
				if (os.path.exists(contentDirectory + language + "/media/" + item["filename"])):
					print ("	Content Exists: " + item["filename"])
				else:
					print ("	LOAD CONTENT: " + item["filename"])
					try:
						os.system("wget '" + item["resourceURL"] + "' -O " + contentDirectory + language + "/media/" + item["filename"])
						print ("		Content Downloaded to: " + item["filename"])
					except:
						print ("		FAILED To Download: " + item["title"])
				print ("	Checking Image Content: " + item["image"])
				if (os.path.exists(contentDirectory + language + "/images/" + item["image"])):
					print ("	Content Exists: " + item["image"])
				else:
					try:
						os.system("wget '" + item["imageURL"] + "' -O " + contentDirectory + language + "/images/" + item["image"])
						print ("		Content Downloaded to: " + item["image"])
					except:
						print ("		FAILED To Download: " + item["title"])

print ("Done.")