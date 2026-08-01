# Manual loop bounds for heads the search cannot bound.
# Schema: {function: {head address: (bound, kind, justification)}}
# Addresses are low 32 bits, as in loop_counts.py.

loop_bounds = {
    'invokeUntyped_Retype': {
        0x84010658: (32, 'relative', 'inlined memzero store loop, 256/8 stores per entry'),
    },
}
