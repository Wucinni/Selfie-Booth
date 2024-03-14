![](README_Assets/selfie_booth_logo.png)

Desktop application and web server for 360 selfie videos gallery and download.

This application:
1. Can display videos with sound.
2. Has built in QRs.
3. Has a flask server for video display and download.

# Getting Started

## Installation

You will need the latest Python version available, preferably 3.10 which this bot was created in.

<details><summary>Instructions</summary>
   
1. Install Python (preferably 3.10, any later version should be fine).
2. Install all the required packages by running autoconfig.py for each functionality.
3. Everything is done, just run selfiebooth_app.py and enjoy!

:warning: For flask server to run outside the local area network you have to open the port by using the batch file 'allow_site_through_firewall.cmd'.
</details>

# Documentation

## Background

- Application background can be changed by replacing background.png from templates folder.
- By replacing the background you have to cut specific areas from the image for QRs in order to change their backgrounds. QRs have their own background in the templates folder. Just use Snipping Tool and cut where the QRs would be.
  
:warning: Do not rename the file, standard name is 'background.png' otherwise fails may appear.

## Video Display

- Video display is set by default to the user Desktop.
- In case the application fails to display the video: select again the directory using the top left menu and reopen the application
- 
:warning: Application works only with '.mp4', '.avi', '.mkv' files.

## Flask Server
- By default Flask Server will run on LAN using the IPv4 Address.
- Standard port is set to flask default(5000).
  
:warning: If flask server fails to run you can manually change the IP and Port by using the top left menu.

:warning: If you modified the running port, you have to run again the batch file ('allow_site_through_firewall.cmd') in order to open the newly chosen port through firewall.

:warning: In order to access the webside worldwide you have to do port forwarding in router settings.

# Gallery

Desktop GUI:

https://raw.githubusercontent.com/Wucinni/Selfie-Booth/development/README_Assets/demo.mp4
