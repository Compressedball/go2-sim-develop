import math

def euler_from_quaternion(q):
    siny_cosp = 2 * (q.w*q.z + q.x*q.y)
    cosy_cosp = 1 - 2 * (q.y*q.y + q.z*q.z)
    return math.atan2(siny_cosp, cosy_cosp)