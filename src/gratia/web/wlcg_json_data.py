import datetime
import json
import urllib2
import simplejson
import string
import os.path
from gratia.web.gratia_urls import GratiaURLS

class WLCGWebUtil:
    def wlcg_pledges(self, month=datetime.datetime.now().month, year=datetime.datetime.now().year):     
            
        thisyear = str(year)
        debug=1
	sites_per_accountname={}
	fednames_and_accounts={}

        cms_fed = {}
        atlas_fed = {}
        alice_fed = {}

        cms_pledge = {}
        atlas_pledge = {}
        alice_pledge = {}

        #url = 'http://gstat-wlcg.cern.ch/apps/topology/2/json'
        srchUrl = 'TopologyUrl'
        modName = 'wlcg_pledges'
        print "%s: srchUrl: %s" % (modName, srchUrl)
        try:
            url = getattr(globals()['GratiaURLS'](), 'GetUrl')(srchUrl)
            print "%s: SUCCESS: getattr(globals()['GratiaURLS'](), 'GetUrl')(%s)" % (modName,srchUrl)
            print "%s: retUrl: %s" % (modName, url)
        except:
            print "%s: FAILED: getattr(globals()['GratiaURLS'](), 'GetUrl')(urlname=%s)" % (modName,srchUrl)
            pass
        response  = urllib2.urlopen(url)
	s = response.read()
	x = simplejson.loads(s)
	#resourcesnestedlist=x['aaData']
	for obj in x:
	    if('USA'==obj['Country']):   
		try:
			sites_per_accountname[obj['FederationAccountingName']].append(obj['Site'])
		except KeyError:
			sites_per_accountname[obj['FederationAccountingName']]=[obj['Site']]

		fednames_and_accounts[obj['Federation']]=obj['FederationAccountingName']#Name is key
	    if('USA'==obj['Country'] and obj['Federation'].find('CMS') >= 0):  
		cms_fed[obj['FederationAccountingName']]=1;
	    if('USA'==obj['Country'] and obj['Federation'].find('ATLAS') >= 0):  
		atlas_fed[obj['FederationAccountingName']]=1;
	    if('USA'==obj['Country'] and obj['Federation'].find('ALICE') >= 0):  
		alice_fed[obj['FederationAccountingName']]=1;
        if(debug > 0):
	        for key in sites_per_accountname:
			print "\n FederationAccountingName: ",key	
			for key2 in sites_per_accountname[key]:
				print "\n\t Site: %s"%(key2)	
	        for key in cms_fed:
			print "\n CMS FederationAccountingName- %s "%(key)	
	        for key in atlas_fed:
			print "\n ATLAS FederationAccountingName- %s "%(key)	
	        for key in alice_fed:
			print "\n ALICE FederationAccountingName- %s "%(key)	

        #url = 'http://gstat-wlcg.cern.ch/apps/pledges/resources/'+thisyear+'/2/json'
        srchUrl = 'PledgeUrl'
        modName = 'wlcg_pledges'
        print "%s: srchUrl: %s" % (modName, srchUrl)
        try:
            url = getattr(globals()['GratiaURLS'](), 'GetUrl')(srchUrl)
            print "%s: SUCCESS: getattr(globals()['GratiaURLS'](), 'GetUrl')(%s)" % (modName,srchUrl)
            print "%s: retUrl: %s" % (modName, url)
        except:
            print "%s: FAILED: getattr(globals()['GratiaURLS'](), 'GetUrl')(urlname=%s)" % (modName,srchUrl)
            pass
        response  = urllib2.urlopen(url)
	s = response.read()
	x = simplejson.loads(s)
	#resourcesnestedlist=x['aaData']
	for obj in x:
	    if('USA'==obj['Country'] and 'HEP-SPEC06' == obj['PledgeUnit']):
		try:
		   int(obj['ATLAS']) #atlas number exists
                   atlas_pledge[fednames_and_accounts[obj['Federation']]] = {'pledge': obj['ATLAS'], 'site_names': sites_per_accountname[fednames_and_accounts[obj['Federation']]]}
		except:
		   None

		try:
		   int(obj['CMS']) #cms number exists
                   cms_pledge[fednames_and_accounts[obj['Federation']]] = {'pledge': obj['CMS'], 'site_names': sites_per_accountname[fednames_and_accounts[obj['Federation']]]}
		except:
		   None

		try:
		   int(obj['ALICE']) #alice number exists
                   alice_pledge[fednames_and_accounts[obj['Federation']]] = {'pledge': obj['ALICE'], 'site_names': sites_per_accountname[fednames_and_accounts[obj['Federation']]]}
		except:
		   None
        if(debug > 0):
	        for key in cms_pledge:
			print "\n %s %s"%(key, cms_pledge[key]['pledge'])	
			for key2 in cms_pledge[key]['site_names']:
				print "\n\t %s"%(key2)	
        if(debug > 0):
	        for key in cms_fed:
			print "\n cms_fed: ",key	
	        for key in atlas_fed:
			print "\n atlas_fed: ",key	
        return atlas_pledge, cms_pledge, atlas_fed, cms_fed, alice_pledge, alice_fed


#WLCGWebUtil().wlcg_pledges()

