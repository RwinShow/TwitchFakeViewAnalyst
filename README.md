# Twitch Fake View Analyst

Twitch Fake View Analyst is a **[Python](https://www.python.org/)**-based repository designed to provide comprehensive analysis and monitoring capabilities for Twitch chat users. This repository offers a foundation for tracking general user activity, identifying fake users, and conducting in-depth analyses using **[pyTwitchAPI](https://github.com/Teekeks/pyTwitchAPI)**.

The repository includes a Python file that allows you to monitor the joining and leaving patterns of users in Twitch chat. By collecting and analyzing this data, you can gain insights into user engagement and identify any suspicious or fake view activity.

## Important note
Using this program requires basic knowledge of Python. This code was written in a short time and there is a lot of room for improvement. if you find any bugs, don't hesitate to let me know, I currently don't have any plans on further developing this bot but I would fix the bugs. Please keep this in mind: one major flaw of this system is that Twitch does not report membership changes(join and part) for IRC if there are more than 1,000 users.

## Prerequisite
In order to run this code you need to:
- Have **Python** running properly on your computer (if you don't know how to do this, use a beginner's guide)
- Install **pyTwitchAPI** for **Python**, you can install using pip:
>```pip install twitchAPI```
- Register an Application on Twitch and save its App ID and Secret
> Go to [Twitch Dev Console](https://dev.twitch.tv/console) and register your application (This is required for pyTwitchAPI).

## How to use
Using the python file provided you can see the users chatting, joining, and leaving a specific Twitch channel. You can log this data and use it alongside with pyTwitchAPI to:\
1- Check if the user has a history of chatting in that stream.\
2- Check if the user follows the current Twitch channel or related Twitch channels (Same language, Same game, etc.)\
3- Check if the user has a history of chatting or watching related channels (By running this on multiple related channels).\
4- Calculate and check user's watch time in the current Twitch channel or related channels.

By inspecting these activities you can create a "safety score" for each user and consequently for each streamer's broadcast. This safety score can indicate the possibility of fake views for that broadcast.
