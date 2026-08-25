# Manual loop bounds for heads the search cannot bound.
# Schema: {function: {head address: (bound, kind, justification)}}
# Addresses are low 32 bits, as in loop_counts.py.

# System limits the WCET bounds depend on.

N_EP = 16

N_RQ = 16

B_SC = 8

N_REFILL = ((1 << B_SC) - 88) // 16

# ceil(usage_max / MIN_BUDGET)
N_BUDGET_REFILLS = 8

assert N_EP >= 1 and N_RQ >= 1
assert B_SC >= 8, "below seL4_MinSchedContextBits no sched context can exist"
assert N_REFILL >= 2, "refill_absolute_max(B_SC) must admit a non-degenerate ring"
assert N_BUDGET_REFILLS >= 1

loop_bounds = {
    'invokeUntyped_Retype': {
        0x84010658: (32, 'relative', 'inlined memzero store loop, 256/8 stores per entry'),
    },

    'fastpath_call': {
        0x840115bc: (64, 'relative', 'lookup_fp: bits += radix+guard, radix >= 1, exits at bits >= 64'),

        0x840117c4: (4, 'relative', 'fastpath_copy_mrs: fastpath_mi_check dominates, length <= 4'),
    },

    'fastpath_reply_recv': {
        0x840119b0: (64, 'relative', 'lookup_fp: bits += radix+guard, radix >= 1, exits at bits >= 64'),
        0x84011a5c: (64, 'relative', 'lookup_fp: bits += radix+guard, radix >= 1, exits at bits >= 64'),

        0x84011c40: (N_EP, 'relative',
                     'tcbEPAppend: walk is bounded by the endpoint receive-queue '
                     'length, a system assumption (N_EP)'),

        0x84011ce0: (4, 'relative', 'fastpath_copy_mrs: fastpath_mi_check dominates, length <= 4'),
    },

    'sendIPC': {
        0x8400c1c4: (N_EP, 'relative',
                     'tcbEPAppend on the endpoint send queue; bounded by the '
                     'queue length only (N_EP)'),
    },
    'receiveIPC': {
        0x8400dec8: (N_EP, 'relative',
                     'tcbEPAppend on the endpoint receive queue; bounded by the '
                     'queue length only (N_EP)'),
    },
    'receiveSignal': {
        0x8400b4e4: (N_EP, 'relative',
                     'tcbEPAppend on the notification queue; bounded by the '
                     'queue length only (N_EP)'),
    },

    'reorderEP': {
        0x84005fd4: (N_EP, 'relative',
                     'tcbEPAppend re-insertion walk after a priority change; '
                     'bounded by the endpoint queue length only (N_EP)'),
    },
    'reorderNTFN': {
        0x84006340: (N_EP, 'relative',
                     'tcbEPAppend re-insertion walk after a priority change; '
                     'bounded by the notification queue length only (N_EP)'),
    },

    'cancelAllIPC': {
        0x84008b10: (N_EP, 'relative',
                     'restarts every TCB on the endpoint queue: one iteration '
                     'per queued receiver/sender (N_EP)'),
    },
    'cancelAllSignals': {
        0x84008c28: (N_EP, 'relative',
                     'restarts every TCB on the notification queue: one '
                     'iteration per queued waiter (N_EP)'),
    },

    'cancelBadgedSends': {
        0x84008d18: (N_EP, 'relative',
                     'walks the whole endpoint send queue filtering on badge: '
                     'one iteration per queued sender (N_EP)'),
    },

    'awaken': {
        0x84008f14: (N_RQ, 'relative',
                     'tcbReleaseDequeue pops one entry per iteration, so at '
                     'most the release-queue length (N_RQ)'),
    },

    'tcbReleaseEnqueue': {
        0x8400a718: (N_RQ, 'relative',
                     'ordered insert walks the earlier entries of the release '
                     'queue; bounded by its length only (N_RQ)'),
    },

    'ensure_sufficient_head': {
        0x840033f0: (N_REFILL - 1, 'relative',
                     'pops one refill per iteration and stops with at least '
                     'one left: at most refill_absolute_max(B_SC) - 1'),
    },

    'refill_unblock_check': {
        0x84005674: (N_REFILL - 1, 'relative',
                     'merges overlapping refills, popping one per iteration '
                     'and stopping at a single refill: at most '
                     'refill_absolute_max(B_SC) - 1'),
    },

    'refill_budget_check_loop': {
        0x8400348c: (N_BUDGET_REFILLS, 'relative',
                     'usage falls by at least MIN_BUDGET per iteration: '
                     'ceil(usage_max / MIN_BUDGET) = N_BUDGET_REFILLS'),
    },
}
