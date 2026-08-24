#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

import graph_refine.loop_bounds as loop_bounds
import graph_refine.trace_refute as trace_refute
import graph_refine.target_objects as target_objects
from graph_refine.target_objects import functions
import graph_refine.problem as problem
import imm_utils
import sys
import traceback

def isPhantomHead(funs_with_phantom_preempt, f, head):
    return head in funs_with_phantom_preempt.get(f, [])

#extract all loop heads from loops_by_fs
def loopHeadsToWorkOn(lbfs, funs_with_phantom_preempt, worker_ids):
    ret = []
    n_ignored = 0
    for f in lbfs:
        for head in lbfs[f]:
            if (not isPhantomHead(funs_with_phantom_preempt, f, head)) and ("ignore" in lbfs[f][head][1]):
                n_ignored +=1
            elif (-1 in worker_ids) or (lbfs[f][head][2] in worker_ids):
                ret.append(head)
    print 'ignored %d loops' % n_ignored
    print 'working on %s' % str(map(hex,ret))
    return ret

def phantomPreemptsAnnoFileName(target_dir_name):
    return '%s/preempt_refutes.txt' % target_dir_name

def convert_loop_bounds(target_dir_name, worker_ids=None, cached_only=False):
    # deep recursion when hashing big loop bodies. bench.init resets this
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 5000))
    if worker_ids == None:
        worker_ids = set([-1])
    print 'target_dir_name: %s' % target_dir_name
    args = target_objects.load_target(target_dir_name)
    target_dir = target_objects.target_dir
    context = {}
    execfile('%s/loop_counts.py' % target_dir,context)
    assert 'loops_by_fs' in context
    lbfs = context['loops_by_fs']
    context = {}
    execfile('%s/phantom_preempt.py' % target_dir,context)
    funs_with_phantom_preempt = context['functions']
    for f in sorted(funs_with_phantom_preempt):
        v = funs_with_phantom_preempt[f]
        if f not in lbfs:
            print ('WARNING: %s is in phantom_preempt.py but has no loop heads in '
                   'loop_counts.py' % f)
            continue
        assert isinstance(v, list), 'phantom_preempt.py entries must be head lists: %s' % f
        for head in v:
            if head not in lbfs[f]:
                print ('WARNING: phantom_preempt.py lists %s head %s, which is '
                       'not a loop head' % (f, hex(head)))
    # only the full pass writes this
    preempt_annotations_file = None
    if funs_with_phantom_preempt and (-1 in worker_ids):
        preempt_annotations_file = open(phantomPreemptsAnnoFileName(target_dir), 'w')
    #print 'funs_with_phantom_preempt: %s' % str(funs_with_phantom_preempt)
    bin_heads = loopHeadsToWorkOn(lbfs, funs_with_phantom_preempt, worker_ids)
    funs_with_unbounded_loop = set()
    #all_loop_heads = loop_bounds.get_all_loop_heads()
    print 'bin_heads: ' + str(bin_heads)
    for head in bin_heads:
        f = trace_refute.get_body_addrs_fun(head)
        if f not in lbfs:
            lbfs[f] = {}
        ret= None
        # downgraded to 'incomplete' wherever the search gave up early
        failure = 'refuted'
        if isPhantomHead(funs_with_phantom_preempt, f, head):
             # the ILP preemption limit is the real bound
             ret = (10 ** 9, 'phantom_preempt')
             if preempt_annotations_file:
                 preempt_annotations_file.write("#" + f + "\n")
                 preempt_annotations_file.write("[%s]:phantom_preemp_point\n\n" % hex(head))

             print '%s injected with phantom preemption point' % f
        else:
            try:
                ret = loop_bounds.get_bound_super_ctxt(head,[],
                    known_bound_only = cached_only)
            except problem.Abort, e:
                failure = 'incomplete'
                print 'failed to analyse %s, problem aborted' % f
            except AssertionError, e:
                # uncuttable fused cycle, record the head as failed
                failure = 'incomplete'
                traceback.print_exc()
                print 'failed to analyse %s, assertion failure: %s' % (f, e)
            except:
                print "Unexpected error:", sys.exc_info()
                raise
        old_worker = lbfs[f][head][2]
        if ret == None or ret[1]== 'None':
            if cached_only:
                comment = 'did not find cached result'
            else:
                comment = 'ignore: %s' % failure
            lbfs[f][head] = (2**30, comment, old_worker)
            funs_with_unbounded_loop.add((f, head))
        else:
            lbfs[f][head] = (ret[0],ret[1], old_worker)
        imm_utils.genLoopheads(lbfs, target_objects.target_dir, incremental_head=(f,head))
    if preempt_annotations_file:
        preempt_annotations_file.close()
    unex_unbounded_funcs = set([(f, head) for (f, head) in funs_with_unbounded_loop
                                 if not isPhantomHead(funs_with_phantom_preempt, f, head)])
    if unex_unbounded_funcs:
        by_verdict = {}
        for (f, head) in unex_unbounded_funcs:
            desc = lbfs[f][head][1]
            verdict = desc.split(': ', 1)[1] if ': ' in desc else desc
            by_verdict.setdefault(verdict, []).append((f, head))
        print 'functions with unbounded loop and not bounded by preemption, by verdict:'
        for verdict in sorted(by_verdict):
            print '  %s: %s' % (verdict,
                ', '.join('%s@%s' % (f, hex(head))
                          for (f, head) in sorted(by_verdict[verdict])))
        # failing a worker would abort the others
        if -1 in worker_ids:
            return None
    if -1 in worker_ids:
        still_ignored = [(f, head) for f in lbfs for head in lbfs[f]
                         if 'ignore' in lbfs[f][head][1]
                         and not isPhantomHead(funs_with_phantom_preempt, f, head)]
        if still_ignored:
            print ('loops still marked ignore in loop_counts.py '
                   '(need entries in assumed_loop_bounds.py): %s'
                   % ', '.join('%s@%s' % (f, hex(head))
                                for (f, head) in sorted(still_ignored)))
    return lbfs

if __name__== '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("target_dir_name")
    parser.add_argument('--worker_id', type=int, help="what bound marker is this instance responsible for, -1 means everything", default= -1)
    parser.add_argument('--worker_ids', type=str, help="multiple worker IDs, e.g. 1,2,3", default= None)
    parser.add_argument('--cached_only', type=bool, default=False, help="Only read what's cached in LoopBounds.txt")
    args = parser.parse_args()
    worker_ids = set ([args.worker_id])
    if args.worker_ids != None:
      ids = args.worker_ids.split(",")
      try:
        worker_ids = set(map(int,ids))
      except ValueError, e:
        print "Worker IDs not numeric: %s" % ids
        sys.exit(-1)
    target_dir_name = args.target_dir_name
    print "I am workers %s" % sorted(worker_ids)
    lbfs = convert_loop_bounds(target_dir_name, worker_ids, cached_only = args.cached_only)
    if lbfs is None:
        sys.exit(-1)

