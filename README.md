# InterstateOutlaws-v0.2

![screenshot](https://github.com/elr0b0h0b0/InterstateOutlaws-v0.2/blob/main/circle_of_death.png)
![screenshot](https://github.com/elr0b0h0b0/InterstateOutlaws-v0.2/blob/main/water_wheel.png)


Contents
1. Introduction and Features
2. Usage
3. The Server
4. Credits and Contact

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.1 Introduction

Interstate Outlaws (IO) is a vehicular death match based game created mostly by college students from the United States, Great Britain, and Australia. It uses Crystal Space, CEL, and ODE. It is written in C++ and Python. Inspiration for this project came from old auto combat games the creators played when they were young. IO will be perpetually updated for an indefinite period of time. The software is free under the GPL license, but the developers respectfully request donations through the website to support current and future operations.

In the future, the developers are planning numerous new features. These include, but are not limited to: Sound; Pedestrian mode; More accurate physics modeling; More detailed vehicle models with functioning doors, hoods, and trunks; Storage for small arms and other items in the trunk of the vehicle; Much larger scale and detailed maps; Map Editor; Interchangeable power and drivetrains; Custom vehicle and pedestrian textures; Additional types of game play.

IMPORTANT NOTE: This software is still under heavy development and cannot be expected to perform as a polished product. Please visit our forums and provide constructive feedback that will help us fix problems in future updates.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.2 Features

 - 6 unique vehicles with their own gear settings and weapon setups
 - 2 different maps
 - 6 weapons to be mounted
 - Insanely complex damage model
 - Aggressive (but stupid) AI

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2.1 Usage

Please copy the files in the "shared_objects" directory to your /usr/lib folder.

To start the game run outlaws.py or any "shortcut" to outlaws.py.

When you start, you will be suspended in mid-air (perhaps slightly too high) for a short time, then dropped onto the map. 

The controls are:
 w                       accelerate.
 s                       brake.
 a                       steer left.
 d                       steer right.
 space                   hand brake
 t                       target next opponent
 Numbers 1-0             Fire individual weapons
 l                       link together weapons of same type
 click on weapon in HUD  link / unlink weapon
 ctrl                    fire linked weapons
 left alt                start typing a message
 enter                   send message
 c                       cycles camera view
 h                       toggles HUD
 r                       removes vehicle from "stuck" condition
 escape                  quit menu

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

3.1 The server

In order to start a lobby server, you can run the shortcut name 'IO Server' or execute outlaws-lobbyserver.py within the game's base folder. The settings for the server are stored in the file ioData/servers/celstart.cfg within the game's folder. The settings you will want to change are:

Outlaws.LobbyServer.Name - This is the name of the server. It should be the first thing you should change.
Outlaws.Server.MaxClients - This is the number of people allowed to enter your lobby.
Outlaws.Server.MaxChildServers - The number of people allowed to host games on your lobby.

Once running, the lobby server will do two things. First, report to the IO master server so that clients know where to find it. Second, field requests from clients to join games. Games are handled by the user that "hosts" it and the lobby server simply reports the location of said games. This system is slightly inefficient, but we have plans to change it in the future.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

4.1 Credits

Logan Jaybush........Team Lead
Chris Fraser.........Programming Lead
Brian Sims...........3D Artist
Mark Rademaker.......3D Artist
Jon De'Ath...........Information Technology
Tristan Richmond.....Public Relations

The team would like to thank: Michael Alvey, Sam Goodwin, Tyler Gowans, Ryan Hollett, Vincent Knecht, Jonathan MacDonald, Alan Malnar, Pablo Martin, Daniel McClain, Aaron Pickett, Milos Rancic, Stewart Riddell, Jason Rushford, Jorrit Tyberghein, Australian National University, City of Prescott Arizona, City of Prescott Valley Arizona, Crystal Space Development Team, Embry-Riddle Aeronautical University, Yavapai County Arizona, our families, and the Interstate community.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

4.2 Contact

Bug-Reports be made in the issues section. If you want to see a feature, please help us by adding it!

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
