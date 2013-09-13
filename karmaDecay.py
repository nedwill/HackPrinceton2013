# Best Repost Method - Kyle Dhillon and Ned Williamson
# 3/30/2013 Princeton Hackathon
# Uses http://karmadecay.com

# given Reddit page URL returns string of matching URL, None if no matches
def karmaDecayBest(site):
    decaySite = site[site.index('/r'):]
    decaySite = "http://karmadecay.com" + decaySite
    print decaySite
        
    from bs4 import BeautifulSoup
    import urllib2
    from urllib2 import urlopen

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

#test and print site
print karmaDecayBest(site)
