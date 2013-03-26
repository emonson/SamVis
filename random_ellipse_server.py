#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cherrypy
import json
import numpy as N

# //Dynamic, random dataset
# var dataset = [];											//Initialize empty array
# var colordata = [];
# var filldata = [];
# var numDataPoints = 100;										//Number of dummy data points to create
# var maxRange = 400 + Math.random() * 600;						//Max range of new values
# var maxRadius = 50;
# for (var i = 0; i < numDataPoints; i++) {					//Loop numDataPoints times
#		var newX = (Math.random() * maxRange);	//New random integer
#		var newY = (Math.random() * maxRange);	//New random integer
#		var newRX = (Math.random() * maxRadius);	//New random integer
#		var newRY = (Math.random() * maxRadius);	//New random integer
#		var newPhi = (Math.random() * 90); // NOTE: fix range…
#		var newC = 2*Math.random() - 1;
#		var newF = Math.round(Math.random()*100)/100; // round to two digits
#		dataset.push([newX, newY, newRX, newRY, newPhi, i]);	//Add new numbers to array
#		colordata.push(newC);
#		filldata.push(newF);
# }

#			//New values for dataset
#			var numValues = dataset.length;								//Count original length of dataset
#			var maxRange = 400 + Math.random() * 600;						//Max range of new values
#			dataset = [];													//Initialize empty array
#			for (var i = 0; i < numValues; i++) {					//Loop numDataPoints times
#				var newX = (Math.random() * maxRange);	//New random integer
#				var newY = (Math.random() * maxRange);	//New random integer
#				var newRX = (Math.random() * maxRadius);	//New random integer
#				var newRY = (Math.random() * maxRadius);	//New random integer
#				var newPhi = (Math.random() * 90); // NOTE: fix range...
#				dataset.push([newX, newY, newRX, newRY, newPhi, i]);					//Add new numbers to array
#			}

class EllipseData:
	
	def __init__(self):
		
		self.n_pts = 100
		self.max_val = 1000
		self.min_val = 400
		self.max_radius = 50
		
	def index(self):
		return "Random Ellipse Server"
	
	def newdata(self, n=None):
		
		if n:
			# parameters come in and get parsed out as strings
			self.n_pts = int(n)
		
		maxRange = self.min_val + N.random.random(self.n_pts)*(self.max_val-self.min_val)
		newX = N.round(N.random.random(self.n_pts) * maxRange, 2).tolist()
		newY = N.round(N.random.random(self.n_pts) * maxRange, 2).tolist()
		newRX = N.round(N.random.random(self.n_pts) * self.max_radius, 2).tolist()
		newRY = N.round(N.random.random(self.n_pts) * self.max_radius, 2).tolist()
		newPhi = N.round(N.random.random(self.n_pts) * 90, 2).tolist()
		newC = N.round(2 * N.random.random(self.n_pts) - 1, 2).tolist()
		newF = N.round(N.random.random(self.n_pts), 2).tolist()

		zipped = zip(newX, newY, newRX, newRY, newPhi, range(self.n_pts))
		data = {'data':zipped, 'color':newC, 'fill':newF}
		return json.dumps(data)
		
	index.exposed = True
	newdata.exposed = True

cherrypy.config.update({
		'server.socket_port': 9000, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(EllipseData())
