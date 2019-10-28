# import the Flask class from the flask module
from flask import Flask, render_template
import flask
import pandas as pd
import pickle
import requests 
from bs4 import BeautifulSoup

def load_pickle(file_name):
    with open(file_name, 'rb') as f:
        unpickled_object = pickle.load(f)
    return unpickled_object

def parse_html(text):
	return BeautifulSoup(text, "html.parser").get_text()

#-------- DATA GOES HERE -----------#
stories_df = load_pickle('stories_df.pkl')

summaries_df = load_pickle('summaries_df.pkl')

# comments_df = load_pickle('comments_df.pkl')

tag_names = ['Python',
 'Mobile',
 'Design',
 'Security',
 'Blockchain',
 'AI/Machine Learning',
 'Google',
 'Microsoft',
 'Apple',
 'Facebook',
 'Amazon',
 'Startups',
 'Politics',
 'Databases',
 'Linux',
 'Data Science',
 'Science',
 'Math',
 'Javascript',
 'Web Dev',
 'DevOps',
 'Hardware/IoT',
 'AR/VR',
 'Games']


#-------- ROUTES GO HERE -----------#

# create the application object
app = Flask(__name__)

# use decorators to link the function to a url
# @app.route("/stories")
# def stories():
# 	return render_template('stories.html', stories_df=stories_df.head(60), tag_names=tag_names)

@app.route("/")
def stories():
	return render_template('stories.html', stories_df=stories_df.sample(60), tag_names=tag_names, tag="all")

@app.route("/stories/<id>")
def story(id):

	summary = summaries_df.loc[int(id), "article_summary"]
	unavailable_msg = "Sorry, a summary is unfortunately unavailable for this story at this time."
	
	if type(summary) != str or summary == "":
		summary = unavailable_msg
	elif "must log in to continue" in summary:
		summary = unavailable_msg
	elif "checkout with SVN using the repository’s web address" in summary:
		summary = unavailable_msg
	elif "website uses cookies to improve your experience" in summary:
		summary = unavailable_msg
	elif "repository has been archived by the owner" in summary:
		summary = unavailable_msg
	elif "can’t perform that action at this time" in summary:
		summary = unavailable_msg
	elif "always have the option to delete your Tweet location history" in summary:
		summary = unavailable_msg
	elif "browser does not support all of the required features" in summary:
		summary = unavailable_msg
	elif "you would like to continue anyway" in summary:
		summary = unavailable_msg
	elif "page has moved to" in summary:
		summary = unavailable_msg
	elif "report has been saved" in summary:
		summary = unavailable_msg
	elif "unsupported on your device" in summary:
		summary = unavailable_msg
	elif "cannot display this file" in summary:
		summary = unavailable_msg

	try:
		story_json = requests.get('https://hacker-news.firebaseio.com/v0/item/{}.json'.format(id)).json()
		
		comments_ids = story_json["kids"]
		try:
			comments_ids = comments_ids[:5]
		except:
			pass
		comments = []
		for each_comment_id in comments_ids:
			comment_json = requests.get('https://hacker-news.firebaseio.com/v0/item/{}.json'.format(each_comment_id)).json()
			try:
				commenter = comment_json["by"]
			except:
				commenter = "unknown"
			try:
				comment_text = parse_html(comment_json["text"])
				comments.append((commenter, comment_text)) 
			except:
				pass
	except:
		comments = []

	return render_template('story.html', story_row=stories_df.loc[int(id), :], stories_df=stories_df, tag_names=tag_names, summary=summary, comments_list=comments)

@app.route("/tags/<tag_name>")
def tag(tag_name):
	# return all stories with tag id = {}
	if 'q' in tag_name:
		tag_name = tag_name.replace('q', '/')

	return render_template('stories.html', stories_df=stories_df[stories_df[tag_name] == 1].sample(60), tag_names=tag_names, tag=tag_name)

# def article(url):
# 	return redirect(url)

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)