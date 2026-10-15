
    if s6f is not None:   # [s6f] ConvNeXt slot = (1 - A_S6F) * rank(R7) + A_S6F * rank(S6F0) over the studies both scored; a study S6F0 failed on keeps rank(R7)
        _x6f = pct_on(s6f[c].values, ~our_fail & ~s6f_fail)
        ro = np.where(np.isnan(_x6f), ro, (1.0 - A_S6F) * ro + A_S6F * _x6f)
