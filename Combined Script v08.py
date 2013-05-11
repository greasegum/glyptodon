#############################
### A.A. Geoparsing v0.86 ###
#############################


#Test if behind columbia.edu
import socket
print 'Getting your external domain...'
def getExternalIP():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(('google.com', 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip

try:
    rdomain_lookup = socket.gethostbyaddr(getExternalIP())
    cu_dns = "columbia.edu" in rdomain_lookup[0]
    print ('domain: '+ rdomain_lookup[0])
    print 'Your access to JSTOR provided by Columbia University Libraries.'

except:
    print 'Can\'t get your domain name. Assuming you are on a CU network...'
    cu_dns = True

#Loading the stable-id list
print 'Loading the stable-id list...'
id_file = 'jstor-aa-stable-ids.csv'
id_list = []

with open(id_file, 'r') as id_data:
    for each_line in id_data:
        each_line = each_line.strip('\n')
        id_list.append(each_line)

#set number of articles to test with
max_articles = 2
article_count = 50

#######
##Connect to Server
#######

def jstor_connect():

    import mechanize
    import cookielib

    print ('Instantiating Browser...')
    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = cookielib.CookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but won't hang on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    r = br.open('http://www.jstor.org.ezproxy.cul.columbia.edu/')

    br.select_form(nr=0)
    br.form['username'] = 'emg2162'
    br.form['password'] = 'zorg13'
    br.submit()
    return cj

##    print br.response().read()

print 'Connecting...'
if cu_dns != True:
    cj = jstor_connect()
else:
    print 'Already Connected...'
    
########

def jstor_process(stable_id, cu_dns_test):
    article_pdf = stable_id+ '.pdf'
    article_path = 'pdf/' + article_pdf
   
    if cu_dns_test == True:
        article_url = 'http://www.jstor.org/stable/pdfplus/'+ article_pdf+ '?acceptTC=true'
    else:
        article_url = 'http://www.jstor.org.ezproxy.cul.columbia.edu/stable/pdfplus/'+ article_pdf+ '?acceptTC=true'

##    download an article pdf
    import requests
    print 'Begin downloading article ['+ stable_id+ '] to ../pdf/...'
    if cu_dns_test == True:
        with open(article_path, 'wb') as fh: fh.write(requests.get(article_url).content)
    else:
        with open(article_path, 'wb') as fh: fh.write(requests.get(article_url, cookies = cj).content)
    
##    convert article to Plaintext
    from subprocess import call
    article_text = 'txt/'+ stable_id+ '.txt'
    print 'converting article ['+ stable_id+ '] to plaintext...'
    call("pdf2txt -p 2,3,4,5,6 -o "+ article_text+ " -n "+ article_path, shell=True) ##find a way to ditch cover page
    print '[ditched cover page.]' 
    
##    delete pdf to save space
##    from os import remove
##    remove (article_pdf)

def CallPlaceMaker(stable_id):
    import requests
    import textwrap
    import string

##redundant?    article_text = stable_id+ '.txt' 

    with open(article_text, 'r') as raw_file:
        raw = raw_file.read()
    cooked = raw.translate(string.maketrans("",""), string.punctuation)
    cooked = cooked.replace(' ', '+').replace('\n', '+')#.replace('AMERICAN ANTIQUITY'...
    chunks = textwrap.wrap(cooked,25000)
    count = 0
#    print chunks
#    raise Exception

    for bite in chunks:
        payload = {'documentContent': bite,
               'documentType': 'text/plain',
               'outputType': 'json',
               'appid': '8esBn8zV34HsT7soLbpvr_QBrkdM4rk75MljMJnyo1fqDjXnpD3ceolhuzabzEdOAx0nkJqIeq4aJC1EBehztSeQEcqSgoo-',
##             'characterLimit': '50000'
               }
        count = count + 1
        print 'Uploading cooked text (part ' + str(count)+'/'+ str(len(chunks))+') to Yahoo! PlaceMaker...'
        r = requests.post('http://wherein.yahooapis.com/v1/document', data=payload)
        output_r = r.text
        output_r = output_r.encode('ascii', 'replace')

        try:
            print 'Saving arbitrary text chunk (part ' + str(count)+'/'+ str(len(chunks))+')to chunk/'
            chunk_path = 'chunk/'+ stable_id+ 'raw-part-'+ str(count)+'.txt'#
            with open(chunk_path, 'wt') as output_chunk:
                output_chunk.write(bite)

        except IOError as err:
            print('File error: ' + str(err))

        try:
            print 'Writing PlaceMaker json file...'
            ypm_return = 'json/'+ stable_id+ 'raw-part-'+ str(count)+'.json'#
            with open(ypm_return, 'wt') as output_ypm:
                output_ypm.write(output_r)

            #keep a log of .json files created
#            with open('.ypm.xml.log', 'at') as logfile_w: #rewrite with pickle (for 0.9)
#                logfile_w.write(ypm_return+ '\n')

        except IOError as err:
            print('File error: ' + str(err))


##
#Scrape XML Data for <placeDetails>...</> only
##to convert json to dict import simplejson, simplejson.loads(string)
            
##def scrape_placeDetails():
##
##    from lxml import etree
##    
##    scrub_list = []
##    try:
##        with open('.ypm.xml.log', 'r') as logfile_r:
##            for each_xml in logfile_r:
##                scrub_list.append(each_xml)
##
##    except IOError as err:
##        print('Couldn\'t get log file.' + str(err))
##
##    for each_mess in scrub_list:
##        each_mess = each_mess.strip('\n')
##        scrubbed_xml_output = 'scraped-'+ each_mess
##        with open(scrubbed_xml_output, 'wt') as output_file:
##            print>>output_file, '<?xml version="1.0" encoding="UTF-8" ?>\n  <document>'
##            for el in etree.parse(each_mess).xpath('.//placeDetails'):
##                print>>output_file, (etree.tostring(el))#.strip('\n')
##            print>>output_file, '</document>'
##
##    #delete dirty .xml to avoid clutter
##    from os import remove
##    remove(each_mess)

#######################
###execute functions###
#######################


for each_id in id_list:
    if article_count <= max_articles:
        article_count = article_count + 1
        jstor_process(each_id, cu_dns)
        CallPlaceMaker(each_id)

##    else:
##        print 'Scraping XML...'
##        scrape_placeDetails()
print 'Done!'
