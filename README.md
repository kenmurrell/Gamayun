# Gamayun 

Local language detector using trigrams modelling, dockerized

![gamayun](gamayun-picture.jpg)

### Details

* Supports 19 European languages
* Doesn't require an internet connection

### Setup
1) Install docker and docker-compose

2) Run the following command create and run the container 
```
docker-compose -f docker-compose.yml up --scale worker=2 --build
```

This starts a webservice that listens at localhost:5000

#### Example

```bash
curl -X GET "http://localhost:5000/detect/Pour%20notre%20bien%20%C3%A0%20tous%20les%20deux%2C%20esp%C3%A9rons%20que%20%C3%A7a%20fonctionne." -H  "accept: application/json"
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 101
Access-Control-Allow-Origin: *

{
  "task_id": "e2eab43a-26ea-4d66-ada7-1519ac29de72",
  "url": "http://localhost:5000/check/e2eab43a-26ea-4d66-ada7-1519ac29de72"
}
```

and when navigating to the above URL
```bash
curl -X GET localhost:5000/check_task/a86327b8-2d9b-470d-96a9-a27ad87e2c49
```

**Response**
```
{
  "status": "SUCCESS",
  "result": [
    {
      "language": "french",
      "iso639_1": "fr",
      "iso639_2": "fre",
      "match": "99.98%"
    }
  ],
  "task_id": "e2eab43a-26ea-4d66-ada7-1519ac29de72"
}
```

### References 

* Borrowed the trigram maps from [abadojack](https://github.com/abadojack), go check him out
