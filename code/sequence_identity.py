import os
import re

def is_nucleic_sequence(seq):
    nucleic_chars = {'A', 'T', 'C', 'G', 'U'}
    seq_upper = seq.upper()
    for char in seq_upper:
        if char not in nucleic_chars:
            return False
    return True

def parse_fasta(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    entries = re.split(r'>', content)[1:]
    chains = []
    for entry in entries:
        lines = entry.split('\n')
        if not lines:
            continue
        header = lines[0].strip()
        seq = ''.join(line.strip() for line in lines[1:] if line.strip())
        if not seq:
            continue
        chains.append((header, seq))
    return chains

def get_representative_seqs(chains):
    protein_seqs = []
    nucleic_seqs = []
    for header, seq in chains:
        if is_nucleic_sequence(seq):
            nucleic_seqs.append(seq)
        else:
            protein_seqs.append(seq)
    rep_protein = max(protein_seqs, key=len) if protein_seqs else None
    rep_nucleic = max(nucleic_seqs, key=len) if nucleic_seqs else None
    return rep_protein, rep_nucleic

def process_directory(directory):
    file_data = {}
    for filename in os.listdir(directory):
        if filename.endswith('.fasta'):
            file_id = filename.split('.')[0]
            file_path = os.path.join(directory, filename)
            chains = parse_fasta(file_path)
            rep_protein, rep_nucleic = get_representative_seqs(chains)
            file_data[file_id] = {
                'protein': rep_protein,
                'nucleic': rep_nucleic
            }
    return file_data

def calculate_identity(seq1, seq2):
    if seq1 is None or seq2 is None:
        return 0.0
    if len(seq1) != len(seq2):
        return 0.0
    match = 0
    for a, b in zip(seq1.upper(), seq2.upper()):
        if a == b:
            match += 1
    return (match / len(seq1)) * 100 if len(seq1) > 0 else 0.0

def find_similar_pairs(file_data, threshold=40):
    similar_pairs = []
    file_ids = list(file_data.keys())
    for i in range(len(file_ids)):
        id1 = file_ids[i]
        data1 = file_data[id1]
        for j in range(i + 1, len(file_ids)):
            id2 = file_ids[j]
            data2 = file_data[id2]
            protein_identity = calculate_identity(data1['protein'], data2['protein'])
            nucleic_identity = calculate_identity(data1['nucleic'], data2['nucleic'])
            if protein_identity > threshold or nucleic_identity > threshold:
                similar_pairs.append((id1, id2, protein_identity, nucleic_identity))
    return similar_pairs

def main():
    directory = '/Users/wangyuxuan/Desktop/data/fasta/all'
    file_data = process_directory(directory)
    similar_pairs = find_similar_pairs(file_data, 40)
    print("Similar pairs with sequence identity >40%:")
    for pair in similar_pairs:
        id1, id2, p_ident, n_ident = pair
        reasons = []
        if p_ident > 40:
            reasons.append(f"protein: {p_ident:.2f}%")
        if n_ident > 40:
            reasons.append(f"nucleic: {n_ident:.2f}%")
        print(f"{id1} and {id2} ({', '.join(reasons)})")

if __name__ == '__main__':
    main()