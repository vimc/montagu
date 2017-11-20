from settings import get_secret
import requests
import json

class Notifier:
    def __init__(self, channel):
        path = get_secret('slack/deploy-webhook')
        self.enabled = len(channel) > 0
        self.url = 'https://hooks.slack.com/services/{}'.format(path)
        self.channel = "#" + channel
        self.username = "montagu-bot"
        self.icon = ":robot_face:"
        self.headers = {'Content-Type': 'application/json'}
    def post(self, message):
        if not self.enabled:
            return
        data = json.dumps({"text": message,
                           "channel": self.channel,
                           "username": self.username,
                           "icon_emoji": self.icon})
        r = requests.post(self.url, data=data, headers=self.headers)
        if r.status_code >= 300:
            raise Exception("Error sending message: " + r.reason)
