from otree.api import *
import math
import random  # ランダムモジュールを追加

doc = """
公共財ゲーム - 各プレイヤーに選好パラメータ τi をランダムに割り当てます。初期保有はありません。
"""

class C(BaseConstants):
    NAME_IN_URL = 'my_public_goods'
    PLAYERS_PER_GROUP = 5  # プレイヤー数を3に設定
    NUM_ROUNDS = 5  # ゲームは5回繰り返される
    BENEFIT_FUNCTION = 100  # 便益関数の定数部分
    CONTRIBUTION_COST = 20  # 貢献する場合のコストc


class Subsession(BaseSubsession):
    pass

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
    tau = models.FloatField(initial=cu(0))

    def set_tau(player):
        player.tau += random.randint(1, 3)

    final_payoff = models.FloatField(doc="プレイヤーの最終的な利得")

    def set_payoffs(self):
        players = self.group.get_players()
        total_contribution = sum([p.contribution for p in players])
        self.group.total_contribution = total_contribution
        # benefit_functionを現在のラウンドに基づいて呼び出す
        benefit = self.benefit_function(total_contribution, self.subsession.round_number)
        self.group.benefit = benefit / C.PLAYERS_PER_GROUP

        for p in players:
            if p.contribution == 1:
                p.final_payoff = round(p.tau * benefit - C.CONTRIBUTION_COST, 1)
            else:
                p.final_payoff = round(p.tau * benefit, 1)


    # ラウンドに応じたシフトを適用 (シフト値は1)
    def benefit_function(self, x, round_number):
        shift = 1 + 1 * round_number  # シフト値をラウンドごとに1ずつ増加
        return 100 / (1 + math.exp(-(x - shift)))


class Introduction(Page):
    """ゲームのルールを説明するイントロダクションページ"""

    def vars_for_template(self):
        # 効用関数の説明を二行に分ける
        utility_function_1 = "u<sub>i</sub>(s<sub>i</sub>, s<sub>−i</sub>) = τ<sub>i</sub>  ρ(n<sub>g</sub>(s, s<sub>−i</sub>)) − c"
        utility_function_2 = "u<sub>i</sub>(ϕ, s<sub>−i</sub>) = τ<sub>i</sub>  ρ(n<sub>g</sub>(ϕ, s<sub>−i</sub>))"
        
        
        return {
            'num_rounds': C.NUM_ROUNDS,
            'utility_function_1': utility_function_1,
            'utility_function_2': utility_function_2,
            'description': "各プレイヤーは、自身の利益を最大化するために、"
                           "公共財に貢献するか否かを選択します。ゲームは5ラウンド続きます。"
        }

class PlayerWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for player in self.group.get_players():
            player.set_tau()

class Mypage(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        # 現在のラウンドに基づいて便益関数を表示する
        round_number = self.subsession.round_number
        shift = 1 + 1 * round_number  # シフト値は1
        benefit_function = f"ρ(x) = 100 / (1 + exp(-(x - {shift})))"
        x_values = list(range(0, 11))  # 0から10までの範囲
        y_values = [100 / (1 + math.exp(-(x - shift))) for x in x_values]
        return {
            'player_tau': self.tau,
            'benefit_function': benefit_function,
            'x_values': x_values,  # x軸データ
            'y_values': y_values,  # y軸データ
        }


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for player in self.group.get_players():
            player.set_payoffs()


class Results(Page):
    def vars_for_template(self):
        return {
            'total_contribution': self.group.total_contribution,
            'player_tau': self.tau,
            'final_payoff': self.final_payoff,
        }


# ページシーケンスにIntroductionページを追加
page_sequence = [Introduction, PlayerWaitPage, Mypage, ResultsWaitPage, Results]












