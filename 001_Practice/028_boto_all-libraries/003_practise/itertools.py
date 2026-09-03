
nums = [1,2,3,4,5]
i_nums1 = iter(nums)
i_nums = nums.__iter__()

print(i_nums1)
print(i_nums)
print(dir(i_nums))

print(next(i_nums1))
print(next(i_nums1))
print(next(i_nums1))
for num in i_nums:
    print(num)