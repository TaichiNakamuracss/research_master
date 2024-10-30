from otree.constants import BaseConstants  # noqa
from otree.models import BaseGroup, BasePlayer, BaseSubsession  # noqa
from otree.views import Page  # noqa

doc = """
This application provides a webpage instructing participants how to get paid.
Examples are given for the lab and Amazon Mechanical Turk (AMT).
"""


class C(BaseConstants):
    NAME_IN_URL = 'payment_info'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# FUNCTIONS
# PAGES
class PaymentInfo(Page):
    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        return dict(redemption_code=participant.label or participant.code)


page_sequence = [PaymentInfo]


from otree.api import *
import math

doc = """
公共財ゲーム - 各プレイヤーに選好パラメータ τi をランダムに割り当てます。初期保有はありません。
"""

class C(BaseConstants):
    NAME_IN_URL = 'my_public_goods'
    PLAYERS_PER_GROUP = 3  # プレイヤー数を3に設定
    NUM_ROUNDS = 5  # ゲームは5回繰り返される
    MULTIPLIER = 2
    BENEFIT_FUNCTION = 100  # 便益関数の定数部分
    CONTRIBUTION_COST = 20  # 貢献する場合のコストc


class Subsession(BaseSubsession):
    pass

import random
class Group(BaseGroup):
    total_contribution = models.IntegerField()
    benefit = models.FloatField()
    tau = models.CurrencyField(initial=cu(0))

def set_tau(group, Group):
    group.tau = group.tau + random.randint(1, 3)

class Player(BasePlayer):
    contribution = models.BooleanField(
        choices=[
            (1, '貢献する'),
            (0, '貢献しない')
        ],
        doc="プレイヤーが公共財に貢献するかどうか"
    )
    
    final_payoff = models.FloatField(doc="プレイヤーの最終的な利得")

    def set_payoffs(self):
        players = self.group.get_players()
        contributions = [p.contribution for p in players]
        group.total_contribution = sum(contributions)
        group.individual_share = (
        group.total_contribution / C.PLAYERS_PER_GROUP)
        # benefit_functionを現在のラウンドに基づいて呼び出す
        benefit = self.benefit_function(group.total_contribution, self.subsession.round_number)
        self.group.benefit = benefit

        for p in players:
            if p.contribution == 1:
                p.final_payoff = p.tau * benefit - C.CONTRIBUTION_COST
            else:
                p.final_payoff = p.tau * benefit

    # ラウンドに応じたシフトを適用 (シフト値は1)
    def benefit_function(self, x, round_number):
        shift = 1 + 1 * round_number  # シフト値をラウンドごとに1ずつ増加
        return 100 / (1 + math.exp(-(x - shift)))


class Introduction(Page):
    """ゲームのルールを説明するイントロダクションページ"""

    def vars_for_template(self):
        # 効用関数の説明を二行に分ける
        utility_function_1 = "ui(si, s−i) = τi * ρ(ng(s, s−i)) − c (si = s)"
        utility_function_2 = "ui(ϕ, s−i) = τi * ρ(ng(ϕ, s−i)) (si = ϕ)"
        
        return {
            'num_rounds': C.NUM_ROUNDS,
            'utility_function_1': utility_function_1,
            'utility_function_2': utility_function_2,
            'description': "各プレイヤーは、自身の利益を最大化するために、"
                           "公共財に貢献するか否かを選択します。ゲームは5ラウンド続きます。"
        }

class PlayerWaitPage(WaitPage):
    after_all_players_arrive = set_tau

class Mypage(Page):
    form_model = 'player'
    form_fields = ['contribution']
    def vars_for_template(self):
        return {
            'benefit': self.group.benefit,
            'player_tau': self.p.tau,
        }


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for player in self.group.get_players():
            player.set_payoffs()


class Results(Page):
    def vars_for_template(self):
        return {
            'total_contribution': self.group.total_contribution,
            'benefit': self.group.benefit,
            'player_tau': self.tau,
            'final_payoff': self.final_payoff,
        }


# ページシーケンスにIntroductionページを追加
page_sequence = [Introduction, Mypage, ResultsWaitPage, Results]
