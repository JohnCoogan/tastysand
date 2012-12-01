# Twitter to MongoDB Streamer

## Description
Simple python script to save tweets from a twitter stream to a [MongoDB](http://www.mongodb.org/) database.

## How it works
The script takes a list of terms and runs forever. Terms can be updated on the fly and auto-create collections in MongoDB. I recommend MongoLab for ease-of-use if your dataset is expected to be under 500MB (it's free then).

## Directions
`python stream.py --user=oauth.json --server=localhost --database=TwitterStream --file=terms-example.txt`

*	**oauth.json** contains Twitter OAuth keys.
*	**db.json** contains DB connection info.
*	**terms.txt** contains a list of search terms (one per line).

Dependencies are listed in requirments.txt