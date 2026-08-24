# Manual loop bounds for heads the search cannot bound.
# Schema: {function: {head address: (bound, kind, justification)}}
# Addresses are low 32 bits, as in loop_counts.py.

# Longest endpoint receive queue. The kernel does not cap it.
MAX_EP_QUEUE_LEN = 16

loop_bounds = {
    'invokeUntyped_Retype': {
        0x84010658: (32, 'relative', 'inlined memzero store loop, 256/8 stores per entry'),
    },

    # target.py skips the fastpath, so these heads are bounded by hand.

    'fastpath_call': {
        0x840115bc: (64, 'relative', 'lookup_fp: bits += radix+guard, radix >= 1, exits at bits >= 64'),

        0x840117c4: (4, 'relative', 'fastpath_copy_mrs: fastpath_mi_check dominates, length <= 4'),
    },

    'fastpath_reply_recv': {
        0x840119b0: (64, 'relative', 'lookup_fp: bits += radix+guard, radix >= 1, exits at bits >= 64'),
        0x84011a5c: (64, 'relative', 'lookup_fp: bits += radix+guard, radix >= 1, exits at bits >= 64'),

        0x84011c40: (MAX_EP_QUEUE_LEN, 'relative',
                     'tcbEPAppend: walk is bounded by the endpoint receive-queue '
                     'length, a system assumption (MAX_EP_QUEUE_LEN)'),

        0x84011ce0: (4, 'relative', 'fastpath_copy_mrs: fastpath_mi_check dominates, length <= 4'),
    },
}
