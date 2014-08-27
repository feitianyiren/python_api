import sys
import json
from argparse import ArgumentParser

from riskiq.api import Client
from riskiq.config import Config
from riskiq.render import renderer

FILTERS = ('blackhole', 'sakura', 'exploitKit')
CONFIDENCES = ('H', 'M', 'L')

def bl_lookup(client, url, oneline=False, short=False, as_json=False):
    data = client.get_blacklist_lookup(url)
    if as_json:
        print(json.dumps(data, indent=4))
    else:
        print(renderer(data, 'blacklist/lookup'))

def bl_incident(client, url, oneline=False, short=False, as_json=False):
    data = client.get_blacklist_incident(url)
    if as_json:
        print(json.dumps(data, indent=4))
    else:
        print(renderer(data, 'blacklist/incident'))

def bl_incidentlist(client, oneline=False, short=False, as_json=False,
    **kwargs):
    data = client.get_blacklist_incident_list(**kwargs)
    if as_json:
        print(json.dumps(data, indent=4))
    else:
        print(renderer(data, 'blacklist/incident'))

def bl_list(client, bl_filter=None, oneline=False, short=False, as_json=False,
    **kwargs):
    if bl_filter not in (None, ) + FILTERS:
        raise ValueError('Invalid filter. Must be one of %s' % str(FILTERS))
    data = client.get_blacklist_list(blacklist_filter=bl_filter, **kwargs)
    if as_json:
        print(json.dumps(data, indent=4))

def bl_malware(client, oneline=False, short=False, as_json=False,
    bl_filter=None, confidence=None, **kwargs):
    if bl_filter not in (None, ) + FILTERS:
        raise ValueError('Invalid filter.\nMust be one of %s' % str(FILTERS))
    if confidence not in (None, ) + CONFIDENCES:
        raise ValueError('Invalid confidence.\n'
            'Must be one of %s' % str(CONFIDENCES))
    data = client.get_blacklist_malware(blacklist_filter=bl_filter,
        confidence=confidence, **kwargs)
    if as_json:
        print(json.dumps(data, indent=4))

def main():
    parser = ArgumentParser()
    parser.add_argument('-l', '--oneline', action="store_true",
        help="Output one line per entry")
    parser.add_argument('-s', '--short', action="store_true",
        help="Output in short format (print matching input indicator only)")
    parser.add_argument('-j', '--json', action="store_true", dest='as_json',
        help="Output as JSON")

    subs = parser.add_subparsers(dest='cmd')

    lookup_parser = subs.add_parser('lookup', help='Query blacklist on URL')
    lookup_parser.add_argument('url')

    incident_parser = subs.add_parser('incident', help='Query blacklist incident '
        'on URL')
    incident_parser.add_argument('url')

    incident_list_parser = subs.add_parser('incidentlist',
        help='query blacklist incidents within timeframe')
    incident_list_parser.add_argument('--all-workspace-crawls', '-a',
        action='store_true', help='Filter crawls to those on workspace')
    incident_list_parser.add_argument('--days', '-d', default=1, type=int,
        help='days to query')
    incident_list_parser.add_argument('--start', '-s', default=None,
        help='start datetime in yyyy-mm-dd HH:MM:SS format')
    incident_list_parser.add_argument('--end', '-e', default=None,
        help='end datetime in yyyy-mm-dd HH:MM:SS format')

    list_parser = subs.add_parser('list', help = 'query blacklisted resources')
    list_parser.add_argument('--filter', '-f', default=None,
        help='Filter to one of "blackhole", "sakura" or "exploitKit"')
    list_parser.add_argument('--days', '-d', default=1, type=int,
        help='days to query')
    list_parser.add_argument('--start', '-s', default=None,
        help='start datetime in yyyy-mm-dd HH:MM:SS format')
    list_parser.add_argument('--end', '-e', default=None,
        help='end datetime in yyyy-mm-dd HH:MM:SS format')

    malware_parser = subs.add_parser('malware',
        help='Query for all discovered malware resources generated within a '
            'particular period.')
    malware_parser.add_argument('--filter', '-f', default=None,
        help='Filter to one of "blackhole", "sakura" or "exploitKit"')
    malware_parser.add_argument('--confidence', '-c', default=None,
        help='Restrict results to malicious probability of H, M, or L\n'
            '(high, medium or low)')
    malware_parser.add_argument('--days', '-d', default=1, type=int,
        help='days to query')
    malware_parser.add_argument('--start', '-s', default=None,
        help='start datetime in yyyy-mm-dd HH:MM:SS format')
    malware_parser.add_argument('--end', '-e', default=None,
        help='end datetime in yyyy-mm-dd HH:MM:SS format')

    args = parser.parse_args()
    config = Config()
    client = Client(token=config.get('api_token'), key=config.get('api_private_key'),
                    server=config.get('api_server'), version=config.get('api_version'))

    kwargs = {'as_json': args.as_json, 'oneline': args.oneline, 
        'short': args.short}
    if hasattr(args, 'days'):
        kwargs['days'] = args.days
        kwargs['start'] = args.start
        kwargs['end'] = args.end
    if args.cmd == 'lookup':
        bl_lookup(client, args.url, **kwargs)
    elif args.cmd == 'incidentlist':
        bl_incidentlist(client, all_workspace_crawls=args.all_workspace_crawls,
            **kwargs)
    elif args.cmd == 'incident':
        bl_incident(client, args.url, **kwargs)
    elif args.cmd == 'list':
        try:
            bl_list(client, bl_filter=args.filter, **kwargs)
        except ValueError as e:
            print(args.usage())
            print(str(e))
            sys.exit(1)
    elif args.cmd == 'malware':
        try:
            bl_malware(client, bl_filter=args.filter,
                confidence=args.confidence, **kwargs)
        except ValueError as e:
            print(args.usage())
            print(str(e))
            sys.exit(1)

if __name__ == '__main__':
    main()
