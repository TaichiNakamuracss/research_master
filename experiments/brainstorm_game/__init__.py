import random
import pandas as pd
import ast
import json
from otree.api import *


doc = """
SIPのインターバースプロジェクトで実施するアイデア出しゲームです。
"""


class C(BaseConstants):
    NAME_IN_URL = "brainstorm_game"
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 5
    ACCEPT_UTILITY = 10
    SUBMIT_COST = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    round_for_reward = models.IntegerField()


class Player(BasePlayer):
    idea_set = models.StringField(initial="[]")
    submit_ideas = models.StringField(initial="[]")
    accept_idea_lower = models.IntegerField(
        initial=-1,  # 初期値は−1とし、Reporting Wait Page で設定
    )
    accept_idea_upper = models.IntegerField(
        initial=-1,  # 初期値は−1とし、Reporting Wait Page で設定
    )
    report_lower = models.IntegerField(min=1)
    report_upper = models.IntegerField(max=100)
    report_ideas = models.StringField(initial="[]")


def set_payoffs(group):
    players = group.get_players()
    for player in players:
        profit = 0
        cost = 0
        for submit_idea in ast.literal_eval(player.submit_ideas):
            for p in player.get_others_in_group():
                if (
                    submit_idea not in ast.literal_eval(p.idea_set)
                    and p.accept_idea_lower <= int(submit_idea)
                    and int(submit_idea) <= p.accept_idea_upper
                ):
                    profit += C.ACCEPT_UTILITY
            cost += C.SUBMIT_COST

        player.payoff += profit - cost


# PAGES
class Instruction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        example_reward = C.ACCEPT_UTILITY * 3 - C.SUBMIT_COST
        return {"example_reward": example_reward}


class ReportingWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.round_for_reward = random.randint(1, group.round_number)
        df_ideas: pd.DataFrame = pd.read_csv("brainstorm_game/idea_sets_data.csv")
        df_accept_range: pd.DataFrame = pd.read_csv(
            "brainstorm_game/accept_range_data.csv"
        )
        for p in group.get_players():
            p.accept_idea_lower = int(
                int(df_accept_range.iat[group.round_number - 1, p.id_in_group * 2 - 2])
            )  # 各プレイヤの真の意見の下限をを保存
            p.accept_idea_upper = int(
                int(df_accept_range.iat[group.round_number - 1, p.id_in_group * 2 - 1])
            )  # 各プレイヤの真の意見の上限をを保存
            p.idea_set = str(
                ast.literal_eval(
                    df_ideas.iat[group.round_number - 1, p.id_in_group - 1]
                )
            )


class Reporting(Page):
    timeout_seconds = 300
    timer_text = "話し合い残り時間："
    form_model = "player"
    form_fields = ["report_lower", "report_upper"]

    @staticmethod
    def error_message(player: Player, values):
        if values["report_lower"] > values["report_upper"]:
            return "レポートの下限はレポートの上限以下になるようにしてください。"

    # 時間切れが生じた際の処理。入力済みの値はそのまま反映、何も入力されてなければ[0, 100]が入る
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # タイムアウト時のデフォルト値設定
        if timeout_happened:
            if player.report_upper == 1:
                player.report_upper = 100


class SubmitWaitPage(WaitPage):
    pass


class Submit(Page):
    form_model = "player"
    form_fields = ["submit_ideas"]

    @staticmethod
    def vars_for_template(player: Player):
        # idea_set をリストに戻す
        idea_set = ast.literal_eval(player.idea_set)
        return {"idea_set": idea_set}


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = "set_payoffs"


class Results(Page):
    pass


class FinalResult(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        selected_player = player.in_round(player.group.round_for_reward)
        return dict(
            players_selected_round=[
                p.in_round(player.group.round_for_reward)
                for p in player.group.get_players()
            ],
            final_payoff=selected_player.payoff,
        )


page_sequence = [
    Instruction,
    ReportingWaitPage,
    Reporting,
    SubmitWaitPage,
    Submit,
    ResultsWaitPage,
    Results,
    FinalResult,
]
