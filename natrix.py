#!/usr/local/bin/python

from collections import defaultdict
import re
import json
import networkx as nx
from networkx.readwrite import json_graph
import lxml
from lxml import etree
from lxml import objectify
from io import StringIO, BytesIO

class natrixObj:

	def __init__(self, ObjType, GUID, InstanceGuid, Inputs, Outputs):
		self.objType = ObjType
		self.guid = GUID
		self.instanceGuid = InstanceGuid
		self.inputs = Inputs
		self.outputs = Outputs

	def __repr__(self):
		return "type = " + self.objType + ", GUID: "+ self.guid 

def makeGHObject(obj):

	objcontainer = obj.find(".//chunk[@name='Container']")

	objType =  obj.find(".//item[@name='Name'][@type_name='gh_string']").text
	GUID = obj.find(".//item[@name='GUID'][@type_name='gh_guid']").text
	InstanceGuid = objcontainer.find(".//item[@name='InstanceGuid'][@type_name='gh_guid']").text
	Inputs = [getattr(inparam.find(".//item[@name='Source']"), "text", "None") for inparam in objcontainer.findall(".//chunk[@name='param_input']")]
	Outputs = [getattr(outparam.find(".//item[@name='InstanceGuid']"), "text", "None") for outparam in objcontainer.findall(".//chunk[@name='param_output']")]

	nobj = natrixObj(objType, GUID, InstanceGuid, Inputs, Outputs)

	return nobj
	

def printGHObject(obj):
	print "================"
	print "Object:", obj.find(".//item[@type_name='gh_string']").text
	objcontainer = obj.find(".//chunk[@name='Container']")
#	print "GUID:", obj.find(".//item[@name='GUID'][@type_name='gh_guid']").text
	print "Instance_GUID:", objcontainer.find(".//item[@type_name='gh_guid']").text
#	print "Source:", getattr(objcontainer.find(".//item[@name='Source']"), "text", "None")
#	print "SourceCount:", getattr(objcontainer.find(".//item[@name='SourceCount']"), "text", 0)
	
	if( objcontainer.find(".//chunk[@name='param_input']") is not None):
		for inparam in objcontainer.findall(".//chunk[@name='param_input']"):
			print "----- INPUT: Source:", getattr(inparam.find(".//item[@name='Source']"), "text", "None")
			print "----- INPUT: SourceCount:", getattr(inparam.find(".//item[@name='SourceCount']"), "text", 0)

	if( objcontainer.find(".//chunk[@name='param_output']") is not None):
		for outparam in objcontainer.findall(".//chunk[@name='param_output']"):
			print "----- OUTPUT GUID:", getattr(outparam.find(".//item[@name='InstanceGuid']"), "text", "None")




def parseXMLAsGraph(xmlfile):
	tree = etree.parse(xmlfile)

	defObjs = tree.find(".//chunk[@name='DefinitionObjects']")

	defObjCount = defObjs.find(".//item[@name='ObjectCount']").text

#	for eachobj in defObjs.findall(".//chunk[@name='Object']"):
#		printGHObject(eachobj)
	for nobj in [makeGHObject(obj) for obj in defObjs.findall(".//chunk[@name='Object']")]:
		print nobj
	'''
	root = tree.getroot()
	print [ el.tag for el in root.iterchildren() ]
	print tree.getroot()
	print "--"


		

	#initialize directed graph w/ parallel edges
	G = nxDiGraph()

	#ADD EDGES
	for adj in adjHistory:
		#generate unique edge key
		edgeKey = adjToKey(adj)
		source = screenNameObfIndex[adj["user.screenName"]] # source
		target = screenNameObfIndex[adj["target.screenName"]] # target 
		G.add_edge(source,
				target,
				edgeKey, #key
				adj) # more data

		G.node[source]['lastAdj'] = adj

	print "G.number_of_edges()", G.number_of_edges() 

	for posterScreenName, count in postersWithoutReferencesCount.iteritems():
		thisdict = {}
		thisdict.update(soloUserDict)
		thisdict.update({"total_posts": count, "screenName": posterScreenName, "user.id":screenNameObfIndex[posterScreenName], "has_references": "false"})
#		G.add_node(screenNameObfIndex[posterScreenName]) #, attr_dict=thisdict)
	'''


def main():

	parseXMLAsGraph("ghxs/example1.ghx")

if __name__ == "__main__":
	main()

