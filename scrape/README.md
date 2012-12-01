# Twitter to MongoDB Streamer

## Description
Simple python script to save tweets from a twitter stream to a [MongoDB](http://www.mongodb.org/) database.

## How it works
The script takes a list of terms and runs forever. Terms can be updated on the fly and auto-create collections in MongoDB. I recommend MongoLab for ease-of-use if your dataset is expected to be under 500MB (it's free then).

## Directions
`python stream.py -o oauth.json -d db.json -t terms.txt`

*	**oauth.json** contains Twitter OAuth keys.
*	**db.json** contains DB connection info.
*	**terms.txt** contains a list of search terms (one per line).

## Deployment
Running on a server is usually best so the process can stay up for a sizable amount of time.
Notes: Dependencies are listed in requirments.txt Procfile allows you to easily deploy as a worker to Heroku.

*	`heroku create [name]`
*	`git push heroku master`
*	`heroku ps:scale worker=1`
*	`heroku logs`