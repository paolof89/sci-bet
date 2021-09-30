select a.*,
b.h_avg_scored, b.h_avg_conceded, b.h_avg_elo,
b.a_avg_scored, b.a_avg_conceded, b.a_avg_elo,
elo_relative, elo_diff, scored_relative, scored_diff,
conceded_relative, conceded_diff
from matches a left join features_basic b
on a.MATCH_ID = b.MATCH_ID