import bisect


def luckyNumbers(matrix):
    # mins = [min(i) for i in matrix]
    # maxs = [max(i) for i in zip(*matrix)]
    for i in zip(*matrix):
        print(max(i))
    for i in matrix:
        print(min(i))
    # return list(set(maxs) & set(mins))


# print(luckyNumbers([[3, 7, 8], [9, 11, 13], [15, 16, 17]]))


def numSpecial(mat):
    final_count = 0
    for i in range(len(mat)):
        counter = 0
        if mat[i].count(1) > 1:
            break
        if mat[i].count(i) == 1:
            counter += 1
        for x in range(len(mat[i])):
            if mat[i][x] == 1:
                counter += 1
        if counter == 1:
            final_count += 1

        return final_count


mat = [[1, 0, 0], [0, 0, 1], [1, 0, 0]]


# print(numSpecial(mat))


def removeelement(lis, val):
    # replaced_text = ''
    for i in lis:
        if val == i:
            # replaced_text = str(lis).replace(str(i), '_')
            lis.remove(i)
    return len(lis)


nums = [3, 2, 2, 3]
val = 3


# print(removeelement(nums, val))


def strStr(haystack, needle):
    if needle == "":
        return 0

    for i in range(len(haystack) - len(needle) + 1):
        if haystack[i:i + len(needle)] == needle:
            return i

    return -1


haystack = "sadbutsad"
needle = "sad"


# print(strStr(haystack, needle))


def search_insert(nums, target):
    left = 0
    right = len(nums) - 1
    print(right)
    print(left)
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    # return left


# Example usage:
num = [1, 3, 5, 7, 9]
target = 4
result = search_insert(num, target)
print(result)  # Output: 2
