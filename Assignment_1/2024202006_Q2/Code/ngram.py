# ngram.py

import re
from collections import defaultdict
import math

class NgramCharacterModel:
    def __init__(self, corpus, n=3):

        self.n = n
        self.ngram_counts = defaultdict(int)
        self.prefix_counts = defaultdict(int)
        self.words = set()
        
        self._train(corpus)

    def _train(self, corpus):
        """
        Train the n-gram model by populating self.ngram_counts and self.prefix_counts.
        We also store all distinct words in self.words for prefix matching later.
        """
        # Simple splitting into words (you can refine this if you want)
        tokens = corpus.split()

        for word in tokens:
            # store the word for later prefix-based lookups
            self.words.add(word)
            
            # Pad the word with (n-1) start symbols (#) and an end symbol ($)
            # e.g. for n=2 (bigram): "#word$"
            #      for n=3 (trigram): "##word$"
            padded_word = ("#" * (self.n - 1)) + word + "$"

            # Slide over each n-gram in the padded word
            for i in range(len(padded_word) - self.n + 1):
                ngram = padded_word[i : i + self.n]     # e.g. "#w", "wo", ...
                prefix = ngram[:-1]                     # e.g. "#" for bigram, "##" for trigram, etc.
                
                self.ngram_counts[ngram] += 1
                self.prefix_counts[prefix] += 1

    def _word_probability(self, word):
        """
        Compute the probability of an entire word using the character-level n-gram model.
        P(word) = product of P(each character | its (n-1)-character prefix)
        """
        # Pad the word similarly as in training
        padded_word = ("#" * (self.n - 1)) + word + "$"

        log_prob = 0.0  # we'll use log probabilities to avoid underflow
        for i in range(len(padded_word) - self.n + 1):
            ngram = padded_word[i : i + self.n]
            prefix = ngram[:-1]
            count_ngram = self.ngram_counts[ngram]
            count_prefix = self.prefix_counts[prefix]

            if count_prefix == 0:
                # If prefix wasn't seen, probability is extremely low.
                # You could also add smoothing here if you like.
                return 0.0
            else:
                # P(next_char | prefix) = count(ngram) / count(prefix)
                prob = count_ngram / count_prefix
                # accumulate log(prob)
                log_prob += math.log(prob)

        return math.exp(log_prob)  # return normal probability

    def _generate_word(self, prefix):
        """
        Returns a single 'best guess' word from the training corpus that starts with `prefix`.
        Uses the n-gram probability to pick the best match among known words.
        """
        # Filter words that start with the given prefix
        candidates = [w for w in self.words if w.startswith(prefix)]
        if not candidates:
            return prefix  # if no known word starts with prefix, just return the prefix as-is

        # Pick the candidate with the highest n-gram probability
        best_word = max(candidates, key=self._word_probability)
        return best_word

    def predict_top_words(self, prefix, top_k=10):
        """
        Returns the top_k most probable completions from the training corpus that start with `prefix`.
        """
        # Filter words by prefix
        candidates = [w for w in self.words if w.startswith(prefix)]
        if not candidates:
            return []

        # Sort candidates by probability in descending order
        candidates.sort(key=self._word_probability, reverse=True)
        return candidates[:top_k]
