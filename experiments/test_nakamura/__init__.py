from otree.api import *
import math
import random

doc = """
公共財ゲーム - 各プレイヤーに選好パラメータをランダムに割り当てます。初期保有はありません。
"""

class C(BaseConstants):
    NAME_IN_URL = 'my_public_goods'
    PLAYERS_PER_GROUP = 5  # 1グループあたりのプレイヤー数
    NUM_ROUNDS = 5  # ゲームは5回繰り返される
    BENEFIT_FUNCTION = 100  # 便益関数の定数部分
    CONTRIBUTION_COST = 20  # 貢献する場合のコストc
    FIXED_REWARD = 1500  # 固定報酬

class Subsession(BaseSubsession):
    def creating_session(self):
        # プレイヤーをグループに分ける
        self.set_group_matrix(
            [self.get_players()[i:i + C.PLAYERS_PER_GROUP] for i in range(0, len(self.get_players()), C.PLAYERS_PER_GROUP)]
        )


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
    dynamic_reward = models.FloatField(doc="動的報酬")

    def set_payoffs(self):
        players = self.group.get_players()
        total_contribution = sum([p.contribution for p in players])
        self.group.total_contribution = total_contribution
        # benefit_functionを現在のラウンドに基づいて呼び出す
        benefit = self.benefit_function(total_contribution, self.subsession.round_number)
        self.group.benefit = benefit

        for p in players:
            if p.contribution == 1:
                p.final_payoff = round(p.tau * benefit - C.CONTRIBUTION_COST, 0)
            else:
                p.final_payoff = round(p.tau * benefit, 0)

    def benefit_function(self, x, round_number):
        shift = 8 - 2 * round_number  # シフト値をラウンドごとに1ずつ増加
        return 100 / (1 + math.exp(-(x - shift)))

class Introduction(Page):
    """ゲームのルールを説明するイントロダクションページ"""

    def vars_for_template(self):
        return {
            'num_rounds': C.NUM_ROUNDS,
            'cost': C.CONTRIBUTION_COST,
        }

class PlayerWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for player in self.group.get_players():
            player.set_tau()

class Mypage(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(self):
        round_number = self.subsession.round_number
        shift = 8 - 2 * round_number  # シフト値は1
        table_data = lambda tau: [
            {
                'others_contributions': i,
                'contribute_benefit': round(tau * (100 / (1 + math.exp(-(i + 1 - shift)))) - C.CONTRIBUTION_COST, 0),
                'not_contribute_benefit': round(tau * (100 / (1 + math.exp(-(i - shift)))), 0),
            }
            for i in range(C.PLAYERS_PER_GROUP)
        ]
        return {
            'player_tau': self.tau,
            'table_data_tau_1': table_data(1),  # \u03c4 = 1の場合
            'table_data_tau_2': table_data(2),  # \u03c4 = 2の場合
            'table_data_tau_3': table_data(3),  # \u03c4 = 3の場合
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

class FinalResults(Page):
    """5回目のラウンド終了後にランダムで1回を選んで結果を表示するページ"""
    def is_displayed(self):
        # 最終ラウンドの後のみこのページを表示
        return self.round_number == C.NUM_ROUNDS

    def vars_for_template(self):
        # ランダムで1ラウンドを選ぶ
        random_round = random.randint(1, C.NUM_ROUNDS)
        selected_round = self.in_round(random_round)

        # 最終利得を0円〜1000円にマッピング
        min_payoff = 0  # 最小報酬
        max_payoff = 500  # 最大報酬
        min_final_payoff = -C.CONTRIBUTION_COST  # 最小利得 (貢献時の最低値)
        max_final_payoff = 3 * 100  # 最大利得 (最大 \tau と最大 benefit)

        # 報酬の計算
        final_payoff = selected_round.final_payoff
        dynamic_reward = round(
            min_payoff + (final_payoff - min_final_payoff) * (max_payoff - min_payoff) / (max_final_payoff - min_final_payoff),
            0
        )
        # 報酬は0円から1000円の範囲内に収める
        dynamic_reward = max(min(dynamic_reward, max_payoff), min_payoff)

        # 動的報酬をプレイヤーに保存
        self.dynamic_reward = dynamic_reward

        return {
            'random_round': random_round,  # ランダムに選ばれたラウンド
            'final_payoff': final_payoff,  # 選ばれたラウンドのプレイヤーの結果
            'player_tau': selected_round.tau,  # 選ばれたラウンドでのプレイヤーの \u03c4
            'dynamic_reward': dynamic_reward,  # 最終利得に基づく報酬
            'fixed_reward': C.FIXED_REWARD,  # 固定報酬
            'total_reward': C.FIXED_REWARD + dynamic_reward,  # 合計報酬
        }

page_sequence = [Introduction, PlayerWaitPage, Mypage, ResultsWaitPage, Results, FinalResults]













