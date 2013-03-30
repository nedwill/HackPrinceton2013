import praw
r = praw.Reddit(user_agent='NedKyle')

numSubmissions = 25

submissions = r.get_subreddit('all').get_rising(limit=numSubmissions)

samples = [[[0 for x in xrange(5)] for y in xrange(15)] for z in xrange(25)]

import pickle
import time
import calendar

our_list = []

for submission in submissions:
	our_list += [submission]

minute = 0
while(minute < 15):
	i = 0
	print minute
	for submission in our_list:
		#submission = submissions[i]
		samples[i][minute][0] = submission.title
		samples[i][minute][1] = submission.score
		samples[i][minute][2] = submission.created_utc
		samples[i][minute][3] = calendar.timegm(time.gmtime())
		samples[i][minute][4] = submission.permalink
		i += 1
	time.sleep(60)
	minute += 1
	#for submission in submissions:
		#submission.refresh()

pickle.dump(samples, open('data.pkl', 'wb'))
#data = pickle.load(open('data.pkl', 'rb'))

#help(praw.objects.Submission)
