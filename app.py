#!/usr/bin/env /usr/bin/python
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
import datetime
import dateutil.parser
import sys
import subprocess
from Foundation import *

#Which port would you like the service to run on?
service_port = 4445
#Enable debugging in response output? (turn off for production use)
debug = True

app = Flask(__name__)
api = Api(app)

#this creates the appropriate calendar applescript for us to run
def createCalendar(start_time,end_time,summary,description,UID,calendar):
	#this template creates the applescript we want to run
	applescript_template = """
		tell application "Calendar"
			tell calendar "{calendar}"
				make new event at end of events with properties {{summary:"{summary}", start date:date "{start_time}", end date:date "{end_time}",description:"{description}"}}
			end tell
		end tell
	"""
	#format the dates so applescript accepts them.  It expects date in %YYYY-%MM-%DDT%hh:%mm:%ss format
	ascript_start = dateutil.parser.parse(start_time).strftime("%B %d, %Y %I:%M:%S %p")
	ascript_end = dateutil.parser.parse(end_time).strftime("%B %d, %Y %I:%M:%S %p")	
	return applescript_template.format(calendar=calendar,start_time=ascript_start,end_time=ascript_end,uid=UID,summary=summary,description=description)
	
#this class
class Calendar(Resource):
	def post(self,calendar):
		json_data = request.get_json(force=True)
		this_cal_data = createCalendar(json_data['start_time'],json_data['end_time'],json_data['summary'],json_data['description'],json_data['UID'],calendar)
		try:
			s = NSAppleScript.alloc().initWithSource_(this_cal_data)
			s.executeAndReturnError_(None)
			return jsonify(status="Success",event=json_data['summary'],uid=json_data['UID'])
		except:
			return jsonify(status="Error",event=json_data['summary'],uid=json_data['UID'])

class Help(Resource):
	def get(self):
		print "docs go here"
		
api.add_resource(Help, '/calendar')		
api.add_resource(Calendar, '/calendar/<string:calendar>')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=service_port, debug=debug)
