# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 18:33:45 2022

@author: Zed
"""

# img_viewer.py

# we will clean these up later but for now even leave unused imports
#we are not in cleanup phase yet
from PIL import Image 
from utils import launcherUtils, githubUtils
import PySimpleGUI as sg
import cloudscraper
import io
import json
import os.path
import requests
import sys



# Folder where script is placed, It looks in this for the Exectuable
if getattr(sys, 'frozen', False):
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    LauncherDir = os.path.dirname(__file__)

installpath = str(LauncherDir + "\\resources\\")

#intialize default variables so they are never null
currentModderSelected = None
currentModSelected = None
currentModURL = None
currentModImage = None


#comment this out if you want to test with a local file
moddersAndModsJSON = requests.get("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/ListOfMods.json").json()

j_file = json.dumps(moddersAndModsJSON)
#print(moddersAndModsJSON["Modding Community"][0]["name"])
#print(moddersAndModsJSON["Modding Community"][0]["URL"])


# First the window layout in 2 columns

mod_list_column = [
	[sg.Text("Mod Creator")],
    #would be nice to add default_value="Modding Community", below, but if we do that it doesnt trigger the update event currently
	[sg.Combo(list(moddersAndModsJSON.keys()), enable_events=True, key='pick_modder', size=(30, 0))],
    [sg.Text("Their Mods")],
    #would be nice to add default_value="Randomizer", below, but if we do that it doesnt trigger the update event currently
	[
        sg.Combo([], key='pick_mod', size=(30, 0),enable_events=True )  # there must be values of selected item
        
    ],
]



# For now will only show the name of the file that was chosen
mod_details_column = [
    [sg.Text("Choose an mod from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-SELECTEDMODIMAGE-")],

]

installed_mods_column = [
    [sg.Text("Installed mods")],
	[sg.Listbox(values=["This List is not", "Classic+"],size=(60,5),key="InstalledModListBox",enable_events=True)],
    [sg.Text(size=(40, 1), key="-TOUT-")],

]

# ----- Full layout -----
layout = [
    [
        sg.Column(mod_list_column),
        sg.VSeperator(),
        sg.Column(mod_details_column),
		[sg.Column(installed_mods_column)],
		[sg.Btn(button_text="Launch!")],
		[sg.Btn(button_text="Uninstall")]
    ]
]

url= "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/appicon.ico"
jpg_data = (
                cloudscraper.create_scraper(
                    browser={"browser": "firefox", "platform": "windows", "mobile": False}
                )
                .get(url)
                .content
            )
            
pil_image = Image.open(io.BytesIO(jpg_data))
png_bio = io.BytesIO()
pil_image.save(png_bio, format="PNG")
iconfile = png_bio.getvalue()

url= "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/noRepoImageERROR.png"
jpg_data = (
                cloudscraper.create_scraper(
                    browser={"browser": "firefox", "platform": "windows", "mobile": False}
                )
                .get(url)
                .content
            )
            
pil_image = Image.open(io.BytesIO(jpg_data))
png_bio = io.BytesIO()
pil_image.save(png_bio, format="PNG")
noimagefile = png_bio.getvalue()

window = sg.Window('OpenGOAL Mod Launcher v0.02', layout, icon= iconfile, finalize=True)
def bootup():
    print("BOOT")
    
    #installed mods
    subfolders = [ f.name for f in os.scandir(r"C:\Users\Zed\AppData\Roaming\OpenGOAL-Mods") if f.is_dir() ]
    if subfolders == []:
        subfolders = ["No Mods Installed"]
    print(subfolders)
    window["InstalledModListBox"].update(subfolders)
    
    #default mod selection on boot
    window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(1,1)))
    item = "Modding Community"
    window['pick_modder'].update(item)
    
    title_list = [i["name"] for i in moddersAndModsJSON[item]]
    window['pick_mod'].update(value=title_list[0], values=title_list)



    currentModderSelected = "Modding Community"
    currentModSelected = "Randomizer"
    currentModURL = "https://github.com/OpenGOAL-Unofficial-Mods/opengoal-randomizer-mod-pack/tree/main"
    currentModImage = None

    [currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleModSelected()
    
    
    #print(window['InstalledModListBox'].get()[0])
    #folder = values["InstalledModListBox"]
    #[currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleInstalledModSelected()
    
	
def handleModSelected():
    tmpModderSelected = window['pick_modder'].get()
    tmpModSelected = window['pick_mod'].get()
    tmpModURL = None
    tmpModImage = None
    
    for i in range(len(moddersAndModsJSON[tmpModderSelected])):
        if moddersAndModsJSON[tmpModderSelected][i]["name"] == tmpModSelected:
            tmpModURL = moddersAndModsJSON[tmpModderSelected][i]["URL"]
    
    tpmModImage = githubUtils.returnModImageURL(tmpModURL)

    
    url = tpmModImage
    try:
        r = requests.head(tpmModImage).status_code
        print(str(r))
        if r == 200:
            jpg_data = (
                cloudscraper.create_scraper(
                    browser={"browser": "firefox", "platform": "windows", "mobile": False}
                )
                .get(url)
                .content
            )
            
            pil_image = Image.open(io.BytesIO(jpg_data))
            png_bio = io.BytesIO()
            pil_image.save(png_bio, format="PNG")
            png_data = png_bio.getvalue()
            window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(png_data ,resize=(250,250)))
            # prints the int of the status code. Find more at httpstatusrappers.com :)    
        if r != 200:
            window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))

    except requests.exceptions.MissingSchema:
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))

    return [tmpModderSelected, tmpModSelected, tmpModURL, tmpModImage]

def handleInstalledModSelected():
    tmpModderSelected = window['pick_modder'].get()
    tmpModSelected = window['InstalledModListBox'].get()[0]
    
    print(tmpModSelected)
    tmpModURL = None
    tmpModImage = None
    tmpModderlist = list(moddersAndModsJSON.keys()) 
    for i in range(len(tmpModderlist)):
        print(moddersAndModsJSON)
        print(moddersAndModsJSON[1])
    #TODO This is where we need to update the dropdowns (currentmodselected and currentmodder) But going through this list/dict/json thing is a nightmare

       # if moddersAndModsJSON[tmpModderSelected][i]["name"] == tmpModSelected:
            # tmpModURL = moddersAndModsJSON[tmpModderSelected][i]["URL"]
    
    tpmModImage = githubUtils.returnModImageURL(tmpModURL)
    
    url = tpmModImage
    try:
        r = requests.head(tpmModImage).status_code
        print(str(r))
        if r == 200:
            jpg_data = (
                cloudscraper.create_scraper(
                    browser={"browser": "firefox", "platform": "windows", "mobile": False}
                )
                .get(url)
                .content
            )
            
            pil_image = Image.open(io.BytesIO(jpg_data))
            png_bio = io.BytesIO()
            pil_image.save(png_bio, format="PNG")
            png_data = png_bio.getvalue()
            window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(png_data ,resize=(250,250)))
            # prints the int of the status code. Find more at httpstatusrappers.com :)    
        if r != 200:
            window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))

    except requests.exceptions.MissingSchema:
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))

    return [tmpModderSelected, tmpModSelected, tmpModURL, tmpModImage]
bootupcount = 0
# Run the Event Loop
if bootupcount == 0:
    bootup()
while True:
    event, values = window.read()


    
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    
    # Folder name was filled in, make a list of files in the folder
    if event == "InstalledModListBox" and not  window["InstalledModListBox"].get() == ['No Mods Installed']:
        subfolders = [ f.name for f in os.scandir(r"C:\Users\Zed\AppData\Roaming\OpenGOAL-Mods") if f.is_dir() ]
        print(window['InstalledModListBox'].get()[0])
        folder = values["InstalledModListBox"]
        print(folder)
        [currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleInstalledModSelected()
        print("Printing avalible information below for debug purposes, remove these later")
        print(currentModderSelected)
        print(currentModSelected)
        print(currentModURL)
        print(currentModImage)
        try:
            # Get list of files in folder
            file_list = os.listdir(r"C:\Users\Zed\AppData\Roaming\OpenGOAL-Mods")
        except:
            file_list = []


     
        window["InstalledModListBox"].update(subfolders)
    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update(filename)
            window["-SELECTEDMODIMAGE-"].update(filename=filename)

        except:
            pass
    elif event =='pick_modder':
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(1,1)))
        item = values[event]
        print(item)
        title_list = [i["name"] for i in moddersAndModsJSON[item]]
        window['pick_mod'].update(value=title_list[0], values=title_list)
        [currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleModSelected()
        
    elif event =='pick_mod':
        [currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleModSelected()
        
    elif event == "Launch!":
        [currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleModSelected()
        print(" ")
        print("Printing avalible information below for debug purposes, remove these later")
        print(currentModderSelected)
        print(currentModSelected)
        print(currentModURL)
        print(currentModImage)

        if currentModURL is None:
            sg.Popup('No mod selected', keep_on_top=True)
        else:
            window['Launch!'].update(disabled=True)
            print("Launch button hit!")

            [linkType, currentModURL] = githubUtils.identifyLinkType(currentModURL)
            launcherUtils.launch(currentModURL, currentModSelected, linkType)
            
            #turn the button back on
            window['Launch!'].update(disabled=False)
            
    elif event == "Uninstall":
        [currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleModSelected()
        print(currentModSelected)
        if currentModSelected in installedMods:
            print("Installed")
        print("")
        print("uninstallButton hit!")
        print("Do things here")

window.close()