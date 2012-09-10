import argparse
import logging
import sys
from subprocess import STDOUT, Popen
import MySQLdb as mysql
import MySQLdb.cursors as cursors

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
        
def create_database(input_file, host, port, username, password):
    with open(input_file, "rb") as f:
        logging.info("Starting 'mysql' subprocess")
        process = Popen(args=['mysql', "-v", "-u", username, "-p" + password,
                              "--default-character-set=utf8",
                              "-h", host, "-P", port],
                        stdin=f,
                        stdout=sys.stdout,
                        stderr=STDOUT)
        if not process.wait() == 0:
            logging.info("Database creation process failed.")
            raise AssertionError()
        else:
            logging.info("Database creation process complete.")
            return 0
        
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
    logging.info("Working on: users")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new) as new_cur:
            # Retrieve old fields
            old_cur.execute("SELECT user, pass, privileges FROM users ORDER BY id ASC;")
            
            old_data = [("Unknown", "Empty", 0)] + list(old_cur)
            # Create our insert query
            query = """INSERT INTO users (username, password, privileges)
            VALUES (%s, %s, %s)"""
            new_cur.executemany(query, old_data)
    # DJs
    logging.info("Working on: djs")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new) as new_cur:
            # retrieve old djids from old users
            old_cur.execute("SELECT djid FROM users ORDER BY id ASC;")
            links = []
            for userid, rest in enumerate(old_cur):
                links.append((userid+2, rest[0]))
            for userid, djid in links:
                # Get djid info
                old_cur.execute("""SELECT djname, djtext, djimage, 
                                visible, priority, css FROM djs WHERE id=%s;""",
                                (djid,))
                # Put info into new djs table
                for name, description, image, visible, priority, css in old_cur:
                    new_cur.execute("""INSERT INTO djs (id, name, description, 
                    image, visible, priority, user, css) VALUES (%s, %s, %s,
                    %s, %s, %s, %s, %s);""", (djid, name, description,
                                              image, visible, priority,
                                              userid, css))
    
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
                    new_cur.execute("SELECT id FROM users WHERE username=%s;", (login,))
                    for poster, in new_cur:
                        old_data.append((nid, header, text, mail, poster, time))
            # lovely query
            query = """INSERT INTO news_comments (news_id, nickname,
            text, mail, poster, time) VALUES (%s, %s, %s, %s, %s, %s);"""
            
            # execute, done
            new_cur.executemany(query, old_data)
            
    # Relays, don't need anything special really
    logging.info("Working on: relays")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("SELECT * FROM relays;")
            query = """INSERT INTO relays (id, relay_name, relay_owner,
            base_name, port, mount, bitrate, format, listeners, listener_limit,
            active, admin_auth) VALUES (%s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s);"""
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
            query = """INSERT INTO players (name, useragent) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name);"""
            new_cur.executemany(query, players)
            
            # prepare iterator for listener
            listeners = []
            for ip, lastset, player in old_data:
                new_cur.execute("SELECT id FROM players WHERE useragent=%s;", (player[:200],))
                for row, in new_cur:
                    player = row
                listeners.append((ip, player, 0, lastset, None))
            # Prepare query
            query = """INSERT INTO listeners (ip, players_id, banned,
            last_seen, nicknames_id) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE
            KEY UPDATE last_seen=VALUES(last_seen);"""
            # Add all of them to listeners
            new_cur.executemany(query, listeners)
            
    # Nicknames time! yay, we create a fake default hostname here since we
    # don't save these in the old database
    logging.info("Working on: nicknames")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("SELECT nick, authcode FROM enick;")
            
            # Add fake hostname
            new_cur.execute("INSERT INTO hostnames (hostname) VALUES ('Fake');")
            hostname = new_cur.lastrowid
            # prepare iterator
            nicknames = []
            for nick, passcode in old_cur:
                nicknames.append((nick, passcode, hostname))
                
            
            
            # QUERY
            query = """INSERT INTO nicknames (nick, passcode, hostnames_id)
            VALUES (%s, %s, %s);"""
            
            new_cur.executemany(query, nicknames)
            
    # The fun starts
    def add_track(cursor, meta, length=0):
        try:
            cursor.execute("""INSERT INTO track 
            (metadata, length) VALUES (%s, %s);""", (meta, length))
            return new_cur.lastrowid
        except mysql.IntegrityError:
            cursor.execute("""SELECT id FROM track
             WHERE hash=SHA1(%s);""", (meta,))
            for track_id, in cursor:
                return track_id
    def add_album(cursor, album):
        try:
            cursor.execute("""INSERT INTO album (name) VALUES (%s)
            ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id);""",
                           (album,))
            return cursor.lastrowid
        except mysql.IntegrityError:
            cursor.execute("""SELECT id FROM album WHERE name=%s;""",
                           (album,))
            for album_id, in cursor:
                return album_id
    def add_song(cursor, metadata, tid):
        cursor.execute("""INSERT INTO songs (hash, track_id) VALUES
                (SHA1(%s), %s) ON DUPLICATE KEY UPDATE
                 id=LAST_INSERT_ID(id), track_id=VALUES(track_id);""", (metadata, tid))
        return cursor.lastrowid
    def link_track_album(cursor, tid, aid):
        cursor.execute("""INSERT INTO track_has_album (track_id, album_id)
        VALUES (%s, %s);""", (tid, aid))
    def get_user_id(cursor, username):
        if not username:
            username = "Unknown"
        cursor.execute("SELECT id FROM users WHERE username=%s;", (username,))
        for id, in cursor:
            if id:
                return id
            elif username != "Unknown":
                return get_user_id(cursor, "Unknown")
            else:
                raise ValueError("Unknown user")
    def get_dj_id(cursor, username):
        cursor.execute("SELECT djs.id AS id FROM djs JOIN users ON users.id = djs.user WHERE users.username=%s;", (username,))
        for id, in cursor:
            return id
    def get_nick_id(cursor, nick):
        cursor.execute("SELECT id FROM nicknames WHERE nick=%s;", (nick,))
        for id, in cursor:
            return id
    def add_collection(cursor, **kwargs):
        column_list = ["songs_id", "usable", "filename",
                       "good_upload", "need_reupload",
                       "popularity", "status", "decline_reason",
                       "comment", "original_filename"]
        length = 0
        for key in kwargs.iterkeys():
            if not key in column_list:
                raise TypeError("Unsupported argument")
            length += 1
        insert = ",".join(["%s"]*length)
        update, columns, data = ["id=LAST_INSERT_ID(id)"], [], []
        for keys, items in kwargs.iteritems():
            update.append("{0}=VALUES({0})".format(keys))
            columns.append(keys)
            data.append(items)
        update = ",".join(update)
        columns = ",".join(columns)
            
        cursor.execute("""INSERT INTO collection ({columns}) VALUES
        ({insert}) ON DUPLICATE KEY UPDATE
        {update};""".format(columns=columns, insert=insert, update=update),
        data)
        return cursor.lastrowid
    def add_editor(cursor, collection, user, action, time=None):
        cursor.execute("""INSERT INTO collection_editors 
        (users_id, action, time, collection_id) VALUES
        (%s, %s, %s, %s);""", (user, action, time, collection))
        return cursor.lastrowid
    def add_tag(cursor, tag):
        cursor.execute("""INSERT INTO tags (name) VALUES
        (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id);""", (tag,))
        return cursor.lastrowid
    def link_collection_tag(cursor, cid, tid):
        try:
            cursor.execute("""INSERT INTO collection_has_tags (collection_id, tags_id)
            VALUES (%s, %s);""", (cid, tid))
        except mysql.IntegrityError:
            pass
    def add_listener(cursor, **kwargs):
        column_list = ["ip", "players_id", "banned",
                       "last_seen", "nicknames_id"]
        length = 0
        for key in kwargs.iterkeys():
            if not key in column_list:
                raise TypeError("Unsupported argument")
            length += 1
        insert = ",".join(["%s"]*length)
        update, columns, data = ["id=LAST_INSERT_ID(id)"], [], []
        for keys, items in kwargs.iteritems():
            update.append("{0}=VALUES({0})".format(keys))
            columns.append(keys)
            data.append(items)
        update = ",".join(update)
        columns = ",".join(columns)
            
        cursor.execute("""INSERT INTO listeners ({columns}) VALUES
        ({insert}) ON DUPLICATE KEY UPDATE
        {update};""".format(columns=columns, insert=insert, update=update),
        data)
        if cursor.lastrowid == 0:
            try:
                cursor.execute("SELECT id FROM listeners WHERE ip=%s", (kwargs['ip'],))
                for id, in cursor:
                    return id
            except:
                return 0
        return cursor.lastrowid
    def add_uploads(cursor, listener, time, collection):
        cursor.execute("""INSERT INTO uploads (listeners_id, time, collection_id)
        VALUES (%s, %s, %s);""", (listener, time, collection))
        return cursor.lastrowid
    def add_played(cursor, songs_id, time, dj):
        cursor.execute("""INSERT INTO played (time, songs_id, djs_id) VALUES
        (%s, %s, %s);""", (time, songs_id, dj))
        return cursor.lastrowid
    def add_fave(cursor, songs_id, nicknames_id):
        cursor.execute("""INSERT INTO faves (songs_id, nicknames_id) VALUES
        (%s, %s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id);""",
        (songs_id, nicknames_id))
        return cursor.lastrowid
    logging.info("Working on: songs from esong")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("SELECT id, hash, meta, len FROM esong;")
            
            for id, hash, meta, len in old_cur:
                # Add the usual esong
                track_id = add_track(new_cur, meta, len)
                songs_id = add_song(new_cur, meta, track_id)

                # Do our eplay
                old_cur.execute("""SELECT dt AS time FROM eplay JOIN esong ON
                esong.id = eplay.isong WHERE eplay.isong=%s;""", (id,))
                for time, in old_cur:
                    add_played(new_cur, songs_id, time, get_dj_id(new_cur, "wessie"))
                    
                # Do our efave
                old_cur.execute("""SELECT enick.nick AS nick FROM efave JOIN
                enick ON enick.id=efave.inick WHERE efave.isong=%s;""",
                (id,))
                for nick, in old_cur:
                    add_fave(new_cur, songs_id=songs_id,
                             nicknames_id=get_nick_id(new_cur, nick))
    logging.info("Working on: songs from tracks")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("""SELECT * FROM tracks;""")
            # Create track and album, link them
            for id, artist, track, album, path, tags, priority, lastplayed, lastrequested, usable, accepter, lasteditor, hash, requestcount, need_reupload in old_cur:
                metadata = artist + " - " + track if artist else track
                # Create track entry
                track_id = add_track(new_cur, metadata)
                album_id = add_album(new_cur, album)
                # Link album and track entry together
                link_track_album(new_cur, track_id, album_id)
                
                # Create song entry, link to track entry
                song_id = add_song(new_cur, metadata, track_id)
                
                # Create collection entry
                collection_id = add_collection(new_cur, songs_id=song_id,
                                               usable=usable, filename=path,
                                               need_reupload=need_reupload,
                                               popularity=requestcount,
                                               status=STATUS_ACCEPTED)
                
                # add accepter
                user_id = get_user_id(new_cur, accepter)
                add_editor(new_cur, collection_id, user_id, action="accept")
                
                # add editor
                user_id = get_user_id(new_cur, lasteditor)
                add_editor(new_cur, collection_id, user_id, action="edit")
                
                # Create all the tags
                for tag in tags.split(" "):
                    tag_id = add_tag(new_cur, tag)
                    link_collection_tag(new_cur, collection_id, tag_id)

    logging.info("Working on: songs from pending")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("""SELECT * FROM pending;""")
            for id, artist, track, album, path, comment, origname, submitter, submitted, dupe_flag, replacement in old_cur:
                # Create our listeners
                
                metadata = artist + " - " + track if artist else track
                
                track_id = add_track(new_cur, metadata)
                album_id = add_album(new_cur, album)
                
                link_track_album(new_cur, track_id, album_id)
                
                song_id = add_song(new_cur, metadata, track_id)
                
                listeners_id = add_listener(new_cur, ip=submitter,
                                            last_seen=submitted)
                collection_id = add_collection(new_cur, songs_id=song_id,
                                               filename=path,
                                               status=STATUS_REPLACEMENT if replacement else STATUS_PENDING,
                                               comment=comment, 
                                               original_filename=origname)
                try:
                    add_uploads(new_cur, listeners_id, submitted, collection_id)
                except:
                    print listeners_id, collection_id
                    
    logging.info("Working on: songs from postpending")
    with Cursor(options_old, cursortype=cursors.Cursor) as old_cur:
        with Cursor(options_new, cursortype=cursors.Cursor) as new_cur:
            old_cur.execute("""SELECT * FROM postpending;""")
            for id, trackid, meta, ip, accepted, time, reason, good_upload in old_cur:
                # Create our listeners
                
                metadata = meta
                
                track_id = add_track(new_cur, metadata)
                
                song_id = add_song(new_cur, metadata, track_id)
                
                listeners_id = add_listener(new_cur, ip=ip,
                                            last_seen=time)
                collection_id = add_collection(new_cur, songs_id=song_id,
                                               status=STATUS_ACCEPTED if accepted else STATUS_DECLINED,
                                               good_upload=good_upload,
                                               decline_reason=reason)
                try:
                    add_uploads(new_cur, listeners_id, ip, collection_id)
                except:
                    print listeners_id, collection_id
                    
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
    parser.add_argument("--sql-file",
                        dest="sql_file",
                        nargs="?",
                        required=True,
                        help="File that contains the SQL database creation statements.")
    """parser.add_argument("--new-database",
                        dest="new_database",
                        nargs="?",
                        required=False,
                        default="radio_main",
                        help="Database name of the new database.")"""
                        
    args = parser.parse_args()
    print args
    
    try:
        create_database(args.sql_file, args.host, args.port,
                         args.user, args.passwd)
    except AssertionError:
        pass
    else:
        move_data(args.host, args.port, args.user,
                   args.passwd, args.old_database)