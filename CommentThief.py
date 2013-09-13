# CommentThief - Kyle Dhillon and Ned Williamson
#3/30/2013 Princeton Hackathon
# uses http://karmadecay.com, praw, BeautifulSoup

import praw
from bs4 import BeautifulSoup
import urllib2
from urllib2 import urlopen
r = praw.Reddit(user_agent='NedKyle')

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
            print site + ": original post"
        elif topComment(prevPost) == None:
            print "no comment"
        else:
            print site + ": " + topComment(prevPost)        

submissions = r.get_subreddit('pics').get_new(limit=20)  
sites = []
for sub in submissions:
    sitename = sub.permalink
    sites.append(sitename)

thief(sites)


def 
print "starting"
site = "http://www.reddit.com/r/funny/comments/1bb6cu/high_way/"
sub = praw.objects.Submission.from_url(r,url=site)
print topComment(karmaDecayBest(site))
r.login('yoloswagkarma','hackprinceton')
sub.add_comment('lol')
#also, upvote!



    
