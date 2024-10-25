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
    def creating_session(self):
        import random
        for player in self.get_players():
            player.tau = random.choice([1, 2, 3])
            print(f"Player {player.id_in_group} has tau = {player.tau}")  # デバッグ用のログ


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
        players = self.group.get_players()
        total_contribution = sum([p.contribution for p in players])
        self.group.total_contribution = total_contribution
        # benefit_functionを現在のラウンドに基づいて呼び出す
        benefit = self.benefit_function(total_contribution, self.subsession.round_number)
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


class Mypage(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        # 現在のラウンドに基づいて便益関数を表示する
        round_number = self.subsession.round_number
        shift = 1 + 1 * round_number  # シフト値は1
        benefit_function = f"ρ(x) = 100 / (1 + exp(-(x - {shift})))"
        return {
            'player_tau': self.tau,
            'benefit_function': benefit_function,
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











