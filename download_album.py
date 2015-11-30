import os
import sys
import time
import timeit
import urllib
from Queue import Queue
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys


baseURL = "http://facebook.com/"
username = ""
password = ""
albumLink = ""
albumName = ""
albumUser = ""
max_workers = 8

class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            link = self.queue.get()
            fileName = link[::-1].split("/")[0][::-1].split("?")[0]
            urllib.urlretrieve(link, albumName + "/" + fileName)
            self.queue.task_done()

def findAlbum(browser):
    global username
    global password
    global albumLink
    global albumName
  
    try:  
        privateAlbum = raw_input("Private Album? (y/n)")
        if privateAlbum is 'y':
            username = raw_input("Email: ")
            password = raw_input("Password: ")

            browser.get(baseURL)

            print "[Logging In]"

            browser.find_element_by_id("email").send_keys(username)
            browser.find_element_by_id("pass").send_keys(password)
            browser.find_element_by_id("loginbutton").click()

        albumLink = raw_input("Album Link: ")
        print "[Loading Album]"
        browser.get(albumLink)
        albumName = browser.find_element_by_class_name("fbPhotoAlbumTitle").text

    except:
        print "Login failed."
        browser.quit()

def createAlbumPath():
    global albumName
    # create album path
    x = 0
    while True:
        if x:
            albumName = albumName + str(x)

        if not os.path.exists(albumName):
            os.makedirs(albumName)
            break
        x += 1

def getImageLinks(browser):
    # scroll to bottom
    previousHeight = 0
    reachedEnd = 0

    while reachedEnd != None:
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        currentHeight = browser.execute_script("return document.body.scrollHeight")

        if previousHeight == currentHeight:
            reachedEnd = None

        previousHeight = currentHeight
        time.sleep(0.3)

    return browser.execute_script("var list = []; Array.prototype.forEach.call(document.querySelectorAll('.uiMediaThumb[ajaxify]:not(.coverWrap)'), function(el) { var src = el.getAttribute('ajaxify'); var key = 'src='; src = src.substr(src.indexOf(key) + key.length); src = unescape(src.substr(0, src.indexOf('&'))); list.push(src) }); return list;")


def main():
    print "[Facebook Album Downloader v1]"
    start = timeit.default_timer()

    # hide images
    prefs = {"profile.managed_default_content_settings.images": 2}
    extensions = webdriver.ChromeOptions()
    extensions.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=extensions)

    findAlbum(browser)
    createAlbumPath()

    queue = Queue()

    for x in range(max_workers):
        worker = DownloadWorker(queue)
        worker.daemon = True
        worker.start()

    print "[Getting Image Links]"
    linkImages = getImageLinks(browser)
    print "[Found: " + str(len(linkImages)) + "]"

    for fullRes in linkImages:
        queue.put(fullRes)

    print "[Downloading...]"
    queue.join()

    browser.quit()

    stop = timeit.default_timer()
    print "[Time taken: %ss]" % str(stop - start)
    raw_input("Press any key to continue...")


if __name__ == "__main__":
    if not os.path.exists(os.path.dirname(sys.argv[0]) + 'chromedriver.exe'):
        print "[chromedriver.exe not found in directory! It must be in this folder and named chromedriver.exe]"
        print "[Download: http://chromedriver.storage.googleapis.com/index.html?path=2.20/ ]"
        raw_input("Press any key to exit...")
    else: 
        main()