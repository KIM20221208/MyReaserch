from datetime import datetime
import requests
import uuid
import json
import urllib.parse


class Review:
    def __init__(self, id, author, date, hours, content, comments, source, helpful, funny, recommended
                 , franchise, game_name):
        self.id = id
        self.author = author
        self.date = date
        self.hours = hours
        self.content = content
        self.comments = comments
        self.source = source
        self.helpful = helpful
        self.funny = funny
        self.recommended = recommended
        self.franchise = franchise
        self.game_name = game_name

    def get_content(self):
        return self.id, self.author, self.date, self.hours, self.content, self.comments, self.source, self.helpful, \
               self.funny, self.recommended, self.franchise, self.game_name


def get_reviews(appID, source, franchise, game_name):
    """Function which gets the appropriate JSON file from the steamAPI and appends the reviews into a list
    :parameter
    appID - The appID of the steam game
    source - Platform the review was found (Steam)
    franchise - Franchise the game belongs to
    game_name - Name of the game
    """

    print("Fetching Reviews..")
    reviews_list = []
    cursor = "*"

    while True:
        try:
            game_url = 'http://store.steampowered.com/appreviews/' + appID + '?json=1&cursor=' + cursor + '&filter=recent'
            response = requests.get(game_url).json()
            cursor = urllib.parse.quote(response['cursor'])

            if response['query_summary']['num_reviews'] != 0:
                for item in response['reviews']:
                    author = uuid.uuid5(uuid.NAMESPACE_DNS, item['author']['steamid'])
                    date = datetime.fromtimestamp(item['timestamp_created']).strftime('%d-%m-%y')

                    item['recommendationid'] = Review(item['recommendationid'],  # ID
                                                      str(author),  # Review Author
                                                      date,  # Date review was written
                                                      item['author']['playtime_forever'],  # Total play time of reviewer
                                                      item['review'],  # Review content
                                                      item['comment_count'],  # Comments on the review
                                                      source,  # Platform review was written on
                                                      item['votes_up'],  # Review helpful count
                                                      item['votes_funny'],  # Review funny count
                                                      item['voted_up'],
                                                      # If the reviewer recommended the game or not (True/False)
                                                      franchise,  # Franchise of the game
                                                      game_name  # Game Name
                                                      )

                    reviews_list.append(item['recommendationid'])

            else:
                break

        except:
            break
    print("Reviews Collected: " + str(len(reviews_list)))

    return reviews_list  # List contains all gathered reviews


def json_string(id, author, date, hours, content, comments, source, helpful, funny, recommended, franchise, gameName):
    """Function which transforms individual strings into a JSON string"""
    _ = {
        "id": id,
        "author": author,
        "date": date,
        "hours": hours,
        "content": content,
        "comments": comments,
        "source": source,
        "helpful": helpful,
        "funny": funny,
        "recommended": recommended,
        "franchise": franchise,
        "gameName": gameName
    }
    return _


if __name__ == '__main__':
    review_ids = get_reviews("730", "steam", "Persona", "Persona 5 Strikers")

    count = 0
    file_count = 1
    review_list = []

    for item in review_ids:
        if count == 5000 or item == review_ids[len(review_ids) - 1]:
            with open("{}reviews.txt".format(file_count), "w") as f:
                json.dump(review_list, f, indent=4, separators=(',', ': '))
                f.close()
            count = 0
            file_count += 1
            review_list = []

        id, author, date, hours, content, comments, source, helpful, funny, recommended, franchise, gameName = \
            review_ids[review_ids.index(item)].get_content()

        _ = json_string(id, author, date, hours, content, comments, source, helpful, funny, recommended, franchise,
                        gameName)

        review_list.append(_)
        count += 1