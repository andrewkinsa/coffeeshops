# coffeeshops

This code is implemented using Python (specifically, python 2, though
it would be straightforward to change it to python 3). It uses Django
as a web framework.

For the purposes of the exercise, I only used Django for HTTP support
and URL routing. In real life, I would use its ORM and REST framework,
which would make the code much shorter, more concise and obviously much
more robust.

All my code is in `shops/views.py`, the rest is mostly Django
boilerplate.

Set-up instructions tested in Mac OS X and Linux.

## API endpoints

    /v1/coffeeshops (GET, POST)
    /v1/coffeeshops/?nearest_to=<address> (GET)
    /v1/coffeeshops/<id> (GET, DELETE, PUT)

GET `/v1/coffeeshops` returns a JSON list of all known shops. For
consistency, `/v1/coffeeshops?nearest_to=<address>` also returns a
list, always containig one element.

POST on coffeeshops, and GET/PUT on an individual shop all return a
full JSON representation of that shop, for consistency.

## Implementation notes

* Used Open Street Maps geocoder instead of Google Maps.

* No comments in the code. In production code, I would have added some
  high-level comments.

* Likewise, in production code I would have done more error handling,
  and *maybe* structured error reporting (JSON instead of plain text).


## Setting Up

Clone the repository:

    git clone git@github.com:andrewkinsa/coffeeshops.git
    cd coffeeshops

Create and activate a python virtual environment:

    virtualenv coffeeshops # (might need to install virtualenv, eg "sudo apt install virtualenv" in Ubuntu)
    source coffeeshops/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

Run the Django dev server:

    ./manage.py runserver

## Testing

    # list all known shops
    curl http://127.0.0.1:8000/v1/coffeeshops

    # return shop with id 13
    curl http://127.0.0.1:8000/v1/coffeeshops/13

    # now delete it (using "-v" to examine HTTP status code)
    curl -v --request DELETE http://127.0.0.1:8000/v1/coffeeshops/13

    # trying to delete again (should return 404 Not Found)
    curl --request DELETE http://127.0.0.1:8000/v1/coffeeshops/13

    # the same with a GET request
    curl http://127.0.0.1:8000/v1/coffeeshops/13

    # finding shops nearest to the given address
    curl "http://127.0.0.1:8000/v1/coffeeshops?nearest_to=535%20Mission%20St.,%20San%20Francisco,%20CA"
    curl "http://127.0.0.1:8000/v1/coffeeshops?nearest_to=252%20Guerrero%20St,%20San%20Francisco,%20CA%2094103,%20USA"

    # testing geocoding failures
    curl -v http://127.0.0.1:8000/v1/coffeeshops?nearest_to=NotExisting,NA,USA

    # adding a new shop (note automatic geocoding if coordinates are not specified)
    curl -v -d '{"name": "Starbucks", "address": "1269 Centre St, Newton, MA"}' http://127.0.0.1:8000/v1/coffeeshops

    # verifying that it is used for searches
    curl http://127.0.0.1:8000/v1/coffeeshops?nearest_to=Newton,MA

    # modifying it
    curl --request PUT -d '{"name": "Starbucks", "address": "1269 Centre St, Newton, MA", "lat":1, "lng":1}' http://127.0.0.1:8000/v1/coffeeshops/57

    # PUT can also be used to create a new shop
    curl -v --request PUT -d '{"name": "Thinking Cup", "address": "165 Tremont St, Boston, MA 02111"}' http://127.0.0.1:8000/v1/coffeeshops/100

    # Testing malformed requests (all should return 400 Bad Request)
    curl -v -d '33' http://127.0.0.1:8000/v1/coffeeshops
    curl -v -d 'xx' http://127.0.0.1:8000/v1/coffeeshops
    curl -v -d '{"name": "foo"}' http://127.0.0.1:8000/v1/coffeeshops
    curl -v -d '{"name": "shop", "address": "somewhere", "foo": "bar"}' http://127.0.0.1:8000/v1/coffeeshops

    # Testing unsupported methods
    curl -v --request DELETE http://127.0.0.1:8000/v1/coffeeshops
    curl -v --request POST http://127.0.0.1:8000/v1/coffeeshops/13
