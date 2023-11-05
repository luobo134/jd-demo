def twoSum(nums, target):
    num_map = {}

    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        else:
            num_map[num] = i

    #如果未找到配对，则返回空列表
    return []