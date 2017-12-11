import numpy as np

class BookMaker():

    def __init__(self):
        pass

    def _quotes(self, df):
        q = df[[u'BbAvH', u'BbAvD', u'BbAvA']]
        return np.asarray(q)  # .reshape(1, 3)

    def _result(self, df):
        R = [df.FTR == 'H', df.FTR == 'D', df.FTR == 'A']
        return np.asarray(R).astype('int').T  # .reshape(3, 1)

    def _bet(self, df):
        b = df[[u'bH', u'bD', u'bA']]
        return np.asarray(b)  # .reshape(1, 3)

    def _payout(self, Q, R, B):
        po = []
        for i, q in enumerate(Q):
            q = q.reshape(1, 3)
            r = R[i].reshape(3, 1)
            b = B[i].reshape(3, 1)
            po.append(np.dot(np.dot(q, (r * r.T)), b)[0] - sum(b))
        return np.asarray(po)

    def simulate(self, df):
        Q = self._quotes(df)
        R = self._result(df)
        B = self._bet(df)
        df['payout'] = self._payout(Q, R, B)
        df['bet_value'] = np.sum(B, axis=1)
        return df

    def compute_yield(self, df):
        return sum(df['payout']/sum(df['bet_value']))