
import urllib

from template import Template
from auth import Authenticate

class Navigation(Authenticate, Template):

    def parse_dom(self):
        super(Navigation, self).parse_dom()
        self.site_sets = {}
        self.vo_sets = {}
        for setsDom in self.dom.getElementsByTagName("sets"):
            for setDom in setsDom.getElementsByTagName("set"):
                name = setDom.getAttribute("name")
                kind = setDom.getAttribute("kind")
                text = str(setDom.firstChild.data).strip()
                info = [i.strip() for i in text.split(',')]
                if kind == 'site':
                    self.site_sets[name] = info
                elif kind == 'vo':
                    self.vo_sets[name] = info

    def navFromRoles(self, data):
        self.user_roles(data)
        if data['is_site_owner']:
            sites = {}
            for site in data['site_ownership']:
                sites[site] = 'site?facility=%s' % site
            data['navigation']['Site Owner'] = sites
        if data['is_vo_owner']:
            vos = {}
            for vo in data['vo_ownership']:
                vos[vo] = 'vo_owner?vo=%s' % vo
            data['navigation']['VO Owner'] = vos
        if data['is_vo_member']:
            vos = {}
            for vo in data['vo_membership']:
                vos[vo] = 'vo_member?vo=%s' % vo
            data['navigation']['VO Membership'] = vos

    def gridNav(self, data):
        info = {"Accounting By Site": "bysite",
                "Accounting By VO":   "byvo",
                "Monitoring By Site": "monbysite",
                "Monitoring By VO":   "monbyvo",
                "Opportunistic Usage": "vo_opp",
               }
        data['navigation']['Grid-wide'] = info

    def otherNav(self, data):
        info = {}
        data['navigation']['Other'] = info
        for vo, members in self.vo_sets.items():
            set_info = '|'.join(members)
            set_info = urllib.quote(set_info, safe='')
            info['%s Set' % vo] = 'vo?vo=%s' % set_info
        for site, members in self.site_sets.items():
            set_info = '|'.join(members)
            set_info = urllib.quote(set_info, safe='')
            info['%s Set' % site] = 'site?facility=%s' % set_info
        
    def defaultData(self, data):
        super(Navigation, self).defaultData(data)
        data['navigation'] = data.get('navigation', {})
        self.navFromRoles(data)
        self.gridNav(data)
        self.otherNav(data)
        return data

