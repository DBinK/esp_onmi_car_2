# 定义比特流
bitstream = b'\x01\x02\x03\x04'  # 示例比特流

# 将比特流转换为数字
# 第一个参数是比特流，第二个参数指定字节序为大端
number = int.from_bytes(bitstream, 'big')

print("转换后的数字是: %d" % number)