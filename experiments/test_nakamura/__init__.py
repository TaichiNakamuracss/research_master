from otree.api import *

doc = """
公共財ゲーム - 各プレイヤーに選好パラメータ τi をランダムに割り当てます。初期保有はありません。
"""

class C(BaseConstants):
    NAME_IN_URL = 'my_public_goods'
    PLAYERS_PER_GROUP = 3  # プレイヤー数を3に設定
    NUM_ROUNDS = 1
    MULTIPLIER = 2
    BENEFIT_FUNCTION = 100  # 便益関数の定数部分
    CONTRIBUTION_COST = 20  # 貢献する場合のコストc


class Subsession(BaseSubsession):
    def creating_session(self):
        import random
        for player in self.get_players():
            # τi をランダムに1, 2, 3から割り当てる
            player.tau = random.choice([1, 2, 3])


class Group(BaseGroup):
    total_contribution = models.IntegerField()
    individual_share = models.CurrencyField()  # 必要に応じて IntegerField に変更可能
    benefit = models.CurrencyField()  # 便益を保存するためのフィールド


class Player(BasePlayer):
    contribution = models.IntegerField(
        choices=[
            [1, '貢献する'],
            [0, '貢献しない'],
        ],
        label='公共財に貢献しますか？',
    )
    tau = models.IntegerField()  # 選好パラメータ τi


def benefit_function(contributions_sum):
    from math import exp
    return C.BENEFIT_FUNCTION / (1 + exp(-(contributions_sum - 2)))


def set_payoffs(group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    total_contribution = sum(contributions)

    # グループの合計貢献を保存
    group.total_contribution = total_contribution
    group.individual_share = total_contribution * C.MULTIPLIER / len(players)

    # 便益を計算して保存
    benefit = benefit_function(total_contribution)
    group.benefit = benefit  # 便益を group に保存
    
    for player in players:
        tau_i = player.tau
        if player.contribution == 1:
            player.payoff = tau_i * benefit - C.CONTRIBUTION_COST
        else:
            player.payoff = tau_i * benefit


# PAGES
class MyPage(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        return {
            'tau': self.player.tau,  # プレイヤーの選好パラメータをテンプレートに渡す
        }


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'


class Results(Page):
    def vars_for_template(self):
        return {
            'total_contribution': self.group.total_contribution,
            'individual_share': self.group.individual_share,
            'payoff': self.player.payoff,
            'benefit': self.group.benefit,  # グループの便益をテンプレートに渡す
        }


page_sequence = [MyPage, ResultsWaitPage, Results]
