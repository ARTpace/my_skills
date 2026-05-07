---
name: Excel Analysis
description: 分析 Excel 电子表格、创建数据透视表、生成图表并执行数据分析。用于分析 Excel 文件、电子表格、表格数据或 .xlsx 文件。
---

# Excel 分析

## 快速开始

使用 pandas 读取 Excel 文件：

```python
import pandas as pd

# 读取 Excel 文件
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# 显示前几行
print(df.head())

# 基本统计
print(df.describe())
```

## 读取多个工作表

处理工作簿中的所有工作表：

```python
import pandas as pd

# 读取所有工作表
excel_file = pd.ExcelFile("workbook.xlsx")

for sheet_name in excel_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(f"\n{sheet_name}:")
    print(df.head())
```

## 数据分析

执行常见分析任务：

```python
import pandas as pd

df = pd.read_excel("sales.xlsx")

# 分组和聚合
sales_by_region = df.groupby("region")["sales"].sum()
print(sales_by_region)

# 筛选数据
high_sales = df[df["sales"] > 10000]

# 计算指标
df["profit_margin"] = (df["revenue"] - df["cost"]) / df["revenue"]

# 按列排序
df_sorted = df.sort_values("sales", ascending=False)
```

## 创建 Excel 文件

写入带格式的数据到 Excel：

```python
import pandas as pd

df = pd.DataFrame({
    "Product": ["A", "B", "C"],
    "Sales": [100, 200, 150],
    "Profit": [20, 40, 30]
})

# 写入 Excel
writer = pd.ExcelWriter("output.xlsx", engine="openpyxl")
df.to_excel(writer, sheet_name="Sales", index=False)

# 获取工作表进行格式设置
worksheet = writer.sheets["Sales"]

# 自动调整列宽
for column in worksheet.columns:
    max_length = 0
    column_letter = column[0].column_letter
    for cell in column:
        if len(str(cell.value)) > max_length:
            max_length = len(str(cell.value))
    worksheet.column_dimensions[column_letter].width = max_length + 2

writer.close()
```

## 数据透视表

以编程方式创建数据透视表：

```python
import pandas as pd

df = pd.read_excel("sales_data.xlsx")

# 创建数据透视表
pivot = pd.pivot_table(
    df,
    values="sales",
    index="region",
    columns="product",
    aggfunc="sum",
    fill_value=0
)

print(pivot)

# 保存数据透视表
pivot.to_excel("pivot_report.xlsx")
```

## 图表和可视化

从 Excel 数据生成图表：

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("data.xlsx")

# 创建柱状图
df.plot(x="category", y="value", kind="bar")
plt.title("Sales by Category")
plt.xlabel("Category")
plt.ylabel("Sales")
plt.tight_layout()
plt.savefig("chart.png")

# 创建饼图
df.set_index("category")["value"].plot(kind="pie", autopct="%1.1f%%")
plt.title("Market Share")
plt.ylabel("")
plt.savefig("pie_chart.png")
```

## 数据清洗

清洗和准备 Excel 数据：

```python
import pandas as pd

df = pd.read_excel("messy_data.xlsx")

# 删除重复项
df = df.drop_duplicates()

# 处理缺失值
df = df.fillna(0)  # 或 df.dropna()

# 去除空白
df["name"] = df["name"].str.strip()

# 转换数据类型
df["date"] = pd.to_datetime(df["date"])
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

# 保存清洗后的数据
df.to_excel("cleaned_data.xlsx", index=False)
```

## 合并和连接

合并多个 Excel 文件：

```python
import pandas as pd

# 读取多个文件
df1 = pd.read_excel("sales_q1.xlsx")
df2 = pd.read_excel("sales_q2.xlsx")

# 垂直连接
combined = pd.concat([df1, df2], ignore_index=True)

# 在共同列上合并
customers = pd.read_excel("customers.xlsx")
sales = pd.read_excel("sales.xlsx")

merged = pd.merge(sales, customers, on="customer_id", how="left")

merged.to_excel("merged_data.xlsx", index=False)
```

## 高级格式设置

应用条件格式和样式：

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font

# 创建 Excel 文件
df = pd.DataFrame({
    "Product": ["A", "B", "C"],
    "Sales": [100, 200, 150]
})

df.to_excel("formatted.xlsx", index=False)

# 加载工作簿进行格式设置
wb = load_workbook("formatted.xlsx")
ws = wb.active

# 应用条件格式
red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")

for row in range(2, len(df) + 2):
    cell = ws[f"B{row}"]
    if cell.value < 150:
        cell.fill = red_fill
    else:
        cell.fill = green_fill

# 加粗表头
for cell in ws[1]:
    cell.font = Font(bold=True)

wb.save("formatted.xlsx")
```

## 性能提示

- 使用 `read_excel` 时配合 `usecols` 只读取特定列
- 对于非常大的文件使用 `chunksize`
- 根据文件类型考虑使用 `engine='openpyxl'` 或 `engine='xlrd'`
- 使用 `dtype` 参数指定列类型以加快读取速度

## 可用包

- **pandas** - 数据分析和操作（主要）
- **openpyxl** - Excel 文件创建和格式设置
- **xlrd** - 读取旧版 .xls 文件
- **xlsxwriter** - 高级 Excel 写入功能
- **matplotlib** - 图表生成
