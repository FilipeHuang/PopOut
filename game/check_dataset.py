import csv
from collections import Counter

def check_dataset(filepath="dataset.csv"):
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    print(f"=== DATASET REPORT ===")
    print(f"Total de exemplos: {len(rows)}")
    print(f"Número de colunas: {len(header)}")

    # Verifica linhas com colunas a menos
    bad_rows = [i for i, r in enumerate(rows) if len(r) != len(header)]
    if bad_rows:
        print(f"⚠️  Linhas com erro: {bad_rows}")
    else:
        print(f"✅ Todas as linhas têm {len(header)} colunas")

    # Distribuição das jogadas
    moves = [r[-1] for r in rows]
    counter = Counter(moves)
    print(f"\nDistribuição de jogadas (top 10):")
    for move, count in counter.most_common(10):
        bar = "█" * (count // 50)
        print(f"  {move:12s} → {count:5d}  {bar}")

    # Verifica valores inválidos no tabuleiro
    invalid = 0
    for row in rows:
        for cell in row[:42]:
            if cell not in ['0', '1', '2']:
                invalid += 1
    if invalid:
        print(f"\n⚠️  Células com valor inválido: {invalid}")
    else:
        print(f"\n✅ Todos os valores do tabuleiro são válidos (0, 1, 2)")

    # Distribuição por jogador
    players = [r[42] for r in rows]
    player_count = Counter(players)
    print(f"\nDistribuição por jogador:")
    for p, count in player_count.items():
        print(f"  Jogador {p}: {count} exemplos")

    # Verifica duplicados
    all_states = [tuple(r[:-1]) for r in rows]
    duplicates = len(all_states) - len(set(all_states))
    if duplicates:
        print(f"\n⚠️  Estados duplicados encontrados: {duplicates}")
    else:
        print(f"\n✅ Nenhum estado duplicado")

if __name__ == "__main__":
    check_dataset("dataset.csv")