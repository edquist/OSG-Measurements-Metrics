#!/usr/bin/env python

import sys
import os
import datetime
import time
import urllib2
import ConfigParser
from xml.dom.minidom import parse
import socket
socket.setdefaulttimeout(300)

from pkg_resources import resource_stream

from gratia.graphs.animated_thumbnail import animated_gif

timestr = str(datetime.datetime.now())

def parseOpts( args ):
  # Stupid python 2.2 on SLC3 doesn't have optparser...
  keywordOpts = {}
  passedOpts = []
  givenOpts = []
  length = len(args)
  optNum = 0
  while ( optNum < length ):
    opt = args[optNum]
    hasKeyword = False
    if len(opt) > 2 and opt[0:2] == '--':
      keyword = opt[2:]
      hasKeyword = True
    elif opt[0] == '-':
      keyword = opt[1:]
      hasKeyword = True
    if hasKeyword:
      if keyword.find('=') >= 0:
        keyword, value = keyword.split('=', 1)
        keywordOpts[keyword] = value
      elif optNum + 1 == length:
        passedOpts.append( keyword )
      elif args[optNum+1][0] == '-':
        passedOpts.append( keyword )
      else:
        keywordOpts[keyword] = args[optNum+1]
        optNum += 1
    else:
      givenOpts.append( args[optNum] )
    optNum += 1
  return keywordOpts, passedOpts, givenOpts


def skip_section(section):
    if section == 'General' or section == 'variables':
        return True
    if section.startswith('animated_thumbnail'):
        return True
    return False

def generateImages(cp, timestamp, src, dest, replace=False, variables={}, 
        entry=None):
    # Make sure general-purpose graphs get made first
    sections = cp.sections()
    filtered_sections = []
    for s in sections:
        if s.find(":") < 0:
            filtered_sections.append(s)
    for s in sections:
        if s.find(":") >= 0:
            filtered_sections.append(s)
    for section in filtered_sections:
        if entry != None and section != entry:
            continue
        if skip_section(section):
            continue
        has_generated=False
        image_path = cp.get(section, 'image')
        for varname, vals in variables.items():
            rep = ':' + varname
            if rep in section:
                has_generated=True
                for val in vals:
                    my_section = section.replace(rep, val)
                    my_image_path = image_path.replace(rep, val)
                    filename = dest % my_section
                    generateImage(filename, my_image_path, timestamp, src, 
                        dest, replace)
        if not has_generated:            
            filename = dest % section
            generateImage(filename, image_path, timestamp, src, dest, replace)
       

def generateImage(filename, image_path, timestamp, src, dest, replace):
        source = src + image_path
        source = source.replace(':today', str(timestamp))
        erroroccured=False
        stopwatch = -time.time()
        if os.path.exists(filename) and not replace:
            print "%s Not overwritting %s " %(timestr, filename)
            return
        try:
            input = urllib2.urlopen(source)
            output = open(filename, 'w')
            output.write(input.read())
            input.close()
            output.close()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception, e:
            erroroccured=True
            print >> sys.stderr, "%s Exception occurred while making static " \
                "copy of %s : %s" % (timestr, source, str(e))
        if(not erroroccured):
            print "%s Created image %s to %s - Took %.2f seconds." % (timestr, source, filename, stopwatch + time.time())


def generate(cp, entry=None):

    src = cp.get("General", "Source")
    orig_dest = cp.get("General", "Dest")
    start_str = cp.get("General", "StartDate")
    utcOffset = cp.getint("General", "UTCOffset")
    suffix = cp.get("General", "Suffix")
    replace = cp.getboolean("General", "Replace")
    try:
        generate_hist_graphs = cp.getboolean("General", "GenerateHistoricalGraphs")
    except:
        generate_hist_graphs = False
    variables = parse_variables(cp)
    
    today_date = datetime.date.today()
    today = datetime.datetime(today_date.year, today_date.month, today_date.day)
    one_day = datetime.timedelta(1, 0)
    time_tuple = time.strptime(start_str, '%Y-%m-%d')
    firstDate = datetime.datetime(*time_tuple[0:3])
    curDate = today

    while curDate >= firstDate:
        if (today - curDate).days > 30:
            continue
        timestamp = int(curDate.strftime('%s')) + 3600*utcOffset
        if curDate == today:
            dest = os.path.join(orig_dest, 'today')
            try:
                os.makedirs(dest)
            except OSError, e:
                if e.errno != 17:
                    raise
            dest = os.path.join(dest, '%s' + suffix)
            generateImages(cp, timestamp, src, dest, replace=True, \
                variables=variables, entry=entry)
        if  not generate_hist_graphs:
            print "%s Historical graph parameter not set exiting now...\n"%(timestr)
            break
            
        dest = os.path.join(orig_dest, curDate.strftime('%Y/%m/%d'))
        try:
            os.makedirs(dest)
        except OSError, e:
            if e.errno != 17:
                raise
        dest = os.path.join(dest, '%s' + suffix)
        generateImages(cp, timestamp, src, dest, replace=(replace or \
            curDate==today), variables=variables)
        generateImages(cp, timestamp, src, dest, replace=replace, 
                       variables=variables)
        destdir = os.path.join(orig_dest, curDate.strftime('%Y/%m/%d'))
        generate_thumbnails(cp, destdir)
        curDate = curDate - one_day

def parse_variables(cp):
    if not cp.has_section('variables'):
        return {}
    retval = {}
    for option in cp.options('variables'):
        url = cp.get('variables', option)
        retval[option] = get_variable_values(url)
    return retval

def get_variable_values(url):
    retval = []
    try:
        xmldoc = urllib2.urlopen(url)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, e:
        print >> sys.stderr, "%s Exception occurred while getting variable " \
            "values: %s" % (timestr, str(e))
        return retval
    dom = parse(xmldoc)
    for pivot in dom.getElementsByTagName('pivot'):
        pivot_str = pivot.getAttribute('name')
        if len(pivot_str) > 0:
            retval.append(pivot_str)
    return retval

def generate_thumbnails(cp, dest=None):
    if dest == None:
        dest = cp.get('General', 'Dest') + '/today'
    for section in cp.sections():
        if not section.startswith('animated_thumbnail'):
            continue
        try:
            height = cp.getint(section, 'height')
        except:
            height = 10000
        try:
            width = cp.getint(section, 'width')
        except:
            width = 1000
        try:
            grey = cp.getboolean(section, 'grey')
        except:
            grey = False
        source = [os.path.join(dest, i.strip()) for i in cp.get(section, \
                  'source').split(',')]
        output = os.path.join(dest, cp.get(section, 'output'))
        animated_gif(output, source, (width, height), greyscale=grey)

def main():
    kwArgs, passed, given = parseOpts(sys.argv[1:])
    global timestr
    
    config_files = kwArgs.get('config', '').split(',')
    config_files = [os.path.expandvars(i) for i in config_files \
                    if len(i.strip()) > 0]
    for config_file in config_files:
        if not os.path.exists(config_file):
            print >> sys.stderr, "%s Config file %s not found." % (timestr, config_file)
            sys.exit(1)

    if not config_files:
        config_files = ["/etc/osg_graphs.conf"]

    cp = ConfigParser.ConfigParser()
    cp.read(config_files)
   
    try:
        if not cp.getboolean("General", "Enabled"):
            print "%s Config file %s does not have Enabled=true in [General]." % \
                (timestr, ", ".join(config_files))
            print "%s Exiting 0 as requested." % (timestr)
            sys.exit(0)
    except SystemExit:
        raise
    except:
        print sys.stderr, "%s Unable to determine if config file %s has been enabled." % (timestr, ", ".join(config_files))
        sys.exit(1)
 
    if 'entry' in kwArgs:
        generate(cp, entry=kwArgs['entry'])
    else:
        generate(cp)
        generate_thumbnails(cp)

if __name__ == '__main__':
    main()

