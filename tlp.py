from youtubesearchpython import VideosSearch
import threading
from random import choice
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from flask import Flask, render_template, request

flaskapp = Flask(__name__)

nothing = ('', 204)
taglines = ["I'm never passing you the aux again","ThinkLikePotato V2, 2.0, etc."]

songQueue = []

class song:
    def __init__(self, url, title):
        self.url = url
        self.title = title

#######################################################################

def searchSong(songRequest):
    searchResult = VideosSearch(songRequest, limit = 1).result()
    if len(searchResult["result"]) > 0: 
        songName = (searchResult["result"][0]["title"])
        songLink = (searchResult["result"][0]["link"])
        songQueue.append(song(songLink,songName))
        if (len(songQueue) == 1):
            nextSong()
    else:
        print("Search results returned no videos. Please check that your song suggestion was spelt correctly.")

def initBrowser():
    global chrome
    global actions
    #webbrowser.register("edge", None, webbrowser.GenericBrowser("C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"))
    #edge = webbrowser.get("edge")
    options = Options()
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument(r"--user-data-dir=C:\Users\Admin\AppData\Local\Google\Chrome\User Data")#zachd #Admin
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome = webdriver.Chrome(options=options)	
    actions = ActionChains(chrome)

def nextSong():
    global chrome
    global actions
    if len(songQueue) == 0:
        actions.key_down(Keys.SHIFT).send_keys("n").key_up(Keys.SHIFT)
        actions.perform()
    else:
        if songQueue[0].title in chrome.title.replace(" - YouTube",""):
            songQueue.pop(0)
        if len(songQueue) != 0:
            chrome.get(songQueue[0].url+"?autoplay=1")

            global elementCurrentPlaybackTime 
            global elementTimeSeperator
            global videoLength
            elementTimeSeperator = chrome.find_element(By.CLASS_NAME, "ytp-time-separator")
            elementCurrentPlaybackTime= chrome.find_element(By.CLASS_NAME,"ytp-time-current")
            videoLength = chrome.find_element(By.CLASS_NAME,"ytp-time-duration").text
        else:
            actions.key_down(Keys.SHIFT).send_keys("n").key_up(Keys.SHIFT)
            actions.perform()

#######################################################################
### THREADS ####
################

def playerLoop():
    global elementCurrentPlaybackTime
    global videoLength
    currentPlaybackTime = "0:00"
    while True:
        try:
            chrome.execute_script("""setTimeout(function(){let video = document.querySelector("#movie_player");setInterval(function(){video.dispatchEvent(new Event('mousemove'));},100);},1500)""")
            currentPlaybackTime = elementCurrentPlaybackTime.text
        except:pass
        try:
            if currentPlaybackTime == videoLength and chrome.title.replace(" - YouTube","") == songQueue[0].title:
                nextSong()
        except:pass

def webLoop():
    flaskapp.run(debug=True, use_reloader=False,host="0.0.0.0")

#######################################################################
### FLASK ####
##############

@flaskapp.route('/')
def mainIndex():
    global chrome
    global songQueue
    currentSong = chrome.title.replace(" - YouTube","")
    if currentSong == "YouTube" or ") YouTube" in currentSong:
        currentSong = "No Song Playing"
    randomTagline = choice(taglines)

    songListHTML=""
    color = "#161616"
    lastColor = "#434343"
    for song in songQueue:
        (color,lastColor) = (lastColor,color)
        songListHTML = songListHTML + f"""<div class="songListItem" style="background-color: {color};"><i class="songListItemText">{song.title}</i></div>"""

    return render_template('main.html',tagline=randomTagline,currentSong=currentSong,songList=songListHTML)

@flaskapp.route('/playPauseBtn', methods=['POST'])
def playPause():
    global actions
    actions.send_keys("k")
    actions.perform()
    return nothing

@flaskapp.route('/backBtn', methods=['POST'])
def back():
    global actions
    actions.send_keys("0")
    actions.perform()
    return nothing

@flaskapp.route('/skipBtn', methods=['POST'])
def skip():
    nextSong()
    return nothing

@flaskapp.route('/volUp', methods=['POST'])
def volUp():
    global actions
    global elementTimeSeperator
    actions.click(elementTimeSeperator).send_keys(Keys.ARROW_UP)
    actions.perform()
    return nothing

@flaskapp.route('/volDown', methods=['POST'])
def volDown():
    global actions
    global elementTimeSeperator
    actions.click(elementTimeSeperator).send_keys(Keys.ARROW_DOWN)
    actions.perform()
    return nothing

@flaskapp.route('/addSong', methods=['POST'])
def addSong():
    if request.form.get("songRequest") != "":
        searchSong(request.form.get("songRequest"))
    return nothing

#######################################################################

initBrowser()
chrome.get("https://www.youtube.com")

elementTimeSeperator = None
elementCurrentPlaybackTime = None
videoLength = None
playerElement = None

if __name__ == "__main__":
    playerThread = threading.Thread(target=playerLoop)
    webThread = threading.Thread(target=webLoop)
    playerThread.start()
    webThread.start()

    
    