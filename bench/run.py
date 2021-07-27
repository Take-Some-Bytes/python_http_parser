"""Run benchmarks OR the python profiler."""

import argparse

import mod
import mod.bench
import mod.profile

argparser = argparse.ArgumentParser(
    description='Run project benchmarks or profile the HTTPParser.'
)
argparser.add_argument(
    '-t', '--type', default='bench', choices=['bench', 'profile'],
    help="""\
Specify what to run. Could either be 'bench' or 'profile'.
'bench' runs the benchmarks, and 'profile' profiles the
code. Default 'bench'.
"""
)
argparser.add_argument(
    '-i', '--id', default='0', choices=['0', '1', '2'],
    help="""\
Specify the request or response ID to benchmark or profile with. Default 0.
'0' is normal length, '1' is long, and '2' is short.
"""
)
argparser.add_argument(
    '-m', '--mode', default='both', choices=['req', 'res', 'both'],
    help="""\
Whether to run with in 'req' mode, 'res' mode, or run 'both'. Default 'both'.
"""
)

args = argparser.parse_args()
args.id = int(args.id)

if args.type == 'bench':
    req = False
    res = False
    if args.mode == 'both':
        req = True
        res = True
    elif args.mode == 'req':
        req = True
    elif args.mode == 'res':
        res = True

    mod.bench.run(req, res, args.id, args.id)
elif args.type == 'profile':
    req = False
    res = False
    if args.mode == 'both':
        req = True
        res = True
    elif args.mode == 'req':
        req = True
    elif args.mode == 'res':
        res = True

    mod.profile.run(req, res, args.id, args.id)
