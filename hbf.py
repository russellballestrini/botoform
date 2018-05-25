from botoform import build_parser, get_evpc_from_args

parser = build_parser("Example of how to hack your own botoform tools.")
args = parser.parse_args()
evpc = get_evpc_from_args(args)

print(evpc.cidr_block)
