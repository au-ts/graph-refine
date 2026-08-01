# Functions whose loops are bounded by preemption.
# True marks every loop head, a list marks just those heads.
# Only the first group has real preemptionPoint() calls.

functions = {
    'cteRevoke':                True,
    'cteDelete':                True,
    'finaliseSlot':             True,
    'invokeUntyped_Retype':     [0x8401064c],
    'cancelAllIPC':             True,
    'cancelAllSignals':         True,
    'cancelBadgedSends':        True,
    'refill_budget_check_loop': True,
    'ensure_sufficient_head':   True,
    'refill_unblock_check':     True,
    'awaken':                   True,
    'tcbReleaseEnqueue':        True,
    'reorderEP':                True,
    'reorderNTFN':              True,
    'sendIPC':                  True,
    'receiveIPC':               True,
    'receiveSignal':            True,
}
