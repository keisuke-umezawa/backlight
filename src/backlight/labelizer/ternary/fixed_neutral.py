import numpy as np

from ..common import LabelType, TernaryDirection
from ..labelizer import Label, Labelizer


class FixedNeutralLabelizer(Labelizer):
    def validate_params(self):
        assert "lookahead" in self._params
        assert "neutral_atol" in self._params
        assert "neutral_rtol" in self._params

    def generate(self, mkt):
        mid = mkt.mid.copy()
        future_price = mid.shift(freq="-{}".format(self._params["lookahead"]))
        diff = (future_price - mid).reindex(mid.index)
        diff_abs = diff.abs()
        neutral_band = np.isclose(
            np.zeros(len(diff_abs)),
            diff_abs,
            rtol=self._params["neutral_rtol"],
            atol=self._params["neutral_atol"],
        )
        U, N, D = 0, 1, 2
        df = mid.to_frame("mid")
        df.loc[:, "label_diff"] = diff
        df.loc[df.label_diff > 0, "label"] = TernaryDirection.UP.value
        df.loc[df.label_diff < 0, "label"] = TernaryDirection.DOWN.value
        df.loc[neutral_band, "label"] = TernaryDirection.NEUTRAL.value
        return Label(LabelType.TERNARY, df[["label_diff", "label"]])