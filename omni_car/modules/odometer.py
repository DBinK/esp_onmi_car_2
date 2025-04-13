def odometer(v_lf, v_rf, v_rb, v_lb):
    v_x = (v_lf + v_rf - v_rb - v_lb) / 2.0
    v_y = (v_lf - v_rf + v_rb - v_lb) / 2.0
    v_w = (-v_lf + v_rf + v_rb - v_lb) / 2.0
    
    return v_x, v_y, v_w

# 示例
lf_velocity = 2.0  # 左前轮速度
rf_velocity = 2.0  # 右前轮速度
rb_velocity = 1.0 # 右后轮速度
lb_velocity = -1.0 # 左后轮速度

v_x, v_y, v_w = inverse_kinematics(lf_velocity, rf_velocity, rb_velocity, lb_velocity)

print(f"前进速度: {v_x}, 侧向速度: {v_y}, 角速度: {v_w}")