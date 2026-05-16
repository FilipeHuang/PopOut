import csv
import math
from collections import Counter
from generate_dataset import state_to_features

class Node:
    def __init__(self, feature=None, label=None):
        self.feature = feature
        self.label = label          #class label (if leaf node)
        self.children = {}          #dict: {feature_value: child_node}
        self.majority_class = None  #majority class in the data reaching this node
        self.class_counts = None    #Counter of class labels at this node(used for top‑k predictions)
    def is_leaf(self): return self.label is not None

def entropy(data, label="move"):
    n = len(data)
    if n == 0: return 0
    counts = Counter(row[label] for row in data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c > 0)

def information_gain(data, feature, label="move"):
    n = len(data)
    if n == 0: return 0
    base_entropy = entropy(data, label)
    values = set(row[feature] for row in data)
    weighted = sum(
        (len(subset := [r for r in data if r[feature] == v]) / n) * entropy(subset, label)
        for v in values
    )
    return base_entropy - weighted

def gain_ratio(data, feature, label="move"):
    #normalise information gain by the entropy of the feature values (split information).
    #this avoids the bias of information gain toward features with many values.
    n = len(data)
    #if split information is zero(all examples have same feature value)
    if n == 0: return 0
    ig = information_gain(data, feature, label)
    values = set(row[feature] for row in data)
    split_info = -sum(
        (len([r for r in data if r[feature] == v]) / n) *
        math.log2(len([r for r in data if r[feature] == v]) / n)
        for v in values
        if len([r for r in data if r[feature] == v]) > 0
    )
    if split_info == 0: return 0
    return ig / split_info

def id3(data, features, label="move", depth=0, max_depth=12, min_samples=5):
    classes = [row[label] for row in data]
    counts = Counter(classes)
    majority = counts.most_common(1)[0][0]
    #stop if all examples same class
    if len(set(classes)) == 1:
        n = Node(label=classes[0])
        n.class_counts = counts
        return n
    #stop if no features left, max depth reached, or too few samples
    if not features or depth >= max_depth or len(data) < min_samples:
        n = Node(label=majority)
        n.class_counts = counts
        return n
    #choose best feature by gain ratio
    best_feat = max(features, key=lambda f: gain_ratio(data, f, label))
    #if best gain ratio is zero, stop and return leaf with majority class
    if gain_ratio(data, best_feat, label) <= 0:
        n = Node(label=majority)
        n.class_counts = counts
        return n

    node = Node(feature=best_feat)
    node.majority_class = majority
    node.class_counts = counts

    values = set(row[best_feat] for row in data)
    remaining = [f for f in features if f != best_feat]

    for val in values:
        subset = [row for row in data if row[best_feat] == val]
        if not subset:
            n = Node(label=majority)
            n.class_counts = counts
            node.children[val] = n
        else: node.children[val] = id3(subset, remaining, label, depth + 1, max_depth, min_samples)
    return node

def predict(node, row):
    if node.is_leaf(): return node.label
    val = row.get(node.feature)
    if val not in node.children:
        child_labels = _collect_labels(node)
        if child_labels: return Counter(child_labels).most_common(1)[0][0]
        return node.majority_class
    return predict(node.children[val], row)

def predict_top_k(node, row, k=2):
    if node.is_leaf(): return [move for move, count in node.class_counts.most_common(k)]
    val = row.get(node.feature)
    if val not in node.children:
        child_labels = _collect_labels(node)
        if child_labels:
            counts = Counter(child_labels)
            return [move for move, count in counts.most_common(k)]
        return [node.majority_class]
    return predict_top_k(node.children[val], row, k)

def _collect_labels(node):
    if node.is_leaf(): return [node.label]
    labels = []
    for child in node.children.values(): labels.extend(_collect_labels(child))
    return labels

def load_dataset(filepath="dataset.csv"):
    data = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed = {}
            for k, v in row.items():
                if k == "move" or k == "phase" or k in ("center_adv", "lr_balance"): processed[k] = v
                else:
                    try: processed[k] = int(v)
                    except ValueError: processed[k] = v
            data.append(processed)
    return data

def train_tree(max_depth=12, min_samples=5, filepath="dataset.csv"):
    try:
        data = load_dataset(filepath)
        features = [f for f in data[0].keys() if f != "move"]
        tree = id3(data, features, label="move", max_depth=max_depth, min_samples=min_samples)
        return tree, features
    except FileNotFoundError: return None, None

def get_id3_move(state, tree, features):
    # Safety check if training failed
    if tree is None:
        legal_moves = state.get_legal_moves()
        return legal_moves[0] if legal_moves else None
    state_dict = state_to_features(state)
    try:
        prediction = predict(tree, state_dict)
        if not prediction:
            legal_moves = state.get_legal_moves()
            return legal_moves[0] if legal_moves else None
        # Convert prediction like "4_put" → (4, 'put')
        col_str, action = prediction.split("_")
        move = (int(col_str), action)

        legal_moves = state.get_legal_moves()
        
        if move in legal_moves: return move
        # Fallback 1: Try same action in any column
        same_action = [m for m in legal_moves if m[1] == action]
        if same_action: return same_action[len(same_action) // 2]
        # Fallback 2: Random legal move
        return legal_moves[0] if legal_moves else None
    except Exception:
        # Final safety net
        legal_moves = state.get_legal_moves()
        return legal_moves[0] if legal_moves else None
