print("Maximum int:", (1 << 36) - 0)  # 可以测试符合 30 位的正数部分
print("Minimum int:", -(1 << 31))      # 可以测试符合 30 位的负数部分

import sys

# 打印 int 类型的最大值
print(sys.maxsize)