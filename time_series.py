"""
Handy time-series plotting interface.

Reads time series data from file and plots along with (optionally) thresholds
and a target curve.
"""
#!/usr/bin/env python

from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
import pandas as pd


def get_target(
    target_start_date, target_gradient, target_start=None, ts=None, thresholds=None
):
    """
    Derive target curve.
    
    Given a start date, gradient and (optionally) and end value, creates a
    time series representing a straight-line target curve. The start value is
    inferred from the original data set (unless given), and the end value
    is chosen to be to lower (higher) than all thresholds if the gradient is
    negative (positive).
    """

    # Choose a starting y-value for target curve
    if target_start is None:
        # Find timestamp in the index nearest to given start date, and use that
        idx = (np.abs(ts.index - target_start_date)).argmin()
        target_start_date = ts.index[idx]
        target_start = ts[target_start_date]

    # The target curve ends when it crossed all thresholds
    if target_gradient > 0:
        target_end = max(thresholds)
    else:
        target_end = min(thresholds)

    target_end_date = target_start_date + timedelta(
        days=((target_end - target_start) / target_gradient)
    )

    target_index = pd.date_range(target_start_date, target_end_date)
    target_value = np.linspace(target_start, target_end, num=len(target_index))
    return pd.Series(target_value, index=target_index)


def work(
    time_series_filename,
    png_filename,
    thresholds,
    threshold_names,
    threshold_colours,
    y_axis_label="Value",
    target_start=None,
    target_start_date=None,
    target_gradient=None,
):
    """
    Workhorse for time series plotting.
    
    Given a datafile, plots time series data and (optionally), multiple
    thresholds, a target curve.
    """

    try:
        ts = pd.read_csv(
            time_series_filename,
            delimiter=";",
            header=None,
            names=["Observations"],
            parse_dates=True,
            index_col=1,
            squeeze=True,
        )
    except:
        print("Could not read data file")
        raise

    # Calculate weekly mean
    ra = ts.rolling(window=7)

    # Calculate running average
    ea = ts.expanding()

    # Calculate 'target' curve
    target = get_target(
        target_start_date, target_gradient, ts=ts, thresholds=thresholds
    )

    # Calculate thresholds
    thresholds_index = [
        min(ts.index[0], target.index[0]),
        max(ts.index[-1], target.index[-1]),
    ]

    # Plot all
    for ithreshold, threshold in enumerate(thresholds):
        plt.plot(
            thresholds_index,
            [threshold, threshold],
            "--",
            color=threshold_colours[ithreshold],
            label=threshold_names[ithreshold],
        )
    ts.plot(style="b.")
    ra.mean().plot(style="b-", label="Rolling weekly average")
    ea.mean().plot(style="b-", label="Running average")
    target.plot(style="--", color="grey")

    plt.legend(fontsize="small", loc="lower left")
    plt.ylabel(y_axis_label)
    plt.xlabel("Date")
    plt.savefig(png_filename, format=None, dpi=200)
