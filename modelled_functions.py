#
# SPDX-License-Identifier: BSD-2-Clause
#

# List the functions trace_refute can model: those with a pairing and with
# instructions of their own in the decompiled graph. An address in any other
# function must not reach trace_refute.

# usage: python2 modelled_functions.py <target_dir> <output>

import sys

import target_objects
import trace_refute

if __name__ == '__main__':
    if len (sys.argv) != 3:
        print 'Usage: modelled_functions.py <target_dir> <output>'
        sys.exit (1)
    [_, target_dir, out] = sys.argv
    target_objects.load_target (target_dir)
    from target_objects import pairings

    trace_refute.setup_body_addrs ()
    fns = sorted (f for f in trace_refute.fun_addrs_counts if f in pairings)
    f = open (out, 'w')
    f.write ('\n'.join (fns) + '\n')
    f.close ()
    print 'wrote %d function(s) to %s' % (len (fns), out)
