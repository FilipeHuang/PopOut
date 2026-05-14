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

def load_dataset(filepath):
    data = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed = {}
            for k, v in row.items():
                if k == "move":
                    processed[k] = v
                else:
                    # Convert cell values to int (0, 1, 2 representing empty, player1, player2)
                    processed[k] = int(v) if v else 0
            data.append(processed)
    return data

def train_tree(filepath, max_depth=10):
    try:
        data = load_dataset(filepath)
        # Get all features except 'move'
        features = [f for f in data[0].keys() if f != "move"]
        tree = id3(data, features, label="move", max_depth=max_depth)
        return tree, features
    except FileNotFoundError:
        print(f"File {filepath} not found!")
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

def print_tree(node, indent=""):
    if node.is_leaf():
        print(f"{indent}-> {node.label}")
        return
    
    print(f"{indent}{node.feature}:")
    for val, child in node.children.items():
        print(f"{indent}  if {node.feature} == {val}:")
        print_tree(child, indent + "    ")

def evaluate(tree, test_data, features):
    correct = 0
    for row in test_data:
        pred = predict(tree, row)
        if pred == row["move"]:
            correct += 1
    return correct / len(test_data) if test_data else 0

def split_data(data, test_ratio=0.2, seed=42):
    import random
    random.seed(seed)
    shuffled = data.copy()
    random.shuffle(shuffled)
    split_idx = int(len(shuffled) * (1 - test_ratio))
    return shuffled[:split_idx], shuffled[split_idx:]

if __name__ == "__main__":
    # Train on dataset_2.csv
    filepath = "newdatasets/dataset_2com5.csv"
    tree, features = train_tree(filepath, max_depth=10)
    
    if tree:
        print(f"Features used: {features[:5]}... (total {len(features)} features)")
        print(f"Examples loaded from {filepath}")
        
        # Load all data for splitting
        all_data = load_dataset(filepath)
        print(f"Total examples: {len(all_data)}")
        
        # Split 80/20
        train_data, test_data = split_data(all_data, test_ratio=0.2)
        print(f"Train: {len(train_data)} | Test: {len(test_data)}")
        
        # Retrain on training data only (for proper evaluation)
        tree = id3(train_data, features, label="move", max_depth=10)
        
        # Print the tree
        print("\n=== DECISION TREE ===")
        print_tree(tree)
        
        # Evaluate on test set
        acc = evaluate(tree, test_data, features)
        print(f"\nTest accuracy: {acc * 100:.1f}%")
    else:
        print("Failed to train tree. Check file path.")