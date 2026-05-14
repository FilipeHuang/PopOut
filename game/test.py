# Avaliação rápida — cola isto no Python interativo ou num ficheiro test.py
from id3_popout import load_dataset, predict, train_tree

data = load_dataset('dataset.csv')
features = [f for f in data[0].keys() if f != 'move']
tree, _ = train_tree(filepath='dataset.csv')

correct = 0
for row in data:
    pred = predict(tree, row)
    if pred == row['move']:
        correct += 1

accuracy = correct / len(data)
print(f'Accuracy no treino: {accuracy:.1%}')