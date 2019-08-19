import praw
import re
import json
from helper import *
from collections import Counter

arr = [line.strip() for line in open("login_detail", "r").readlines()]

reddit = praw.Reddit(user_agent='User Diff reddit',
                  client_id=arr[0],
                  client_secret=arr[1],
                  username=arr[2],
                  password=arr[3])

def query_author_subreddits(user):
    print("Querying comments")
    comment_subreddits = [comment.subreddit_id for comment in user.comments.new(limit=None)]
    print("Querying submissions")
    submission_subreddits = [subm.subreddit_id for subm in user.submissions.new(limit=None)]
    return dict(Counter(comment_subreddits + submission_subreddits))

def author_subreddits(user, cursor):
    print("Getting comments and submissions for {}".format(user))
    query = """SELECT subreddits, date_updated FROM users where id = ?"""
    cursor.execute(query, (user.id,))
    data = cursor.fetchone()
    if data is None:
        print("Not in DB; querying")
        fullset = query_author_subreddits(user)
        query = """INSERT INTO users (id, username, subreddits, date_updated) VALUES (?, ?, ?, ?)"""
        cursor.execute(query, (user.id, user.name, json.dumps(fullset), now_date()))
    elif expired_date(date_from_str(data[1])):
        print("Found dirty in DB; updating")
        fullset = query_author_subreddits(user)
        query = """UPDATE users SET subreddits = ?, date_updated = ? WHERE id = ?; """
        cursor.execute(query, (json.dumps(fullset), now_date(), user.id))
    else:
        print("Found in DB")
        fullset = json.loads(data[0])
    return fullset

def comparison_text(user1, user2):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    u1set, u2set = author_subreddits(user1, cursor), author_subreddits(user2, cursor)
    conn.commit()
    s = ""
    s += "Comparing /u/{0} and /u/{1}\n\n".format(user1.name, user2.name)
    s += "Similarity (Dice coefficient): {0:.4f}\n\n".format(dice_dist(u1set, u2set))
    s += "Similarity (Jaccard distance): {0:.4f}\n\n".format(jaccard_dist(u1set, u2set))
    s += "Similarity (Overlap coefficient): {0:.4f}\n\n".format(overlap_dist(u1set, u2set))
    s += "Subreddits in common: {}\n\n".format(", ".join(subreddit_from_id(k, reddit) for k in union(u1set, u2set)))
    conn.close()
    return s

def find_most_similar_users(user, dist_func=jaccard_dist):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    user_set = author_subreddits(user, cursor)
    conn.commit()
    query = """SELECT username, subreddits FROM users where id != ?"""
    data = cursor.execute(query, (user.id,)).fetchall()
    if data:
        data = [(item[0], dist_func(set(item[1].split(",")), user_set)) for item in data]
        similar = sorted(data, key=lambda item: item[1])[-10:]
        return similar
    conn.close()
    return []

def similar_text(user, dist_func=jaccard_dist):
    s = ""
    s += "The most similar users to /u/{}:\n\n".format(user.name)
    s += table_str(("Rank", "User", "distance coefficient"), [(str(index+1), "/u/" + val[0], "{0:0.4f}".format(val[1])) for index, val in enumerate(reversed(find_most_similar_users(user, dist_func)))])
    return s

def parse_redditor(name, default):
    if name == "self":
        return default
    elif re.match(r"/u/.*", name):
        return reddit.redditor(name[3:])
    elif re.match(r"u/.*", name):
        return reddit.redditor(name[2:])

def populate_db():
    #go through all and add to the database...
    subreddit = reddit.subreddit("all")
    comments = subreddit.stream.comments()

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    for comment in comments:
        author = comment.author # Fetch author
        print(author.name, author_subreddits(author, cursor))
        conn.commit()
    conn.close()
