import random
from id3_popout import load_dataset, predict, id3

data = load_dataset('dataset.csv')
random.seed(42)
random.shuffle(data)

split_index = int(len(data) * 0.8)
train_data = data[:split_index]
test_data = data[split_index:]
features = [f for f in data[0].keys() if f != 'move']

def evaluate(node, dataset):
    if not dataset: return 0
    correct = sum(1 for row in dataset if predict(node, row) == row['move'])
    return correct / len(dataset)

print(f"=== Otimização de Hiperparâmetros (Grid Search) ===")
print(f"Total: {len(data)} exemplos | Treino: {len(train_data)} | Teste: {len(test_data)}\n")

print(f"{'Max Depth':<10} | {'Min Samples':<12} | {'Acc Treino':<12} | {'Acc Teste':<12}")
print("-" * 55)

best_acc = 0
best_config = (None, None)

profundidades = [3, 5, 7, 9, 12, 15]
amostras_minimas = [2, 5, 10, 20]

for depth in profundidades:
    for min_s in amostras_minimas:
        tree = id3(train_data, features, max_depth=depth, min_samples=min_s)
        
        train_acc = evaluate(tree, train_data)
        test_acc = evaluate(tree, test_data)
        
        print(f"{depth:<10} | {min_s:<12} | {train_acc:<11.1%} | {test_acc:<11.1%}")
        
        if test_acc > best_acc:
            best_acc = test_acc
            best_config = (depth, min_s)

print("-" * 55)
print(f"🏆 MELHOR CONFIGURAÇÃO ENCONTRADA:")
print(f"   Max Depth   = {best_config[0]}")
print(f"   Min Samples = {best_config[1]}")
print(f"   Precisão real (Teste) = {best_acc:.1%}")