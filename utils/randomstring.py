import random
import argparse

DEF_LEN=12

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description=f"Simple random string generator.\nDefaults: generate {DEF_LEN} alphanumeric characters.")
	parser.add_argument("--number", action="store_true", help="Include numeric characters.")
	parser.add_argument("--upper", action="store_true", help="Include uppercase alphabet characters.")
	parser.add_argument("--lower", action="store_true", help="Include lowercase alphabet characters.")
	parser.add_argument("--min-length", type=int, help="Minimum output length.", default=-1)
	parser.add_argument("--max-length", type=int, help="Maximum output length.", default=-1)
	parser.add_argument("--length", type=int, help="Output length. Takes precedence over range lengths.", default=-1)
	parser.add_argument("--count", type=int, help="Generate this many times strings.", default=1)
	args = parser.parse_args()
	
	# valid count?
	if args.count <= 0: args.count = 1
	
	# check length
	if args.length > 0:
		minlen, maxlen = args.length, args.length
	elif args.length <= 0:
		if args.min_length > 0 and args.max_length > 0 and args.min_length <= args.max_length:
			minlen, maxlen = args.min_length, args.max_length
		else:
			minlen, maxlen = DEF_LEN, DEF_LEN
			
	# check options
	options = []
	if args.number: options.append(0)
	if args.upper: options.append(1)
	if args.lower: options.append(2)
	if len(options) == 0: options.extend((0,1,2))
	
	# charset
	charset = [
		['0','1','2','3','4','5','6','7','8','9'],
		['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'],
		['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']]
	
	# begin generate!
	random.seed()
	for count in range(args.count):
		result = []
		for i in range(random.randint(minlen, maxlen)):
			selcharset = charset[options[random.randrange(0, len(options))]]
			result.append(selcharset[random.randrange(0, len(selcharset))])
		print(''.join(result))
		