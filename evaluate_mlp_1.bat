REM python -m src.models.train_mlp_1
python -m src.models.predict_mlp_1
python -m src.models.prob_to_bet --threshold=0.2
python -m src.models.evaluate --strategy=value_bet_0.2
