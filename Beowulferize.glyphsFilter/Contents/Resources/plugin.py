# encoding: utf-8

###########################################################################################################
#
#
#	Filter with dialog Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter%20with%20Dialog
#
#	For help on the use of Interface Builder:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################

from __future__ import print_function

import objc, random
from GlyphsApp import *
from GlyphsApp.plugins import *

def approxLengthOfSegment(segment):
	if len(segment) == 2:
		p0,p1 = [NSPoint(p.x, p.y) for p in segment]
		return ((p1.x - p0.x) ** 2 + (p1.y - p0.y)**2) ** 0.5
	elif len(segment) == 4:
		p0, p1, p2, p3 = [NSPoint(p.x, p.y) for p in segment]
		chord = distance(p0, p3)
		cont_net = distance(p0, p1) + distance(p1, p2) + distance(p2, p3)
		return (cont_net + chord) * 0.5 * 0.996767352316
	else:
		print("Segment has unexpected length:\n" + segment)
	

class Beowulferize(FilterWithDialog):
	
	# Definitions of IBOutlets
	
	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()
	
	# Text field in dialog
	maxShakeField = objc.IBOutlet()
	shouldAddPointsField = objc.IBOutlet()
	thresholdLengthField = objc.IBOutlet()
	
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'Beowulferize',
			'de': u'Beowulferisieren',
			'fr': u'Beowulfeur',
			'es': u'Beowulferisador',
		})
		
		# Word on Run Button (default: Apply)
		self.actionButtonLabel = Glyphs.localize({
			'en': u'Shake',
			'de': u'Schütteln',
			'fr': u'Secouer',
			'es': u'Agitar',
		})
		
		# Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)
	
	# On dialog show
	def start(self):
		
		# Set default value
		Glyphs.registerDefault('com.mekkablue.beowulferize.shake', 15.0)
		if Glyphs.defaults['com.mekkablue.beowulferize.shake'] == "GlyphsToolHand":
			Glyphs.defaults['com.mekkablue.beowulferize.shake'] = None
			
		Glyphs.registerDefault('com.mekkablue.beowulferize.thresholdLength', 100.0)
		if Glyphs.defaults['com.mekkablue.beowulferize.thresholdLength'] == "GlyphsToolHand":
			Glyphs.defaults['com.mekkablue.beowulferize.thresholdLength'] = None
			
		Glyphs.registerDefault('com.mekkablue.beowulferize.shouldAddPoints', True)
		if Glyphs.defaults['com.mekkablue.beowulferize.shouldAddPoints'] == "GlyphsToolHand":
			Glyphs.defaults['com.mekkablue.beowulferize.shouldAddPoints'] = None
		
		# Set value of text field
		self.maxShakeField.setStringValue_(Glyphs.defaults['com.mekkablue.beowulferize.shake'])
		self.shouldAddPointsField.setIntValue_(Glyphs.defaults['com.mekkablue.beowulferize.shouldAddPoints'])
		self.thresholdLengthField.setStringValue_(Glyphs.defaults['com.mekkablue.beowulferize.thresholdLength'])
		self.thresholdLengthField.setEnabled_(Glyphs.defaults['com.mekkablue.beowulferize.shouldAddPoints'])
		
		# Set focus to text field
		self.maxShakeField.becomeFirstResponder()
		
	# Actions triggered by UI
	@objc.IBAction
	def setShake_(self, sender):
		Glyphs.defaults['com.mekkablue.beowulferize.shake'] = sender.floatValue()
		self.update()
	
	@objc.IBAction
	def setShouldAddPoints_(self, sender):
		Glyphs.defaults['com.mekkablue.beowulferize.shouldAddPoints'] = sender.intValue()
		self.thresholdLengthField.setEnabled_(Glyphs.defaults['com.mekkablue.beowulferize.shouldAddPoints'])
		self.update()
	
	@objc.IBAction
	def setThresholdLength_(self, sender):
		Glyphs.defaults['com.mekkablue.beowulferize.thresholdLength'] = sender.floatValue()
		self.update()
	
	@objc.python_method
	def addPointsOnPaths(self, thisLayer, thresholdLength=0.0):
		for thisPath in thisLayer.paths:
			pathTimesForNodeInsertion = []
			numOfNodes = len(thisPath.nodes)

			# step through nodes:
			for i in range(numOfNodes):
				if thisPath.nodes[i].type != OFFCURVE:
					currentNode = thisPath.nodes[i]
					
					# determine segment:
					segment = [currentNode.position,]
					addNodes = True
					while addNodes:
						nextNode = currentNode.nextNode
						segment.append(nextNode.position)
						addNodes = nextNode.type == OFFCURVE
						currentNode = nextNode
						
					# collect path time for node insertion if segment is long enough:
					if approxLengthOfSegment(segment) > thresholdLength:
						pathTimesForNodeInsertion.append(i + 0.5)
			
			# step backwards through collected path times and insert nodes:
			for pathTime in reversed(sorted(pathTimesForNodeInsertion)):
				thisPath.insertNodeWithPathTime_(pathTime)
		
	# Actual filter
	@objc.python_method
	def filter(self, thisLayer, inEditView, customParameters):
		
		# Called on font export, get value from customParameters:
		if 'shake' in customParameters:
			shake = abs(float(customParameters['shake']))
			if 'thresholdLength' in customParameters:
				shouldAddPoints = True
				thresholdLength = float(customParameters['thresholdLength'])
			else:
				shouldAddPoints = False
				
		# Called through UI, use stored value:
		else:
			shake = abs(float(Glyphs.defaults['com.mekkablue.beowulferize.shake']))
			thresholdLength = float(Glyphs.defaults['com.mekkablue.beowulferize.thresholdLength'])
			shouldAddPoints = bool(Glyphs.defaults['com.mekkablue.beowulferize.shouldAddPoints'])
		
		# insert points if user asks for it:
		if shouldAddPoints:
			self.addPointsOnPaths(thisLayer, thresholdLength=thresholdLength)
		
		# shake nodes:
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				thisNode.x +=  (-shake + 2 * shake * random.random())
				thisNode.y +=  (-shake + 2 * shake * random.random())
			thisPath.checkConnections()
		
	
	def generateCustomParameter(self):
		if Glyphs.defaults['com.mekkablue.beowulferize.shouldAddPoints']:
			return "%s; shake:%s; thresholdLength:%s;" % (
				self.__class__.__name__,
				Glyphs.defaults['com.mekkablue.beowulferize.shake'],
				Glyphs.defaults['com.mekkablue.beowulferize.thresholdLength'],
			)
		else:
			return "%s; shake:%s;" % (
				self.__class__.__name__,
				Glyphs.defaults['com.mekkablue.beowulferize.shake'],
			)
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
