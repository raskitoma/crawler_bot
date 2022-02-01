# Plazabot

Current version: ***1.1a***

Bot for monitor/record/notify possible available items from a list of items from retail website URL.

***

- Full featured Frontend with log reading, settings editor, item list editor.
- Full functional API Backend
- Full support of DB engines. (Supports PostgreSQL on Docker, fallback to Sqlite)
- Most complete log registry with records of all possible operations within Crawler/API/Frontend operations.
- Captures screenshot of possible errors directly to DB
- Compatible with distintive match using a class object text. (Everything works so far except for Amazon it's kind of trying, uses id instead of class object)
- Idle Timer after a matched item is found (skip for x minutes)
- Frontend shows Crawler status (enabled/disabled, Iteration, Line proccesed)
- Notifications Supported:
  - SMTP Email using Google OATH2
  - SMTP Email using std Smtp library with TLS
  - Slack Webhook Push
  - SMS with Clickatell using custom curl

***

## Table of Contents

1. [Requirements](#requirements)
2. [Usage](#usage)
3. [Known Issues](#known-issues)
4. [Coming Soon Features](#comming-soon-features)
    1. [Next Release 1.1](#next-release-11)
    2. [Future Releases](#future-releases)

## Requirements

***

- **Docker** (Recommended):
  - docker.io and docker compose installed on host machine

***

- Direct on system (soon to be deprecated):
  - Gecko driver (Mozilla)
  - Install dependencies *[requirements.txt](requirements.txt)*

## Usage

***

- **Docker** (Recommended):
  - Inside program folder run `docker-compose build` and wait until docker image is properly builded
  - To run just type `docker-compose up -d`

***

- Master script (for direct run on system / soon to be deprecated) is **[pb_api.py](pb_api.py)**

***

Either method, just go to your browser and type `http://localhost:5000/`

## Known Issues

- Fix Target False Positives ex:
  > `PS5 Digital,https://www.target.com/p/playstation-5-digital-edition-console/-/A-81114596#lnk=sametab,h-text-grayDark,Out of stock in stores near you>`

## Coming Soon Features

### Next Release 1.2

- Add Whatsapp Alerts (sort of working) using direct FB/WA API
- Per Item x Per User Alerts Config. (Alerts.cfg)
- Per User x Per Plaforms (Users.cfg)
- Add the current timestamp on the console log when an item has been found and the time that i will restart (this will be deprecated, has no use).

### Future Releases

- Amazon Price Search
