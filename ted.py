import cgi
import datetime
import os
import urllib

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext import db

class FrontPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.redirect(users.create_login_url('/map/'))

class GeoLocation(db.Model):
    longitude = db.StringProperty()
    latitude = db.StringProperty()
    timestamp = db.StringProperty()
    device_key = db.StringProperty()
    device_label = db.StringProperty()
    altitude = db.StringProperty()
    speed = db.StringProperty()
    heading = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class Fetch(webapp.RequestHandler):
    def get(self):
        message = '...'
        url = 'http://www.instamapper.com/api?action=getPositions&amp;key=###ENTER YOUR DEVICE_KEY HERE###&amp;num=10&amp;format=json'
        d = urlfetch.fetch(url)
        if d.status_code == 200:
            locations = dict(simplejson.loads(d.content))
            locations = locations['positions']
            for location in locations:
                location = dict(location)

                geo_location = GeoLocation()
                geo_location.longitude = str(float(location['longitude']))
                geo_location.latitude = str(float(location['latitude']))
                geo_location.timestamp = str(location['timestamp'])
                geo_location.device_key = location['device_key']
                geo_location.device_label = location['device_label']
                geo_location.altitude = str(location['altitude'])
                geo_location.speed = str(location['speed'])
                geo_location.heading = str(location['heading'])
                geo_location.put()

            message = locations
        else:
            message = 'Something went wrong'
        self.response.out.write(message)   

class Map(webapp.RequestHandler):
    def get(self):
        message = 'Not working yet'
        d = db.GqlQuery('SELECT * FROM GeoLocation ORDER BY date DESC')
        d = d.get()
        if d:
            message = '<img src="http://maps.google.com/maps/api/staticmap?zoom=14&amp;size=512x512&amp;maptype=roadmap&amp;markers=color:blue|label:S|' + d.latitude + ',' + d.longitude + '&amp;sensor=false">'
        self.response.out.write(message) 

application = webapp.WSGIApplication(
                                     [('/', FrontPage),
                                      ('/map/', Map),
                                      ('/map/fetch/', Fetch),

                                      ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

