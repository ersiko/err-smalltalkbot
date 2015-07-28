# Backward compatibility
from errbot.version import VERSION
from errbot.utils import version2array
if version2array(VERSION) >= [1,6,0]:
    from errbot import botcmd, BotPlugin
else:
    from errbot.botplugin import BotPlugin
    from errbot.jabberbot import botcmd

from myconfig import OpenWeatherMapAPIToken
import urllib
from pyquery import PyQuery as pq
import datetime
import time
import json
import requests
from pytz import timezone

__author__ = 'Tomas Nunez'

class SmalltalkBot(BotPlugin):

    @botcmd
    def weather(self, mess, args):
        """ Tells the weather in a city
        Example: !weather city
        """
        #Docu en http://openweathermap.org/api
        if not args:
            return 'Which city do you want to check?'
        args = args.strip()
        if str(args) == "Uranus":
            return "Mine is warm...What about yours?"
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + str(args) + '&APPID='+ OpenWeatherMapAPIToken +'&units=Metric')
        return 'The closest city I have data is ' + r.json()['name'] + ' and according to openweathermap weather is: ' + r.json()['weather'][0]['description'] + ' and temperature is ' + str(r.json()['main']['temp']) + ' Celsius'

    @botcmd
    def time(self, mess, args):
        """ Tells the time in a city
        Example: !time city
        """
        if not args:
            return 'Which city do you want to check?'
        args = args.strip()
        if str(args) == "Uranus":
            return "Mine is well...What about in yours?"
        maps_search = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address=' + str(args) + '&sensor=false')
        city_tz = requests.get('https://maps.googleapis.com/maps/api/timezone/json?location=' + str(maps_search.json()["results"][0]["geometry"]["location"]["lat"]) + ',' + str(maps_search.json()["results"][0]["geometry"]["location"]["lng"]) + '&timestamp=' + str(int(time.time())) + '&sensor=false')
        fmt = "%Y-%m-%d %H:%M:%S %Z%z"

        return "I'm guessing you are asking for " + maps_search.json()['results'][0]['formatted_address'] + ". The timezone is " + city_tz.json()['timeZoneName'] + " and time there is " + datetime.datetime.now(timezone(city_tz.json()['timeZoneId'])).strftime(fmt)

    @botcmd(split_args_with=None)
    def location_setother(self, mess, args):
        """ Sets location for another user
        Example: !location setother Tomas Jaipur"
        """

        if len(args) <= 1:
            yield "You need a user AND a location"
            return "Example: !location setother Tomas Jaipur"

        requester = mess.frm.node
        user = args[0].strip().title()
        user_location = " ".join(args[1:]).title()
        users = self.shelf['users']

        if user in self.shelf['nicknames']:
            user = self.shelf['nicknames'][user]

        yield "Ok, " + requester + ", trying to set "+ user + " location to " + user_location
        try:
            users[user] = user_location
            self.shelf['users'] = users
        except Exception:
            raise "I can't update that user"
        return "Done!"


    @botcmd
    def location_set(self, mess, args):
        """ Sets your location
        Example: !location set Jaipur"
        """

        requester = str(mess.frm.resource).title()
        users = self.shelf['users']
        user_location = args.strip().title()
        if requester in self.shelf['nicknames']:
            requester = self.shelf['nicknames'][requester]

        yield "Ok, " + requester + ", trying to set your location to " + user_location

        try:
            users[requester]=user_location
            self.shelf['users'] = users
        except KeyError:
            raise "I can't update that user"
        return "Done!"


    @botcmd
    def location_get(self, mess, args):
        """ Gets the location for a user
        Example: !location get Tomas"
        """
        user = args.strip().title()
        if user in self.shelf['users']:
            return "Location for user " + user + " is " + self.shelf['users'][user]
        else:
            if user in self.shelf['nicknames']:
                username = self.shelf['nicknames'][user]
                return "User " + user + " is a nickname for " + username + ". Location for user " + username + " is " + self.shelf['users'][username]
            else:
                return "I have no record for user " + user

    @botcmd
    def smalltalk(self, mess, args):
        """ Gives you a small amount of information to start smalltalk with someone
        Example: !smalltalk Tomas
        """
        user = args.strip().title()
        if user in self.shelf['users']:
            pass
        else:
            if user in self.shelf['nicknames']:
                user = self.shelf['nicknames'][user]
            else:
                return "I have no record for user " + user

        try:
            user_location = self.shelf['users'][user]

            yield "Location for user " + user + " is " + user_location
            maps_search = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address=' + user_location + '&sensor=false')
            location_latitude = maps_search.json()["results"][0]["geometry"]["location"]["lat"]
            location_longitude = maps_search.json()["results"][0]["geometry"]["location"]["lng"]
            city_tz = requests.get('https://maps.googleapis.com/maps/api/timezone/json?location=' + str(location_latitude) + ',' + str(location_longitude) + '&timestamp=' + str(int(time.time())) + '&sensor=false')
            fmt = "%Y-%m-%d %H:%M:%S %Z%z"
            yield maps_search.json()['results'][0]['formatted_address'] + " is in " + city_tz.json()['timeZoneName'] + " timezone, and now it's " + datetime.datetime.now(timezone(city_tz.json()['timeZoneId'])).strftime(fmt) + " there."
            openweathermap = requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + user_location + '&APPID='+ OpenWeatherMapAPIToken +'&units=Metric')
            yield 'The closest city I have data is ' + openweathermap.json()['name'] + ' and according to openweathermap, weather is: ' + openweathermap.json()['weather'][0]['description'] + ' and temperature is ' + str(openweathermap.json()['main']['temp']) + ' Celsius'
#            return "Done!"

        except KeyError:
            yield "I have no record for user "

    @botcmd
    def user_del(self, mess, args):
        """ Lists all available users
        Example: !user list
        """
        user = args.strip().title()
        users = self.shelf['users']
        try:
            del users[user]
            self.shelf['users'] = users
            return "User "+ user + " deleted successfully"
        except KeyError:
            raise "There's no user " + user +" in the database"

    @botcmd
    def user_list(self, mess, args):
        """ Lists all available users
        Example: !user list
        """
        return self['users']
    @botcmd(split_args_with=None)
    def nick_add(self, mess, args):
        """ Assigns a nickname to a name
        Example: !nick add name nickname
        """
        if len(args) <= 1:
            yield "You need a user AND a nickname"
            return "Example: !nick add nunez Tomas"
        nicknames = self.shelf['nicknames']
        users = self.shelf['users']
        user = args[0].strip().title()
        nickname = " ".join(args[1:]).strip().title()

        yield "Username " + user + " and nickname " + nickname

        if user in users:
            pass
        else:
            yield "Error. User " + user + " doesn't exist in users table"
            return

        if nickname in nicknames:
            yield "Warning: Nickname " + nickname + " was already there with value " + nicknames[nickname] + ". Overwriting..."
        nicknames[nickname] = user
        self.shelf['nicknames'] = nicknames

    @botcmd
    def nick_list(self, mess, args):
        """ Lists all available nicknames
        Example: !nick list
        """
        return self['nicknames']

    @botcmd
    def nick_del(self, mess, args):
        """ Deletes a nickname
        Example: !nick del nickname
        """
        nick = args.strip().title()
        nicknames = self.shelf['nicknames']
        try:
            del nicknames[nick]
            self.shelf['nicknames'] = nicknames
            return "Nickname " + nick + " deleted successfully"
        except KeyError:
            raise "There's no nickname " + nick + " in the database"


    @botcmd
    def user_init(self, mess, args):
        self['users'] = {}
        self['nicknames'] = {}
