import pandas as pd
import numpy as np
from scipy import stats

ALPHA = 0.05

df = pd.read_csv("ab_test_data.csv")

control = df[df["group"] == "control"]["converted"]
test = df[df["group"] == "test"]["converted"]

n_control, n_test = len(control), len(test)
p_control, p_test = control.mean(), test.mean()

p_pooled = (control.sum() + test.sum()) / (n_control + n_test)
se_pooled = np.sqrt(p_pooled * (1 - p_pooled) * (1 / n_control + 1 / n_test))
z_stat = (p_test - p_control) / se_pooled
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

se_diff = np.sqrt(p_control * (1 - p_control) / n_control + p_test * (1 - p_test) / n_test)
diff = p_test - p_control
z_crit = stats.norm.ppf(1 - ALPHA / 2)
ci_low = diff - z_crit * se_diff
ci_high = diff + z_crit * se_diff

relative_uplift = diff / p_control

print("=== Описательная статистика ===")
print(f"Контроль: n={n_control}, конверсия={p_control:.4f}")
print(f"Тест:     n={n_test}, конверсия={p_test:.4f}")
print()
print("=== Z-тест для разности пропорций ===")
print(f"Разница:            {diff:+.4f} ({relative_uplift:+.1%} к контролю)")
print(f"95% доверительный интервал разницы: [{ci_low:.4f}, {ci_high:.4f}]")
print(f"z-статистика:       {z_stat:.3f}")
print(f"p-value:            {p_value:.4f}")

if p_value < ALPHA:
    print(f"Результат статистически значим на уровне alpha={ALPHA}")
else:
    print(f"Статистической значимости на уровне alpha={ALPHA} не обнаружено")

baseline_rate = p_control
mde = 0.15 * baseline_rate
effect_size = mde / np.sqrt(baseline_rate * (1 - baseline_rate))
z_alpha = stats.norm.ppf(1 - ALPHA / 2)
z_beta = stats.norm.ppf(0.8)
required_n = ((z_alpha + z_beta) / effect_size) ** 2

print()
print("=== Требуемый размер выборки (ретроспективно) ===")
print(f"При базовой конверсии {baseline_rate:.1%} и желаемом MDE 15% отн.")
print(f"нужно по {required_n:.0f} наблюдений на группу для мощности 80%")
print(f"Фактически собрано: control={n_control}, test={n_test}")
