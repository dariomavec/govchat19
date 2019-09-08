import json
import ssl
import logging
logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

from google.transit import gtfs_realtime_pb2
from google.protobuf import json_format
import urllib.request
from geopy import distance


STOPS = {'8100': {'stop_id': '8100', 'stop_name': 'Gungahlin Place Platform 1', 'stop_lat': -35.1856039, 'stop_lon': 149.13548740000002, 'stop_url': 'https://cmet.com.au/light-rail-stops/gungahlin-place/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'GGN'}, '8101': {'stop_id': '8101', 'stop_name': 'Gungahlin Place Platform 2', 'stop_lat': -35.185673200000004, 'stop_lon': 149.1354648, 'stop_url': 'https://cmet.com.au/light-rail-stops/gungahlin-place/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'GGN'}, 'GGN': {'stop_id': 'GGN', 'stop_name': 'Gungahlin Place', 'stop_lat': -35.185639, 'stop_lon': 149.135481, 'stop_url': 'https://cmet.com.au/light-rail-stops/gungahlin-place/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8104': {'stop_id': '8104', 'stop_name': 'Manning Clark North Platform 1', 'stop_lat': -35.186960799999994, 'stop_lon': 149.14342219999997, 'stop_url': 'https://cmet.com.au/light-rail-stops/manning-clark-north/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'MCK'}, '8105': {'stop_id': '8105', 'stop_name': 'Manning Clark North Platform 2', 'stop_lat': -35.1870359, 'stop_lon': 149.1434058, 'stop_url': 'https://cmet.com.au/light-rail-stops/manning-clark-north/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'MCK'}, 'MCK': {'stop_id': 'MCK', 'stop_name': 'Manning Clark North', 'stop_lat': -35.186986, 'stop_lon': 149.143372, 'stop_url': 'https://cmet.com.au/light-rail-stops/manning-clark-north/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8106': {'stop_id': '8106', 'stop_name': 'Mapleton Avenue Platform 1', 'stop_lat': -35.1934347, 'stop_lon': 149.1510139, 'stop_url': 'https://cmet.com.au/light-rail-stops/mapleton-avenue/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'MPN'}, '8107': {'stop_id': '8107', 'stop_name': 'Mapleton Avenue Platform 2', 'stop_lat': -35.1934216, 'stop_lon': 149.1509264, 'stop_url': 'https://cmet.com.au/light-rail-stops/mapleton-avenue/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'MPN'}, 'MPN': {'stop_id': 'MPN', 'stop_name': 'Mapleton Avenue', 'stop_lat': -35.193381, 'stop_lon': 149.150972, 'stop_url': 'https://cmet.com.au/light-rail-stops/mapleton-avenue/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8108': {'stop_id': '8108', 'stop_name': 'Nullarbor Avenue Platform 1', 'stop_lat': -35.2003844, 'stop_lon': 149.1493763, 'stop_url': 'https://cmet.com.au/light-rail-stops/nullarbor-avenue/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'NLR'}, '8109': {'stop_id': '8109', 'stop_name': 'Nullarbor Avenue Platform 2', 'stop_lat': -35.2003745, 'stop_lon': 149.1492863, 'stop_url': 'https://cmet.com.au/light-rail-stops/nullarbor-avenue/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'NLR'}, 'NLR': {'stop_id': 'NLR', 'stop_name': 'Nullarbor Avenue', 'stop_lat': -35.20055, 'stop_lon': 149.149294, 'stop_url': 'https://cmet.com.au/light-rail-stops/nullarbor-avenue/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8110': {'stop_id': '8110', 'stop_name': 'Well Station Drive Platform 1', 'stop_lat': -35.209050700000006, 'stop_lon': 149.14740469999998, 'stop_url': 'https://cmet.com.au/light-rail-stops/well-station-drive/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'WSN'}, '8111': {'stop_id': '8111', 'stop_name': 'Well Station Drive Platform 2', 'stop_lat': -35.2090473, 'stop_lon': 149.1473109, 'stop_url': 'https://cmet.com.au/light-rail-stops/well-station-drive/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'WSN'}, 'WSN': {'stop_id': 'WSN', 'stop_name': 'Well Station Drive', 'stop_lat': -35.20905, 'stop_lon': 149.14735, 'stop_url': 'https://cmet.com.au/light-rail-stops/well-station-drive/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8114': {'stop_id': '8114', 'stop_name': 'EPIC and Racecourse Platform 1', 'stop_lat': -35.2284977, 'stop_lon': 149.14424340000002, 'stop_url': 'https://cmet.com.au/light-rail-stops/epic-racecourse/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'EPC'}, '8115': {'stop_id': '8115', 'stop_name': 'EPIC and Racecourse Platform 2', 'stop_lat': -35.22850089999999, 'stop_lon': 149.14422, 'stop_url': 'https://cmet.com.au/light-rail-stops/epic-racecourse/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'EPC'}, 'EPC': {'stop_id': 'EPC', 'stop_name': 'EPIC and Racecourse', 'stop_lat': -35.2285, 'stop_lon': 149.14422, 'stop_url': 'https://cmet.com.au/light-rail-stops/epic-racecourse/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8116': {'stop_id': '8116', 'stop_name': 'Phillip Avenue Platform 1', 'stop_lat': -35.235845399999995, 'stop_lon': 149.1439324, 'stop_url': 'https://cmet.com.au/light-rail-stops/phillip-avenue/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'PLP'}, '8117': {'stop_id': '8117', 'stop_name': 'Phillip Avenue Platform 2', 'stop_lat': -35.2357995, 'stop_lon': 149.1438889, 'stop_url': 'https://cmet.com.au/light-rail-stops/phillip-avenue/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'PLP'}, 'PLP': {'stop_id': 'PLP', 'stop_name': 'Phillip Avenue', 'stop_lat': -35.235794, 'stop_lon': 149.14392800000002, 'stop_url': 'https://cmet.com.au/light-rail-stops/phillip-avenue/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8118': {'stop_id': '8118', 'stop_name': 'Swinden Street Platform 1', 'stop_lat': -35.244467799999995, 'stop_lon': 149.1346206, 'stop_url': 'https://cmet.com.au/light-rail-stops/swinden-street/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'SWN'}, '8119': {'stop_id': '8119', 'stop_name': 'Swinden Street Platform 2', 'stop_lat': -35.244464, 'stop_lon': 149.134502, 'stop_url': 'https://cmet.com.au/light-rail-stops/swinden-street/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'SWN'}, 'SWN': {'stop_id': 'SWN', 'stop_name': 'Swinden Street', 'stop_lat': -35.24447, 'stop_lon': 149.13461999999998, 'stop_url': 'https://cmet.com.au/light-rail-stops/swinden-street/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8120': {'stop_id': '8120', 'stop_name': 'Dickson Platform 1', 'stop_lat': -35.250558899999994, 'stop_lon': 149.1337551, 'stop_url': 'https://cmet.com.au/light-rail-stops/dickson-interchange/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'DKN'}, '8121': {'stop_id': '8121', 'stop_name': 'Dickson Platform 2', 'stop_lat': -35.250557799999996, 'stop_lon': 149.133725, 'stop_url': 'https://cmet.com.au/light-rail-stops/dickson-interchange/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'DKN'}, 'DKN': {'stop_id': 'DKN', 'stop_name': 'Dickson Interchange', 'stop_lat': -35.250558000000005, 'stop_lon': 149.133739, 'stop_url': 'https://cmet.com.au/light-rail-stops/dickson-interchange/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8122': {'stop_id': '8122', 'stop_name': 'Macarthur Avenue Platform 1', 'stop_lat': -35.260159200000004, 'stop_lon': 149.13219750000002, 'stop_url': 'https://cmet.com.au/light-rail-stops/macarthur-avenue/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'MCR'}, '8123': {'stop_id': '8123', 'stop_name': 'Macarthur Avenue Platform 2', 'stop_lat': -35.2601563, 'stop_lon': 149.13216359999998, 'stop_url': 'https://cmet.com.au/light-rail-stops/macarthur-avenue/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'MCR'}, 'MCR': {'stop_id': 'MCR', 'stop_name': 'Macarthur Avenue', 'stop_lat': -35.260158000000004, 'stop_lon': 149.132228, 'stop_url': 'https://cmet.com.au/light-rail-stops/macarthur-avenue/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8124': {'stop_id': '8124', 'stop_name': 'Ipima Street Platform 1', 'stop_lat': -35.2658969, 'stop_lon': 149.131272, 'stop_url': 'https://cmet.com.au/light-rail-stops/ipima-street/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'IPA'}, '8125': {'stop_id': '8125', 'stop_name': 'Ipima Street Platform 2', 'stop_lat': -35.265894700000004, 'stop_lon': 149.1312436, 'stop_url': 'https://cmet.com.au/light-rail-stops/ipima-street/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'IPA'}, 'IPA': {'stop_id': 'IPA', 'stop_name': 'Ipima Street', 'stop_lat': -35.265896999999995, 'stop_lon': 149.131283, 'stop_url': 'https://cmet.com.au/light-rail-stops/ipima-street/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8126': {'stop_id': '8126', 'stop_name': 'Elouera Street Platform 1', 'stop_lat': -35.272618, 'stop_lon': 149.1301981, 'stop_url': 'https://cmet.com.au/light-rail-stops/elouera-street/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'ELA'}, '8127': {'stop_id': '8127', 'stop_name': 'Elouera Street Platform 2', 'stop_lat': -35.2726172, 'stop_lon': 149.13015990000002, 'stop_url': 'https://cmet.com.au/light-rail-stops/elouera-street/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'ELA'}, 'ELA': {'stop_id': 'ELA', 'stop_name': 'Elouera Street', 'stop_lat': -35.272617, 'stop_lon': 149.130172, 'stop_url': 'https://cmet.com.au/light-rail-stops/elouera-street/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}, '8128': {'stop_id': '8128', 'stop_name': 'Alinga Street Platform 1', 'stop_lat': -35.2779344, 'stop_lon': 149.129346, 'stop_url': 'https://cmet.com.au/light-rail-stops/alinga-street-city/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'ALG'}, '8129': {'stop_id': '8129', 'stop_name': 'Alinga Street Platform 2', 'stop_lat': -35.2779315, 'stop_lon': 149.12930690000002, 'stop_url': 'https://cmet.com.au/light-rail-stops/alinga-street-city/', 'location_type': 0, 'wheelchair_boarding': 0, 'parent_station': 'ALG'}, 'ALG': {'stop_id': 'ALG', 'stop_name': 'Alinga Street', 'stop_lat': -35.277933000000004, 'stop_lon': 149.129331, 'stop_url': 'https://cmet.com.au/light-rail-stops/alinga-street-city/', 'location_type': 1, 'wheelchair_boarding': 0, 'parent_station': None}}


def get_trams():
  feed = gtfs_realtime_pb2.FeedMessage()
  response = urllib.request.urlopen('http://files.transport.act.gov.au/feeds/lightrail.pb')
  feed.ParseFromString(response.read())
  d = json_format.MessageToDict(feed)
  ret = []
  for entity in d["entity"]:
    if 'vehicle' in entity.keys():
      output = entity['vehicle']
      if output['stopId'] in STOPS.keys():
          output['stopInfo'] = STOPS[output['stopId']]
      else:
          output['stopInfo'] = []

      ret.append(output)

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
