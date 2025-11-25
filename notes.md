
## 2025-11-24

So far, i have written a simple program that can fetch a specific timespan of the video feed and create a video clip from it.

in order to turn this into a useful tool, it will need to be able to identify material ids, asset ids, and clip start and end times programatically rather than these being set as variable values in the code. So the next step is to use the agenda api or the sitemap and scrape agendas from the html for start and end times, and to find the events themselves. It may be the case that a static url is used for live events that can always be visited - then the app can check this url periodically to see if there is a live event in progress. 

For the code design in main.py, everything is currently written in functions. I can see all of this code becoming part of a module for creating a specific clip. This would mean creating a service class that can be instanciated for a specific material id, asset id, and start/end times. It could also take a class that encapsulates the ffmpeg stuff called something like CipProcessor as an injected dependency. Then lots of the things that are being passed around as arguments (asset id, material id, stream quality) become class attributes. I don't like the idea of wrapping all of the code into classes for the sake of it, but i can see that everything in main.py could become a module clip.py that has one class, a dataclass and a few helper functions. Probably the actual video processing stuff (ffmpeg) should go in its own module. 

Also, I am currently using temporary files to store the bytes of video and audio data before they are sent as inputs to ffmpeg. I wanted to use in memory buffers of bytes - in order to have two of these piped into ffmpeg I would need named pipes (could use stdin when i only worked with the video stream). Named pipes seem really complicated on windows. I think i will eventually set this up as an app running in a docker container - i will build the image from ubuntu and then can go back to exploring named pipes, or even streaming the responses straight into the subprocess. 


## 2025-11-25

after getting the complete list of urls from the event stream api, I tested one of the urls and was successfully taken to a webpage with a video stream for a debate. When inspecting with devtools, i found that the video and audio segments were being sent in .m4s instead of .ts on some pages (not most). On this page, the original manifest file is still .m3u8 and containted the addresses for the specific manifest files, which listed all the segments with the .m4s extension. So it would be possible to update the parse_manifest function to find the appropriate extension for a particular stream and return it so it can be used in requests.
I noticed that on this page the path was slightly different, specifying .../hsl/. in the path between vod-idx.ism and the file name.