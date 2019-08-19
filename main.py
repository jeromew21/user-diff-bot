from bot import *

def handle_comment(comment):
    text = comment.body # Fetch body
    author = comment.author # Fetch author
    if not comment.saved:
        lower = text.lower()
        if lower.startswith("/u/user_diff_bot") or lower.startswith("u/user_diff_bot"):
            print("{}: \"{}\"".format(now_date(), text))
            args = text.split(" ")[1:]
            if args[0] == "compare":
                user1 = parse_redditor(args[1], None)
                user2 = parse_redditor(args[2], None)
                try:
                    print("Found users", user1.id, user2.id)
                except:
                    print("Exception occured.")
                else:
                    replytext = comparison_text(user1, user2) + "\n\n" + MESSAGE
                    print("Replying:", replytext)
                    comment.reply(replytext)
            elif tuple(args[0:3]) == ("most", "similar", "to"):
                user = parse_redditor(args[3], author)
                try:
                    print("Found user", user.id)
                except:
                    print("Exception occured.")
                else:
                    replytext = similar_text(user) + "\n\n" + MESSAGE
                    print("Replying:", replytext)
                    comment.reply(replytext)
                    print("Reply saved.")
            comment.save()

if __name__ == "__main__":
    subreddit = reddit.subreddit("testingground4bots")
    comments = subreddit.stream.comments()

    for comment in comments:
        try:
            handle_comment(comment)
        except Exception as e:
            print(e)
