from datetime import datetime
import requests
import uuid
import json
import urllib.parse


class Review:
    def __init__(self, id, author, date, hours, last_two_weeks, last_played, content, comments, helpful, funny, recommended
                 , game_name):
        self.id = id
        self.author = author
        self.date = date
        self.hours = hours
        self.last_two_weeks = last_two_weeks
        self.last_played = last_played
        self.content = content
        self.comments = comments
        self.helpful = helpful
        self.funny = funny
        self.recommended = recommended
        self.game_name = game_name

    def get_content(self):
        return self.id, self.author, self.date, self.hours, self.last_two_weeks, self.last_played, self.content, \
               self.comments, self.helpful, self.funny, self.recommended, self.game_name


def get_reviews(appID, game_name):
    """Function which gets the appropriate JSON file from the steamAPI and appends the reviews into a list
    :parameter
    appID - The appID of the steam game
    game_name - Name of the game
    """

    print("Fetching Reviews..")
    reviews_list = []
    cursor = "*"

    while True:
        try:
            game_url = 'http://store.steampowered.com/appreviews/' + appID + '?json=1&cursor=' + cursor + '&filter=topratted'
            response = requests.get(game_url).json()
            cursor = urllib.parse.quote(response['cursor'])

            if response['query_summary']['num_reviews'] != 0 and len(reviews_list) < 500:
                for item in response['reviews']:
                    author = uuid.uuid5(uuid.NAMESPACE_DNS, item['author']['steamid'])
                    date = datetime.fromtimestamp(item['timestamp_created']).strftime('%d-%m-%y')
                    last_played = datetime.fromtimestamp(item['author']['last_played']).strftime('%d-%m-%y')

                    item['recommendationid'] = Review(item['recommendationid'],  # ID
                                                      str(author),  # Review Author
                                                      date,  # Date review was written
                                                      item['author']['playtime_forever'],  # Total play time of reviewer
                                                      item['author']['playtime_last_two_weeks'],  # Last Two Weeks
                                                      last_played,  # last played
                                                      item['review'],  # Review content
                                                      item['comment_count'],  # Comments on the review
                                                      item['votes_up'],  # Review helpful count
                                                      item['votes_funny'],  # Review funny count
                                                      item['voted_up'],
                                                      # If the reviewer recommended the game or not (True/False)
                                                      game_name  # Game Name
                                                      )

                    reviews_list.append(item['recommendationid'])

            else:
                break

            print("Reviews Collected: " + str(len(reviews_list)))

        except:
            break

    return reviews_list  # List contains all gathered reviews


def json_string(id, author, date, hours, last_tow_weeks, last_played, content, comments, helpful, funny, recommended, gameName):
    """Function which transforms individual strings into a JSON string"""
    _ = {
        "id": id,
        "author": author,
        "date": date,
        "hours": hours,
        "last_tow_weeks": last_tow_weeks,
        "last_played": last_played,
        "content": content,
        "comments": comments,
        "helpful": helpful,
        "funny": funny,
        "recommended": recommended,
        "gameName": gameName
    }
    return _


def get_reviews_run(appID, game_name):
    review_ids = get_reviews(appID, game_name)

    count = 0
    file_count = 1
    review_list = []

    for item in review_ids:
        if count == 5000 or item == review_ids[len(review_ids) - 1]:
            with open(f"{game_name}_{file_count}reviews.json", "w") as f:
                json.dump(review_list, f, indent=4, separators=(',', ': '))
                f.close()
            count = 0
            file_count += 1
            review_list = []

        id, author, date, hours, last_tow_weeks, last_played, content, comments, helpful, funny, recommended, \
        gameName = review_ids[review_ids.index(item)].get_content()

        _ = json_string(id, author, date, hours, last_tow_weeks, last_played, content, comments, helpful, funny,
                        recommended, gameName)

        review_list.append(_)
        count += 1
