import argparse
import logging
import sys
from subprocess import STDOUT, Popen
import MySQLdb as mysql
import MySQLdb.cursors as cursors
import os

sys.path.append(os.getcwd()) # settings fix

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import settings
from django.contrib.auth.models import Group, User
from radio_project.models import *
logging.basicConfig(level=logging.INFO)

STATUS_PENDING = 0
STATUS_ACCEPTED = 1
STATUS_DECLINED = 2
STATUS_REPLACEMENT = 3

class Cursor(object):
    def __init__(self, options=None, cursortype=cursors.DictCursor, lock=None):
        if options:
            options.update({'use_unicode': True,
                          'charset': 'utf8'})
        super(Cursor, self).__init__()
        self.conn = mysql.connect(**options)
        self.type = cursortype
        
    def __enter__(self):
        self.cur = self.conn.cursor(self.type)
        return self.cur
    
    def __exit__(self, type, value, traceback):
        self.cur.close()
        self.conn.commit()
        return
        
def move_data(host, port, username, password, old_db):
    options = {"host": host,
               "port": int(port),
               "user": username,
               "passwd": password}
    options_old = options.copy()
    options_old.update({"db": old_db})
    
    options_new = options.copy()
    options_new.update({"db": "radio_main"})
    
    # Users

    def get_user(username):
        if not username:
            username = "Unknown"
        return User.objects.get(username=username)
    
    # Create the groups we want
    for groupname in ["Database", "Accepter", "DJ", "Newsposter", "Admin"]:
        group, created = Group.objects.get_or_create(name=groupname)
        group.save()
    gdict = {1: Group.objects.get(name="Accepter"),
             2: Group.objects.get(name="DJ"),
             3: Group.objects.get(name="Newsposter"),
             4: Group.objects.get(name="Admin")}
    logging.info("Working on: users")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
            # Retrieve old fields
            old_cur.execute("SELECT user, pass, privileges FROM users ORDER BY id ASC;")
            
            old_data = [("Unknown", "Empty", 0)] + list(old_cur)
            # Create our insert query
            for name, pwd, privileges in old_data:
                try:
                    user = User.objects.get(username=name)
                except:
                    user = User.objects.create_user(name, "fake@email.com")
                if gdict.get(privileges, None):
                    user.groups.add(gdict.get(privileges))
                user.save()
    # DJs
    logging.info("Working on: djs")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new) as new_cur:
            # retrieve old djids from old users
            old_cur.execute("SELECT user, djid FROM users ORDER BY id ASC;")
            links = []
            for user, djid in old_cur:
                links.append((User.objects.get(username=user).id, djid))
                
            # Dummy entry
            new_cur.execute("""INSERT INTO dj (id, name, description, 
                visible, priority, user, theme) VALUES (%s, %s,
                %s, %s, %s, %s, %s);""", (0, 'Unknown', 'Unknown',
                                          False, 0,
                                          get_user('Unknown').id, 'default'))
            for userid, djid in links:
                # Get djid info
                old_cur.execute("""SELECT djname, djtext, djimage, 
                                visible, priority FROM djs WHERE id=%s;""",
                                (djid,))
                
                
                # Put info into new djs table 
                for name, description, image, visible, priority in old_cur:
                    new_cur.execute("""INSERT INTO dj (id, name, description, 
                    visible, priority, user, theme) VALUES (%s, %s,
                    %s, %s, %s, %s, %s);""", (djid, name, description,
                                              visible, priority,
                                              userid, 'default'))
    # News
    logging.info("Working on: news")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new) as new_cur:
            # Get old data
            old_cur.execute("SELECT id, header, time, newstext, cancomment, 8 AS poster FROM news;")
            
            query = """INSERT INTO news (id, title, time, text, commenting, poster)
            VALUES (%s, %s, %s, %s, %s, %s)"""
            
            new_cur.executemany(query, old_cur)
            
    # News comments
    logging.info("Working on: news_comments")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            # Create news id index, because someone didn't delete comments
            new_cur.execute("SELECT id FROM news;")
            existing_items = [i for i, in new_cur]
            
            # get old data
            old_cur.execute("SELECT nid, header, text, mail, login, time FROM comments;")
            old_data = []
            # Filter login values into user ids, why ;_;
            for nid, header, text, mail, login, time in old_cur:
                if not nid in existing_items:
                    continue
                if login == '':
                    old_data.append((nid, header, text, mail, None, time))
                else:
                    new_cur.execute("SELECT id FROM auth_user WHERE username=%s;", (login,))
                    for poster, in new_cur:
                        old_data.append((nid, header, text, mail, poster, time))
            # lovely query
            query = """INSERT INTO news_comment (news_id, nickname,
            text, mail, poster, time) VALUES (%s, %s, %s, %s, %s, %s);"""
            
            # execute, done
            new_cur.executemany(query, old_data)
            
    # Relays, don't need anything special really
    logging.info("Working on: relays")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("SELECT * FROM relays;")
            query = """INSERT INTO relay (id, relay_name, relay_owner,
            base_name, port, mount, bitrate, format, priority, listeners,
            listener_limit, active, admin_auth) VALUES (%s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s);"""
            new_cur.executemany(query, old_cur)
            
    # Playerstats
    logging.info("Working on: playerstats")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("SELECT ip, lastset, player FROM playerstats;")
            old_data = list(old_cur)
            
            # Create players entries
            players = []
            for ip, lastset, player in old_data:
                players.append((useragent_to_player(player), player))
            query = """INSERT INTO player (name, useragent) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name);"""
            for play in players:
                try:
                    new_cur.execute(query, play)
                except:
                    play = (play[0], play[0][:200])
                    new_cur.execute(query, play)
            # prepare iterator for listener
            listeners = []
            for ip, lastset, player in old_data:
                new_cur.execute("SELECT id FROM player WHERE useragent=%s;", (player[:200],))
                for row, in new_cur:
                    player = row
                listeners.append((ip, player, 0, lastset, None))
            # Prepare query
            query = """INSERT INTO listener (ip, player_id, banned,
            last_seen, nicknames_id) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE
            KEY UPDATE last_seen=VALUES(last_seen);"""
            # Add all of them to listeners
            for l in listeners:
                try:
                    new_cur.execute(query, l)
                except:
                    raise
                    print l
            #new_cur.executemany(query, listeners)
            
    # Nicknames time! yay, we create a fake default hostname here since we
    # don't save these in the old database
    logging.info("Working on: nicknames")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("SELECT nick, authcode FROM enick;")
            
            # Add fake hostname
            hostname, created = Hostname.objects.get_or_create(hostname='Fake')
            
            # prepare iterator
            for nick, passcode in old_cur:
                nickname = Nickname.objects.create(hostname=hostname,
                                                             passcode=passcode)
                alias, created = NicknameAlias.objects.get_or_create(name=nick,
                                                                 nickname=nickname)
            
    # The fun starts
    def add_track(meta, length=0):
        return Track.factory.create_from_string(meta, length=length)

    def add_album(album):
        album, created = Album.objects.get_or_create(name=album)
        return album

    def add_song(metadata, track):
        return Song.factory.create_from_string(metadata, track=track)
    
    def link_track_album(tid, aid):
        link, created = TrackHasAlbum.objects.get_or_create(track=tid,
                                                            album=aid)
        return link
    
    def get_dj(username):
        return Dj.objects.get(user__username=username)
        
    def get_nick(nick):
        return Nickname.objects.get(names__name=nick)
        
    def add_collection(track=None, **kwargs):
        collection, created = Collection.objects.get_or_create(track=track,
                                                defaults=kwargs)
        return collection

    def add_editor(collection, user, action, time=None):
        editor = CollectionEditor.objects.create(user=user,
                                                           action=action,
                                                           collection=collection,
                                                           time=time)
        return editor
    
    def add_tag(tag):
        tag, created = Tag.objects.get_or_create(name=tag)
        return tag
    
    def link_track_tag(track, tag):
        tag, created = TrackHasTag.objects.get_or_create(track=track, tag=tag)
        
    def add_listener(ip=None, **kwargs):
        listener, created = Listener.objects.get_or_create(ip=ip,
                                                            defaults=kwargs)
        return listener
    
    def add_uploads(listener, time, collection):
        upload = Upload.objects.create(listener=listener,
                                                 time=time,
                                                 collection=collection)
        return upload

    def add_played(song, time, dj):
        played = Played.objects.create(song=song,
                                                time=time,
                                                dj=dj)
        return played

    def add_fave(song, nickname):
        fave, created = Fave.objects.get_or_create(song=song,
                                             nickname=nickname)
        return fave
    
    logging.info("Working on: songs from esong (This one takes longest)")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("SELECT id, hash, meta, len FROM esong;")
            
            for id, hash, meta, len in old_cur:
                # Add the usual esong
                track = add_track(meta, len)
                song = add_song( meta, track)

                # Do our eplay
                old_cur.execute("""SELECT dt AS time FROM eplay JOIN esong ON
                esong.id = eplay.isong WHERE eplay.isong=%s;""", (id,))
                for time, in old_cur:
                    add_played(song, time, get_dj("Unknown"))
                    
                # Do our efave
                old_cur.execute("""SELECT enick.nick AS nick FROM efave JOIN
                enick ON enick.id=efave.inick WHERE efave.isong=%s;""",
                (id,))
                for nick, in old_cur:
                    add_fave(song=song,
                             nickname=get_nick(nick))
                    
    logging.info("Working on: songs from tracks (Not as long as above)")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("""SELECT * FROM tracks;""")
            # Create track and album, link them
            for id, artist, track, album, path, tags, priority, lastplayed, lastrequested, usable, accepter, lasteditor, hash, requestcount, need_reupload in old_cur:
                metadata = artist + " - " + track if artist else track
                # Create track entry
                track = add_track(metadata)
                album = add_album(album)
                # Link album and track entry together
                link_track_album(track, album)
                
                # Create song entry, link to track entry
                song = add_song(metadata, track)
                
                # Create collection entry
                collection = add_collection(track=track,
                                               usable=usable, filename=path,
                                               need_reupload=need_reupload,
                                               popularity=requestcount,
                                               status=STATUS_ACCEPTED)
                
                # add accepter
                user = get_user(accepter)
                add_editor(collection, user, action="accept")
                
                # add editor
                user = get_user(lasteditor)
                add_editor(collection, user, action="edit")
                
                # Create all the tags
                for tag in tags.split(" "):
                    tag = add_tag(tag)
                    link_track_tag(track, tag)

    logging.info("Working on: songs from pending")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("""SELECT * FROM pending;""")
            for id, artist, track, album, path, comment, origname, submitter, submitted, dupe_flag, replacement in old_cur:
                # Create our listeners
                
                metadata = artist + " - " + track if artist else track
                
                track_id = add_track(metadata)
                album_id = add_album(album)
                
                link_track_album(track_id, album_id)
                
                song_id = add_song(metadata, track_id)
                
                listeners_id = add_listener(ip=submitter,
                                            last_seen=submitted)
                collection_id = add_collection(track=track_id,
                                               filename=path,
                                               status=STATUS_REPLACEMENT if replacement else STATUS_PENDING,
                                               comment=comment, 
                                               original_filename=origname,
                                               usable=0)
                try:
                    add_uploads(listeners_id, submitted, collection_id)
                except:
                    print listeners_id, collection_id
                    
    logging.info("Working on: songs from postpending")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        old_cur.execute("""SELECT * FROM postpending;""")
        for id, trackid, meta, ip, accepted, time, reason, good_upload in old_cur:
            # Create our listeners
            
            metadata = meta
            
            track = add_track(metadata)
            
            song = add_song(metadata, track)
            
            listener = add_listener(ip=ip,
                                    last_seen=time)
            
            collection = add_collection(track=track,
                                        status=STATUS_ACCEPTED if accepted else STATUS_DECLINED,
                                        good_upload=good_upload,
                                        decline_reason=reason,
                                        usable=0)
            try:
                add_uploads(listener, time, collection)
            except:
                #print listeners_id, collection_id
                raise
                    
    logging.info("Finished database transfer.")

    
def useragent_to_player(useragent):
    useragent = useragent.lower()
    if ('foobar' in useragent):
        return "Foobar2000"
    elif ('winampmpeg' in useragent):
        return "WinAmp"
    elif ('itunes' in useragent):
        return "iTunes"
    elif ('nsplayer' in useragent):
        return "Windows Media Player"
    elif ('mplayer' in useragent):
        return "MPlayer"
    elif ('videolan' in useragent) or ('vlc' in useragent):
        return "VLC"
    elif ('android' in useragent):
        return "Android"
    elif ('iphone' in useragent):
        return "iPhone"
    elif ('msie 7.0' in useragent) and ('.net clr' in useragent):
        return "Media Player Classic"
    elif ('firefox' in useragent) or ('trident' in useragent) or ('opera' in useragent) or ('safari' in useragent) or ('chrome' in useragent) or ('chromium' in useragent):
        return "Web Player"
    elif ('hanyuu-sama' in useragent) or ('icecast' in useragent) or ('shoutcast' in useragent):
        return 'Other'
    else:
        return 'Other'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move an old database design to a new database design. This reads old entries from the old database into a new database named 'radio_main' by default.")
    parser.add_argument("-u", "--user",
                        dest="user",
                        nargs="?",
                        required=True,
                        help="User to the MySQL database. Should be someone with read access to old database and write and creation access to new database.")
    parser.add_argument("-p", "--pass",
                        dest="passwd",
                        nargs="?",
                        required=True,
                        help="Password for user specified.")
    parser.add_argument("-s", "--host",
                        dest="host",
                        nargs="?",
                        required=False,
                        default="localhost",
                        help="Address of the MySQL server to use.")
    parser.add_argument("-P", "--port",
                        dest="port",
                        nargs="?",
                        required=False,
                        default="3306",
                        help="Port of MySQL server to use.")
    parser.add_argument("--old-database",
                        dest="old_database",
                        nargs="?",
                        required=False,
                        default="radiosite",
                        help="Database name of the old database.")
    parser.add_argument("--django",
                        dest="django",
                        nargs="?",
                        required=False,
                        help="Location of django project.")
    """parser.add_argument("--new-database",
                        dest="new_database",
                        nargs="?",
                        required=False,
                        default="radio_main",
                        help="Database name of the new database.")"""
                        
    args = parser.parse_args()
    print args
    
    sys.path.append(args.django)
    
    move_data(args.host, args.port, args.user,
                   args.passwd, args.old_database)