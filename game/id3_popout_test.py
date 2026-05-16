import random
from id3_popout import load_dataset, predict, predict_top_k, id3
# change the name of the file if want to test other datasets from '/data' folder
data = load_dataset('data/dataset_facil.csv')

random.seed(42)
random.shuffle(data)

split_index = int(len(data) * 0.8)
train_data = data[:split_index]
test_data = data[split_index:]

features = [f for f in data[0].keys() if f != 'move']

def evaluate(node, dataset):
    if not dataset: return 0, 0
    correct_top1 = 0
    correct_top2 = 0
    for row in dataset:
        pred_1 = predict(node, row)
        preds_k = predict_top_k(node, row, k=2)
        if pred_1 == row['move']: correct_top1 += 1
        if row['move'] in preds_k: correct_top2 += 1
    return correct_top1 / len(dataset), correct_top2 / len(dataset)

print(f"=== Avaliação ID3 (Top-1 vs Top-2) ===")
print(f"Total: {len(data)} | Treino: {len(train_data)} | Teste: {len(test_data)}\n")

print(f"{'Max Depth':<10} | {'Min Samples':<12} | {'Top-1 Teste':<12} | {'Top-2 Teste':<12}")
print("-" * 55)

best_top2 = 0
best_top1 = 0
best_config = (None, None)

profundidades = [5, 7, 9, 12, 15]
amostras_minimas = [5, 10, 20]

for depth in profundidades:
    for min_s in amostras_minimas:
        tree = id3(train_data, features, max_depth=depth, min_samples=min_s)
        
        top1_test, top2_test = evaluate(tree, test_data)
        
        print(f"{depth:<10} | {min_s:<12} | {top1_test:<11.1%} | {top2_test:<11.1%}")
        
        if top2_test > best_top2 or (top2_test == best_top2 and top1_test > best_top1):
            best_top2 = top2_test
            best_top1 = top1_test
            best_config = (depth, min_s)

print("-" * 55)
print(f"🏆 MELHOR CONFIGURAÇÃO ENCONTRADA:")
print(f"   Max Depth   = {best_config[0]}")
print(f"   Min Samples = {best_config[1]}")
print(f"   Precisão Top-1 = {best_top1:.1%}")
print(f"   Precisão Top-2 = {best_top2:.1%}")
