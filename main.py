#!/usr/bin/env python
####
import re, requests, sys
import urllib3
import os 
from os import path

urllib3.disable_warnings()
s = requests.Session()
PLUGINS = 'plugins'
import subprocess


####
def basic_rfi_params2(f):

  functions = ['require_once\s*\(*\s*\$([a-zA-Z0-9_-]+)\s*\)*','require\s*\(*\s*\$([a-zA-Z0-9_-]+)\s*\)*',
    'include_once\s*\(*\s*\$([a-zA-Z0-9_-]+)\s*\)*','include\s*\(*\s*\$([a-zA-Z0-9_-]+)\s*\)*',
    'file_get_contents\s*\(*\s*\$([a-zA-Z0-9_-]+)\s*\)*','eval\s*\(*\s*\$([a-zA-Z0-9_-]+)\s*\)*'] 
    #'unserialize\s*\(*\s*\$([a-zA-Z0-9_-]+)\s*\)*' ]
  
  methods = ['_GET','_POST','_REQUEST']

  fp = open(f,'r')
  lines = fp.readlines()

  #print 'checking file: %s' % ( f )

  #################################################
  #         require_once( $path ); // RFI #09
  #################################################

  for line in lines:
    for func in functions:
      pattern = func #+ '\s*\(*\s*\$([a-zA-Z0-9_-]+)\s*\)*' ## func # + '\((.*?)\$'# [\);]'
      x = re.compile(pattern)
      #print pattern
      y = re.search(x, line)

      if y:
        param = y.group(1)
        #print '---------------------------------------------------------------------------------'
        print 'name filename: %s' % ( f ) #print 'PATTERN: %s' % ( pattern )
        print 'Found parameter: %s' % ( param )
        print 'Full line:\n%s' % ( line )

        #print '\n---> checking param declaration:'
        # now let's find that param's declaration:
        for line in lines:
          for method in methods:

            temp_patt = param + '(.*?)=(.*?)' + method + '\[(.*?)\]'
            find_declar = re.compile(temp_patt)
            found_declar = re.search(find_declar, line)

            if found_declar:
              print '+ Found declaration of parameter: %s:\n%s' % ( found_declar.group(3), line )

        print '='*80


####
def basic_rfi_params(f):
  functions = ['include','include_once','require','require_once','file_get_contents','readfile','eval']
  methods = ['_GET','_POST','_REQUEST']

  fp = open(f, 'r')
  lines = fp.readlines()
  line_num = 0

  for line in lines:
    line_num += 1

    for function in functions:
      pattern1 = function + '(.?\()\$(.*?)'
      find = re.compile(pattern1)
      found = re.search(find, line)

      if found:
        param = found.group(2)
        print '='*80
        print 'Found function: %s with param %s in file %s (line: %s)\n%s' % ( function, str(param), f, line_num, line)

        # now we'll look for param declaration with one of the methods
        line_num = 0
        for line in lines:
          line_num += 1

          for method in methods:
            declar_patt =  param + '(.*?)=(.*?)' + method
            find_declar = re.compile(declar_patt)
            found_declar = re.search(find_declar, line)

            if found_declar:
              print 'Found param declaration at line %s: %s:\n%s' % (line_num, param, line )
              print ''

        print "="*80


####
def basic_rfi_methods(f):
  methods = ['_GET','_POST','_REQUEST']
  functions = ['include','include_once','require','require_once','file_get_contents','readfile']

  fp = open(f, 'r')
  lines = fp.readlines()
  line_num = 0

  for line in lines:
    line_num += 1
    for method in methods:
      for function in functions:
        #print 'searching for: %s' % ( function )

        pattern1 = function + '(.*?)\$' + method + '\[(.*?)\]'

        find = re.compile(pattern1)
        found = re.search(find, line)

        if found:
          param = found.group(2)
          sanit_check = found.group(1)
          if 'sanitize' not in sanit_check:

            print '[+] ==> Reading %s' % (f) # current file name
            print '[+] Found LFI/RFI bug: %s, %s (param: %s ):\n\t%s' % (f, line_num, param, line)
            print ""
            print "="*80




#### 
def basic_sqli_methods(f):

  methods = ['_GET','_POST','_REQUEST']
  functions = ['SELECT ','INSERT ','UPDATE ','DELETE ']

  fp = open(f, 'r')
  lines = fp.readlines()

  line_num = 0
  for line in lines:
    line_num += 1

    for method in methods:
      for function in functions:

        current_pattern = 'wpdb->(.*?)' + function + '(.*?)\$' + method + '\[(.*?)\]'
        find = re.compile(current_pattern)
        found = re.search(find, line)

        if found:
          print '*'*80
          print 'Checking file: %s' % ( f )
          print 'Found SQLI bug in file %s (param: %s) in line number %s:\n%s' % (f, line_num, found.group(3), line) 
          print '*'*80
          print '\n'
    


####
def readFile(f):
  #print "Reading file: %s" % ( f )

  # here we'll start all the functions to check the source code
  # ex. basic_xss_01(file), etc...

  #basic_rfi_methods(f)      # find GET with include*,etc...
  #basic_rfi_params(f)       # last edit: 23.10.2020 @ 14:18 
  #basic_rfi_params2(f)
  #basic_readfile_bugs(f)   # find readfile,file_*_content, etc... (params)
  #basic_sqli_methods(f)     # basic sqli (method + wp->query)
  print()



####
def check_source(temp_path):
  #print "======================="
  #print "  WE ARE IN check_source() for path: %s" % ( temp_path ) 
  #print "----------------------"


  files = []

  # r=root, d=directories, f = files
  for r, d, f in os.walk(temp_path):
    for file in f:
      if '.php' in file:
        files.append(os.path.join(r, file))

  for f in files:
    #print(f)
    readFile(f) # fullpath

  #print "---------------------"
  #print "============= NEXT CASE ================\n"



####
def main():

  try:
    os.mkdir(PLUGINS)
  except OSError as e:
    print e
    pass

  page_max = 0

  while page_max < 50:
    target = 'https://wordpress.org/plugins/browse/popular/page/' + str(page_max)
    #target = 'https://wordpress.org/plugins/browse/blocks/page/' + str(page_max)

    get_list = s.get(target, verify=False)
    got_list = get_list.text
   
    # 2. prepare a list of links (page1,page2,etc...)
    find_plugin_name = re.compile('<h3 class="entry-title"><a href="https://wordpress.org/plugins/(.*?)/" rel="bookmark">(.*?)</a></h3>')
    found_plug_name = re.findall(find_plugin_name, got_list)

    for plugin in found_plug_name:
      plugin1 = plugin[1].encode('utf8')
      print "On page %s: Found plugin name: %s" % ( page_max,  plugin1 )

      # plugin is found so we can try to download it now:
      full_plugin_link = 'https://wordpress.org/plugins/' + plugin[0]
      visit_plugin_link = s.get(full_plugin_link, verify=False)
      visited_plugin_link = visit_plugin_link.text

      get_this_plugin = re.compile('<a class="plugin-download button download-button button-large" href="(.*?)">Download</a>')
      got_this_plugin = re.search(get_this_plugin, visited_plugin_link)

      plugin_link = got_this_plugin.group(1)

      get_zip_name = re.compile('"https://downloads.wordpress.org/plugin/(.*?)">Download')
      got_zip_name = re.search(get_zip_name, visited_plugin_link )
      #print("ZIP NAME: " + str(got_zip_name.group(1)))

      if path.exists("./plugins/" + got_zip_name.group(1)):
        print("File exists! Skip: " + str(got_zip_name.group(1)))
        continue

      if got_this_plugin and not path.exists("./plugins/" + plugin_link):
        print "Downloading ==> %s" % ( plugin_link ) 
        do_wget = "wget -P ./plugins/ "+ plugin_link
        subprocess.call(do_wget, shell=True)
        print "[+] Plugin %s downloaded! :)" % ( plugin1 ) 

        # now we can move forward to:
        #   - unzip downloaded plugin/zip file
        get_zip_name = re.compile('"https://downloads.wordpress.org/plugin/(.*?)">Download')
        got_zip_name = re.search(get_zip_name, visited_plugin_link ) 

        print plugin_link
        print got_zip_name.group(1)


        if got_zip_name:
          print "  Let's unzip the file: %s" % ( got_zip_name.group(1) )
          print os.curdir 
          # -n never write existing files
          unzip_plugin = "unzip -d ./plugins/ -n ./plugins/" + got_zip_name.group(1) 
          subprocess.call(unzip_plugin,shell=True)

          # now we can move to the next step: checking source to find some bugs
          # 
          #   - try to prepare a nice and charm regexp to find a possible bug(s) ;]
          pwd = os.curdir
          plug_dir_name = got_zip_name.group(1).strip('.zip')
          #temp_path = pwd + "/plugins/" + plug_dir_name 
          temp_path = pwd + "/next_step_plugins/" 
          #temp_path = pwd + "/plugins_allpopular/"

          check_source(temp_path) # our super evil function ];>


          # let's try then.
          print '---------------------------------------------------------------------\n'


    # goto next page with plugins
    page_max += 1


  #if total_found:
    #max = total_found.group(1)
    #print 'Max pages: %s' % ( max ) 

  print 'finished main() now.' 


####
def analyse(temp_path = "./plugins/", level = "1"):
  print "="*80
  print "  Let's find something intresting in: %s" % ( temp_path ) 
  print "="*80

  files = []

  # r=root, d=directories, f = files
  for r, d, f in os.walk(temp_path):
	for file in f:
	  if '.php' in file:
		#print(file)
	    files.append(os.path.join(r, file))

  try:
    for f in files:
      if level == "1":
        basic_rfi_methods(f)      # find GET with include*,etc...
        basic_rfi_params(f)       # last edit: 23.10.2020 @ 14:18 
        basic_rfi_params2(f)
        basic_sqli_methods(f)     # basic sqli (method + wp->query)
      
      if level == "2": 
        basic_rfi_params2(f)
        basic_sqli_methods(f)     # basic sqli (method + wp->query)

      if level == "3": # sqli only
        basic_sqli_methods(f)     # basic sqli (method + wp->query)

  except Exception as e:
    print "#"*80
    print('Whoops! Analysis exception: ' + e.message)
    print "#"*80
    pass
  finally:
    pass



if __name__ == '__main__':

  try:
    module =  sys.argv[1] if len(sys.argv) > 1 else ""
    level =  sys.argv[3] if len(sys.argv) == 4 else ""
    
    if module == 'analyse':
	  pluginDir =  sys.argv[2] if len(sys.argv) > 2 else ""

	  if pluginDir:
		  analyse(pluginDir, level)
		  exit(0)

	  analyse()
	  exit(0)

    main()

  except Exception as e:
    print "#"*80
    print('Whoops! Main exception: ' + e.message)
    print "#"*80
    pass

