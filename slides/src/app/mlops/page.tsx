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
        /* ── 1. Title ─────────────────────────────────────────── */
        {
            tag: "MLOps Final Project",
            tagColor: "badge-emerald",
            title: "",
            content: (
                <div className="flex flex-col items-center justify-center text-center py-4">
                    <h1 className="text-4xl md:text-5xl font-bold mb-3">
                        <span className="bg-gradient-to-r from-emerald-300 via-teal-300 to-cyan-300 bg-clip-text text-transparent">
                            Document QA Assistant
                        </span>
                    </h1>
                    <h2 className="text-xl md:text-2xl text-white/80 font-light mb-2">
                        MLOps Pipeline — Full Lifecycle
                    </h2>
                    <p className="text-sm text-slate-500 mb-6">
                        From code commit to production deployment & continuous retraining
                    </p>
                    <div className="flex gap-2 flex-wrap justify-center mb-6">
                        <span className="badge badge-indigo">Alon DEBASC</span>
                        <span className="badge badge-purple">Axel STOLTZ</span>
                        <span className="badge badge-emerald">Thibault CHESNEL</span>
                    </div>
                    <p className="text-slate-600 text-xs">
                        MLOps — M2 EFREI — March 2026
                    </p>
                </div>
            ),
            notes: "Good morning everyone. Today we will present the complete MLOps lifecycle for our Document QA Assistant project. We built a production-grade question answering application using a BiDAF neural network trained on SQuAD 2.0. This presentation focuses specifically on the MLOps side: how we track experiments, version data and models, automate testing and deployment through CI/CD, and close the feedback loop with automated retraining. Let's get started.",
        },

        /* ── 2. Agenda ────────────────────────────────────────── */
        {
            tag: "Overview",
            tagColor: "badge-emerald",
            title: "Agenda",
            content: (
                <div className="space-y-2 py-2">
                    {[
                        { n: "01", label: "High-Level Architecture & Tech Stack" },
                        { n: "02", label: "Git Branching Strategy & Branch Protection" },
                        { n: "03", label: "Data & Model Versioning (DVC)" },
                        { n: "04", label: "Experiment Tracking (MLflow + DagsHub)" },
                        { n: "05", label: "Model Registry & Promotion Gate" },
                        { n: "06", label: "CI/CD — GitHub Actions (6 Workflows)" },
                        { n: "07", label: "Full Workflow: Branch to Production" },
                        { n: "08", label: "Cloud Deployment (Render IaC)" },
                        { n: "09", label: "Testing Strategy (Unit, Integration, E2E)" },
                        { n: "10", label: "12-Factor App & Configuration" },
                        { n: "11", label: "Automated Retraining & Feedback Loop" },
                    ].map((item) => (
                        <div key={item.n} className="flex items-center gap-3 py-0.5 group">
                            <span className="text-xs font-mono text-emerald-500/60 w-6">{item.n}</span>
                            <span className="text-sm text-slate-300 group-hover:text-white transition-colors">{item.label}</span>
                        </div>
                    ))}
                </div>
            ),
            notes: "Here is the roadmap for our 15-minute presentation. We'll cover every aspect of the MLOps lifecycle — starting from the architecture and branching strategy, then versioning and tracking, model promotion, all six CI/CD workflows, deployment to Render, our testing strategy, configuration management following 12-factor principles, the automated retraining loop, and we'll end with a live demo of the production application.",
        },

        /* ── 3. Architecture ──────────────────────────────────── */
        {
            tag: "Architecture",
            tagColor: "badge-emerald",
            title: "High-Level Architecture",
            content: (
                <div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="emerald">Application Stack</SectionLabel>
                            <DiagramFlowVertical items={[
                                { label: "🌐 Next.js Frontend", sub: "React UI + /api routes (proxy)" },
                                { label: "⚡ FastAPI Backend", sub: "REST API + inference pipeline" },
                                { label: "🤖 BiDAF Model", sub: "PyTorch QA Neural Network" },
                            ]} />
                        </div>
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="purple">MLOps Infrastructure</SectionLabel>
                            <DiagramFlowVertical items={[
                                { label: "🧑‍💻 GitHub", sub: "Code + 6 CI/CD workflows" },
                                { label: "📊 MLflow (DagsHub)", sub: "Experiment tracking + model registry" },
                                { label: "💾 DVC (DagsHub S3)", sub: "Data + checkpoint versioning" },
                                { label: "☁️ Render", sub: "Cloud PaaS (staging + prod)" },
                            ]} />
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3">
                        <SectionLabel>User Interaction Flow</SectionLabel>
                        <DiagramFlow items={["👤 User", "🖥️ Next.js", "⚡ FastAPI", "🤖 BiDAF", "📤 Answer"]} />
                        <div className="text-center mt-2">
                            <span className="text-[11px] text-slate-500">Users can also submit feedback (👍/👎) → stored in Supabase → fed back into retraining</span>
                        </div>
                    </div>
                </div>
            ),
            notes: "Here's our high-level architecture. On the left, the application stack: a Next.js frontend that users interact with, which proxies requests to a FastAPI backend running our BiDAF model for inference. On the right, the MLOps infrastructure: GitHub for code and CI/CD automation, MLflow on DagsHub for experiment tracking and the model registry, DVC also on DagsHub's S3 for versioning both training data and model checkpoints, and Render as our cloud platform hosting both staging and production environments. Importantly, user feedback submitted through the UI goes to Supabase and is pulled back into the retraining pipeline, creating a continuous improvement loop.",
        },

        /* ── 4. Git Branching Strategy ────────────────────────── */
        {
            tag: "Git Strategy",
            tagColor: "badge-indigo",
            title: "Branching Model & Protection",
            content: (
                <div>
                    <div className="glass rounded-xl p-4 mb-4">
                        <SectionLabel color="indigo">Strict Branch Flow</SectionLabel>
                        <DiagramFlow items={["feature/*", "→ dev", "→ staging", "→ main"]} />
                        <p className="text-[11px] text-slate-500 text-center mt-2">
                            Every change follows this exact path — no shortcuts to production
                        </p>
                    </div>
                    <Table
                        headers={["Branch", "Role", "Protection"]}
                        rows={[
                            ["feature/*", "All development", "Naming enforced by GH Action"],
                            ["dev", "Integration branch", "PRs require CI pass (lint + tests + docker)"],
                            ["staging", "Pre-production", "Full test suite + model staging + E2E"],
                            ["main", "Production", "Promotion gate (F1 ≥ 0.5) must pass"],
                        ]}
                        highlight={3}
                    />
                    <div className="glass rounded-xl p-3 mt-4">
                        <SectionLabel color="amber">Branch Name Enforcement</SectionLabel>
                        <div className="code-block text-[11px]">
                            <div className="text-slate-500"># branch-name-check.yml — on: create</div>
                            <div className="text-purple-300">ALLOWED=<span className="text-emerald-300">&quot;^(main|dev|staging|feature/.+)$&quot;</span></div>
                            <div className="text-amber-300">if [[ ! &quot;$BRANCH&quot; =~ $ALLOWED ]]; then exit 1; fi</div>
                        </div>
                    </div>
                </div>
            ),
            notes: "We follow a strict branching strategy with four levels. All development happens on feature branches. They merge into dev for integration, then dev merges to staging for pre-production validation, and finally staging merges to main for production. Every branch name is enforced automatically: when any branch is created, a GitHub Action called branch-name-check validates it against the allowed pattern — main, dev, staging, or feature slash something. Non-conforming branches are immediately rejected. The main branch has the strongest protection: a quality gate checks the model's F1 score and blocks the merge if it's below our threshold of 0.5.",
        },

        /* ── 5. Data & Model Versioning (DVC) ─────────────────── */
        {
            tag: "Versioning",
            tagColor: "badge-amber",
            title: "Data & Model Versioning — DVC",
            content: (
                <div>
                    <div className="glass rounded-xl p-4 mb-4">
                        <SectionLabel color="amber">What DVC Tracks</SectionLabel>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="glass rounded-lg p-3 text-center">
                                <div className="text-2xl mb-1">📄</div>
                                <div className="text-sm font-semibold text-white">Training Data</div>
                                <div className="text-[11px] text-slate-500">train-v2.0.json (~42 MB)</div>
                                <div className="text-[11px] text-slate-500">dev-v2.0.json</div>
                            </div>
                            <div className="glass rounded-lg p-3 text-center">
                                <div className="text-2xl mb-1">🧠</div>
                                <div className="text-sm font-semibold text-white">Model Checkpoints</div>
                                <div className="text-[11px] text-slate-500">checkpoints/ (weights, config)</div>
                                <div className="text-[11px] text-slate-500">finetune_history.json</div>
                            </div>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-4 mb-3">
                        <SectionLabel color="emerald">Remote Storage</SectionLabel>
                        <div className="code-block text-[11px]">
                            <div className="text-slate-500"># DVC remote on DagsHub S3</div>
                            <div className="text-purple-300">remote: <span className="text-emerald-300">s3://dvc @ dagshub.com/akksel1/final_project.s3</span></div>
                            <div className="text-slate-500"># .dvc files tracked in Git → pointer to exact data version</div>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3">
                        <SectionLabel>Full Traceability</SectionLabel>
                        <Bullet icon="🔗">Every MLflow training run logs the <strong className="text-white">DVC data version</strong> (MD5 hash from .dvc file)</Bullet>
                        <Bullet icon="🔗">Every MLflow training run logs the <strong className="text-white">Git commit hash</strong></Bullet>
                        <Bullet icon="→">Any model version can be traced back to the exact data + code that produced it</Bullet>
                    </div>
                </div>
            ),
            notes: "Data and model versioning is handled entirely through DVC — Data Version Control. We track two main things: the SQuAD training and evaluation datasets, which are about 42 megabytes, and the model checkpoints including weights and configuration files. The actual files are stored on DagsHub's S3-compatible remote, while Git only stores lightweight .dvc pointer files. The key here is traceability: every time we train a model, we log both the DVC data version — the MD5 hash from the .dvc pointer — and the Git commit hash as parameters in our MLflow run. This means for any deployed model version, we can trace back to the exact code and the exact data that produced it. That's critical for reproducibility and auditing.",
        },

        /* ── 6. Experiment Tracking (MLflow) ──────────────────── */
        {
            tag: "Tracking",
            tagColor: "badge-purple",
            title: "Experiment Tracking — MLflow + DagsHub",
            content: (
                <div>
                    <div className="glass rounded-xl p-4 mb-4">
                        <SectionLabel color="purple">What We Log Per Run</SectionLabel>
                        <div className="grid grid-cols-3 gap-3">
                            <div className="glass rounded-lg p-3">
                                <div className="text-xs font-semibold text-purple-300 mb-2">Metrics</div>
                                <div className="space-y-1">
                                    {["train_loss", "val_loss", "val_f1", "val_em", "best_val_f1"].map(m => (
                                        <div key={m} className="text-[11px] text-slate-400 font-mono">{m}</div>
                                    ))}
                                </div>
                            </div>
                            <div className="glass rounded-lg p-3">
                                <div className="text-xs font-semibold text-emerald-300 mb-2">Parameters</div>
                                <div className="space-y-1">
                                    {["epochs", "batch_size", "learning_rate", "sample_ratio", "hidden_dim"].map(p => (
                                        <div key={p} className="text-[11px] text-slate-400 font-mono">{p}</div>
                                    ))}
                                </div>
                            </div>
                            <div className="glass rounded-lg p-3">
                                <div className="text-xs font-semibold text-amber-300 mb-2">Traceability</div>
                                <div className="space-y-1">
                                    {["git_commit", "dvc_data_version", "model artifact", "run timestamp"].map(t => (
                                        <div key={t} className="text-[11px] text-slate-400 font-mono">{t}</div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-4">
                        <SectionLabel color="indigo">Infrastructure</SectionLabel>
                        <Bullet icon="🏠">MLflow tracking server hosted on <strong className="text-white">DagsHub</strong> (managed, free tier)</Bullet>
                        <Bullet icon="📦">Models registered in <strong className="text-white">MLflow Model Registry</strong> as &ldquo;QA_Model&rdquo;</Bullet>
                        <Bullet icon="🔐">Credentials injected via <strong className="text-white">GitHub Secrets</strong> + environment variables</Bullet>
                        <Bullet icon="📈">DagsHub UI provides experiment comparison, metric visualization, and artifact browsing</Bullet>
                    </div>
                </div>
            ),
            notes: "For experiment tracking we use MLflow, hosted on DagsHub. Every training run, whether manual or automated, logs a comprehensive set of information. Metrics include training loss, validation loss, F1 score, Exact Match, and best validation F1. Parameters capture all hyperparameters like epochs, batch size, learning rate, and sample ratio. And for traceability, we log the git commit hash and the DVC data version hash. The model artifact itself is also logged and registered in the MLflow Model Registry under the name QA_Model. DagsHub provides a nice UI on top of MLflow for comparing experiments and browsing artifacts. All credentials are stored in GitHub Secrets and injected into CI workflows automatically.",
        },

        /* ── 7. Model Registry & Promotion ────────────────────── */
        {
            tag: "Registry",
            tagColor: "badge-purple",
            title: "Model Registry & Promotion Gate",
            content: (
                <div>
                    <div className="glass rounded-xl p-4 mb-4">
                        <SectionLabel color="purple">Model Lifecycle Stages</SectionLabel>
                        <DiagramFlow items={["🆕 None", "📊 Staging", "🚀 Production"]} />
                        <div className="grid grid-cols-3 gap-2 mt-3">
                            <div className="glass rounded-lg p-2 text-center">
                                <div className="text-[11px] text-slate-400">Registered on</div>
                                <div className="text-xs text-white font-semibold">Training / Fine-tune</div>
                            </div>
                            <div className="glass rounded-lg p-2 text-center">
                                <div className="text-[11px] text-slate-400">Promoted on</div>
                                <div className="text-xs text-white font-semibold">Push → staging</div>
                            </div>
                            <div className="glass rounded-lg p-2 text-center">
                                <div className="text-[11px] text-slate-400">Promoted on</div>
                                <div className="text-xs text-white font-semibold">Push → main (if gate passes)</div>
                            </div>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-4 mb-3">
                        <SectionLabel color="amber">Promotion Gate — promotion_gate.py</SectionLabel>
                        <div className="code-block text-[11px]">
                            <div className="text-slate-500"># Runs on PR to main + on push to main</div>
                            <div className="text-purple-300">f1 = run.data.metrics.get(<span className="text-emerald-300">&quot;best_val_f1&quot;</span>)</div>
                            <div className="text-amber-300">if f1 &lt; F1_THRESHOLD:  <span className="text-slate-500"># default: 0.5</span></div>
                            <div className="pl-4 text-red-300">sys.exit(1)  <span className="text-slate-500"># ❌ Block deployment</span></div>
                            <div className="text-emerald-300">client.transition_model_version_stage(</div>
                            <div className="pl-4 text-emerald-300">name=MODEL_NAME, version=v, stage=<span className="text-amber-300">&quot;Production&quot;</span>)</div>
                        </div>
                    </div>
                    <div className="flex gap-2 justify-center">
                        <span className="badge badge-emerald">✅ F1 ≥ 0.5 → Promote to Production</span>
                        <span className="badge badge-amber">❌ F1 &lt; 0.5 → PR Blocked, Prod unchanged</span>
                    </div>
                </div>
            ),
            notes: "The MLflow Model Registry is our single source of truth for model deployments. Models go through three stages. When first trained, they're registered with no stage. When code is pushed to the staging branch, the deploy-staging workflow transitions the latest model version to the Staging stage. The critical step is the promotion gate. When a PR targets main — meaning staging to main — the promotion gate script runs. It fetches the model's F1 score from MLflow, and if it's below our threshold of 0.5, the pipeline exits with an error, blocking both the merge and any production deployment. Only if the F1 passes does the model get promoted to the Production stage. This ensures production only ever serves models that meet our quality bar. The gate supports both legacy MLflow stages and newer alias-based promotion.",
        },

        /* ── 8. CI/CD Overview ────────────────────────────────── */
        {
            tag: "CI/CD",
            tagColor: "badge-emerald",
            title: "CI/CD — 6 GitHub Actions Workflows",
            content: (
                <div>
                    <Table
                        headers={["Workflow", "Trigger", "Key Steps"]}
                        rows={[
                            ["branch-name-check", "on: create", "Validate branch name pattern"],
                            ["ci.yml", "PR → dev/staging/main", "Lint → Tests → Docker build"],
                            ["deploy-staging", "push → staging", "Tests → Model staging → Render → E2E"],
                            ["promotion-gate", "PR → main", "F1 quality gate (blocks if < 0.5)"],
                            ["deploy-prod", "push → main", "Promotion gate → Render prod deploy"],
                            ["retrain", "Weekly / manual", "Feedback → Fine-tune → Promote → Deploy"],
                        ]}
                    />
                    <div className="glass rounded-xl p-3 mt-4">
                        <SectionLabel>Design Principles</SectionLabel>
                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <Bullet icon="🔒">Every merge requires <strong className="text-white">passing CI</strong></Bullet>
                                <Bullet icon="🚫">Production deployment <strong className="text-white">blocked</strong> if model quality drops</Bullet>
                            </div>
                            <div>
                                <Bullet icon="🔄">Staging serves as a <strong className="text-white">full pre-production replica</strong></Bullet>
                                <Bullet icon="🤖">Retraining is <strong className="text-white">fully automated</strong> (weekly or on-demand)</Bullet>
                            </div>
                        </div>
                    </div>
                </div>
            ),
            notes: "We have six GitHub Actions workflows that together automate the entire lifecycle. Branch-name-check validates naming conventions on branch creation. The CI pipeline runs on every pull request to dev, staging, or main — it lints with Ruff, runs all tests with pytest, and validates Docker image builds. Deploy-staging fires on push to the staging branch, running the full test suite, transitioning the model to Staging in MLflow, deploying to Render, and running E2E tests with Playwright against the live staging URL. The promotion gate runs on every PR to main: it checks the model's F1 score and blocks the merge if it's below our threshold. Deploy-prod triggers on push to main after merge, re-runs the promotion gate, promotes the model to Production, and triggers the Render production deploy hook. Finally, the retrain workflow runs weekly or on manual dispatch — pulling user feedback from Supabase, fine-tuning the model, and committing the results. Let me now walk through the complete flow visually.",
        },

        /* ── 9. CI Pipeline Detail ────────────────────────────── */
        {
            tag: "CI/CD",
            tagColor: "badge-emerald",
            title: "CI Pipeline — ci.yml",
            content: (
                <div>
                    <div className="glass rounded-xl p-3 mb-4">
                        <div className="flex gap-2 flex-wrap mb-2">
                            <span className="badge badge-indigo">on: pull_request → dev, staging, main</span>
                            <span className="badge badge-purple">on: push → dev</span>
                        </div>
                    </div>
                    <div className="grid grid-cols-3 gap-3 mb-4">
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="emerald">Job 1: Lint</SectionLabel>
                            <Bullet icon="→">ruff check .</Bullet>
                            <Bullet icon="→">ruff format --check .</Bullet>
                            <div className="glass rounded-lg p-2 mt-2">
                                <p className="text-[10px] text-slate-500">Runs first — fast feedback</p>
                            </div>
                        </div>
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="indigo">Job 2: Tests</SectionLabel>
                            <Bullet icon="→">DVC pull (fetch data)</Bullet>
                            <Bullet icon="→">pytest tests/ -v</Bullet>
                            <div className="glass rounded-lg p-2 mt-2">
                                <p className="text-[10px] text-slate-500">needs: lint</p>
                            </div>
                        </div>
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="purple">Job 3: Docker</SectionLabel>
                            <Bullet icon="→">Build backend image</Bullet>
                            <Bullet icon="→">Build frontend image</Bullet>
                            <div className="glass rounded-lg p-2 mt-2">
                                <p className="text-[10px] text-slate-500">needs: lint · push: false</p>
                            </div>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3">
                        <DiagramFlow items={["🔍 Lint (Ruff)", "→ 🧪 Tests (pytest)", "→ 🐳 Docker Build"]} />
                        <p className="text-[11px] text-slate-500 text-center mt-2">Tests and Docker build run <strong className="text-white">in parallel</strong> after lint passes — fast CI feedback</p>
                    </div>
                </div>
            ),
            notes: "Let me zoom into the CI pipeline. It triggers on every pull request targeting dev, staging, or main, and also on direct pushes to dev. There are three jobs. First, Lint runs Ruff for both code quality checks and formatting verification — this runs first because it's fast and catches simple issues immediately. Then, two jobs run in parallel after lint passes: Tests pulls the versioned data from DVC and runs our full pytest suite — 38+ unit tests and 12 integration tests. Docker Build validates that both the backend and frontend Dockerfiles compile correctly, but doesn't push images anywhere — this is purely for validation. By running tests and Docker in parallel, we keep the CI feedback loop fast.",
        },

        /* ── 10. Deploy Staging Detail ────────────────────────── */
        {
            tag: "CI/CD",
            tagColor: "badge-emerald",
            title: "Deploy Staging — deploy-staging.yml",
            content: (
                <div>
                    <div className="glass rounded-xl p-3 mb-3">
                        <span className="badge badge-indigo">on: push → staging</span>
                        <span className="text-[11px] text-slate-500 ml-2">Triggered after merging dev → staging</span>
                    </div>
                    <DiagramFlowVertical items={[
                        { label: "1️⃣ Full Test Suite", sub: "Ruff lint + format + DVC pull + pytest" },
                        { label: "2️⃣ Docker Build (validate)", sub: "Backend + Frontend images (no push)" },
                        { label: "3️⃣ Deploy Candidate Model", sub: "MLflow: transition latest → Staging stage" },
                        { label: "4️⃣ Trigger Render Staging Deploy", sub: "curl RENDER_STAGING_DEPLOY_HOOK" },
                        { label: "5️⃣ E2E Tests (Playwright)", sub: "Wait for staging URL → run qa-flow.spec.ts" },
                    ]} />
                    <div className="glass rounded-xl p-3 mt-3">
                        <SectionLabel color="amber">Key Insight</SectionLabel>
                        <Bullet icon="⚡">Docker build & model staging run <strong className="text-white">in parallel</strong> after tests pass</Bullet>
                        <Bullet icon="🧪">E2E tests run <strong className="text-white">against the live staging environment</strong> — not just locally</Bullet>
                        <Bullet icon="🔄">Staging is a <strong className="text-white">full replica</strong> of prod (same infrastructure, different model alias)</Bullet>
                    </div>
                </div>
            ),
            notes: "The staging deployment pipeline is the most comprehensive workflow. It fires when code is pushed to the staging branch, meaning after a dev-to-staging merge. Five steps execute in sequence. First, the full test suite runs again — even though CI already ran on the PR — because the merge commit might differ. Second, Docker images are built to validate. Third, the latest model version in MLflow is transitioned to the Staging stage using the MLflow client API. Docker build and model staging happen in parallel after tests pass. Fourth, we trigger the Render staging deploy hook, which rolls out the new code to the staging backend and frontend services. Fifth and critically, after Render finishes deploying, Playwright E2E tests run against the live staging URL — not locally. The test fills a context, asks a question, gets an answer, and submits feedback, validating the entire user journey in the real staging environment.",
        },

        /* ── 11. Production Deploy Detail ─────────────────────── */
        {
            tag: "CI/CD",
            tagColor: "badge-emerald",
            title: "Production Gate & Deploy",
            content: (
                <div>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="amber">PR to main — promotion-gate.yml</SectionLabel>
                            <div className="glass rounded-lg p-3 mb-2">
                                <span className="badge badge-indigo">on: pull_request → main</span>
                            </div>
                            <Bullet icon="1.">Fetch model from MLflow (Staging or latest)</Bullet>
                            <Bullet icon="2.">Read F1 score from run metrics</Bullet>
                            <Bullet icon="3.">Compare against threshold (0.5)</Bullet>
                            <Bullet icon="→">❌ Fail → <strong className="text-red-300">PR blocked</strong></Bullet>
                            <Bullet icon="→">✅ Pass → <strong className="text-emerald-300">PR mergeable</strong></Bullet>
                        </div>
                        <div className="glass rounded-xl p-4">
                            <SectionLabel color="emerald">Push to main — deploy-prod.yml</SectionLabel>
                            <div className="glass rounded-lg p-3 mb-2">
                                <span className="badge badge-indigo">on: push → main</span>
                            </div>
                            <Bullet icon="1."><strong className="text-white">Re-run</strong> promotion gate (safety net)</Bullet>
                            <Bullet icon="2.">Promote model → <strong className="text-white">Production stage</strong></Bullet>
                            <Bullet icon="3.">curl RENDER_PROD_DEPLOY_HOOK</Bullet>
                            <Bullet icon="→">Render deploys backend + frontend + slides</Bullet>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3">
                        <SectionLabel>Safety Design</SectionLabel>
                        <Bullet icon="🛡️">Model promoted <strong className="text-white">only</strong> after passing the F1 gate <strong className="text-white">twice</strong> (PR + push)</Bullet>
                        <Bullet icon="🔒">If gate ever fails → production is <strong className="text-white">never updated</strong> (safe rollback by design)</Bullet>
                    </div>
                </div>
            ),
            notes: "Getting code to production involves two workflows that work together. First, when a PR is opened from staging to main, the promotion-gate workflow runs automatically. It queries MLflow for the model in the Staging stage — or falls back to the latest version — reads its F1 score, and blocks the PR if it's below 0.5. This is a required status check, meaning the merge button stays grayed out until the gate passes. Second, after the PR is merged and code is pushed to main, the deploy-prod workflow fires. It re-runs the promotion gate as a safety net, then promotes the model to the Production stage in the MLflow registry, and finally triggers the Render production deploy hook. This rolls out the new backend, frontend, and slides services. The key safety property is that the model is promoted to Production only if it passes the F1 gate twice — once on the PR and once on the push. If anything fails, production stays unchanged.",
        },

        /* ── 12. Full Workflow Diagram ────────────────────────── */
        {
            tag: "Full Picture",
            tagColor: "badge-emerald",
            title: "Complete Workflow: Branch → Production",
            content: (
                <div>
                    <DiagramFlowVertical items={[
                        { label: "① Create feature/* branch", sub: "branch-name-check.yml validates naming" },
                        { label: "② PR → dev", sub: "ci.yml: Lint → Tests → Docker build" },
                        { label: "③ Merge to dev, then PR → staging", sub: "ci.yml runs again on PR" },
                        { label: "④ Merge to staging", sub: "deploy-staging.yml: Full suite → Model→Staging → Render → E2E" },
                        { label: "⑤ PR → main", sub: "promotion-gate.yml: F1 ≥ 0.5 required" },
                        { label: "⑥ Merge to main", sub: "deploy-prod.yml: Gate re-run → Model→Prod → Render deploy" },
                    ]} />
                    <div className="glass rounded-xl p-3 mt-3">
                        <div className="grid grid-cols-3 gap-2 text-center">
                            <div>
                                <div className="text-lg font-bold text-emerald-300">6</div>
                                <div className="text-[10px] text-slate-500">GH Actions workflows</div>
                            </div>
                            <div>
                                <div className="text-lg font-bold text-purple-300">3</div>
                                <div className="text-[10px] text-slate-500">Quality gates</div>
                            </div>
                            <div>
                                <div className="text-lg font-bold text-amber-300">2</div>
                                <div className="text-[10px] text-slate-500">Environments (staging + prod)</div>
                            </div>
                        </div>
                    </div>
                </div>
            ),
            notes: "Let me walk through the complete path a code change takes to reach production. Step one: a developer creates a feature branch — the branch-name-check validates the naming convention immediately. Step two: they open a PR to dev, and the CI pipeline runs lint, tests, and Docker build. Step three: after merging to dev, a new PR is opened from dev to staging — CI runs again on the PR. Step four: once merged to staging, the deploy-staging pipeline runs the full test suite, transitions the model to Staging in MLflow, deploys to Render staging, and runs E2E tests. Step five: a PR is opened from staging to main — the promotion gate checks the model's F1 score and blocks the merge if it's below threshold. Step six: after merging to main, deploy-prod re-runs the gate, promotes the model to Production, and triggers the Render production deploy. That's six workflows, three quality gates, and two deployment environments all orchestrated automatically.",
        },

        /* ── 13. Cloud Deployment ─────────────────────────────── */
        {
            tag: "Deployment",
            tagColor: "badge-indigo",
            title: "Cloud Deployment — Render (IaC)",
            content: (
                <div>
                    <div className="glass rounded-xl p-4 mb-4">
                        <SectionLabel color="indigo">Infrastructure as Code — render.yaml</SectionLabel>
                        <Table
                            headers={["Service", "Runtime", "Branch", "Model Alias"]}
                            rows={[
                                ["qa-backend-staging", "Python (FastAPI)", "staging", "staging"],
                                ["qa-frontend-staging", "Node (Next.js)", "staging", "—"],
                                ["qa-backend-prod", "Python (FastAPI)", "main", "production"],
                                ["qa-frontend-prod", "Node (Next.js)", "main", "—"],
                                ["qa-frontend-slides", "Node (Next.js)", "main", "—"],
                            ]}
                            highlight={2}
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="emerald">Deployment Methods</SectionLabel>
                            <Bullet icon="🔗">Deploy hooks triggered by GH Actions</Bullet>
                            <Bullet icon="🔄">Auto-deploy on branch push (Render native)</Bullet>
                            <Bullet icon="📦">Build: pip install uv → uv sync → download checkpoints</Bullet>
                        </div>
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="purple">Model Loading</SectionLabel>
                            <Bullet icon="🧠">Backend loads model from MLflow registry</Bullet>
                            <Bullet icon="🏷️">Uses <strong className="text-white">alias</strong> to resolve version</Bullet>
                            <Bullet icon="🔀">staging alias → staging env</Bullet>
                            <Bullet icon="🔀">production alias → prod env</Bullet>
                        </div>
                    </div>
                </div>
            ),
            notes: "Our cloud infrastructure is defined entirely as code in render.yaml — a Render Blueprint. We have 5 services across two environments. Staging has a Python FastAPI backend and a Node.js Next.js frontend, both tracking the staging branch. Production mirrors this with backend and frontend on the main branch, plus a slides service for this very presentation. Deployment happens two ways: GitHub Actions call Render deploy hooks after successful pipeline runs, and Render also auto-deploys natively when it detects new commits on the tracked branch. The backend build command installs uv, syncs dependencies, and downloads model checkpoints. At runtime, the backend resolves which model to load through MLflow aliases: the staging backend uses the staging alias, and the production backend uses the production alias. This means each environment always serves the correct model version without any manual intervention.",
        },

        /* ── 14. Testing Strategy ─────────────────────────────── */
        {
            tag: "Testing",
            tagColor: "badge-amber",
            title: "Testing Strategy",
            content: (
                <div>
                    <Table
                        headers={["Category", "Files", "Count", "Runs In"]}
                        rows={[
                            ["Unit Tests", "test_preprocessing, test_metrics, test_data_loader, test_splitter, test_augmentation", "38+", "ci.yml + staging"],
                            ["Integration Tests", "test_api_health, test_api_qa, test_api_data, test_inference", "12", "ci.yml + staging"],
                            ["E2E Test", "qa-flow.spec.ts (Playwright)", "1", "deploy-staging (live)"],
                        ]}
                        highlight={2}
                    />
                    <div className="grid grid-cols-3 gap-3 mt-4">
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="emerald">Unit</SectionLabel>
                            <p className="text-[11px] text-slate-400">
                                Tokenization, vocabulary building, F1/EM metrics, SQuAD loader, dataset splitting, data augmentation
                            </p>
                        </div>
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="indigo">Integration</SectionLabel>
                            <p className="text-[11px] text-slate-400">
                                FastAPI endpoint testing (health, QA inference, data endpoints), full inference pipeline
                            </p>
                        </div>
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="amber">E2E (Playwright)</SectionLabel>
                            <p className="text-[11px] text-slate-400">
                                Real browser: paste context → ask question → get answer → submit feedback
                            </p>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3 mt-3 text-center">
                        <span className="badge badge-emerald">50+ automated tests</span>
                        <span className="mx-2 text-slate-600">·</span>
                        <span className="badge badge-indigo">Run on every PR</span>
                        <span className="mx-2 text-slate-600">·</span>
                        <span className="badge badge-amber">E2E on live staging</span>
                    </div>
                </div>
            ),
            notes: "Our testing strategy has three layers. At the base, 38+ unit tests cover all core components: text preprocessing, tokenization, vocabulary building, F1 and Exact Match metric computation, the SQuAD data loader, dataset splitting, and data augmentation. Then 12 integration tests validate the FastAPI endpoints — health checks, the QA inference endpoint, data endpoints — and the full inference pipeline end-to-end. Both unit and integration tests run in the CI pipeline on every PR and again during staging deployment. At the top, one comprehensive E2E test uses Playwright with a real Chromium browser to simulate the entire user journey on the live staging environment: loading the page, pasting a context, typing a question, clicking Get Answer, verifying the answer appears, and submitting feedback. This catches integration issues that unit tests can't — like frontend-backend communication, deployment configuration, and real browser rendering.",
        },

        /* ── 15. 12-Factor App ────────────────────────────────── */
        {
            tag: "Configuration",
            tagColor: "badge-indigo",
            title: "12-Factor App & Configuration",
            content: (
                <div>
                    <div className="glass rounded-xl p-4 mb-4">
                        <SectionLabel color="indigo">Principle: Config in Environment Variables</SectionLabel>
                        <p className="text-xs text-slate-400 mb-3">All environment-specific configuration is injected via environment variables — <strong className="text-white">never hardcoded</strong>.</p>
                        <div className="code-block text-[11px]">
                            <div className="text-slate-500"># api/config.py — centralized settings</div>
                            <div className="text-purple-300">ENVIRONMENT = os.environ.get(<span className="text-emerald-300">&quot;ENVIRONMENT&quot;</span>, <span className="text-emerald-300">&quot;development&quot;</span>)</div>
                            <div className="text-purple-300">MLFLOW_MODEL_ALIAS = os.environ.get(<span className="text-emerald-300">&quot;MLFLOW_MODEL_ALIAS&quot;</span>, <span className="text-emerald-300">&quot;production&quot;</span>)</div>
                            <div className="text-purple-300">MLFLOW_TRACKING_URI = os.environ.get(<span className="text-emerald-300">&quot;MLFLOW_TRACKING_URI&quot;</span>)</div>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="emerald">Staging Config</SectionLabel>
                            <div className="space-y-1">
                                <div className="text-[11px] text-slate-400 font-mono">ENVIRONMENT=<span className="text-emerald-300">staging</span></div>
                                <div className="text-[11px] text-slate-400 font-mono">MLFLOW_MODEL_ALIAS=<span className="text-emerald-300">staging</span></div>
                            </div>
                        </div>
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="amber">Production Config</SectionLabel>
                            <div className="space-y-1">
                                <div className="text-[11px] text-slate-400 font-mono">ENVIRONMENT=<span className="text-amber-300">production</span></div>
                                <div className="text-[11px] text-slate-400 font-mono">MLFLOW_MODEL_ALIAS=<span className="text-amber-300">production</span></div>
                            </div>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-3 mt-3">
                        <SectionLabel>Secrets Management</SectionLabel>
                        <Bullet icon="🔐"><strong className="text-white">GitHub Secrets</strong> — MLflow credentials, DagsHub tokens, Supabase keys (CI/CD)</Bullet>
                        <Bullet icon="🔐"><strong className="text-white">Render env vars</strong> — same secrets for deployed services (runtime)</Bullet>
                        <Bullet icon="🚫">Zero secrets in code, .env files are gitignored</Bullet>
                    </div>
                </div>
            ),
            notes: "We follow the 12-factor app methodology, particularly the strict separation of config from code. All environment-specific settings are read from environment variables through a centralized config module in api/config.py. The same codebase runs unchanged across development, staging, and production — only the environment variables differ. Staging uses ENVIRONMENT=staging and MLFLOW_MODEL_ALIAS=staging to load the staging model. Production uses ENVIRONMENT=production and the production alias. Secrets like MLflow credentials, DagsHub tokens, and Supabase API keys are stored in two places: GitHub Secrets for CI/CD pipelines, and Render environment variables for the deployed services. Zero secrets ever appear in the codebase — .env files are gitignored.",
        },

        /* ── 16. Automated Retraining ─────────────────────────── */
        {
            tag: "Retraining",
            tagColor: "badge-amber",
            title: "Automated Retraining & Feedback Loop",
            content: (
                <div>
                    <div className="glass rounded-xl p-3 mb-3">
                        <div className="flex gap-2 flex-wrap">
                            <span className="badge badge-amber">retrain.yml</span>
                            <span className="badge badge-indigo">cron: Sunday 02:00 UTC</span>
                            <span className="badge badge-purple">or: manual workflow_dispatch</span>
                        </div>
                    </div>
                    <DiagramFlowVertical items={[
                        { label: "1️⃣ Pull User Feedback", sub: "Supabase → convert to SQuAD format → DVC push" },
                        { label: "2️⃣ Fine-Tune Model", sub: "Download checkpoints → DVC pull → fine_tune.py → DVC push" },
                        { label: "3️⃣ Commit & Promote", sub: "Commit .dvc pointers → promotion_gate.py → Render deploy" },
                    ]} />
                    <div className="grid grid-cols-2 gap-3 mt-3">
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="emerald">Configurable Parameters</SectionLabel>
                            <Table
                                headers={["Param", "Default"]}
                                rows={[
                                    ["sample_ratio", "0.10 (10% of data)"],
                                    ["epochs", "2"],
                                    ["batch_size", "16"],
                                    ["learning_rate", "0.0003"],
                                ]}
                            />
                        </div>
                        <div className="glass rounded-xl p-3">
                            <SectionLabel color="purple">Feedback Loop</SectionLabel>
                            <DiagramFlowVertical items={[
                                { label: "👤 User submits 👎" },
                                { label: "📝 Correction saved (Supabase)" },
                                { label: "🔄 Pulled as new training data" },
                                { label: "🧠 Model improves" },
                            ]} />
                        </div>
                    </div>
                </div>
            ),
            notes: "The automated retraining pipeline closes the MLOps feedback loop. It runs weekly every Sunday at 2 AM UTC, or can be triggered manually with custom parameters. Step one: pull user feedback from Supabase. When users give a thumbs-down on an answer, they can provide the correct answer. Our script converts those corrections into SQuAD format triplets and appends them to the training dataset, then pushes the updated data to DVC. Step two: fine-tune the model. We download the existing checkpoints, pull the latest training data from DVC, run the fine-tuning script with configurable hyperparameters — default is 10% of data for 2 epochs — and log everything to MLflow. Step three: commit and promote. We commit the updated .dvc pointer files to the repository, run the promotion gate to check if the retrained model meets the F1 threshold, and trigger a Render deploy if it passes. The beauty of this is that user feedback continuously improves the model without any manual intervention.",
        },

        /* ── 17. Thank You ─────────────────────────────────── */
        {
            tag: "",
            tagColor: "",
            title: "",
            content: (
                <div className="flex flex-col items-center justify-center text-center py-8">
                    <h1 className="text-5xl font-bold mb-4">
                        <span className="bg-gradient-to-r from-emerald-300 via-teal-300 to-cyan-300 bg-clip-text text-transparent">
                            Thank You
                        </span>
                    </h1>
                    <p className="text-lg text-slate-400 mb-6">Questions on our MLOps implementation?</p>
                    <div className="flex gap-3 mb-6">
                        <span className="badge badge-indigo">Alon DEBASC</span>
                        <span className="badge badge-purple">Axel STOLTZ</span>
                        <span className="badge badge-emerald">Thibault CHESNEL</span>
                    </div>
                    <div className="glass rounded-xl p-4 mt-2 max-w-md">
                        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[11px] text-slate-500">
                            <div>🌐 Production URL</div>
                            <div className="text-slate-400 font-mono">onrender.com</div>
                            <div>📦 GitHub</div>
                            <div className="text-slate-400 font-mono">akksel1/final_project</div>
                            <div>📊 MLflow</div>
                            <div className="text-slate-400 font-mono">dagshub.com</div>
                        </div>
                    </div>
                </div>
            ),
            notes: "Thank you for your attention. To summarize, we've built a complete MLOps lifecycle covering experiment tracking with MLflow, data and model versioning with DVC, six automated CI/CD workflows with GitHub Actions, a model promotion gate that protects production quality, infrastructure-as-code deployment on Render, a three-layer testing strategy, 12-factor configuration management, and an automated retraining pipeline that closes the feedback loop. We're happy to take any questions about our MLOps implementation.",
        },
    ];
}

export default function MLOpsPresentationPage() {
    return <Presentation slides={buildSlides()} />;
}
