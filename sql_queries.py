import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE staging_events (
	artist text,
	auth text,
	firstname text,
	gender text,
	iteminsession int,
	lastname text,
	length numeric(10,5),
	level text,
	location text,
	method text,
	page text,
	registration bigint,
	sessionid int,
	song text,
	status int,
	ts bigint,
	useragent text,
	userid int
);
""")

staging_songs_table_create = ("""
CREATE TABLE staging_songs (
	num_songs int,
	artist_id text,
	artist_latitude numeric(8,5),
	artist_longitude numeric(8,5),
	artist_location text,
	artist_name text,
	song_id text,
	title text,
	duration numeric(10,5),
	year int
);
""")

songplay_table_create = ("""
CREATE TABLE songplays (
	songplay_id int IDENTITY(0,1),
	start_time timestamp NOT NULL,
	user_id int NOT NULL,
	level text,
	song_id text,
	artist_id text,
	session_id int,
	location text,
	user_agent text
);
""")

user_table_create = ("""
CREATE TABLE users (
	user_id int NOT NULL,
	first_name text,
	last_name text,
	gender text,
	level text
);
""")

song_table_create = ("""
CREATE TABLE songs (
	song_id text NOT NULL,
	title text,
	artistid text,
	year int,
	duration numeric(18,0)
);
""")

artist_table_create = ("""
CREATE TABLE artists (
	artist_id text NOT NULL,
	name text,
	location text,
	lattitude numeric(18,0),
	longitude numeric(18,0)
);
""")

time_table_create = ("""
CREATE TABLE time (
	start_time timestamp NOT NULL,
	hour int,
	day int,
	week int,
	month text,
	year int,
	weekday text
);
""")

# STAGING TABLES

staging_events_copy = ("""
copy staging_events from '{}' 
credentials 'aws_iam_role={}'
json '{}';
""").format(config.get("S3", "LOG_DATA"), config.get("IAM_ROLE", "ARN"), config.get("S3", "LOG_JSONPATH"))

staging_songs_copy = ("""
copy staging_songs from '{}' 
credentials 'aws_iam_role={}'
json 'auto' truncatecolumns;
""").format(config.get("S3", "SONG_DATA"), config.get("IAM_ROLE", "ARN"))

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays(start_time,user_id,level,song_id,artist_id,session_id,location,user_agent)
    SELECT
        events.start_time, 
        events.userid, 
        events.level, 
        songs.song_id, 
        songs.artist_id, 
        events.sessionid, 
        events.location, 
        events.useragent
    FROM (
        SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
        FROM staging_events
        WHERE page='NextSong'
        ) events
    LEFT JOIN staging_songs songs
    ON events.song = songs.title
        AND events.artist = songs.artist_name
        AND events.length = songs.duration
""")

user_table_insert = ("""
INSERT INTO users(user_id,first_name,last_name,gender,level)
    SELECT distinct userid, firstname, lastname, gender, level
    FROM staging_events
    WHERE page='NextSong'
""")

song_table_insert = ("""
INSERT INTO songs(song_id,title,artistid,year,duration)
    SELECT distinct song_id, title, artist_id, year, duration
    FROM staging_songs
""")

artist_table_insert = ("""
INSERT INTO artists(artist_id,name,location,lattitude,longitude)
    SELECT distinct artist_id, artist_name, artist_location, artist_latitude, artist_longitude
    FROM staging_songs
""")

time_table_insert = ("""
INSERT INTO time(start_time, hour, day, week, month, year, weekday)
    SELECT start_time, extract(hour from start_time), extract(day from start_time), extract(week from start_time), 
        extract(month from start_time), extract(year from start_time), extract(dayofweek from start_time)
    FROM songplays
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
