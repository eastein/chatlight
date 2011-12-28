# What's This?

This is an IRC bot that analyzes traffic on a channel and uses it to output to a light art installation to physically and visually bridge the gap between the virtual world and the physical one.

# Dependencies

* pyzmq (http://www.zeromq.org/bindings:python)
* mediorc (https://github.com/eastein/mediorc)
* pyserial

# Programs

## chatlight

This program connects to an IRC channel, analyzes by keywords, and produces json messages over a ZeroMQ PUB socket (bound) that describe the state of the channel and related events.

## watch_reports

The `watch_reports` program connects to the ZeroMQ PUB socket that `chatlight` publishes on and converts the json messages to instructions for running the 2 blink counters for each light on the physical sculpture.  These instructions are sent over serial in a binary checksummed format to the arduino.

## chatlight (arduino)

The arduino sketch listens on the serial input and also operates the blinkers.  It defaults to a "scan" that makes a red light move back and forth along the top (to show that it has not got instructions yet).

# Example

    ./watch_reports tcp://127.0.0.1:23000
    ./chatlight irc.example.org nick34231 #channel tcp://0.0.0.0:23000

# TODO

* usage for both programs

# Tests

To run unit tests, use:

    nosetests -vv tests
