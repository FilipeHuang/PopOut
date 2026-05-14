import csv
import math
from collections import Counter

# ──────────────────────────────────────────────────────────────────────────────
# Importa o extractor de features do generate_dataset
# ──────────────────────────────────────────────────────────────────────────────
from generate_dataset import state_to_features


class Node:
    def __init__(self, feature=None, label=None):
        self.feature = feature
        self.label = label
        self.children = {}
        self.majority_class = None

    def is_leaf(self):
        return self.label is not None


# ── Métricas de impureza ───────────────────────────────────────────────────────

def entropy(data, label="move"):
    n = len(data)
    if n == 0:
        return 0
    counts = Counter(row[label] for row in data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c > 0)


def information_gain(data, feature, label="move"):
    n = len(data)
    if n == 0:
        return 0
    base_entropy = entropy(data, label)
    values = set(row[feature] for row in data)
    weighted = sum(
        (len(subset := [r for r in data if r[feature] == v]) / n) * entropy(subset, label)
        for v in values
    )
    return base_entropy - weighted


def gain_ratio(data, feature, label="move"):
    """
    Ganho de informação normalizado pela entropia intrínseca da feature.
    Penaliza features com muitos valores distintos (evita overfitting em
    features de alta cardinalidade).
    """
    n = len(data)
    if n == 0:
        return 0
    ig = information_gain(data, feature, label)
    values = set(row[feature] for row in data)
    split_info = -sum(
        (len([r for r in data if r[feature] == v]) / n) *
        math.log2(len([r for r in data if r[feature] == v]) / n)
        for v in values
        if len([r for r in data if r[feature] == v]) > 0
    )
    if split_info == 0:
        return 0
    return ig / split_info


# ── Algoritmo ID3 com melhorias ────────────────────────────────────────────────

def id3(data, features, label="move", depth=0, max_depth=12, min_samples=5):
    """
    ID3 com:
    - Critério de paragem por min_samples (evita folhas com 1-2 exemplos)
    - Gain ratio em vez de information gain puro
    - majority_class guardado em cada nó para fallback robusto
    """
    classes = [row[label] for row in data]
    majority = Counter(classes).most_common(1)[0][0]

    # Paragem: só uma classe
    if len(set(classes)) == 1:
        return Node(label=classes[0])

    # Paragem: sem features, profundidade máx, ou amostras abaixo do mínimo
    if not features or depth >= max_depth or len(data) < min_samples:
        return Node(label=majority)

    # Escolhe a melhor feature por gain ratio
    best_feat = max(features, key=lambda f: gain_ratio(data, f, label))

    # Se o gain ratio for 0 (nenhuma feature ajuda), cria folha
    if gain_ratio(data, best_feat, label) <= 0:
        return Node(label=majority)

    node = Node(feature=best_feat)
    node.majority_class = majority

    values = set(row[best_feat] for row in data)
    remaining = [f for f in features if f != best_feat]

    for val in values:
        subset = [row for row in data if row[best_feat] == val]
        if not subset:
            node.children[val] = Node(label=majority)
        else:
            node.children[val] = id3(subset, remaining, label, depth + 1, max_depth, min_samples)

    return node


# ── Predição com fallback robusto ──────────────────────────────────────────────

def predict(node, row):
    """
    Navega a árvore. Se encontra um valor de feature não visto no treino,
    usa majority voting dos filhos existentes em vez de só o majority_class
    do nó — reduz o erro em estados não vistos.
    """
    if node.is_leaf():
        return node.label

    val = row.get(node.feature)

    if val not in node.children:
        # Fallback: voto maioritário dos labels de todos os filhos
        child_labels = _collect_labels(node)
        if child_labels:
            return Counter(child_labels).most_common(1)[0][0]
        return node.majority_class

    return predict(node.children[val], row)


def _collect_labels(node):
    """Recolhe recursivamente todos os labels nas folhas de um nó."""
    if node.is_leaf():
        return [node.label]
    labels = []
    for child in node.children.values():
        labels.extend(_collect_labels(child))
    return labels


# ── Carregamento do dataset ────────────────────────────────────────────────────

def load_dataset(filepath="dataset.csv"):
    data = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # As features estratégicas são strings (low/mid/high) ou ints pequenos
            processed = {}
            for k, v in row.items():
                if k == "move" or k == "phase" or k in ("center_adv", "lr_balance"):
                    processed[k] = v  # já são strings discretas
                else:
                    try:
                        processed[k] = int(v)
                    except ValueError:
                        processed[k] = v
            data.append(processed)
    return data


def train_tree(max_depth=12, min_samples=5, filepath="dataset.csv"):
    try:
        data = load_dataset(filepath)
        features = [f for f in data[0].keys() if f != "move"]
        tree = id3(data, features, label="move",
                   max_depth=max_depth, min_samples=min_samples)
        return tree, features
    except FileNotFoundError:
        return None, None


# ── Interface com o jogo ───────────────────────────────────────────────────────

def get_id3_move(state, tree, features):
    """
    Dado um estado do jogo, extrai as features estratégicas,
    percorre a árvore e devolve o movimento previsto.
    Verifica se o movimento é legal antes de o retornar.
    """
    state_dict = state_to_features(state)

    prediction = predict(tree, state_dict)
    if not prediction:
        return None

    try:
        col_str, action = prediction.split("_")
        move = (int(col_str), action)
    except (ValueError, AttributeError):
        return None

    # Verificação de legalidade: só devolve se o movimento for válido
    legal_moves = state.get_legal_moves()
    if move in legal_moves:
        return move

    # Se não for legal, escolhe o movimento legal com a mesma ação se possível
    same_action = [m for m in legal_moves if m[1] == action]
    if same_action:
        return same_action[len(same_action) // 2]  # coluna central disponível

    return legal_moves[0] if legal_moves else None
