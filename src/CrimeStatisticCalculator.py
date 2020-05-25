# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------

import numpy as np


class CrimeStatisticCalculator:
    def __init__(self, data:  np.ndarray):
        self.data = data

    def calculate_mean(self) -> np.ndarray:
        return np.mean(self.data)

    def calculate_median(self) -> np.ndarray:
        return np.median(self.data)

    def calculate_std(self) -> np.ndarray:
        return np.std(self.data)
