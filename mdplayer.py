#!/usr/bin/env python

# Copyright (c) 2009, Malthe Borch
#
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.  Redistributions
# in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.  Neither the name of
# the <ORGANIZATION> nor the names of its contributors may be used to
# endorse or promote products derived from this software without
# specific prior written permission.  THIS SOFTWARE IS PROVIDED BY THE
# COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import re
import cmd
import commands
import threading
import optparse

usage = "Usage: %prog [options] playlist\n" \
        "Format is line-terminated track queries (e.g. \"Nine Inch Nails - Heresy\")."

parser = optparse.OptionParser(usage=usage)
parser.add_option("-a", "--application", dest="application",
                  help="Music player application", default="Vox")

(options, args) = parser.parse_args()

try:
    source = args[0]
except:
    parser.error("must provide playlist argument.")

re_kmd = re.compile(r'(\w+)\s*=\s*(?:["\']*)([^"\']+)')
spotlight_keys = 'kMDItemAlbum', 'kMDItemTitle', 'kMDItemDurationSeconds'
cmd_list = "mdls"
cmd_find = "mdfind"
cmd_play = "open -g -a %s" % options.application
args = " ".join("-name %s" % key for key in spotlight_keys)

tracks = [track.strip('\n ') for track in open(source).readlines()]
tracks = filter(None, tracks)

class Queue(threading.Thread):
    def __init__(self, event):
        super(Queue, self).__init__()
        self.number = 0
        self.event = event

    def play(self, track):
        track = track.strip().replace('-', ' ')

        # find file
        status, output = commands.getstatusoutput("%s '%s'" % (cmd_find, track))
        if status != 0:
            print output.decode('utf-8')
        else:
            filenames = output.split('\n')
            for filename in filenames:
                ext = os.path.splitext(filename)[1]
                if ext in (".ogg", ".mp3", ".flac", ".wma", ".aac"):
                    break
            else:
                return

            # extract metadata
            status, output = commands.getstatusoutput("%s %s '%s'" % (cmd_list, args, filename))
            if status != 0:
                print output.decode('utf-8')
            else:
                d = {}
                for line in output.split('\n'):
                    key, value = re_kmd.match(line).groups()
                    d[key] = value

                try:
                    album = d['kMDItemAlbum']
                    title = d['kMDItemTitle']
                    length = float(d['kMDItemDurationSeconds'])
                except ValueError, e:
                    print "Skipped %s (%s)." % (filename, e)
                    self.number += 1
                    return

                # play music
                status, output = commands.getstatusoutput("%s '%s'" % (cmd_play, filename))

                # we the track plays until the end, jump to next
                if self.event.wait(length):
                    self.number += 1
                self.event.clear()

    def again(self):
        self.event.set()

    def next(self):
        self.number += 1
        self.event.set()

    def prev(self):
        self.number -= 1
        self.event.set()

    def run(self):
        while self.number is not None:
            self.number = self.number % len(tracks)
            self.play(tracks[self.number])

    def stop(self):
        self.number = None
        self.event.set()

class Console(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.event = threading.Event()
        self.queue = Queue(self.event)
        self.queue.start()

    def emptyline(self):
        pass

    def do_p(self, message):
        self.queue.prev()

    def do_n(self, message):
        self.queue.next()

    def do_r(self, message):
        self.queue.again()

    def do_q(self, message):
        self.queue.stop()
        return 1

if __name__ == "__main__":
    print "PLAY: p - previous; n - next; r - repeat; q - quit."

    console = Console()
    console.cmdloop()
    console.queue.join()
