from otree.api import *
import math

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
            player.tau = random.choice([1, 2, 3])


class Group(BaseGroup):
    total_contribution = models.IntegerField()
    benefit = models.FloatField()

class Player(BasePlayer):
    contribution = models.BooleanField(
        choices=[
            (1, '貢献する'),
            (0, '貢献しない')
        ],
        doc="プレイヤーが公共財に貢献するかどうか"
    )
    tau = models.IntegerField(doc="プレイヤーの公共財への選好 (τ)", initial=1)
    final_payoff = models.FloatField(doc="プレイヤーの最終的な利得")

    def set_payoffs(self):
        # グループ内のプレイヤーを取得
        players = self.group.get_players()
        
        # 合計貢献額を計算
        total_contribution = sum([p.contribution for p in players])
        self.group.total_contribution = total_contribution
        
        # 便益を計算
        benefit = self.benefit_function(total_contribution)
        self.group.benefit = benefit

        # 各プレイヤーの利得を計算
        for p in players:
            if p.contribution == 1:  # 貢献した場合
                p.final_payoff = p.tau * benefit - C.CONTRIBUTION_COST
            else:  # 貢献しなかった場合
                p.final_payoff = p.tau * benefit

    def benefit_function(self, x):
        return 100 / (1 + math.exp(-(x - 2)))


class Mypage(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        benefit_function = "ρ(x) = 100 / (1 + exp(-(x - 2)))"
        return {
            'player_tau': self.tau,  # self.player.tau を正しく使用
            'benefit_function': benefit_function,
        }


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        # 全プレイヤー到着後に payoff を設定
        for player in self.group.get_players():
            player.set_payoffs()


class Results(Page):
    def vars_for_template(self):
        return {
            'total_contribution': self.group.total_contribution,
            'benefit': self.group.benefit,
            'player_tau': self.tau,  # self.player.tau を正しく使用
            'final_payoff': self.final_payoff,  # self.player.final_payoff を正しく使用
        }


page_sequence = [Mypage, ResultsWaitPage, Results]







