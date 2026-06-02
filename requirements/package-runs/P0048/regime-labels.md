# P0048 regime labels

thresholds = {'near_zero_abs': 0.05, 'positive': 0.201919, 'negative': -0.201919, 'spike_positive': 0.807675, 'spike_negative': -0.807675}

class_balance = {'binary_positive_bottleneck': {'counts': {'0': 23134, '1': 11834}, 'share': {'0': 0.6615762983299016, '1': 0.3384237016700984}}, 'binary_positive_spike': {'counts': {'0': 31423, '1': 3545}, 'share': {'0': 0.8986215968885839, '1': 0.10137840311141615}}, 'multiclass_regime': {'counts': {'near_zero': 19716, 'negative_or_spike_negative': 37, 'positive': 8289, 'small_nonzero': 3381, 'spike_positive': 3545}, 'share': {'near_zero': 0.5638297872340425, 'negative_or_spike_negative': 0.0010581102722489132, 'positive': 0.23704529855868223, 'small_nonzero': 0.09668840082361016, 'spike_positive': 0.10137840311141615}}}

Negative and negative-spike regimes are merged into `negative_or_spike_negative` for multiclass modeling because P0047/P0048 counts are sparse.
