# You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order and each of their nodes contain a single digit. Add the two numbers and return it as a linked list.
# 
# You may assume the two numbers do not contain any leading zero, except the number 0 itself.
# 
# Input: (2 -> 4 -> 3) + (5 -> 6 -> 4)
# Output: 7 -> 0 -> 8


# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, x):
        self.val = x
        self.next = None

    def __str__(self):
        x = self
        s = []
        while x:
            s.append(str(x.val))
            x = x.next
        return ' ,'.join(s)


class Solution(object):
    def addTwoNumbers(self, l1, l2):
        """
        :type l1: ListNode
        :type l2: ListNode
        :rtype: ListNode
        """
        previous = ListNode(0)
        first = previous
        while l1 or l2:
            l1_val = l1.val if l1 else 0
            l2_val = l2.val if l2 else 0
            n = l1_val + l2_val
            cur_node = ListNode(n)
            previous.next = cur_node
            if previous.val >= 10:
                cur_node.val += 1
                previous.val -= 10
            previous = cur_node
            l1 = l1.next if l1 else None
            l2 = l2.next if l2 else None
        if previous.val >= 10:
            previous.next = ListNode(1)
            previous.val -= 10
        return first.next


def list_to_node(l):
    pre = ListNode(0)
    first = pre
    for i in l:
        cur = ListNode(i)
        pre.next = cur
        pre = cur
    return first.next


print Solution().addTwoNumbers(list_to_node([2, 4, 3]), list_to_node([5, 6, 4]))
