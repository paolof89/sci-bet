select a.*,
b.h_avg_scored, b.h_avg_conceded, b.h_avg_elo,
b.a_avg_scored, b.a_avg_conceded, b.a_avg_elo
from match_teams a left join features_basic b
on a.MATCH_ID = b.MATCH_ID