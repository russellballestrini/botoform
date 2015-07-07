import argparse

from botoform.evpc import EnrichedVPC

def base_parser(description):
    """base parser that all subcommands seem to need."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-p', '--profile', default=None,
      help='botocore profile name for AWS creds and other vars.')
    parser.add_argument('-r', '--region', default=None,
      help='AWS region to use')
    #parser.add_argument('--search-regions', action='store_true', default=False,
    #  help='search regions for VPC with given vpc_name')
    parser.add_argument('--quiet', action='store_true', default=False,
      help='prevent status messages to STDOUT')
    parser.add_argument('vpc_name')
    return parser

def main():
    parser = base_parser('taco')
    args = parser.parse_args()

    evpc = EnrichedVPC(
             vpc_name=args.vpc_name,
             profile_name=args.profile,
             region_name=args.region
           )
    print(evpc.tag_dict['Name'])

if __name__ == '__main__':
    main()
