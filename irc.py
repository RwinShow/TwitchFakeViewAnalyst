import socket
import datetime


class Tag:
    def __init__(self, input=[]):
        i = 0
        self.attr = {}
        for item in input:
            self.attr[item[: item.find("=")]] = item[item.find("=") + 1 :]

    def isBan(self):
        if ("ban-duration" in self.attr) or ("login" in self.attr):
            return False
        if ("target-user-id" in self.attr) and ("ban duration" not in self.attr):
            return True

    def isTimeout(self):
        if ("ban-duration" in self.attr) and ("target-user-id" in self.attr):
            return True
        else:
            return False

    def isEmoteOnly(self):
        if ("emote-only" in self.attr) and ("display-name" not in self.attr):
            return True
        else:
            return False

    def isFollowersOnly(self):
        if "followers-only" in self.attr:
            return True
        else:
            return False

    def isSubsOnly(self):
        if "subs-only" in self.attr:
            return True
        else:
            return False

    def isR9K(self):
        if "r9k" in self.attr:
            return True
        else:
            return False

    def isSlow(self):
        if "slow" in self.attr:
            return True
        else:
            return False

    def show(self):
        print("{}".format(self.attr))


class TwitchChat:
    SERVER = "irc.twitch.tv"
    PORT = 6667
    irc = socket.socket()
    BOT = ""
    PASS = ""
    feed_flag = False
    command_queue = []
    print_events = False
    print_actions = False
    print_message = False
    print_join = False
    print_part = False
    recent_join_counter = 0
    recent_join_timer = -1
    now = datetime.datetime.now()

    def __init__(self, user, password):
        self.BOT = user
        self.PASS = password
        self.irc.connect((self.SERVER, self.PORT))

    def sendIRC(self, command):
        self.irc.send(command.encode())

    def setUsername(self, user):
        self.BOT = user

    def setPassword(self, password):
        self.PASS = password

    def identify(self):
        self.sendIRC("PASS " + self.PASS + "\n" + "NICK " + self.BOT + "\n")

    def requestCAP(self):
        # You can also use the following alongside with membership for more information: twitch.tv/tags twitch.tv/commands
        self.sendIRC("CAP REQ :twitch.tv/membership\r\n")

    def joinChannel(self, channel):
        if self.recent_join_counter < 19:
            self.sendIRC("JOIN #" + channel.lower() + "\n")
            self.recent_join_counter += 1
            if self.recent_join_timer == -1:
                self.recent_join_timer = datetime.datetime.now()
            if self.print_actions:
                print("|BOT JOIN #{}|".format(channel))
            return True
        else:
            self.time_difference = datetime.datetime.now() - self.recent_join_timer
            if self.time_difference.total_seconds() > 10:
                self.sendIRC("JOIN #" + channel.lower() + "\n")
                self.recent_join_timer = datetime.datetime.now()
                self.recent_join_counter = 1
                return True
            else:
                self.command_queue.append(["JOIN", channel])
                return False

    def leaveChannel(self, channel):
        self.sendIRC("PART #" + channel + "\n")
        if self.print_actions:
            print("|BOT PART #{}|".format(channel))

    def readFeed(self):
        while self.feed_flag == False:
            if self.command_queue:  # if there's something in the queue
                if self.command_queue[0][0] == "JOIN":
                    self.time_difference = (
                        datetime.datetime.now() - self.recent_join_timer
                    )
                    if self.time_difference.total_seconds() > 10:
                        if self.joinChannel(self.command_queue[0][1]):
                            self.command_queue.pop(0)

            feedBuffer = self.irc.recv(4096)
            try:
                feed = feedBuffer.decode()
            except:
                print("Error in decoding feedBuffer")
            for line in feed.split("\r\n"):
                if len(line) > 0:
                    self.processFeed(line)

    def processFeed(self, feed):
        if feed.find("PING :tmi.twitch.tv") >= 0:
            self.onPing(feed)
        # elif(feed[0] == ":"): # Twitch has made changes to this section, needs to be updated.
        #      self.processAction(feed) 
        elif feed[0] == ":":
            self.processEvent(feed)

    def processAction(self, feed):
        print(feed)
        pass

    def processEvent(self, feed):
        feed = feed.replace("\r", "").replace("\n", "")
        tmi = feed.find("tmi.twitch.tv")
        tagList = feed[1 : tmi - 1].split(";")
        tags = None

        if len(tagList) > 1:
            tags = Tag(tagList)

        body = feed[tmi + 14 :]
        hashtag = body.find("#")
        colon = body.find(":")

        if body.find("PRIVMSG") == 0:
            channel = body[8 : colon - 1]
            message = body[colon + 1 :]
            self.onMessage(tags, channel, message)

        elif body.find("JOIN") == 0:
            channel = body[hashtag + 1 :]
            user = feed[1 : feed.find("!")]
            self.onJoin(channel, user)

        elif body.find("PART") == 0:
            channel = body[hashtag + 1 :]
            user = feed[1 : feed.find("!")]
            self.onPart(channel, user)

        elif body.find("CLEARCHAT") == 0:
            channel = body[10 : colon - 1]
            user = body[colon + 1 :]

            if tags.isBan():
                self.onBan(tags, channel, user)

            if tags.isTimeout():
                self.onTimeout(tags, channel, user)

        elif body.find("CLEARMSG") == 0:
            channel = body[9 : colon - 1]
            message = body[colon + 1 :]

            self.onClearMessage(tags, channel, message)

        elif body.find("ROOMSTATE") == 0:
            space = body.find(" ")
            at = body.find("@")
            channel = body[space + 1 :]
            if at != -1:
                channel = body[space + 1 : at]

            if tags.isEmoteOnly():
                self.onEmoteOnly(tags, channel)

            elif tags.isFollowersOnly():
                self.onFollowersOnly(tags, channel)

            elif tags.isSubsOnly():
                self.onSubsOnly(tags, channel)

            elif tags.isR9K():
                self.onR9K(tags, channel)

            elif tags.isSlow():
                self.onSlow(tags, channel)

            else:
                self.onRoomState(tags, channel)

        elif body.find("NOTICE") >= 0:
            channel = body[hashtag : colon - 1]
            message = body[colon + 1 :]
            self.onNotice(tags, channel, message)

    def onPing(self, feed):
        self.sendIRC("PONG :tmi.twitch.tv\r\n")

    # override these
    def onNotice(self, tags, channel, message):
        if self.print_events:
            print("{} message {}|".format(channel, message))
        pass

    def onSlow(self, tags, channel):
        if self.print_events:
            print("{} changed slow to {}|".format(channel, tags.attr["slow"]))
        pass

    def onR9K(self, tags, channel):
        if self.print_events:
            print("{} changed r9k to {}|".format(channel, tags.attr["r9k"]))
        pass

    def onSubsOnly(self, tags, channel):
        if self.print_events:
            print("{} changed subs only to {}|".format(channel, tags.attr["subs-only"]))
        pass

    def onFollowersOnly(self, tags, channel):
        if self.print_events:
            print(
                "{} changed followers only to {}|".format(
                    channel, tags.attr["followers-only"]
                )
            )
        pass

    def onEmoteOnly(self, tags, channel):
        if self.print_events:
            print(
                "{} toggled emote only to {}|".format(channel, tags.attr["emote-only"])
            )
        pass

    def onRoomState(self, tags, channel):
        if self.print_events:
            tags.show()
            print("{}'s channel state changes".format(channel))
        pass

    def onClearMessage(self, tags, channel, message):
        if self.print_events:
            print(
                "{}'s message got deleted at {}'s channel. message={}|".format(
                    tags.attr["login"], channel, message
                )
            )
        pass

    def onTimeout(self, tags, channel, user):
        if self.print_events:
            print(
                "{} got timeout at {} for {} seconds".format(
                    user, channel, tags.attr["ban-duration"]
                )
            )
        pass

    def onBan(self, tags, channel, user):
        if self.print_events:
            print("{} got banned at {}|".format(user, channel))
        pass

    def onMessage(self, tags, channel, message):
        if self.print_events or self.print_message:
            # tags.show()
            try:
                print("Channel {} | Message: {} |".format(channel, message))
            except:
                pass
        pass

    def onJoin(self, channel, user):
        if self.print_events or self.print_join:
            try:
                print("Join | Channel {} | User: {} |".format(channel, user))
            except:
                pass

    def onPart(self, channel, user):
        if self.print_events or self.print_join:
            try:
                print("PART | Channel {} | User: {} |".format(channel, user))
            except:
                pass


if __name__ == '__main__':
    tc = TwitchChat("justinfan7685111", "kappa") # You don't need to login with an actual account to read the IRC
    tc.print_events = False
    tc.identify()
    tc.requestCAP()
    tc.joinChannel("CHANNEL_NAME_HERE")
    while True:
        tc.readFeed()
