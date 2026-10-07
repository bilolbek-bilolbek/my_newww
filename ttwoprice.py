import yfinance as yf
import matplotlib.pyplot as plt

# 1. Загрузка данных
data = yf.download("TTWO", start="2025-01-01", end="2026-01-01")

# 2. Просмотр первых строк
print(data.head())

# 3. Построение графика цены закрытия
data['Close'].plot(title="Price history TTWO")
plt.xlabel("Date")
plt.ylabel("Price ($)")
plt.show()

