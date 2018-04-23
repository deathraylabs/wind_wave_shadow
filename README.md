# wind_wave_shadow script

Simple python script that displays the geometric wave shadow cast by the NE Freeport ship channel jetty when the user provides a wind and wave direction. 

## What's it for?

To help decide if it's worth the 1hr+ drive from Houston to Surfside beach to do some surfing or surf kiting.

Surfside beach gets more ridable swell than you would otherwise guess but it's almost exclusively short-period windswell generated by local weather systems. Because the swell is generated locally, it is usually accompanied by the wind that helped generate it; this wind can lead to undesirebly choppy conditions if it's directed onshore. Luckily the approximately 3/4 mile long jetty can act as a chop blocker for certain wind directions, which is what this script is designed to help us decide.

Generally we want the jetty to block the surface level wind and it's associated chop but not to block the incoming windswell. Ideally the wind would be blocked by the jetty or shore while the swell is minimally blocked by the jetty. If that's the case it's possible to have relatively clean surf near the jetty even with relatively strong side to side-onshore wind.

## How to use:

- you need to have python installed on your computer along with the _Pillow_ and _tkinter_ modules
