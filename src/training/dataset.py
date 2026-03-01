import torch
from torch.utils.data import DataLoader, Dataset

from src.data.preprocessing import build_vocabulary, tokenize


def char_to_token_index(context, tokens, char_idx):
    current = 0
    for i, tok in enumerate(tokens):
        start = context.lower().find(tok, current)
        if start == -1:
            start = current
        end = start + len(tok)
        if start <= char_idx < end:
            return i
        current = end
    return len(tokens) - 1


class QADataset(Dataset):
    def __init__(self, examples, vocab, max_context_len=400, max_question_len=60):
        self.vocab = vocab
        self.max_context_len = max_context_len
        self.max_question_len = max_question_len
        self.samples = []

        for ex in examples:
            if ex.is_impossible or len(ex.answers) == 0:
                continue

            context_tokens = tokenize(ex.context)
            question_tokens = tokenize(ex.question)

            if len(context_tokens) == 0 or len(question_tokens) == 0:
                continue

            answer_text = ex.answers[0]["text"]
            answer_start_char = ex.answers[0]["answer_start"]
            answer_end_char = answer_start_char + len(answer_text)

            start_token = char_to_token_index(ex.context, context_tokens, answer_start_char)
            end_token = char_to_token_index(ex.context, context_tokens, answer_end_char - 1)

            if start_token >= max_context_len or end_token >= max_context_len:
                continue

            context_tokens = context_tokens[:max_context_len]
            question_tokens = question_tokens[:max_question_len]

            self.samples.append(
                {
                    "context_tokens": context_tokens,
                    "question_tokens": question_tokens,
                    "start_idx": start_token,
                    "end_idx": end_token,
                }
            )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        unk = self.vocab.get("<UNK>", 1)

        c_ids = [self.vocab.get(t, unk) for t in sample["context_tokens"]]
        q_ids = [self.vocab.get(t, unk) for t in sample["question_tokens"]]

        return {
            "context_ids": torch.tensor(c_ids, dtype=torch.long),
            "question_ids": torch.tensor(q_ids, dtype=torch.long),
            "context_mask": torch.ones(len(c_ids), dtype=torch.bool),
            "question_mask": torch.ones(len(q_ids), dtype=torch.bool),
            "start_idx": torch.tensor(sample["start_idx"], dtype=torch.long),
            "end_idx": torch.tensor(sample["end_idx"], dtype=torch.long),
        }


def collate_fn(batch):
    max_c = max(item["context_ids"].size(0) for item in batch)
    max_q = max(item["question_ids"].size(0) for item in batch)

    context_ids = []
    question_ids = []
    context_masks = []
    question_masks = []
    starts = []
    ends = []

    for item in batch:
        c_len = item["context_ids"].size(0)
        q_len = item["question_ids"].size(0)

        c_padded = torch.zeros(max_c, dtype=torch.long)
        c_padded[:c_len] = item["context_ids"]
        context_ids.append(c_padded)

        q_padded = torch.zeros(max_q, dtype=torch.long)
        q_padded[:q_len] = item["question_ids"]
        question_ids.append(q_padded)

        c_mask = torch.zeros(max_c, dtype=torch.bool)
        c_mask[:c_len] = True
        context_masks.append(c_mask)

        q_mask = torch.zeros(max_q, dtype=torch.bool)
        q_mask[:q_len] = True
        question_masks.append(q_mask)

        starts.append(item["start_idx"])
        ends.append(item["end_idx"])

    return {
        "context_ids": torch.stack(context_ids),
        "question_ids": torch.stack(question_ids),
        "context_mask": torch.stack(context_masks),
        "question_mask": torch.stack(question_masks),
        "start_idx": torch.stack(starts),
        "end_idx": torch.stack(ends),
    }


def build_vocab_from_dataset(dataset, min_freq=2, max_size=50000):
    texts = []
    for ex in dataset.examples:
        texts.append(ex.context)
        texts.append(ex.question)
    return build_vocabulary(texts, min_freq=min_freq, max_size=max_size)


def create_dataloader(
    examples, vocab, batch_size=32, shuffle=True, max_context_len=400, max_question_len=60
):
    ds = QADataset(examples, vocab, max_context_len, max_question_len)
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, collate_fn=collate_fn)
