# tvdb-rest

[![Build Status](https://travis-ci.org/ercpe/tvdb-rest.svg?branch=master)](https://travis-ci.org/ercpe/tvdb-rest) [![Coverage Status](https://coveralls.io/repos/github/ercpe/tvdb-rest/badge.svg?branch=master)](https://coveralls.io/github/ercpe/tvdb-rest?branch=master)

`tvdb-rest` is a client implementation of the [TVDB REST API](https://api.thetvdb.com/swagger). This library *does not* support the "old" XML api!

`tvdb-rest` supports Python 3.4+. Python 2.7 may work, but isn't supported.

## Usage

To use the REST API, you need an TVDB API key. See http://thetvdb.com/wiki/index.php?title=Programmers_API on how to obtain one. 

	from tvdbrest.client import TVDB
	api = TVDB("myusername", "myuserkey", "myapikey")

	for language in api.languages():
		print(language)

	# search for series
	search_results = api.search(name='The Simpsons')
	for series in search_results:
		print(series)

	# fetch series by id
	simpsons = api.series(71663)

	# access actors of series object
	for actor in simpsons.actors():
		print("%s as %s" % (actor, ', '.join(actor.role.split('|'))))

	# list all episodes for series (pagination handled automatically)
	for episode in simpsons.episodes():
		print(episode)

	


## License

See LICENSE.txt
