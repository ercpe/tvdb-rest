# tvdb-rest

`tvdb-rest` is a client implementation of the [TVDB REST API](https://api.thetvdb.com/swagger). This library *does not* support the "old" XML api!

## Usage

To use the REST API, you need an TVDB API key. See http://thetvdb.com/wiki/index.php?title=Programmers_API on how to obtain one. 

	from tvdbrest.client import TVDB
	api = TVDB("myusername", "myuserkey", "myapikey")

	for language in api.languages():
		print(language)

	simpsons = api.series(71663)

	print("Actors:")
	for actor in simpsons.actors():
		print("%s as %s" % (actor, ', '.join(actor.role.split('|'))))


## License

See LICENSE.txt
