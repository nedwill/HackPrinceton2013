#gets top comment from reddit submission
#uses praw 2.0
import praw
r = praw.Reddit(user_agent='NedKyle')

# from a reddit submission URL, gets the top rated comment
def topComment(site):
    sub = praw.objects.Submission.from_url(r,url=site,comment_sort='top')   
    comments = sub.comments
    return sub.comments[0].body
    
site = "http://www.reddit.com/r/gaming/comments/1baurn/miyamoto_knows_whats_up/"
print topComment(site)


