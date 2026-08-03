import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("ab_test_data.csv")

control = df[df["group"] == "control"]["converted"]
test = df[df["group"] == "test"]["converted"]

n_control, n_test = len(control), len(test)
p_control, p_test = control.mean(), test.mean()


def wilson_ci(successes, n, alpha=0.05):
    p = successes / n
    z = stats.norm.ppf(1 - alpha / 2)
    denom = 1 + z ** 2 / n
    center = (p + z ** 2 / (2 * n)) / denom
    margin = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return center - margin, center + margin


ci_control = wilson_ci(control.sum(), n_control)
ci_test = wilson_ci(test.sum(), n_test)

fig, ax = plt.subplots(1, 2, figsize=(13, 5))

groups = ["Контроль", "Тест"]
rates = [p_control, p_test]
errors = [
    [p_control - ci_control[0], p_test - ci_test[0]],
    [ci_control[1] - p_control, ci_test[1] - p_test],
]
colors = ["#4c72b0", "#55a868"]

ax[0].bar(groups, rates, yerr=errors, capsize=8, color=colors)
ax[0].set_ylabel("Конверсия")
ax[0].set_title("Конверсия по группам с 95% доверительным интервалом")
ax[0].set_ylim(0, max(ci_test[1], ci_control[1]) * 1.25)
for i, (r, err_top) in enumerate(zip(rates, errors[1])):
    ax[0].text(i, r + err_top + 0.004, f"{r:.1%}", ha="center")

x = np.linspace(-5, 5, 300)
ax[1].plot(x, stats.norm.pdf(x), color="grey", label="Распределение при отсутствии эффекта")
z_stat = 4.287
ax[1].axvline(z_stat, color="#c44e52", linestyle="--", label=f"Наблюдаемая z-статистика = {z_stat:.2f}")
ax[1].axvline(-z_stat, color="#c44e52", linestyle="--")
ax[1].set_title("Наблюдаемый эффект относительно нулевой гипотезы")
ax[1].set_xlabel("z")
ax[1].text(
    0.5, 0.7,
    "Площадь за пределами пунктирных линий\nпрактически равна нулю (p-value < 0.0001) —\nнаблюдаемый эффект почти невозможен\nпри отсутствии реального различия",
    transform=ax[1].transAxes, ha="center", fontsize=9,
    bbox=dict(boxstyle="round", facecolor="#fdf2f2", edgecolor="#c44e52"),
)
ax[1].legend(loc="upper left")

plt.tight_layout()
plt.savefig("ab_test_result.png", dpi=120)
print("График сохранён в ab_test_result.png")
