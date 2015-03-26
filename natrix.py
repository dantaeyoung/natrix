#!/usr/local/bin/python

from collections import defaultdict
import re
import json
import networkx as nx
from networkx.readwrite import json_graph
import lxml
from lxml import etree
import matplotlib.pyplot as plt

class natrixObj(object):

	def __init__(self, ObjType, GUID, InstanceGuid, Inputs, Outputs):
		self.objType = ObjType
		self.guid = GUID
		self.instanceGuid = InstanceGuid
		self.inputs = Inputs
		self.outputs = Outputs


	def __repr__(self):
		return '==========\n \
TYPE: ' + self.objType + '\n \
GUID: '+ self.guid + '\n \
INSTANCEGUID: '+ self.instanceGuid + '\n \
INPUTS: ' + ', '.join(self.inputs) + '\n\
OUTPUTS: ' + ', '.join(self.outputs) + '\n'

	def toDict(self, internal=False):
		d = { 'type': self.objType,
				'GUID': self.guid,
				}
		if(internal):
			d['internal'] = True
		return d

def makeNatrixObjFromXml(obj):

	objcontainer = obj.find(".//chunk[@name='Container']")

	objType =  obj.find(".//item[@name='Name'][@type_name='gh_string']").text
	GUID = obj.find(".//item[@name='GUID'][@type_name='gh_guid']").text
	InstanceGuid = objcontainer.find(".//item[@name='InstanceGuid'][@type_name='gh_guid']").text

	Inputs = [getattr(inparam.find(".//item[@name='Source']"), "text", "None") for inparam in objcontainer.findall(".//chunk[@name='param_input']")]
	Inputs +=[getattr(inparam.find(".//item[@name='Source']"), "text", "None") for inparam in objcontainer.findall(".//chunk[@name='InputParam']")]
	objInput = getattr(objcontainer.find(".//item[@name='Source'][@type_name='gh_guid']"), "text", None)
	if(objInput is not None):
		Inputs.append(objInput)
		pass
	Inputs = list(set(Inputs))

	Outputs = [getattr(outparam.find(".//item[@name='InstanceGuid']"), "text", "None") for outparam in objcontainer.findall(".//chunk[@name='param_output']")]
	Outputs += [getattr(outparam.find(".//item[@name='InstanceGuid']"), "text", "None") for outparam in objcontainer.findall(".//chunk[@name='OutputParam']")]
	Outputs = list(set(Outputs))

	nobj = natrixObj(objType, GUID, InstanceGuid, Inputs, Outputs)

	return nobj
	


def parseXMLAsGraph(xmlfile):

	#parse xml file
	tree = etree.parse(xmlfile)

	defObjs = tree.find(".//chunk[@name='DefinitionObjects']")
	defObjCount = defObjs.find(".//item[@name='ObjectCount']").text

	# turn objects into natrixObjects
	nobjs = [makeNatrixObjFromXml(obj) for obj in defObjs.findall(".//chunk[@name='Object']")]
	print len(nobjs)
	print defObjCount 

	# assemble directed acyclic graph
	G = nx.DiGraph()

	print nobjs

	for nobj in nobjs:
		for inp in nobj.inputs:
			G.add_edge(inp, nobj.instanceGuid, nobj.toDict())
			print inp, "->", nobj.instanceGuid
		for outp in nobj.outputs:
			G.add_edge(nobj.instanceGuid, outp, nobj.toDict(internal=True))
			print nobj.instanceGuid, "->", outp

	print "G.number_of_nodes()", G.number_of_nodes() 
	print "G.number_of_edges()", G.number_of_edges() 

	fig = plt.figure(figsize=(12,12))
	ax = plt.subplot(111)
	ax.set_title('Graph - Shapes', fontsize=10)
	pos = nx.spring_layout(G)
	nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'))
	nx.draw_networkx_edge_labels(G,pos=nx.spring_layout(G))
	nx.draw(G, pos, node_size=1500, node_color='yellow', font_size=8, font_weight='bold', arrows=True)

	plt.tight_layout()
	plt.savefig("Graph.png", format="PNG")

	for node in nx.topological_sort(G):
		print "====="
		for neigh in G.neighbors(node):
			print node, "->", neigh
			print G.get_edge_data(node, neigh)

	for node in nx.topological_sort(G):
		print "====="
		if(len(G.in_edges(node)) == 0):
			print node, ": has input"
		else:
			print node, "= " ,
		
			if reduce(lambda a, b: a and b, ['internal' in edge[2] for edge in  G.in_edges(node, data=True)]):
				print G.in_edges(node, data=True)[0][0]
			else: 
				print G.in_edges(node, data=True)[0][2]['type'],
				print "( ",
				print ' , '.join([edge[0] for edge in G.in_edges(node, data=True)]),
				print ") "


def main():

	parseXMLAsGraph("ghxs/example1.ghx")

if __name__ == "__main__":
	main()

