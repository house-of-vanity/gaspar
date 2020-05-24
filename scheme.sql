BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "torrents" (
	"id"	TEXT NOT NULL,
	"info_hash"	TEXT NOT NULL,
	"forum_id"	TEXT NOT NULL,
	"poster_id"	TEXT,
	"size"	INT NOT NULL,
	"reg_time"	INT NOT NULL,
	"tor_status" TEXT,
	"seeders"	TEXT,
	"topic_title"	TEXT,
	"seeder_last_seen"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "torrents_history" (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
	"id"	TEXT NOT NULL,
	"info_hash"	TEXT NOT NULL,
	"forum_id"	TEXT NOT NULL,
	"poster_id"	TEXT,
	"size"	INT NOT NULL,
	"reg_time"	INT NOT NULL,
	"tor_status" TEXT,
	"seeders"	TEXT,
	"topic_title"	TEXT,
	"seeder_last_seen"	TEXT
);
CREATE TABLE IF NOT EXISTS "users" (
        id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT
        );
CREATE TABLE IF NOT EXISTS "alerts" (
        user_id TEXT,
        tor_id TEXT,
        UNIQUE(user_id, tor_id)
        );
COMMIT;

