import csv
import math
from collections import Counter

# Aplicar ID3 ao dataset iris como warm-up para validar a nossa implementação antes de a usar no PopOut.


# CARREGAR O DATASET 

def load_iris(filepath="iris.csv"):
    # Lê o ficheiro CSV e devolve uma lista de dicionários,
    # Cada dicionário representa uma flor com as suas medidas e classe.
    # A coluna ID é ignorada porque não tem valor preditivo.
    data = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "sepallength": float(row["sepallength"]),
                "sepalwidth":  float(row["sepalwidth"]),
                "petallength": float(row["petallength"]),
                "petalwidth":  float(row["petalwidth"]),
                "class":       row["class"]
            })
    return data


# DISCRETIZAÇÃO 

# O ID3 trabalha com atributos discretos (categóricos).
# Como o iris tem número contínuos, precisamos de os converter em categorias
# Fazemos isso dividindo o intervalo [min, max] de cada atributo em n_bins partes iguais.

def discretize(data, features, n_bins=3):
    # Calcula os limites de cada bin com base nos dados de treino e converte todos os valores numéricos em categorias.
    # É importante usar APENAS os dados de treino para calcular os limites,

    bin_labels = ["low", "mid", "high"] if n_bins == 3 else [f"b{i}" for i in range(n_bins)]
    thresholds = {}

    for feat in features:
        values = [row[feat] for row in data]
        min_v, max_v = min(values), max(values)
        step = (max_v - min_v) / n_bins
        # guarda os n_bins-1 limites que separam os bins
        thresholds[feat] = [min_v + step * i for i in range(1, n_bins)]

    disc_data = []
    for row in data:
        new_row = dict(row)
        for feat in features:
            # conta quantos limites o valor ultrapassa → determina o bin
            bin_idx = sum(row[feat] > t for t in thresholds[feat])
            new_row[feat] = bin_labels[bin_idx]
        disc_data.append(new_row)

    return disc_data, thresholds, bin_labels

def discretize_row(row, features, thresholds, bin_labels):
    # Versão que discretiza um único exemplo (usada na predição do conjunto de teste)
    new_row = dict(row)
    for feat in features:
        bin_idx = sum(row[feat] > t for t in thresholds[feat])
        new_row[feat] = bin_labels[bin_idx]
    return new_row


# ENTROPIA E GANHO DE INFORMAÇÃO 

# Se todos os exemplos têm a mesma classe, a entropia é 0 (conjunto puro).
# Se as classes estão igualmente distribuídas, a entropia é máxima.
# Aplicar formula da entropia

def entropy(data, label="class"):
    n = len(data)
    if n == 0:
        return 0
    counts = Counter(row[label] for row in data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c > 0)

def information_gain(data, feature, label="class"):
    # O ganho de informação mede o quanto um atributo reduz a entropia do conjunto.
    # Escolhemos sempre o atributo com maior ganho para dividir o nó.
    # Aplicar formula de entropia - weihted
    n = len(data)
    base_entropy = entropy(data, label)
    values = set(row[feature] for row in data)
    weighted = sum(
        (len(subset := [r for r in data if r[feature] == v]) / n) * entropy(subset, label)
        for v in values
    )
    return base_entropy - weighted


# ESTRUTURA DA ÁRVORE 

# Cada nó da árvore é um objeto Node.
# Nós internos têm um atributo e filhos 
# Folhas têm apenas uma classe 

class Node:
    def __init__(self, feature=None, label=None):
        self.feature = feature   # atributo usado para dividir (None se for folha)
        self.label = label       # classe prevista (None se for no interno)
        self.children = {}       # valor_do_atributo: Node filho 

    def is_leaf(self):
        return self.label is not None


# CONSTRUÇÃO DA ÁRVORE (ID3) 

def id3(data, features, label="class", depth=0, max_depth=10):

    # Em cada chamada:
    #   1. Verifica caso base
    #   2. Escolhe o melhor atributo pelo maior IG
    #   3. Divide o conjunto por valor do atributo
    #   4. Chamada recursivamente para cada subconjunto

    classes = [row[label] for row in data]
    majority = Counter(classes).most_common(1)[0][0]

    # Paragem 1: todos os exemplos têm a mesma classe → folha pura
    if len(set(classes)) == 1:
        return Node(label=classes[0])

    # Paragem 2: sem atributos disponíveis ou profundidade máxima → folha com classe maioritária
    if not features or depth >= max_depth:
        return Node(label=majority)

    # Escolhe o atributo que maximiza o ganho de informação
    best_feat = max(features, key=lambda f: information_gain(data, f, label))
    node = Node(feature=best_feat)

    values = set(row[best_feat] for row in data)
    remaining = [f for f in features if f != best_feat]

    for val in values:
        subset = [row for row in data if row[best_feat] == val]
        if not subset:
            # Subconjunto vazio → folha com classe maioritária do pai
            node.children[val] = Node(label=majority)
        else:
            node.children[val] = id3(subset, remaining, label, depth + 1, max_depth)

    return node


# PREDIÇÃO 

def predict(node, row):
    # Percorre a árvore do topo até uma folha, seguindo os valores do exemplo.
    # Se encontrar um valor desconhecido (não visto no treino), usa o primeiro filho como fallback para não quebrar.
    if node.is_leaf():
        return node.label
    val = row.get(node.feature)
    if val not in node.children:
        return predict(list(node.children.values())[0], row)
    return predict(node.children[val], row)


# VISUALIZAÇÃO 

def print_tree(node, indent=0, branch=""):
    # Imprime a árvore em formato de texto indentado para visualização.
    prefix = "    " * indent
    if branch:
        print(prefix + f"[{branch}]")
    if node.is_leaf():
        print(prefix + f"  - CLASS: {node.label}")
    else:
        print(prefix + f"  SPLIT ON: {node.feature}")
        for val, child in sorted(node.children.items()):
            print_tree(child, indent + 1, val)


# ── AVALIAÇÃO ─────────────────────────────────────────────────────────────────

def train_test_split(data, test_ratio=0.2, seed=42):
    # Divide o dataset em treino e teste de forma aleatória mas reprodutível (seed fixa).
    # Usamos 80% para treino e 20% para teste (por convenção, apesar auq aumentar o test_ratio pode dar resultados com melhor precisão, mas isso resulta em overfitting).
    import random
    random.seed(seed)
    shuffled = data[:]
    random.shuffle(shuffled)
    split = int(len(shuffled) * (1 - test_ratio))
    return shuffled[:split], shuffled[split:]

def evaluate(tree, test_data, thresholds, bin_labels, features):
    # Avalia a árvore no conjunto de teste.
    # Para cada exemplo, discretiza com os limiares do treino e prediz a classe.
    correct = 0
    for row in test_data:
        disc = discretize_row(row, features, thresholds, bin_labels)
        pred = predict(tree, disc)
        if pred == row["class"]:
            correct += 1
    return correct / len(test_data)


# MAIN

if __name__ == "__main__":
    FEATURES = ["sepallength", "sepalwidth", "petallength", "petalwidth"]

    data = load_iris("iris.csv")
    print(f"Exemplos carregados: {len(data)}")

    # Split 80/20 com seed fixa(igaul à de cima) para resultados reprodutíveis
    train, test = train_test_split(data, test_ratio=0.2)
    print(f"Treino: {len(train)} | Teste: {len(test)}")

    # Discretiza usando APENAS os dados de treino para evitar data leakage
    disc_train, thresholds, bin_labels = discretize(train, FEATURES, n_bins=3)

    # Treina a árvore ID3
    tree = id3(disc_train, FEATURES, label="class", max_depth=10)

    # Mostra a árvore em texto
    print("\n=== ÁRVORE DE DECISÃO ===")
    print_tree(tree)

    # Avalia no conjunto de teste
    acc = evaluate(tree, test, thresholds, bin_labels, FEATURES)
    print(f"\nPrecisão no teste: {acc * 100:.1f}%")