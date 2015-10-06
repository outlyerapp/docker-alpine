#!/usr/bin/env python
import requests
import uuid
from time import sleep
import sys,getopt

API_KEY = ''  # You need to set this!
API = 'https://www.dataloop.io'
CADVISOR = 'http://127.0.0.1:8080'  # CAdvisor container URL. Change this if on Linux.
DEFAULT_TAGS = ['docker']

# Don't touch anything below this point. In fact don't even scroll down.


def api_header():
    return {"Content-type": "application/json", "Authorization": "Bearer " + API_KEY}


def get_mac():
    return str(uuid.getnode())


def add_tags(fingerprint, tag_list):
    data = {'names': ','.join(tag_list)}
    print 'Adding tags: %s to %s' % (','.join(tag_list), fingerprint)
    try:
        requests.put(API + "/api/agents/" + fingerprint + "/tags",
                            json=data,
                            headers=api_header())
    except Exception as E:
        print 'Failed to add tags: %s' % E
        return False


def get_agent_tags():
    # only get agents from dataloop that match the mac address of dl-dac container
    _resp = requests.get(API + "/api/agents", headers=api_header())
    _agents = {}
    if _resp.status_code == 200:
        for l in _resp.json():
            if l['mac'] == get_mac():
                name = l['name']
                _agents[name] = {}
                _agents[name]['finger'] = l['id']
                _agents[name]['tags'] = l['tags']
    return _agents


def get_container_tags():
    _containers = {}
    try:
        _resp = requests.get(CADVISOR + '/api/v1.3/docker').json()
    except Exception as E:
        print "Failed to query containers: %s" % E
        return False
    for k, v in _resp.iteritems():
        _tags = []
        _name = (v['name'].replace('/docker/', ''))
        for alias in v['aliases']:
            if alias != _name:
                _tags.append(alias)
        _containers[_name[:12]] = _tags
    return _containers


def main(argv):
    global API_KEY, CADVISOR

    try:
       opts, args = getopt.getopt(argv,"ha:c::",["apikey=","cadvisor="])
    except getopt.GetoptError:
       print 'metrics.py -a <apikey> -c <cadvisor address:port>'
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print 'metrics.py -a <apikey> -c <cadvisor address:port>'
          sys.exit()
       elif opt in ("-a", "--apikey"):
          API_KEY = arg
       elif opt in ("-c", "--cadvisor"):
          CADVISOR = arg
    print 'apikey is "', API_KEY , '"'
    print 'cadvisor endpoint is "', CADVISOR, '"'

    print "Container Tag running. Press ctrl+c to exit!"
    while True:
        agent_tags = get_agent_tags()
        # print "agent tags: %s" % agent_tags

        container_tags = get_container_tags()
        # print "container tags: %s" % container_tags

        # # merge tags
        tags = {}
        for agent,detail in agent_tags.iteritems():
            # combine lists
            all_tags = container_tags[agent] + detail['tags'] + DEFAULT_TAGS
        # print "all tags: ", list(set(all_tags)) #dedupe
            diff = list(set(all_tags) - set(detail['tags']))
        tags[agent] = diff

        # push up tags
        for agent, tag_list in tags.iteritems():
            if len(tag_list) > 0:
                add_tags(agent_tags[agent]['finger'], tag_list)


        sleep(5)    #  sleepy time


if __name__ == "__main__":
    main(sys.argv[1:])
