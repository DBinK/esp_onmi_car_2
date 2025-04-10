import time

# 装饰器
def debounce(delay_ns):
    """装饰器: 防止函数在指定时间内被重复调用"""
    def decorator(func):
        last_call_time = 0
        result = None

        def wrapper(*args, **kwargs):
            nonlocal last_call_time, result
            current_time = time.time_ns()
            if current_time - last_call_time > delay_ns:
                last_call_time = current_time
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


def timeit(func):
    """装饰器: 测量函数执行时间, 优化性能的时候测试用"""
    def wrapper(*args, **kwargs):
        start_time = time.time_ns()  # 获取当前时间（纳秒）
        result = func(*args, **kwargs)  # 调用被装饰的函数
        end_time = time.time_ns()  # 获取结束时间（纳秒）
        execution_time = end_time - start_time  # 计算执行时间
        print(f"Function '{func.__name__}' took {execution_time / 1_000_000} ms to execute")
        return result  # 返回函数的结果
    return wrapper


# 数据处理函数
def limit_value(value, min_value=-3000, max_value=3000):
    """限制输入的值在给定的范围内。"""
    return min(max(value, min_value), max_value)
    
def map_value(self, value, original_block, target_block):
    """将给定的值映射到给定的目标范围。"""
    original_min, original_max = original_block
    target_min, target_max = target_block
    
    # 计算映射值
    mapped_value = target_min + (value - original_min) * (target_max - target_min) / (original_max - original_min)
    
    return mapped_value

# 时间差计算类
class TimeDiff:
    def __init__(self):
        """初始化TimeDiff类，设置last_time为None。"""
        self.last_time = None

    def time_diff(self):
        """计算两次调用之间的时间差，单位为微秒。"""
        current_time = time.time_ns()  # 获取当前时间（单位：纳秒）

        if self.last_time is None:  # 如果是第一次调用，更新last_time
            self.last_time = current_time
            return 0.000_001  # 防止除零错误

        else:  # 计算时间差
            diff = (current_time - self.last_time)   # 计算时间差
            self.last_time = current_time  # 更新上次调用时间
            return diff  # 返回时间差ns