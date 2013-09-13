#Ned Williamson and Kyle Dhillon
#reddit.py v0.2
#Ranks hotness of growing stories in specified subreddits

#Changelog
#v0.1 Hackathon Presentation
#v0.2 See comment below

#sup kyle. now this does the top 30 from our 100 initial instead of posts >3 points because
#I wanted to include more subreddits. turns out pics people don't read the comments.
#I also improved the printing a bit in addition to making the thief only run once every 30 minutes
#so we can potentially run it 24/7 at some point when it's really stable.

#todo
#organize below list... lol
#clean up and refactor code, fix style, split into multiple files? with classes?
#don't repeat stolen comments -> keep a list, possibly save between sessions?
#different modes: data collection mode, ranking/prediction mode, thief mode (autobot)
#gui or cmdline options?

#scrapeNew still has dupes: we need to keep a list of all purged items... or should we let stories that are
#regrowing once again come back into our list? The correct way to do this according to doc:

#if submission.id not in already_done and our_test:
#		do something
#		already_done.append(submission.id)

#posts are stagnating before they grow... unlucky or are we pruning too aggressively? we should prune only as much
#as the size of our top, not all failing stories //update: it was pruning every 2 from demo, i switched it back to 5
#improve print data to have a live table instead of pushing a ton of garbage
#rank by hotness or delta hotness
#(done) instead of using a hard score limit to build a list of posts, take the top 30 from whatever we get
#algorithm change: scrape top 100 at first, check all after 100*2 seconds, then keep the top 30.
#currently we can't really filter by the best new posts in subreddits with tons of new submissions because we'll
#probably monitor some shitty submissions at first if the majority of new posts go nowhere.
#when score = 0 it acts weird because hotness = 0... is this acceptable?
#future: add bot for reposting stories?
#incorporate hotness into algorithm --- maybe rank growth on those of positive hotness first above those with negative
#actual hotness?
#catch http errors and just wait instead of crashing
#graduate stories that have high scores

#praw handles 2 second / 30 second rules automatically. should we remove our manual api checks?


import praw
import pickle
import time
import calendar
import math
from bs4 import BeautifulSoup
import urllib2
from urllib2 import urlopen

def init(username='yoloswagkarma',password='hackprinceton'):
	global r
	r = praw.Reddit(user_agent='NedKyle Hotness Predictor v0.2') #fix this so it's class based
	print "Logging in..."
	r.login(username,password)
	print "Login sucessful!"

def scrapeNew(subreddit='pics+AdviceAnimals+wtf+funny+politics+gaming+AskReddit',scrapeSize=100,returnSize=30):
	submissions = r.get_subreddit(subreddit).get_new(limit=scrapeSize)
	our_list = []
	for submission in submissions:
		#print submission.title
		our_list += [submission]
		#if submission.score > 2: #replace this with top 20 ranked by points instead of a straight limit
	#our_list = list(reversed(sorted(our_list, key=lambda submission: submission.score))) #sort our list by score
	our_list = list(reversed(sorted(our_list, key=lambda submission: hotness(submission.score,
		int(submission.created_utc),calendar.timegm(time.gmtime()))))) #sort our list by hotness
	#print "In original scrape list:"
	#for submission in our_list:
		#print submission.score
	#	print hotness(submission.score,int(submission.created_utc),calendar.timegm(time.gmtime()))
	return our_list[:returnSize]

def getRefreshRate(submissionList):
	trackingNumber = len(submissionList)
	refreshRate = 2*trackingNumber #2 seconds allowed per request
	return refreshRate

def sleepWithPrint(maxSeconds,curMinutes):
	seconds = 0
	while(seconds < maxSeconds):
		print "Cycle "+str(curMinutes+1)+": "+str(seconds+1)+" out of "+str(maxSeconds)+" seconds elapsed."
		time.sleep(1)
		seconds += 1

#def sign(x):				#deprecated, now included in hotness directly
#	if (x > 0): return 1
#	elif (x < 0): return -1
#	else: return 0

def printSampleInfo(sample):
	for element in sample:
		print element

def purgeList(our_list,samples,clearCount=5):
	newsamples = []
	new_our_list = []
	for sample in samples:
		pos = 0
		if (len(sample) >= clearCount): #we have >= clearCount refreshes
			for i in xrange(len(sample)-clearCount,len(sample)): #most recent clearCount refreshes
				if sample[i][-1] > 0:
					pos += 1
			if pos == 0: #all negative or 0
				print "We cleared a sample."
				#printSampleInfo(sample)
				continue
		newsamples += [sample]
		new_our_list += [our_list[samples.index(sample)]]
	if len(samples) > len(newsamples):
		print "We started with "+str(len(samples))+" and now we have "+str(len(newsamples))+"."
	return (new_our_list,newsamples)

def getOverallHotness(submissionSample):
	return submissionSample[-1][-2] - submissionSample[0][-2] #last - first

def minutesAgo(now,created): #give utc times in seconds since epoch
	return (now - created)/60

def getHottestData(data):
	return list(reversed(sorted(data, key=lambda hotness: getOverallHotness(hotness))))

def printHottestData(hottestData,cycle,top=10):
	print "The top "+str(top)+" rising stories based on current data (cycle #"+str(cycle)+"):"
	#return urls in order of size 5 that gives kyle the sites
	for i in xrange(min(len(hottestData),top)):
		age = minutesAgo(calendar.timegm(time.gmtime()),int(hottestData[i][0][2]))
		print "Rank #"+str(i+1)+":"+str(hottestData[i][0][4])
		print "Current hotness: "+str(hottestData[i][-1][-2])
		print "Delta hotness: "+str(getOverallHotness(hottestData[i]))
		print "Submitted: "+str(age)+" minutes ago."
	print ""

def getPermalinks(our_list):
	links = []
	for submission in our_list:
		links += [submission.permalink]
	return links

# given Reddit page URL returns string of matching URL, None if no matches
def karmaDecayBest(site):
	decaySite = site[site.index('/r'):]
	decaySite = "http://karmadecay.com" + decaySite
		
	hdr = {'User-Agent': 'Mozilla/5.0'}
	req = urllib2.Request(decaySite,headers=hdr)
	page = urllib2.urlopen(req)
	soup = BeautifulSoup(page)

	if (soup.find("tr", class_="ns") != None):
		a = None
	else: a = soup.find("tr", class_="result")

	results = []
	while (a != None and a.has_attr('class') and a['class']== [u'result']):
		if (a('td')[0].get_text() != '' and a('td')[2]('div')[5].b != None):
			comments = a('td')[2]('div')[5].b.get_text()
			comments = int(comments[:comments.index(' ')])
			url = a('td')[2]('div')[0].a['href']
			results += (url, comments),
		a = a.next_sibling.next_sibling
	from operator import itemgetter
	newres = tuple(sorted(results, key=itemgetter(1)))
	newres = newres[::-1] 
	if (len(newres) == 0):
		return None
	else: return newres[0][0]
	
# from a reddit submission URL, gets the top rated comment
def topComment(site):
	sub = praw.objects.Submission.from_url(r,url=site,comment_sort='top')   
	comments = sub.comments
	if len(sub.comments) != 0: 
		return sub.comments[0].body
	return None

def thief(sites):
	for site in sites:
		prevPost = karmaDecayBest(site)
		if prevPost == None:
			#print site + ": original post"
			print "original post identified"
		elif topComment(prevPost) == None:
			print "unoriginal, but no comments on previous submission"
		else:
			sub = praw.objects.Submission.from_url(r,url=site)
			#print site + ": " + topComment(prevPost)
			sub.add_comment(topComment(prevPost))
			print "Comment found and submitted!:",topComment(prevPost)
			sub.upvote() #added by kyle after pitch, testing now

def hottestSites(hottestData,top=10):
	sites = []
	for element in hottestData:
		sites += [element[0][4]]
	size = len(sites)
	returnLength = min(size,top)
	return sites[:returnLength]

def main():
	init()
	print "Let's go! We'll be running giving you our predictions until you kill us."
	our_list = scrapeNew()
	monitorSize = 30
	#print "In returned scrape list:"
	#for submission in our_list:
		#print submission.score
	#	print hotness(submission.score,int(submission.created_utc),calendar.timegm(time.gmtime()))
	#return
	samples = [0]*len(our_list)
	cycle = 0 #just for printing info
	while(True): #take cap off once we're done
		for i in xrange(len(our_list)):
			submission = our_list[i]
			now = calendar.timegm(time.gmtime()) #UTC seconds since epoch
			hot = hotness(submission.score,int(submission.created_utc),
				now)
			if not samples[i]: dhotness = 0 #if samples[i] is empty
			else: dhotness = hot - samples[i][-1][-2] #hotness - hotness of last refresh
			data = [submission.title,submission.score,int(submission.created_utc),
			now,submission.permalink,hot,dhotness]
			if not samples[i]: samples[i] = [data]
			else: samples[i] += [data]
		(our_list,samples) = purgeList(our_list, samples)
		hottestData = getHottestData(samples)
		printHottestData(hottestData,cycle)
		#print "hottestdata is:",hottestData
		sites = hottestSites(hottestData)
		if (cycle != 0 and cycle % 30 == 0): thief(sites)
		#thief(sites)
		if len(our_list) < 10:
			print "We have less than 10 hot entries, so we're getting new data."
			needed = monitorSize - len(our_list) #repeating len(our_list), optimize later
			new_entries = scrapeNew(returnSize=needed)
			our_list_permalinks = getPermalinks(our_list)
			for entry in new_entries:
				if entry.permalink not in our_list_permalinks:
					our_list += [entry]
					samples += [[]*len(our_list)] #maybe it's this i have no fucking idea
			print "We updated our list, so we are now monitoring "+str(len(our_list))+" stories."
		#printSampleInfo(samples)
		refreshRate = getRefreshRate(our_list) #this should be a static minute; i'll fix this later
		sleepWithPrint(refreshRate,cycle)
		cycle += 1
		length = len(our_list)
		for i in xrange(len(our_list)):
			submission = our_list[i]
			print "Refreshing submission #"+str(i+1)+" out of "+str(length)+" total."
			submission.refresh()
	#pickle.dump(samples, open('data.pkl', 'wb'))

def hotness(s,ti,tf):
	order = math.log(max(abs(s), 1), 10)
	sign = 1 if s > 0 else -1 if s < 0 else 0
	return order + ((ti - tf)*sign / 45000)

#hotness(score,ti,tf)
def testHotness():
	score = 12
	hours = 30
	print "Score %d's hotness over %d hours:"%(score,hours)
	for i in xrange(hours):
		hoursPassed = i*60*60
		print (hotness(score,0,hoursPassed))

#testHotness()

main()
#data = pickle.load(open('data.pkl', 'rb'))
