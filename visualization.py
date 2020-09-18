#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visualization and plotting
"""

import copy
import emoji
import json
import pandas as pd
import plotly.graph_objects as go

from pathlib import Path

import defs
import ipdb


def get_flags_from_demonyms(country_demonyms):
    country_demonyms_lookup = json.load(open(Path('data/lookup_countries_demonyms.json'), 'r'))[0]
    flags = []
    for demonym in country_demonyms:
        try:
            country = country_demonyms_lookup[demonym].replace(' ', '_')
            flag = emoji.emojize(f':{country}:', use_aliases=True)
            if flag == f':{country}:':
                flag = emoji.emojize(f':flag_for_{country}:', use_aliases=True)
            flags.append(flag)
        except KeyError:
            flags.append(f"{demonym}")
            print(f"Error getting flag for {demonym}")

    return flags


def get_languages_names(language_prefixes):
    lang_lookup = json.load(open(Path('data/lookup_languages.json'), 'r'))
    lang_lookup_dict = {kk['code']: kk['name'] for kk in lang_lookup}
    language_names = []
    for lang in language_prefixes:
        try:
            language_names.append(f"{lang_lookup_dict[lang]}")
        except KeyError:
            language_names.append(f"{lang}")

    return language_names


def step5_plot_table(df):
    df = df.transpose()

    if defs.Y_REPLACE_LANGUAGES_ABBREVIATIONS:
        # Replace language abbreviation with language name and sort the DataFrame
        languages = df.index.to_list()
        renaming_map = {lang: name for lang, name in zip(languages, get_languages_names(languages))}
        df.rename(index=renaming_map, inplace=True)
        df.sort_index(ascending=False, inplace=True)

    rows = []
    for idx, row in df.iterrows():
        rows.append(row.to_list())
    xlabels = df.columns.to_list()
    ylabels = df.index.to_list()

    # yapf: disable
    colorscale=[[0, "rgb(178, 233, 201)"],
                [0.1, "rgb(91, 207, 139)"],
                [0.2, "rgb(69, 201, 123)"],
                [0.3, "rgb(48, 164, 96)"],
                [0.4, "rgb(35, 121, 70)"],
                [0.5, "rgb(29, 99, 58)"],
                [0.6, "rgb(22, 77, 45)"],
                [0.7, "rgb(16, 55, 32)"],
                [0.8, "rgb(10, 33, 19)"],
                [0.9, "rgb(10, 33, 19)"],
                [1.0, "rgb(10, 33, 19)"]]
    # yapf: enable

    colorbar = dict(tick0=defs.THRESHOLD_MIN_VOICE_LENGTH, dtick=40000)

    # xlabel handle exceptions
    replacements = {"Bosnia and Herzegovina": "Bosnian", "Kazakh": "Kazakhstani", "Nepalese": "Nepali"}
    new_xlabels = copy.deepcopy(xlabels)
    for idx, el in enumerate(xlabels):
        if el in replacements:
            new_xlabels[idx] = replacements[el]
    xlabels = new_xlabels

    if defs.Y_ADD_LANGUAGE:
        ylabels = [f"{kk} language" for kk in ylabels]
    if defs.X_ADD_FLAGS:
        flags = get_flags_from_demonyms(xlabels)
        new_xlabels = []
        for nationality, flag in zip(xlabels, flags):
            if nationality != flag:
                new_xlabels.append(f"{flag} {nationality}")
            else:
                new_xlabels.append(f"{flag}")
        xlabels = new_xlabels
    if defs.X_ADD_CUISINE:
        xlabels = [f"{kk} cuisine" for kk in xlabels]

    fig = go.Figure(
        data=go.Heatmap(x=xlabels,
                        y=ylabels,
                        z=rows,
                        zmin=38,
                        colorscale=colorscale,
                        colorbar=colorbar,
                        hovertemplate="Cuisine: %{x}<br>Wikipedia language: %{y}<br>Voice length: %{z}<extra></extra>"))

    # yapf: disable
    fig.update_layout(xaxis={'side': 'top',
                             'tickangle': -60,
                             'tickfont': {'size': 14}},
                      yaxis={'side': 'left',
                             'tickfont': {'size': 14}},
                      xaxis_showgrid=False,
                      yaxis_showgrid=False,
                      margin={'l': 120, 'r': 20, 't': 120, 'b': 20},
                      annotations=[{'x': 0.5,
                                    'y': 1.15,
                                    'showarrow': False,
                                    'text': 'CUISINES',
                                    'font': {'size': defs.AXIS_ANNOTATION_TEXT_SIZE},
                                    'xref': 'paper',
                                    'yref': 'paper'},
                                   {'x': -0.07,
                                    'y': 0.5,
                                    'showarrow': False,
                                    'text': 'LANGUAGES',
                                    'font': {'size': defs.AXIS_ANNOTATION_TEXT_SIZE},
                                    'textangle': -90,
                                    'xref': 'paper',
                                    'yref': 'paper'}])
    # yapf: enable

    fig.show()
    ipdb.set_trace()