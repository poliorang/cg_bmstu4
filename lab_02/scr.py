nums = []
a, b = map(float, input().split())
while a != 0:
    nums.append([a, b])
    a, b = map(float, input().split())

for i in range(len(nums)):
    nums[i][0] += 16.94

for n in nums:
    print(*n)