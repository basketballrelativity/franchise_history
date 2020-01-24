#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 22:22:37 2018

@author: patrickmcfarlane

franchise_history.py is a script that
analyzes and visualizes data related to
basketball franchises across the ABA, NBA,
and WNBA.
"""

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

from py_ball import league, image

HEADERS = {'Connection': 'close',
           'Host': 'stats.nba.com',
           'Origin': 'http://stats.nba.com',
           'Upgrade-Insecure-Requests': '1',
           'Referer': 'stats.nba.com',
           'x-nba-stats-origin': 'stats',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2)' + \
                         'AppleWebKit/537.36 (KHTML, like Gecko) ' + \
                         'Chrome/66.0.3359.117 Safari/537.36'}

def add_logo(fig, logo, x_frac, y_frac):
    """ This function adds a logo to the provided figure

    Args:

        @param **fig** (matplotlib.figure.Figure): Figure object of franchise
            history barchart

        @param **logo** (PngImageFile): PNG image object of logo corresponding
            to a basketball franchise

        @param **x_frac** (float): Value corresponding to the horizontal position
            at which the image is to be initiated

        @param **y_frac** (float): Value corresponding to the vertical position
            at which the image is to be initiated

    Returns:

        **fig** (matplotlib.figure.Figure): Figure object of franchise
            history barchart with the corresponding logo added
    """

    logo.thumbnail((32, 32), Image.ANTIALIAS)
    logo = logo.rotate(180)
    logo = logo.transpose(Image.FLIP_LEFT_RIGHT)
    img_x, img_y = logo.size[0], logo.size[1]
    x_offset = int((fig.bbox.xmax * x_frac - img_x/2))
    y_offset = int((fig.bbox.ymax * y_frac - img_y/2))
    fig.figimage(logo, origin={'lower'},
                 xo=x_offset, yo=y_offset, zorder=10)

    return fig

def add_franchise_changes(fig, years, ind):
    """ This function adds dashed vertical lines when
    the franchise underwent a change (name/city change)

    Args:

        @param **fig** (matplotlib.figure.Figure): Figure object of franchise
            history barchart

        @param **years** (list): List of integers corresponing to years in
            which a franchise change took place

        @param **ind** (float): Value of the vertical location of the bar
            on the barchar

    Returns:

        **fig** (matplotlib.figure.Figure): Figure object of franchise
            history barchart with the franchise changes added
    """

    for year in years:
        plt.plot([year, year], [ind - 0.4, ind + 0.4], 'k--')

    return fig

def plot_franchise_timeline(franchise_df, franchise_ind, league_id):
    """ This function plots the timeline of all franchises
    provided in franchise_df

    Args:

        @param **franchise_df** (pandas.DataFrame): DataFrame of franchise
            metadata, including start and end years

        @param **franchise_ind** (pandas.Series): Series of boolean values
            corresponding to indices in **franchise_df** that correspond
            to a franchise's full history

        @param **league_id** (str): String of a unique league identifier. '00'
            corresponds to the NBA and '10' corresponds to the WNBA

    Returns:

        **fig** (matplotlib.figure.Figure): Figure object of franchise
            history barchart
    """

    franchise_df['YEARS'] = pd.to_numeric(franchise_df['YEARS'])
    franchise_df['START_YEAR'] = pd.to_numeric(franchise_df['START_YEAR'])
    franchise_df['END_YEAR'] = pd.to_numeric(franchise_df['END_YEAR'])

    franchise_df['YEARS'] = franchise_df['END_YEAR'] - \
        franchise_df['START_YEAR']

    unique_franchise_df = franchise_df[franchise_ind]
    unique_franchise_df = unique_franchise_df.sort_values(by='YEARS',
                                                          ascending=True)

    if league_id == '10':
        fig = plt.figure(figsize=(6, 9))
    elif league_id == '00':
        fig = plt.figure(figsize=(6, 12))

    axis = fig.add_axes([0., 0., 0.8, 1., ])

    axis.barh(bottom=range(0, len(unique_franchise_df)),
              width=unique_franchise_df['YEARS'],
              left=unique_franchise_df['START_YEAR'], height=0.5,
              color='grey')

    start_year = min(unique_franchise_df['START_YEAR'])
    end_year = max(unique_franchise_df['END_YEAR'])

    plt.xticks(range(start_year,
                     end_year + 1,
                     int(round((end_year - start_year)/10.0) + 1)),
               rotation=30)

    plt.yticks(range(0, len(unique_franchise_df)),
               unique_franchise_df['TEAM_FULL'],
               rotation=30)

    if league_id == '10':
        horiz_frac = 1
        vertical_frac = 0.12
        increment = 0.08
        league_str = 'WNBA'
        axis.set_xlim(start_year,
                      end_year+4)
    elif league_id == '00':
        horiz_frac = 1
        vertical_frac = 0.09
        increment = 0.031
        league_str = 'NBA'
        axis.set_xlim(start_year,
                      end_year+18)

    ind = 0
    for team_id in unique_franchise_df['TEAM_ID']:
        test_logo = image.Logo(league=league_str,
                               team_id=str(team_id)).image
        fig = add_logo(fig, test_logo, horiz_frac, vertical_frac)
        years_df = \
            franchise_df[franchise_df['TEAM_ID'] == \
                         team_id].sort_values(by='START_YEAR',
                                              ascending=False)
        years = sorted(list(set(years_df['START_YEAR'])))
        fig = add_franchise_changes(fig, years[1:], ind)
        vertical_frac += increment
        ind += 1

    plt.show()

    return fig


def franchise_timeline(league_id):
    """ This function plots the timeline of all franchises in
    the league provided.

    Args:

        @param **league_id** (str): String of a unique league identifier. '00'
            corresponds to the NBA and '10' corresponds to the WNBA

    Returns:

        **fig** (matplotlib.figure.Figure): Figure object of franchise
            history barchart
    """

    franchises = league.League(headers=HEADERS,
                               endpoint='franchisehistory',
                               league_id=league_id)

    franchise_df = pd.DataFrame(franchises.data['FranchiseHistory'])
    franchise_df['TEAM_FULL'] = franchise_df['TEAM_CITY'] + ' ' + \
                                franchise_df['TEAM_NAME']

    franchise_ind = \
        franchise_df.groupby(['TEAM_ID'],
                             sort=False)['YEARS'].transform(max) == \
                   franchise_df['YEARS']

    franchise_fig = plot_franchise_timeline(franchise_df,
                                            franchise_ind,
                                            league_id)

    return franchise_fig
