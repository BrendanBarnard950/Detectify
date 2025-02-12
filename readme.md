This thing is a little scuffed. It's supposed to detect an image, upload it to S3 if it falls within a list of recognized objects, and that's it. Easy as pie. Except not easy as pie, because I decided that the image needs to come from a livestream. Please don't ever try to use this for anything. It's borderline malware that should not exist. The only reason I'm tolerating it's existance is because I wanted to play with image recognition

Ok, if you HAVE to use this, the way I did it was running an RTSP stream through OBS, using standard OBS and a [nice RTSP plugin](https://obsproject.com/forum/resources/obs-rtspserver.1037/)
Then run this like any Django site (`python manage.py runserver`), ignore the migrations (we don't need 'em), and navigate to the stream page. If we're lucky the default settings work and your stream will show up.

I highly recommend scaling your stream down on the OBS side of things. Low FPS, low resolution. Mine is steraming at 360p 10FPS.

Known issues:
- Thread handling (thread created to handle stream monitoring may or may not close properly ¯\\\_(ツ)_/¯ )
  - I know this is right about the opposite of ideal, but this isn't enterprise software, it's image recognition my crap rig is in no way capable of handling. I just want the label to show the detected image's name and the indicator to become green. I can kill any lingering threads pretty easily by shutting the computer down
- The front-end looks horrible
  - UX design is my passion \<3