"""
Referral Utilities — Binary Tree Placement for ILA Global Referral Network.

Handles placing new users into the binary referral tree under their referrer.
Each referrer can have a Left (L) and Right (R) child.
New users are placed in the first available slot via BFS traversal.
"""
from collections import deque


def place_user_in_referral_tree(user, referrer):
    """
    Places the given user into the binary referral tree under the referrer.
    Uses BFS (breadth-first search) to find the first open slot (Left or Right).
    
    Args:
        user: The newly registered User instance to place in the tree.
        referrer: The User instance who referred the new user.
    """
    if not referrer:
        return

    # BFS to find the first available position in the binary tree
    queue = deque([referrer])

    while queue:
        current = queue.popleft()

        # Check Left child
        left_child = current.children.filter(position='L').first()
        if not left_child:
            user.parent = current
            user.position = 'L'
            user.save(update_fields=['parent', 'position'])
            return

        # Check Right child
        right_child = current.children.filter(position='R').first()
        if not right_child:
            user.parent = current
            user.position = 'R'
            user.save(update_fields=['parent', 'position'])
            return

        # Both children exist, continue BFS down the tree
        queue.append(left_child)
        queue.append(right_child)
