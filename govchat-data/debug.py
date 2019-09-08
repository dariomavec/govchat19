import json
from google.transit import gtfs_realtime_pb2
from google.protobuf import json_format
import urllib.request
from geopy import distance
import ssl

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
