import torch
import torch.nn as nn
import torch.nn.functional as F


class EmbeddingLayer(nn.Module):
    """
    Standard Word Embedding layer.
    Converts token indices into dense word vectors.
    """

    def __init__(self, vocab_size: int, embedding_dim: int, dropout: float = 0.2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (batch_size, seq_len) containing token indices.
        Returns:
            Tensor of shape (batch_size, seq_len, embedding_dim).
        """
        return self.dropout(self.embedding(x))


class RNNEncoder(nn.Module):
    """
    Contextual Embedding Layer using a Bidirectional LSTM.
    Encodes the local interactions between words.
    """

    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int = 1, dropout: float = 0.2):
        super().__init__()
        self.rnn = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (batch_size, seq_len, input_dim).
            mask: Optional Tensor of shape (batch_size, seq_len) boolean mask where
            True/1 indicates valid tokens.
        Returns:
            Tensor of shape (batch_size, seq_len, 2 * hidden_dim).
        """
        # Note: For production, pack_padded_sequence can be implemented here using the mask
        # to skip padding tokens computation. For simplicity, we pass padded tensors.
        outputs, _ = self.rnn(x)
        return self.dropout(outputs)


class BiDAFAttention(nn.Module):
    """
    Bi-Directional Attention Flow mechanism.
    Computes Context-to-Query (C2Q) and Query-to-Context (Q2C) attention.
    """

    def __init__(self, hidden_dim: int):
        super().__init__()
        # The similarity function alpha(c, q) = w^T [c; q; c \odot q]
        # Since c and q are outputs from a BiLSTM, their dimension is 2 * rnn_hidden_dim
        # So the concatenated input to the linear layer is
        # 3 * (2 * rnn_hidden_dim) = 6 * rnn_hidden_dim
        self.W = nn.Linear(3 * hidden_dim, 1, bias=False)

    def forward(
        self,
        context: torch.Tensor,
        query: torch.Tensor,
        context_mask: torch.Tensor = None,
        query_mask: torch.Tensor = None,
    ) -> torch.Tensor:
        """
        Args:
            context: Tensor of shape (batch_size, c_len, hidden_dim)
            query: Tensor of shape (batch_size, q_len, hidden_dim)
            context_mask: Optional boolean Tensor of shape (batch_size, c_len) where 1 indicates
            valid context token.
            query_mask: Optional boolean Tensor of shape (batch_size, q_len) where 1 indicates valid
            query token.
        Returns:
            Tensor of shape (batch_size, c_len, 4 * hidden_dim) representing the query-aware context
            representation.
        """
        batch_size, c_len, hidden_dim = context.size()
        q_len = query.size(1)

        # 1. Similarity Matrix Calculation
        # Repeat context and query to form (batch_size, c_len, q_len, hidden_dim) tensors
        c_repeated = context.unsqueeze(2).expand(-1, -1, q_len, -1)
        q_repeated = query.unsqueeze(1).expand(-1, c_len, -1, -1)
        cq_multiplied = c_repeated * q_repeated

        concatenated = torch.cat([c_repeated, q_repeated, cq_multiplied], dim=-1)
        S = self.W(concatenated).squeeze(-1)  # (batch_size, c_len, q_len)

        # Apply masks to similarities
        if query_mask is not None:
            # Mask padded query tokens (columns)
            mask_q = query_mask.unsqueeze(1).expand(-1, c_len, -1)
            S = S.masked_fill(mask_q == 0, -1e9)

        # 2. Context-to-Query (C2Q) Attention
        # Which query words are most relevant to each context word?
        a = F.softmax(S, dim=-1)  # (batch_size, c_len, q_len)
        c2q = torch.bmm(a, query)  # (batch_size, c_len, hidden_dim)

        # 3. Query-to-Context (Q2C) Attention
        # Which context words have the closest similarity to one of the query words?
        if context_mask is not None:
            # Mask padded context tokens (rows) for the max operation
            mask_c = context_mask.unsqueeze(2).expand(-1, -1, q_len)
            S_for_q2c = S.masked_fill(mask_c == 0, -1e9)
        else:
            S_for_q2c = S

        max_q = torch.max(S_for_q2c, dim=-1)[0]  # (batch_size, c_len)
        if context_mask is not None:
            max_q = max_q.masked_fill(context_mask == 0, -1e9)

        b = F.softmax(max_q, dim=-1)  # (batch_size, c_len)
        q2c = torch.bmm(b.unsqueeze(1), context)  # (batch_size, 1, hidden_dim)
        q2c = q2c.expand(-1, c_len, -1)  # (batch_size, c_len, hidden_dim)

        # 4. Final Megre
        # G_i = [c_i; c2q_i; c_i \odot c2q_i; c_i \odot q2c_i]
        G = torch.cat(
            [context, c2q, context * c2q, context * q2c], dim=-1
        )  # (batch_size, c_len, 4 * hidden_dim)

        return G


class OutputLayer(nn.Module):
    """
    Predicts the Start Index and End Index logits over the context sequence.
    """

    def __init__(self, hidden_dim: int):
        super().__init__()
        # hidden_dim here corresponds to the output of the Modeling Layer
        self.start_linear = nn.Linear(hidden_dim, 1)
        self.end_linear = nn.Linear(hidden_dim, 1)

    def forward(self, m: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            m: Modeling layer output of shape (batch_size, seq_len, hidden_dim)
        Returns:
            Tuple of start_logits, end_logits each of shape (batch_size, seq_len)
        """
        start_logits = self.start_linear(m).squeeze(-1)
        end_logits = self.end_linear(m).squeeze(-1)
        return start_logits, end_logits


class QAModel(nn.Module):
    """
    Main PyTorch QA Model combining Embedding, Encoding, Attention, Modeling, and Output.
    Inspired by the BiDAF (Bi-Directional Attention Flow) architecture.
    """

    def __init__(
        self, vocab_size: int, embedding_dim: int = 100, hidden_dim: int = 128, dropout: float = 0.2
    ):
        super().__init__()

        # Output of BiLSTM will be 2 * hidden_dim
        encoder_out_dim = 2 * hidden_dim

        # 1. Word Embedding Layer
        self.embedding = EmbeddingLayer(vocab_size, embedding_dim, dropout)

        # 2. Contextual Embedding Layer (Encoder)
        # Shared weights for both Context and Query encoding
        self.encoder = RNNEncoder(embedding_dim, hidden_dim, num_layers=1, dropout=dropout)

        # 3. Attention Flow Layer
        self.attention = BiDAFAttention(hidden_dim=encoder_out_dim)

        # 4. Modeling Layer
        # Input is 4 * encoder_out_dim (due to concatenation in Attention layer)
        attention_out_dim = 4 * encoder_out_dim
        self.modeling = RNNEncoder(attention_out_dim, hidden_dim, num_layers=2, dropout=dropout)

        # 5. Output Layer
        # BiLSTM outputs 2 * hidden_dim
        self.output = OutputLayer(hidden_dim=encoder_out_dim)

    def forward(
        self,
        context: torch.Tensor,
        query: torch.Tensor,
        context_mask: torch.Tensor = None,
        query_mask: torch.Tensor = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            context: Tensor of shape (batch_size, c_len) containing word indices.
            query: Tensor of shape (batch_size, q_len) containing word indices.
            context_mask: Binary Tensor (1/0) of shape (batch_size, c_len) for valid context tokens.
            query_mask: Binary Tensor (1/0) of shape (batch_size, q_len) for valid query tokens.
        Returns:
            Tuple containing Start Index Logits and End Index Logits.
        """
        # 1. Embeddings
        c_emb = self.embedding(context)
        q_emb = self.embedding(query)

        # 2. Contextual Encoding
        c_enc = self.encoder(c_emb, mask=context_mask)
        q_enc = self.encoder(q_emb, mask=query_mask)

        # 3. Context-Query Attention
        g = self.attention(c_enc, q_enc, context_mask=context_mask, query_mask=query_mask)

        # 4. Modeling Interaction
        m = self.modeling(g, mask=context_mask)

        # 5. Compute Logits
        start_logits, end_logits = self.output(m)

        # Apply mask to logits before returning so padded tokens cannot be selected
        if context_mask is not None:
            # -1e9 acts as -infinity for softmax
            start_logits = start_logits.masked_fill(context_mask == 0, -1e9)
            end_logits = end_logits.masked_fill(context_mask == 0, -1e9)

        return start_logits, end_logits
