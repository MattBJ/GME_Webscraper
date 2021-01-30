import urllib.request
import re
import time
import json
from urllib.error import URLError, HTTPError
import sys

import finviz # an api for https://finviz.com
# https://github.com/mariostoev/finviz

# resource functions:
	# need to return None on success
	# OR need to return:
		# descrioption, title, and link
def get_squoze(): # needs to return
	check_str = "<h1>the squeeze has <u>not</u> been squoze.</h1>"
	req = urllib.request.Request("http://isthesqueezesquoze.com/")
	try:
		page = urllib.request.urlopen(req)
	except URLError as e: # .reason 
		print(e.reason)
		push_noti(
			title="ERROR",
			description=e.reason,
			link="http://isthesqueezesquoze.com/"
			)
		sys.exit(0)
	except HTTPError as e:
		print(e.reason)
		push_noti(
			title="ERORR",
			description=e.reason,
			link="http://isthesqueezesquoze.com/"
			)
		sys.exit(0)
	# print(page.headers) # last modified --> origin server believes resource was last modified
	if(page.status != 200): # error!
		# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
		# READ MORE ON THESE!! 200 is not the only 'success' code
			#... but for THIS scrape on THIS website, it's success!
		push_noti(
			title="SERVER STATUS CODE",
			description=str(page.status),
			link="http://isthesqueezesquoze.com/"
			)
		sys.exit(0)

	pass
	# finished error handling of this request, now can do the actual checking
	html = page.read()
	html_str = html.decode()
	parsed = re.search("<h1>.*</h1>",html_str)
	status = None
	if(parsed):
		status = parsed.group(0) # should be:
		# '<h1>the squeeze has <u>not</u> been squoze.</h1>'
		if(steady_state == status): # == or in
			# print("Diamond cock")
			return None
		else:
			return {"title":"get_squoze()","description":status,"link":"http://isthesqueezesquoze.com/"}
	else:
		return {"title":"get_squoze() ERROR","description":"couldn't find usual html header, check link","link":"http://isthesqueezesquoze.com/"}
	return None
# need to do some outlier detection
	# as it grabs data
def get_finviz():
	gme = finviz.get_stock('GME')
	# I MIGHT NEED ERROR CHECKING HERE!!!
	if(not get_finviz.first):
		get_finviz.first = True
		get_finviz.prev = float(gme['Short Float'][:-1]) # removes '%' and converts to float
		return None
	# now have access to:
	current = float(gme['Short Float'][:-1])
	# always check against epsilons when comparing floats
	if(current < (get_finviz.prev - 0.005)): # short has fallen!
		ret_val = {"title":"get_finvis() short drop","description":"short float: From {}% to {}%".format(get_finviz.prev,current),"link":"https://finviz.com/quote.ashx?t=GME"}
		get_finviz.prev = current
		return ret_val
	elif(current > get_finviz.prev + 0.005): # short has.. risen??
		ret_val = {"title":"get_finvis() short rise","description":"short float: From {}% to {}%".format(get_finviz.prev,current),"link":"https://finviz.com/quote.ashx?t=GME"}
		get_finviz.prev = current
		return ret_val
	else:
		return None
get_finviz.first = False

def push_noti(title,description,link):
	push_url = "https://api.pushmealert.com"

	Profiles = [
		{"user":"###############","key":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"},
		{"user":"###############","key":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
	]

	# ^^ constant

	# going to do POST so I can notify my phone, dont need to get right now
	for i in range(2):
		if(i):
			message = 'Matt: '
		else:
			message = 'Pat: '
		params = {
			'user':Profiles[i]["user"],
			'key':Profiles[i]["key"],
			'title':title,
			# 'title':"Potential Squozening!",
			'message':message + description,
			# 'message':message + 'click on this link and check this site',
			'sound':'3',
			'critical':'1',
			'critical_volume':'100',
			'url':link
			# 'url':'http://isthesqueezesquoze.com/'

		}
		query_string = urllib.parse.urlencode(params)
		data = query_string.encode("ascii")
		with urllib.request.urlopen(url=push_url,data=data) as response:
			packet = json.loads(response.read())
			print("packet type: {}\npacket: {}".format(type(packet),packet))

source_foos = {
	'a':get_squoze,
	'b':get_finviz
}

steady_state = '<h1>the squeeze has <u>not</u> been squoze.</h1>'

counter = 0
if __name__ == "__main__":
	while(True):
		for i in source_foos.keys():
			# do a resource grab
			ret_val = source_foos[i]() # include counter?
			if(ret_val):
				push_noti(
						title=ret_val["title"],
						description=ret_val["description"],
						link=ret_val["link"]
					)
				print("Failed check:\t{}.{}".format(counter,i))
				time.sleep(60) # Check notification!
			else:
				print("Passed check:\t{}.{}".format(counter,i))
				if(i=='b'):
					print("previous finviz short float:\t{}".format(get_finviz.prev))
		counter += 1
		time.sleep(10) # don't spam

# targeting iborrowdesk
	# they only report shorting stocks available at interactive brokers
	# --> one seller
