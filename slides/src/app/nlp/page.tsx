"use client";

import Presentation from "../../components/Presentation";
import {
    Slide,
    DiagramFlow,
    DiagramFlowVertical,
    Table,
    Bullet,
    SectionLabel,
} from "../../components/PresentationSlideUI";

function buildSlides(): Slide[] {
    return [
        /* ── 1. Title ── */
        {
            tag: "NLP Final Project",
            tagColor: "badge-indigo",
            title: "",
            content: (
                <div className="flex flex-col items-center justify-center text-center py-4">
                    <h1 className="text-4xl md:text-5xl font-bold mb-3">
                        <span className="bg-gradient-to-r from-indigo-300 via-purple-300 to-pink-300 bg-clip-text text-transparent">
                            Closed-Domain Question Answering
                        </span>
                    </h1>
                    <h2 className="text-xl md:text-2xl text-white/80 font-light mb-6">
                        with BiDAF on SQuAD 2.0
                    </h2>
                    <div className="flex gap-2 flex-wrap justify-center mb-6">
                        <span className="badge badge-indigo">Alon DEBASC</span>
                        <span className="badge badge-purple">Axel STOLTZ</span>
                        <span className="badge badge-emerald">Thibault CHESNEL</span>
                    </div>
                    <p className="text-slate-600 text-xs">
                        Natural Language Processing — M2 EFREI — March 2026
                    </p>
                </div>
            ),
            notes: "Good morning. Today we'll present our work on building a neural question answering system. Our system takes a paragraph and a question as input and extracts the answer directly from the text, using an architecture called BiDAF trained on Stanford's SQuAD 2.0 dataset.",
        },

        /* ── 2. Agenda ── */
        {
            tag: "Overview",
            tagColor: "badge-indigo",
            title: "Agenda",
            content: (
                <div className="space-y-2 py-2">
                    {[
                        { n: "01", label: "Problem Definition & Task Framing" },
                        { n: "02", label: "Dataset: SQuAD 2.0" },
                        { n: "03", label: "Data Preprocessing Pipeline" },
                        { n: "04", label: "Model Architecture: BiDAF" },
                        { n: "05", label: "BiDAF Attention Deep-Dive" },
                        { n: "06", label: "Training Strategy" },
                        { n: "07", label: "Evaluation & Results" },
                        { n: "08", label: "Live Demonstration" },
                        { n: "09", label: "Conclusion" },
                    ].map((item) => (
                        <div key={item.n} className="flex items-center gap-3 py-1 group">
                            <span className="text-xs font-mono text-indigo-500/60 w-6">{item.n}</span>
                            <span className="text-sm text-slate-300 group-hover:text-white transition-colors">{item.label}</span>
                        </div>
                    ))}
                </div>
            ),
            notes: "Here's the roadmap for our presentation. We'll start by defining the problem, explain how we prepared the data, deep-dive into every layer of our model, show our training setup, and end with results and a live demo.",
        },

        /* ── 3. Problem Definition ── */
        {
            tag: "Context",
            tagColor: "badge-indigo",
            title: "Problem Definition",
            content: (
                <div>
                    <DiagramFlow items={["📄 Context", "❓ Question", "🤖 QA Model", "✅ Answer Span"]} />
                    <div className="mt-4 space-y-1">
                        <Bullet icon="●"><strong className="text-white">Closed-Domain QA</strong> — answer comes <em>from</em> the provided text</Bullet>
                        <Bullet icon="●"><strong className="text-white">Factoid Questions</strong> — short, fact-based (who, what, where, when)</Bullet>
                        <Bullet icon="●"><strong className="text-white">Extractive</strong> — the answer is a contiguous token span in the context</Bullet>
                    </div>
                    <div className="glass rounded-xl p-4 mt-4">
                        <SectionLabel>Example</SectionLabel>
                        <p className="text-xs text-slate-400 leading-relaxed mb-2">
                            <strong className="text-slate-300">Context:</strong> &quot;The Louvre Museum is located in <span className="text-amber-300 font-semibold">Paris, France</span>. It is the world&apos;s largest art museum.&quot;
                        </p>
                        <p className="text-xs text-slate-400">
                            <strong className="text-slate-300">Question:</strong> &quot;Where is the Louvre Museum located?&quot; → <span className="text-emerald-400 font-semibold">&quot;Paris, France&quot;</span>
                        </p>
                    </div>
                </div>
            ),
            notes: "Our task is closed-domain factoid question answering. Unlike open-domain QA, we don't need external knowledge — the answer is always a substring of the context paragraph. This means our model needs to learn to identify where the answer starts and ends within the text. This is fundamentally a span extraction problem.",
        },

        /* ── 4. Dataset ── */
        {
            tag: "Data",
            tagColor: "badge-emerald",
            title: "SQuAD 2.0 Dataset",
            content: (
                <div>
                    <div className="grid grid-cols-2 gap-3 mb-4">
                        {[
                            { label: "Articles", value: "500+", sub: "from Wikipedia" },
                            { label: "Questions", value: "~150k", sub: "total" },
                            { label: "Answerable", value: "~87k", sub: "with answer span" },
                            { label: "Unanswerable", value: "~50k", sub: "is_impossible=true" },
                        ].map((s) => (
                            <div key={s.label} className="glass rounded-xl p-3 text-center">
                                <div className="text-2xl font-bold bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent">{s.value}</div>
                                <div className="text-xs text-slate-400 mt-1">{s.label}</div>
                                <div className="text-[10px] text-slate-600">{s.sub}</div>
                            </div>
                        ))}
                    </div>
                    <div className="glass rounded-xl p-4">
                        <SectionLabel color="emerald">JSON Structure</SectionLabel>
                        <div className="code-block text-[11px]">
                            <div className="text-slate-500">{"{"} data: [{"{"}</div>
                            <div className="pl-4 text-purple-300">title: <span className="text-emerald-300">&quot;Normans&quot;</span>,</div>
                            <div className="pl-4 text-purple-300">paragraphs: [{"{"}</div>
                            <div className="pl-8 text-blue-300">context: <span className="text-emerald-300">&quot;The Normans were...&quot;</span>,</div>
                            <div className="pl-8 text-blue-300">qas: [{"{"}</div>
                            <div className="pl-12 text-amber-300">question: <span className="text-emerald-300">&quot;When were the...?&quot;</span>,</div>
                            <div className="pl-12 text-amber-300">is_impossible: <span className="text-indigo-300">false</span>,</div>
                            <div className="pl-12 text-amber-300">answers: [{"{"} text: <span className="text-emerald-300">&quot;10th century&quot;</span>, answer_start: <span className="text-indigo-300">94</span> {"}"}]</div>
                            <div className="pl-8 text-slate-500">{"}"}]</div>
                            <div className="pl-4 text-slate-500">{"}"}]</div>
                            <div className="text-slate-500">{"}"}]{"}"}</div>
                        </div>
                    </div>
                </div>
            ),
            notes: "SQuAD 2.0 is the standard benchmark for extractive QA. What makes v2.0 special compared to v1.1 is the addition of unanswerable questions — questions that look plausible but have no answer in the text. For our training, we focus on the answerable subset since factoid QA is our goal. Each answer comes with an answer_start index telling us exactly where the answer starts in the context — this is our ground truth for training.",
        },

        /* ── 5. Preprocessing ── */
        {
            tag: "Pipeline",
            tagColor: "badge-amber",
            title: "Data Preprocessing Pipeline",
            content: (
                <div>
                    <DiagramFlowVertical items={[
                        { label: "📄 Raw SQuAD JSON", sub: "train-v2.0.json / dev-v2.0.json" },
                        { label: "🔍 Parse & Extract Triplets", sub: "(context, question, answers)" },
                        { label: "🔀 Filter Answerable Only", sub: "is_impossible = false" },
                        { label: "🧹 Clean Text", sub: "Unicode normalization, whitespace collapse" },
                        { label: "✂️ Tokenize", sub: "Whitespace + punctuation regex split" },
                        { label: "📖 Build Vocabulary", sub: "word → index (50k max, min_freq=2)" },
                        { label: "🔢 Convert to Index Tensors", sub: "Pad to max_context=400, max_question=60" },
                    ]} />
                    <div className="flex gap-2 mt-3 justify-center">
                        <span className="badge badge-amber">⟨PAD⟩ = 0</span>
                        <span className="badge badge-amber">⟨UNK⟩ = 1</span>
                    </div>
                </div>
            ),
            notes: "Here's our full preprocessing pipeline. Starting from the raw JSON, we parse out each context-question-answer triplet and discard unanswerable questions. Then we clean the text — normalizing unicode characters and collapsing whitespace. Tokenization is a regex-based split that separates words and punctuation. We then build a vocabulary from the training set, mapping each word to an integer index. Rare words below frequency 2 become UNK. Finally, we convert everything into padded tensors. Context is capped at 400 tokens and questions at 60.",
        },

        /* ── 6. Why BiDAF ── */
        {
            tag: "Design Choice",
            tagColor: "badge-purple",
            title: "Why BiDAF?",
            content: (
                <div>
                    <div className="glass rounded-xl p-4 mb-4">
                        <p className="text-sm text-slate-300 leading-relaxed">
                            <strong className="text-white">Key insight:</strong> In QA, the model must understand the <em>interaction</em> between context and question — not just each independently.
                        </p>
                    </div>
                    <Table
                        headers={["Approach", "Limitation"]}
                        rows={[
                            ["Bag-of-Words", "No word order, no context interaction"],
                            ["Simple LSTM", "Encodes C and Q separately, late interaction"],
                            ["Attention (unidirectional)", "Misses part of the C↔Q relationship"],
                            ["BiDAF ✅", "Bi-directional: captures C→Q AND Q→C"],
                        ]}
                        highlight={3}
                    />
                    <div className="mt-4 space-y-1">
                        <Bullet icon="1.">Attention flows in <strong className="text-white">both directions</strong></Bullet>
                        <Bullet icon="2.">Computed at <strong className="text-white">each time step</strong> (no early summarization)</Bullet>
                        <Bullet icon="3."><strong className="text-white">Full context</strong> representation reaches the output layer</Bullet>
                    </div>
                </div>
            ),
            notes: "Why did we choose BiDAF over simpler approaches? The core challenge in QA is understanding the relationship between the question and the context. Simple encoders treat them independently. Standard attention goes in one direction — usually context attends to the query. BiDAF adds the reverse: it also asks 'which context words are most relevant to the query as a whole?' This bi-directional flow gives the model a much richer understanding. BiDAF was published by Seo et al. in 2017 and achieved state-of-the-art results on SQuAD at the time.",
        },

        /* ── 7. Architecture Overview ── */
        {
            tag: "Model",
            tagColor: "badge-purple",
            title: "BiDAF Architecture — Overview",
            content: (
                <div>
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1">
                            <DiagramFlowVertical items={[
                                { label: "① Word Embedding", sub: "nn.Embedding → 100-dim + Dropout" },
                                { label: "② Contextual Encoding", sub: "Shared BiLSTM → 256-dim" },
                                { label: "③ Attention Flow", sub: "BiDAF: C2Q + Q2C → 1024-dim" },
                                { label: "④ Modeling Layer", sub: "2-layer BiLSTM → 256-dim" },
                                { label: "⑤ Output Layer", sub: "2 × Linear → start + end logits" },
                            ]} />
                        </div>
                        <div className="flex-1 space-y-2">
                            <div className="glass rounded-xl p-3">
                                <SectionLabel>Layer Dimensions</SectionLabel>
                                <Table
                                    headers={["Layer", "Input", "Output"]}
                                    rows={[
                                        ["Embedding", "token index", "100-dim"],
                                        ["Encoder", "100-dim", "256-dim"],
                                        ["Attention", "256-dim × 2", "1024-dim"],
                                        ["Modeling", "1024-dim", "256-dim"],
                                        ["Output", "256-dim", "c_len logits"],
                                    ]}
                                />
                            </div>
                            <div className="glass rounded-xl p-3">
                                <SectionLabel>Key Detail</SectionLabel>
                                <p className="text-xs text-slate-400">Context and Query share the <strong className="text-indigo-300">same encoder weights</strong> — forcing aligned representations in the same space.</p>
                            </div>
                        </div>
                    </div>
                </div>
            ),
            notes: "Here's the big picture. Our model has 5 layers. Word embeddings convert tokens to dense vectors. A shared bidirectional LSTM encodes both context and query into the same vector space. The BiDAF attention layer computes the interaction between them, producing a 1024-dimensional query-aware context representation. A 2-layer modeling LSTM captures higher-order features. Finally, two linear heads predict where the answer starts and ends. Let's now look at the attention layer in detail.",
        },

        /* ── 8. Attention Deep Dive ── */
        {
            tag: "Core Innovation",
            tagColor: "badge-purple",
            title: "BiDAF Attention — Deep Dive",
            content: (
                <div>
                    <div className="glass rounded-xl p-4 mb-3">
                        <SectionLabel color="purple">Step 1 — Similarity Matrix</SectionLabel>
                        <div className="code-block text-center text-sm mb-2">
                            S<sub>ij</sub> = W<sup>T</sup> [c<sub>i</sub> ; q<sub>j</sub> ; c<sub>i</sub> ⊙ q<sub>j</sub>]
                        </div>
                        <p className="text-[11px] text-slate-500 text-center">Computes how similar each context word is to each query word</p>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="emerald">Step 2 — C2Q Attention</SectionLabel>
                            <p className="text-xs text-slate-400 mb-1">For each context word:</p>
                            <p className="text-xs text-emerald-300 italic">&quot;Which query words are most relevant?&quot;</p>
                            <p className="text-[11px] text-slate-500 mt-2">Softmax across each <strong>row</strong> → weighted sum of query vectors</p>
                        </div>
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="amber">Step 3 — Q2C Attention</SectionLabel>
                            <p className="text-xs text-slate-400 mb-1">For the query as a whole:</p>
                            <p className="text-xs text-amber-300 italic">&quot;Which context words matter most?&quot;</p>
                            <p className="text-[11px] text-slate-500 mt-2">Max across each row → Softmax → weighted context vector</p>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3 mt-3">
                        <SectionLabel color="indigo">Step 4 — Merge</SectionLabel>
                        <div className="code-block text-center text-xs">
                            G<sub>i</sub> = [c<sub>i</sub> ; c2q<sub>i</sub> ; c<sub>i</sub> ⊙ c2q<sub>i</sub> ; c<sub>i</sub> ⊙ q2c<sub>i</sub>]
                        </div>
                        <p className="text-[11px] text-slate-500 text-center mt-1">4 × 256 = <strong className="text-indigo-300">1024-dim</strong> query-aware context representation</p>
                    </div>
                </div>
            ),
            notes: "This is the heart of our model. First, we compute a similarity matrix between every context word and every query word, using a learned linear transformation over their concatenation and element-wise product. Then attention flows in two directions. C2Q asks: for each context word, which query words should I pay attention to? We softmax across each row and take a weighted sum of query vectors. Q2C asks the reverse: which context words are most important to the query overall? We take the column-wise max, then softmax. Finally, we merge everything into a 1024-dimensional query-aware representation for each context token.",
        },

        /* ── 9. Modeling + Output ── */
        {
            tag: "Model",
            tagColor: "badge-purple",
            title: "Modeling Layer & Output",
            content: (
                <div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="purple">Layer 4 — Modeling</SectionLabel>
                            <Bullet icon="•">2-layer Bidirectional LSTM</Bullet>
                            <Bullet icon="•">Input: 1024-dim (attention output)</Bullet>
                            <Bullet icon="•">Output: 256-dim per token</Bullet>
                            <Bullet icon="•">Inter-layer dropout for regularization</Bullet>
                            <div className="glass rounded-lg p-3 mt-3">
                                <p className="text-[11px] text-slate-500">
                                    <strong className="text-slate-300">Purpose:</strong> Capture long-range dependencies and higher-order interactions between attended context words
                                </p>
                            </div>
                        </div>
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="indigo">Layer 5 — Output</SectionLabel>
                            <DiagramFlowVertical items={[
                                { label: "Modeling output", sub: "(batch, c_len, 256)" },
                                { label: "Linear → start_logits", sub: "P(start = i)" },
                                { label: "Linear → end_logits", sub: "P(end = j)" },
                            ]} />
                            <div className="glass rounded-lg p-3 mt-2">
                                <p className="text-[11px] text-slate-500">
                                    <strong className="text-slate-300">Constraint:</strong> end ≥ start. Padding tokens masked to −∞ before softmax.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3 mt-3 text-center">
                        <span className="text-xs text-slate-400">At inference: </span>
                        <span className="text-xs text-indigo-300 font-mono">answer = context[argmax(start) : argmax(end)]</span>
                    </div>
                </div>
            ),
            notes: "The modeling layer is a deeper, 2-layer BiLSTM that processes the attention output. While the encoder captured local word interactions, this layer captures how the attended context words relate to each other over longer distances. The output layer is simple: two separate linear heads project each token's representation to a single score — one for start probability and one for end probability. We mask padding tokens so they can't be selected. At inference, we pick the highest-scoring start, then the highest-scoring end after it, and extract that span.",
        },

        /* ── 10. Training ── */
        {
            tag: "Training",
            tagColor: "badge-emerald",
            title: "Training Strategy",
            content: (
                <div>
                    <div className="grid grid-cols-2 gap-3 mb-4">
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="emerald">Hyperparameters</SectionLabel>
                            <Table
                                headers={["Parameter", "Value"]}
                                rows={[
                                    ["Loss", "CrossEntropy (start+end)/2"],
                                    ["Optimizer", "Adam (lr=0.001)"],
                                    ["Grad Clipping", "max_norm = 5.0"],
                                    ["Batch Size", "16"],
                                    ["Epochs", "4"],
                                    ["Embedding Dim", "100"],
                                    ["Hidden Dim", "128"],
                                    ["Dropout", "0.2"],
                                    ["Vocab Size", "50,002"],
                                    ["Train Samples", "86,793"],
                                    ["Val Samples", "5,915"],
                                ]}
                            />
                        </div>
                        <div className="glass rounded-xl p-4">
                            <SectionLabel>Training Loop</SectionLabel>
                            <DiagramFlowVertical items={[
                                { label: "Batch (C, Q, start, end)" },
                                { label: "Forward Pass" },
                                { label: "CE Loss (start+end)/2" },
                                { label: "Backward + Clip Grads" },
                                { label: "Adam Update" },
                                { label: "Evaluate on Dev (EM+F1)" },
                                { label: " LR Scheduler step" },
                                { label: "💾 Save if F1 improved" },
                                { label: "🛑 Early stop if no gain ×3" },
                            ]} />
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3 text-center">
                        <span className="badge badge-emerald">Best model saved by validation F1</span>
                        <span className="mx-2 text-slate-600">•</span>
                        <span className="badge badge-indigo">Trained on Google Colab GPU</span>
                        <span className="mx-2 text-slate-600">•</span>
                        <span className="badge badge-amber">Early stopping + LR decay</span>
                    </div>
                </div>
            ),
            notes: "For training, our loss function is the average of two cross-entropy losses — one for the start position and one for the end position. We use Adam optimizer at a learning rate of 0.001, with gradient clipping at 5.0 to prevent exploding gradients in the LSTMs. We trained on 86,793 samples with a batch size of 16 for 4 epochs. After each epoch, we evaluate on the 5,915-sample dev set using Exact Match and F1. If the F1 score improves, we save the model checkpoint. Our best checkpoint came from epoch 4. We trained on Google Colab with GPU acceleration.",
        },

        /* ── 11. Evaluation ── */
        {
            tag: "Results",
            tagColor: "badge-amber",
            title: "Evaluation Metrics & Results",
            content: (
                <div>
                    <div className="grid grid-cols-2 gap-3 mb-4">
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="emerald">Exact Match (EM)</SectionLabel>
                            <p className="text-xs text-slate-400 leading-relaxed">
                                Binary score — does the prediction match the gold answer <strong className="text-white">exactly</strong> after normalization?
                            </p>
                        </div>
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="amber">F1 Score</SectionLabel>
                            <p className="text-xs text-slate-400 leading-relaxed">
                                Token-level <strong className="text-white">precision × recall</strong> — measures word overlap between predicted and gold answer.
                            </p>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3 mb-4">
                        <SectionLabel>Answer Normalization</SectionLabel>
                        <DiagramFlow items={["lowercase", "remove punct", "remove articles", "fix whitespace"]} />
                    </div>
                    <Table
                        headers={["Model", "EM", "F1", "Year"]}
                        rows={[
                            ["BiDAF (Seo et al.)", "59.2", "62.1", "2017"],
                            ["Our BiDAF ✅", "43.4", "60.6", "2026"],
                            ["BERT-base", "73.7", "76.3", "2018"],
                            ["BERT-large", "78.7", "81.9", "2018"],
                            ["Human Performance", "86.8", "89.5", "—"],
                        ]}
                        highlight={1}
                    />
                </div>
            ),
            notes: "We use the two standard SQuAD metrics. Exact Match is strict — the prediction must match the gold answer word-for-word after normalization. F1 is more forgiving — it measures the overlap between predicted and gold tokens. Our normalization follows the official SQuAD eval script. Our BiDAF achieves 43.4% Exact Match and 60.6% F1. The F1 is very close to the original BiDAF paper's 62.1, which is a strong result. Our EM is lower at 43.4 versus 59.2, meaning our model sometimes captures part of the answer but not the exact span. BERT-based models perform significantly better because they use pre-trained contextualized embeddings, whereas our embeddings are learned from scratch on SQuAD alone.",
        },

        /* ── 12. Demo ── */
        {
            tag: "Demo",
            tagColor: "badge-emerald",
            title: "Live Demonstration",
            content: (
                <div>
                    <DiagramFlow items={["👤 User", "🖥️ Web UI", "⚡ FastAPI", "🧹 Tokenize", "🤖 BiDAF", "📤 Answer"]} />
                    <div className="glass rounded-xl p-4 mt-4">
                        <SectionLabel color="emerald">How it works</SectionLabel>
                        <div className="space-y-1">
                            <Bullet icon="1.">User pastes a paragraph and types a question</Bullet>
                            <Bullet icon="2.">Frontend sends POST request to FastAPI backend</Bullet>
                            <Bullet icon="3.">Backend tokenizes, encodes, and runs model inference</Bullet>
                            <Bullet icon="4.">Answer span is extracted with confidence score</Bullet>
                            <Bullet icon="5.">UI highlights the answer in the context</Bullet>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-4 mt-3">
                        <SectionLabel color="amber">Originality — Feedback Loop</SectionLabel>
                        <p className="text-xs text-slate-400">
                            Users can 👍 validate or 👎 correct answers through the UI. Corrections generate new <span className="text-indigo-300">(context, question, answer)</span> triplets, augmenting the training dataset for continuous improvement.
                        </p>
                    </div>
                </div>
            ),
            notes: "Let me show you a live demonstration. We'll paste a paragraph from Wikipedia, type a question, and our model will extract and highlight the answer span in real-time. The confidence score tells us how certain the model is. We also implemented an originality feature: users can correct wrong answers via the UI, and those corrections are saved as new training examples for data augmentation.",
        },

        /* ── 13. Conclusion ── */
        {
            tag: "Wrap-up",
            tagColor: "badge-indigo",
            title: "Conclusion",
            content: (
                <div>
                    <div className="glass rounded-xl p-4 mb-3">
                        <SectionLabel>What We Built</SectionLabel>
                        <Bullet icon="✓">Complete extractive QA pipeline: raw JSON → trained BiDAF → API predictions</Bullet>
                        <Bullet icon="✓">End-to-end: preprocessing, training, evaluation, and inference</Bullet>
                        <Bullet icon="✓">Deployable web application with user feedback loop</Bullet>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="emerald">Key Takeaways</SectionLabel>
                            <Bullet icon="→">BiDAF&apos;s bi-directional attention is effective for span extraction</Bullet>
                            <Bullet icon="→">Shared encoder improves representation alignment</Bullet>
                            <Bullet icon="→">SQuAD 2.0 adds realism with unanswerable questions</Bullet>
                        </div>
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="amber">Limitations & Future</SectionLabel>
                            <Bullet icon="→">Embeddings trained from scratch → pre-trained (GloVe) would boost results</Bullet>
                            <Bullet icon="→">Transformer-based (BERT) would reach SotA</Bullet>
                            <Bullet icon="→">User feedback could improve domain-specific performance</Bullet>
                        </div>
                    </div>
                </div>
            ),
            notes: "To wrap up — we built a complete question answering system from scratch, covering every step from data loading to a deployable API. BiDAF's bidirectional attention mechanism proved effective for the span extraction task. Our main limitation is that we train embeddings from scratch, while modern approaches like BERT use massive pre-trained representations. As future work, integrating pre-trained embeddings or fine-tuning a transformer would significantly improve performance.",
        },

        /* ── 14. Thank You ── */
        {
            tag: "",
            tagColor: "",
            title: "",
            content: (
                <div className="flex flex-col items-center justify-center text-center py-8">
                    <h1 className="text-5xl font-bold mb-4">
                        <span className="bg-gradient-to-r from-indigo-300 via-purple-300 to-pink-300 bg-clip-text text-transparent">
                            Thank You
                        </span>
                    </h1>
                    <p className="text-lg text-slate-400 mb-6">Questions?</p>
                    <div className="flex gap-3">
                        <span className="badge badge-indigo">Alon DEBASC</span>
                        <span className="badge badge-purple">Axel STOLTZ</span>
                        <span className="badge badge-emerald">Thibault CHESNEL</span>
                    </div>
                </div>
            ),
            notes: "Thank you for your attention. We're happy to take any questions.",
        },
    ];
}

export default function NLPPresentationPage() {
    return <Presentation slides={buildSlides()} />;
}
