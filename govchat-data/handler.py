import json
import ssl
import logging
logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

from google.transit import gtfs_realtime_pb2
from google.protobuf import json_format
import urllib.request
from geopy import distance

def get_trams():
  feed = gtfs_realtime_pb2.FeedMessage()
  response = urllib.request.urlopen('http://files.transport.act.gov.au/feeds/lightrail.pb')
  feed.ParseFromString(response.read())
  d = json_format.MessageToDict(feed)
  ret = []
  for entity in d["entity"]:
    if 'vehicle' in entity.keys():
      ret.append(entity['vehicle'])
  return ret

def get_qld():
  myssl = ssl.create_default_context();
  myssl.check_hostname=False
  myssl.verify_mode=ssl.CERT_NONE
  feed = gtfs_realtime_pb2.FeedMessage()
  response = urllib.request.urlopen('http://gtfsrt.api.translink.com.au/feed/seq', context=myssl)
  feed.ParseFromString(response.read())
  d = json_format.MessageToDict(feed)
  ret = []
  for entity in d["entity"]:
    if 'vehicle' in entity.keys():
      ret.append(entity['vehicle'])
  return ret


# endpoints
def trams(event, context):
  ret = get_trams()
  return {
      "statusCode": 200,
      "headers": {
         "Access-Control-Allow-Origin": "*",
         "Access-Control-Allow-Credentials": True,
       },
      "body": json.dumps(ret)
    }

def qld(event, context):
  ret = get_qld()
  return {
      "statusCode": 200,
      "headers": {
         "Access-Control-Allow-Origin": "*",
         "Access-Control-Allow-Credentials": True,
       },
      "body": json.dumps(ret)
    }

def vehicles(event, context):
  ret = get_trams() + get_qld()
  return {
      "statusCode": 200,
      "headers": {
         "Access-Control-Allow-Origin": "*",
         "Access-Control-Allow-Credentials": True,
       },
      "body": json.dumps(ret)
    }

def whoami(event, context):
  logger.debug(event["queryStringParameters"])
  params = event["queryStringParameters"]
  userloc = (params["lat"], params["lon"])

  trams = get_trams()
  qld = get_qld()

  gtfsr_vehicles = trams + qld

  gtfsr_locs = [{
      "label": v["vehicle"]["label"],
      "lat": v["position"]["latitude"],
      "lon": v["position"]["longitude"],
      "dist": distance.distance((v["position"]["latitude"], v["position"]["longitude"]), userloc).m
    } for v in gtfsr_vehicles
  ]

  locs = gtfsr_locs # may add non-gtfsr feeds in future

  locs.sort(key = lambda x: x["dist"])

  return {
      "statusCode": 200,
      "headers": {
         "Access-Control-Allow-Origin": "*",
         "Access-Control-Allow-Credentials": True,
       },
      "body": json.dumps(locs[0])
    }


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "headers": {
           "Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Credentials": True,
         },
        "body": json.dumps(body)
    }

    return response
