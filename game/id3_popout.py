import csv
import math
from collections import Counter

class Node:
    def __init__(self, feature=None, label=None):
        self.feature = feature
        self.label = label
        self.children = {}
        self.majority_class = None

    def is_leaf(self):
        return self.label is not None

def entropy(data, label="move"):
    n = len(data)
    if n == 0:
        return 0
    counts = Counter(row[label] for row in data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c > 0)

def information_gain(data, feature, label="move"):
    n = len(data)
    base_entropy = entropy(data, label)
    values = set(row[feature] for row in data)
    weighted = sum(
        (len(subset := [r for r in data if r[feature] == v]) / n) * entropy(subset, label)
        for v in values
    )
    return base_entropy - weighted

def id3(data, features, label="move", depth=0, max_depth=10):
    classes = [row[label] for row in data]
    majority = Counter(classes).most_common(1)[0][0]

    if len(set(classes)) == 1:
        return Node(label=classes[0])

    if not features or depth >= max_depth:
        return Node(label=majority)

    best_feat = max(features, key=lambda f: information_gain(data, f, label))
    
    node = Node(feature=best_feat)
    node.majority_class = majority

    values = set(row[best_feat] for row in data)
    remaining = [f for f in features if f != best_feat]

    for val in values:
        subset = [row for row in data if row[best_feat] == val]
        if not subset:
            node.children[val] = Node(label=majority)
        else:
            node.children[val] = id3(subset, remaining, label, depth + 1, max_depth)

    return node

def predict(node, row):
    if node.is_leaf():
        return node.label
    
    val = row.get(node.feature)
    
    if val not in node.children:
        return node.majority_class
        
    return predict(node.children[val], row)

def load_dataset(filepath="dataset.csv"):
    data = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed = {k: (int(v) if k != "move" else v) for k, v in row.items()}
            data.append(processed)
    return data

def train_tree(max_depth=10, filepath="dataset.csv"):
    try:
        data = load_dataset(filepath)
        features = [f for f in data[0].keys() if f != "move"]
        tree = id3(data, features, label="move", max_depth=max_depth)
        return tree, features
    except FileNotFoundError:
        return None, None

def get_id3_move(state, tree, features):
    state_dict = {}
    for r in range(6):
        for c in range(7):
            state_dict[f"cell_{r}_{c}"] = state.board[r][c]
    state_dict["player"] = state.player
    
    prediction = predict(tree, state_dict)
    if not prediction:
        return None
        
    col_str, action = prediction.split("_")
    return (int(col_str), action)