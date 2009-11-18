MDPlayer
========

Spotlight-based music scheduler for Mac OS X. Playlists are text files
with track queries.

Playlist file example::

  Nine Inch Nails - Heresy
  Kraftwerk - Ohm Sweet Ohm
  Animal Collective - Also Frightened

To schedule playlist::

  $ chmod +x mdplayer.py
  $ mdplayer.py playlist.txt

The scheduler will use the system ``mdfind`` and ``mdls`` services
to locate music files that match the queries.

The default music player is `Vox <http://www.voxapp.uni.cc/>`_. Use
the ``-a`` option to specify a different application.

Why?
----

Playlists are hard to manage using a GUI, and using this scheduler you
can use any application to play your music (iTunes still does not play
FLAC files).

Spotlight importers
-------------------

Spotlight importers expose metadata in files to Spotlight, allowing
easy, powerful desktop searching of your computer's contents.

To improve indexing for FLAC and OGG audio files, Stephen F. Booth
provides `importers <http://sbooth.org/importers/>`_ available as free
software -- `GPL <http://www.gnu.org/licenses/licenses.html#GPL>`_.

Note that Mac OS X comes with full indexing for MP3 files.

License
-------

This software is made available as-is under the BSD license.

Written by Malthe Borch <mborch@gmail.com>.
