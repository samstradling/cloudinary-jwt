# Cloudinary JWT

A simple python app that uploads images to [Cloudinary](https://cloudinary.com), authenticates uses [JSON Web Tokens](https://jwt.io/).

## Usage
Instructions on how to run this app are provided in this file.
### Running
The app has two running modes, development and uWSGI mode.

#### Docker
A docker file is provided and the image is availible on docker hub. Set the environment vaiables (see below), then run:
```bash
docker pull samstradling/cloudinary-jwt
docker run \
  -p ${CLOUD_PORT:-3000}:3000 \
  --env CLOUD_NAME=$CLOUD_NAME \
  --env CLOUD_APIKEY=$CLOUD_APIKEY \
  --env CLOUD_SECRET=$CLOUD_SECRET \
  --env CLOUD_JWT_SECRET=$CLOUD_JWT_SECRET \
  samstradling/cloudinary-jwt
```

Alternatively, use `docker-compose`:
```bash
docker-compose up --build
```

### Parameters
Parameters are read from command line arguments, or environment varibles, not both.

#### Command Line Arguments
Help for the command line arguments can be viewed by running `./main.py -h`.
```bash
$ ./main.py -h
usage: main.py [-h] --name CLOUD_NAME --api_key API_KEY --api_secret
               API_SECRET --jwt_secret JWT_SECRET [--port PORT] [--host HOST]
               [--cors] [--folder DEFAULT_FOLDER]

optional arguments:
  -h, --help            show this help message and exit
  --name CLOUD_NAME, -n CLOUD_NAME
                        "Cloud name" from cloudinary console
  --api_key API_KEY, -k API_KEY
                        "API Key" from cloudinary console
  --api_secret API_SECRET, -s API_SECRET
                        "API Secret" from cloudinary console
  --jwt_secret JWT_SECRET, -j JWT_SECRET
                        JWT Secret used to decrypt tokens.
  --port PORT, -p PORT  Port to run the app on (default: 3000).
  --host HOST           Host to run the app on (default 0.0.0.0).
  --cors                Enable Cross-Origin Resource Sharing (CORS)
  --folder DEFAULT_FOLDER
                        Cloudinary folder to upload to and list files in.
```

#### Environment Variables
| Variable               | Required/Optional | Description                                                            |
|------------------------|-------------------|------------------------------------------------------------------------|
| `CLOUD_NAME`           | Required          | "Cloud name" from cloudinary console (https://cloudinary.com/console). |
| `CLOUD_APIKEY`         | Required          | "API Key" from cloudinary console (https://cloudinary.com/console).    |
| `CLOUD_SECRET`         | Required          | "API Secret" from cloudinary console (https://cloudinary.com/console). |
| `CLOUD_JWT_SECRET`     | Required          | JWT secret, shard with with the secret generator.                      |
| `CLOUD_PORT`           | Optional          | Port to run the app on (default: 3000).                                |
| `CLOUD_HOST`           | Optional          | Host to run the app on (default: 0.0.0.0).                             |
| `CLOUD_CORS`           | Optional          | Enable Cross-Origin Resource Sharing (CORS).                           |
| `CLOUD_DEFAULT_FOLDER` | Optional          | Default cloudinary folder to upload to.                                |

## Errors
### Missing environment variable(s)
No parameters passed through either through parameters or environment variables.
### ModuleNotFoundError: No module named 'cloudinary'
Make sure to install requirements `pip install -r requirements.txt`

## Routes
Authorisation is provided by the `Authorization: Bearer <token>` header, test tokens can be generated using sites like [jwt.io](https://jwt.io/#debugger-io).
### `GET /`
Returns `HTTP 200 "Hello World!"`, no auth required.
```bash
$ curl -H "Authorization: bearer <JWT Token>" "http://example.com/"
Hello World!
```
### `GET /auth`
Returns `HTTP 200` if successfully authenticated, else `HTTP 401`.
```bash
$ curl -H "Authorization: bearer <JWT Token>" "http://example.com/auth/"
{
  "result": "OK"
}
```
### `GET /list/`
Returns a json list of images inside the folder set (CLOUD_DEFAULT_FOLDER).
```json
$ curl -H "Authorization: bearer <JWT Token>" "http://example.com/list/"
{
  "files":[
    {
      "image": "https://res.cloudinary.com/dizrhaqy4/image/upload/f_auto,q_auto:eco/v1524863896/sample.jpg",
      "thumb": "https://res.cloudinary.com/dizrhaqy4/image/upload/c_thumb,f_auto,h_200,w_200,q_auto:eco/v1524863896/sample.jpg"
    }
  ],
  "result":"OK"
}
```

### `GET /list/<path>`
Returns a json list of images inside the `$path` inside the folder  set (CLOUD_DEFAULT_FOLDER). `<path>` can take on multiple parts e.g. `GET /list/path/to/image`.
```bash
$ curl -H "Authorization: bearer <JWT Token>" "http://example.com/list/path/to/my/image"
{
  "files":[
    {
      "image": "https://res.cloudinary.com/dizrhaqy4/image/upload/f_auto,q_auto:eco/v1524863896/path/to/my/image/sample.jpg",
      "thumb": "https://res.cloudinary.com/dizrhaqy4/image/upload/c_thumb,f_auto,h_200,w_200,q_auto:eco/v1524863896/path/to/my/image/sample.jpg"
    }
  ],
  "result":"OK"
}
```
### `POST /upload`
Endpoint to post images to, expects json with key `image` of base64 encoded image:
```bash
$ curl -X POST -H "Authorization: bearer <JWT Token>" -d '{"image": "<base 64 encoded image"}' "http://example.com/upload"
{
  "result": "OK",
  "url": "https://res.cloudinary.com/dizrhaqy4/image/upload/f_auto,q_auto:eco/v1524863896/sample.jpg"
}
```

## Contributions
Contributions are welcomed.
