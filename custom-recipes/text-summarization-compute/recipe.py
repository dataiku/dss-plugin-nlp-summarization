# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import os
import sys

import dataiku
from dataiku.customrecipe import (
    get_input_names_for_role, 
    get_output_names_for_role, 
    get_recipe_config,
)

import nltk
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.utils import get_stop_words

# Get the cache directory defined in resources_init and make sure NLTK uses it
# See below for why using NLTK_DATA is not possible
# https://stackoverflow.com/questions/44857382/change-nltk-download-path-directory-from-default-ntlk-data/47082481#47082481
cache_folder = os.getenv("NLTK_HOME")
nltk.data.path.append(cache_folder)



##################################
# Find python version
##################################

PY2 = sys.version_info[0] == 2


##################################
# Input data
##################################

input_dataset = get_input_names_for_role('input_dataset')[0]
df = dataiku.Dataset(input_dataset).get_dataframe()


##################################
# Parameters
##################################

recipe_config = get_recipe_config()

text_column_name = recipe_config.get('text_column_name', None)
if text_column_name is None:
    raise ValueError("You did not choose a text column.")

n_sentences = recipe_config.get('n_sentences', None)
if n_sentences is None:
    raise ValueError("You did not set a number of sentences.")

method = recipe_config.get('method', None)
if method is None:
    raise ValueError("You did not choose a summarization method.")

elif method == "textrank":
    from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer
elif method == "KL":
    from sumy.summarizers.kl import KLSummarizer as Summarizer
elif method == "LSA":
    from sumy.summarizers.lsa import LsaSummarizer as Summarizer


##################################
# Summarization
##################################

LANGUAGE = "english"

def isvalid(text):
    if text is not None and text == text and text != '':
        return True
    else:
        return False

def summarize(text):
    if isvalid(text): 
        all_capital = False
        # to avoid that all capital letter sentence gives empty output: we lower all and the upper all later on
        if text.upper() == text:
            text = text.lower()
            all_capital = True
        
        if PY2:
            parser = PlaintextParser.from_string(text.decode(
                'ascii', errors='ignore'), Tokenizer(LANGUAGE))
        else:
            parser = PlaintextParser.from_string(text.encode().decode(
                'ascii', errors='ignore'), Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)

        sentences = [str(s) for s in summarizer(
            parser.document, sentences_count=n_sentences)]
        
        if all_capital:
            output_sentences = ' '.join(sentences).upper()
            all_capital = False
        else:
            output_sentences = ' '.join(sentences)

        return output_sentences
    else:
        return ''


# Checking for existing columns with same name
new_column_name = text_column_name + "_summary"
if new_column_name in df.columns:
    j = 1
    while new_column_name + "_{}".format(j) in df.columns:
        j += 1
    new_column_name += "_{}".format(j)

# Adding a new column with computed summaries
df[new_column_name] = [summarize(text) for text in df[text_column_name].values]

# Write recipe outputs
output_dataset = get_output_names_for_role('output_dataset')[0]
dataiku.Dataset(output_dataset).write_with_schema(df)
