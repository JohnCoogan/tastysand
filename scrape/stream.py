# Twitter Keyword Streamer

import threading, datetime, time, re
from optparse import OptionParser
from pymongo import Connection
from ssl import SSLError
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.utils import import_simplejson

json = import_simplejson()
active_terms = {}
STREAM_URL = "https://stream.twitter.com/1/statuses/filter.json?track=%s"

def get_parser():
    parser = OptionParser()
    parser.add_option("-d", "--dbfile", dest="dbfile", help="File with database options")
    parser.add_option("-o", "--oauth", dest="oauthfile", help="File with oauth options")
    parser.add_option("-t", "--terms", dest="termsfile", help="File with terms to search")
    parser.usage = "bad parametres"
    return parser

def updateSearchQuery(options):
    print 'Updating terms: %s' % datetime.datetime.now()
    
    query = ",".join(active_terms.keys())
    
    try:
        streamThread.stopConsume()
    except:
        pass
    
    streamThread = StreamConsumerThreadClass(query,options.oauthfile)
    streamThread.setDaemon(True)
    
    streamThread.start()
    

def addTerm(term):
    if term == '':
        return
    active_terms[term] = term
    
def deleteTerm(term):
    if term == '':
        return
    active_terms.pop(term)
        
    
def updateTerms(options):
    
    fileterms = []
    
    update = False
    f = file(options.termsfile,'r')
    for line in f.readlines():
        term = str.strip(line) 
        
        fileterms.append(term)
        #Check new terms
        if not term in active_terms.keys():
            print "New Term: %s" % term
            addTerm(term)
            update = True
    
    for current in active_terms.keys():
        if not current in fileterms:
            print "Deleted term: %s" % current
            deleteTerm(current)
            update = True
     
    if update:
        updateSearchQuery(options)
           
def prettyPrintStatus(status):
    text = status["text"]
    description = status['user']['screen_name']
    if "retweeted_status" in status:
        description = ("%s RT by %s") % (status["retweeted_status"]["user"]["screen_name"], status['user']['screen_name'])
        text = status["retweeted_status"]["text"]

    try:
        return '[%s][%-36s]: %s' % (status['created_at'], description, text)
    except UnicodeEncodeError:
        return "Can't decode UNICODE tweet"
    except :
        return "Error printing status"

class MongoDBCoordinator:
    def __init__(self,dbfile=''):
        dbinfo = json.loads(open(dbfile,'r').read())
        try:
            self.mongo = Connection(dbinfo['server'])
        except:
            print "Error starting MongoDB"
            raise
        
        self.db = self.mongo[dbinfo['database']]
        self.tuits = {}
    def addTuit(self,tweet):
        for term in active_terms.keys():
            
            content = tweet['text']
            if "retweeted_status" in tweet:
                content = tweet["retweeted_status"]["text"]
                
            strre = re.compile(term, re.IGNORECASE)
            match = strre.search(content)
            if match:
                
                if not term in self.db.collection_names():
                    self.db.create_collection(term)
                
                collection = self.db[term]
                collection.save(tweet)
        
                try:
                    print "[%-15s]%s" % (term, prettyPrintStatus(tweet))           
                except Exception as (e):
                    print "Error %s" % e.message



class MongoDBListener(StreamListener):
    # Listener handles tweets as they are recieved.
    def on_data(self, data):
        # Called when raw data is received.
        # Return False to stop stream and close connection.
        if 'in_reply_to_status_id' in data:
            jstatus = json.loads(data)
            mongo.addTuit(jstatus)
            
        elif 'delete' in data:
            delete = json.loads(data)['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False
        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False

    def on_error(self, status):
        print status
    def on_limit(self, track):
        print "###### LIMIT ERROR #######"

#Class that track the stream
class StreamConsumerThreadClass(threading.Thread):
    def __init__(self,term='',oauthfile=''):
        threading.Thread.__init__(self)
        self.searchterm = term
        self.name = term
        self.consume = True
        
        oauth = json.loads(open(oauthfile,'r').read())
        
        listener = MongoDBListener()
        auth = OAuthHandler(oauth['consumer_key'], oauth['consumer_secret'])
        auth.set_access_token(oauth['access_token'], oauth['access_token_secret'])
    
        self.stream = Stream(auth, listener,timeout=60)  
        
        
    def stopConsume(self):
        self.stream.disconnect()
      
    def run(self):
        now = datetime.datetime.now()
        print "Twitter Stream with terms: %s started at: %s" % (self.getName(), now)
        
        connected = False
        while True:
            try: 
                if not connected:
                    connected = True
                    self.stream.userstream()
            except SSLError, e:
                print e
                connected = False            


if __name__ == "__main__":
    parser = get_parser()
    (options, args) = parser.parse_args()
    print options, args
    
    mongo = MongoDBCoordinator(options.dbfile)
    streamThread = StreamConsumerThreadClass('',options.oauthfile)
    
    try:
        while True:
            updateTerms(options)
            time.sleep(5)
    except KeyboardInterrupt, e:
        print "Closing stream"
        streamThread.stopConsume()
