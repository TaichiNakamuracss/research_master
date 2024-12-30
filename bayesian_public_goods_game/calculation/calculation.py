from scipy.optimize import newton
import numpy as np
from math import comb  # 組み合わせを計算する関数

# 一様分布の範囲を設定（例として [1, 3] とします）
a, b = 1, 3

# 累積分布関数 F(tau) の定義 (一様分布に基づく)
def F(tau):
    if tau < a:
        return 0
    elif tau > b:
        return 1
    else:
        return (tau - a) / (b - a)

# rho(x) の定義
def rho(x):
    return 100 / (1 + np.exp(-(x + 3)))

# 定数の設定
n = 5   # プレイヤーの数
c = 20  # 任意のコスト定数

# 方程式の定義
def equation(tau_star):
    denominator_sum = sum(
        comb(n - 1, k) * (rho(k + 1) - rho(k)) * (1 - F(tau_star))**k * F(tau_star)**(n - 1 - k)
        for k in range(n)
    )
    if denominator_sum == 0:
        return np.inf  # 分母が 0 になる場合
    return tau_star - (c / denominator_sum)  # tau_star = c / 分母 の形

# 初期値リストをより細かく定義（0.05 刻み）
initial_guesses = np.arange(1.0, 3.0, 0.01)  # 範囲 [1.0, 3.0) を細かく分割

# 各初期値で数値解を計算
results = []
for guess in initial_guesses:
    try:
        root = newton(equation, x0=guess)  # 初期値を指定して解を探索
        # 重複を排除して解を保存
        if not any(np.isclose(root, r) for r in results):
            results.append(root)
    except RuntimeError:
        print(f"初期値 {guess} では収束しませんでした。")

# 結果を出力
print("解リスト:", results)







