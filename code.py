# The purpose of this file is to practice writing python code manually.
# File and folder structure will not be the focus of this repo, focus is on merely typing code.
# AI agents are not allowed to write code for this repo, only offer support, ideas, or edits (if requested).


### RCT ###

# [CODE TO BE WRITTEN] 
from dataclasses import dataclass
import pandas as pd
import statsmodels.formula.api as smf

@dataclass
class RCTSpec:
    outcome: str = "y_post"
    treatment: str = "treat" 
    baseline: str = "y_pre"
    unit_id: str = "id"

def balance_check(df: pd.DataFrame, spec: RCTSpec) -> pd.DataFrame:
    rows = []
    for col in [spec.baseline]:
        m_t = df.loc[df[spec.treatment] == 1, col].mean()
        m_c = df.loc[df[spec.treatment] == 0, col].mean()
        rows.append({"variable":col, "mean_treat": m_t, "mean_control": m_c, "diff": m_t - m_c})
    return pd.DataFrame(rows)

def estimate_itt(df: pd.DataFrame, spec: RCTSpec):
    rows = []
    for col in [spec.baseline]:
        m_t = df.loc[df[spec.treatment] == 1, col].mean()
        n_t = df.loc[df[spec.treatment] == 1, col].count()


[CODE FROM HERE]



 # [CODE  TO IMITATE]

# rct_template.py
# Illustrative template (not publication-ready by itself)

from dataclasses import dataclass
import pandas as pd
import statsmodels.formula.api as smf


@dataclass
class RCTSpec:
    outcome: str = "y_post"
    treatment: str = "treat"     # 1 if assigned to treatment
    baseline: str = "y_pre"      # pre-treatment outcome (optional)
    unit_id: str = "id"


def balance_check(df: pd.DataFrame, spec: RCTSpec) -> pd.DataFrame:
    rows = []
    for col in [spec.baseline]:
        m_t = df.loc[df[spec.treatment] == 1, col].mean()
        m_c = df.loc[df[spec.treatment] == 0, col].mean()
        rows.append({"variable": col, "mean_treat": m_t, "mean_control": m_c, "diff": m_t - m_c})
    return pd.DataFrame(rows)


def estimate_itt(df: pd.DataFrame, spec: RCTSpec):
    # ITT with baseline adjustment; HC2 robust SE
    formula = f"{spec.outcome} ~ {spec.treatment} + {spec.baseline}"
    model = smf.ols(formula, data=df).fit(cov_type="HC2")
    return model


def run_rct_pipeline(path: str):
    spec = RCTSpec()
    df = pd.read_csv(path)

    required = [spec.unit_id, spec.treatment, spec.outcome, spec.baseline]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    print("N:", len(df))
    print("\nBalance check:")
    print(balance_check(df, spec))

    res = estimate_itt(df, spec)
    print("\nITT result (coefficient on treat):")
    print(res.summary().tables[1])


if __name__ == "__main__":
    run_rct_pipeline("data/rct_data.csv")



### RDD ###


#[CODE TO BE WRITTEN] 

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

np.random.seed(1)
n = 300
score = np.random.uniform(30, 70, n)
cutoff = 50
treat = (score >= cutoff).astype(int)
y = 10 + 0.4 * score + 5 * treat + np.random.normal(0, 2, n)

df = pd.DataFrame({"y": y, "score": score, "treat": treat})
df["running"] = df["score"] - cutoff

band = 8
local = df[np.abs(df["running"]) <= band]


# [CONTINUE FROM HERE]










 #[CODE TO IMITATE]

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

np.random.seed(1)
n = 300
score = np.random.uniform(30, 70, n)      # running variable
cutoff = 50
treat = (score >= cutoff).astype(int)     # treatment assignment at cutoff
y = 10 + 0.4 * score + 5 * treat + np.random.normal(0, 2, n)

df = pd.DataFrame({"y": y, "score": score, "treat": treat})
df["running"] = df["score"] - cutoff

band = 8                                  # use data near cutoff
local = df[np.abs(df["running"]) <= band]

model = smf.ols("y ~ treat + running + treat:running", data=local).fit()
print(model.summary().tables[1])
print("Estimated jump at cutoff (RDD effect):", round(model.params["treat"], 3))








### Synthetic Control ###


#[CODE TO BE WRITTEN] 


import numpy as np
import pandas as pd
from scipy.optimize import minimize

# fake panel data: unit, time, outcome, treated

np.random.seed(7)
units = ["A", "B", "C", "D", "E"]   # A is treated
times = np.arange(1, 21)
t0 = 12  # treatment starts at time 12

# [CONTINUE FROM HERE] 









 #[CODE TO IMITATE]
 
import numpy as np
import pandas as pd
from scipy.optimize import minimize

# ---- fake panel data: unit, time, outcome, treated ----
np.random.seed(7)
units = ["A", "B", "C", "D", "E"]   # A is treated
times = np.arange(1, 21)
t0 = 12  # treatment starts at time 12

rows = []
for u in units:
    base = np.sin(times / 3) + np.random.normal(0, 0.1, len(times))
    trend = 0.05 * times
    y = base + trend
    if u == "A":
        y = y + np.where(times >= t0, 1.0, 0.0)  # treatment effect after t0
    for t, val in zip(times, y):
        rows.append([u, t, val, int(u == "A")])
df = pd.DataFrame(rows, columns=["unit", "time", "y", "treated"])

# ---- build pre-treatment matrices ----
treated_unit = "A"
controls = [u for u in units if u != treated_unit]

pre = df[df["time"] < t0]
post = df[df["time"] >= t0]

y1_pre = pre[pre["unit"] == treated_unit].sort_values("time")["y"].values
Y0_pre = np.column_stack([
    pre[pre["unit"] == c].sort_values("time")["y"].values for c in controls
])

# ---- choose weights: min ||y1_pre - Y0_pre w||^2, s.t. w>=0 and sum(w)=1 ----
J = Y0_pre.shape[1]
w0 = np.ones(J) / J

def objective(w):
    return np.sum((y1_pre - Y0_pre @ w) ** 2)

constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
bounds = [(0, 1)] * J

res = minimize(objective, w0, method="SLSQP", bounds=bounds, constraints=constraints)
w_hat = res.x

# ---- construct synthetic outcome for all periods ----
Y0_all = np.column_stack([
    df[df["unit"] == c].sort_values("time")["y"].values for c in controls
])
y_synth_all = Y0_all @ w_hat
y_treated_all = df[df["unit"] == treated_unit].sort_values("time")["y"].values

gap = y_treated_all - y_synth_all

print("Estimated control weights:")
for c, w in zip(controls, w_hat):
    print(f"{c}: {w:.3f}")

print("\nAverage post-treatment effect (simple ATT path average):")
print(gap[times >= t0].mean())






### Language Modeling ###

#[CODE TO BE WRITTEN] 

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

text = "hello world " * 200  # replace with your own text






# [CODE TO IMITATE]

# character_lm_minimal.py — minimal character-level language model (PyTorch)
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Training text — replace with a file read or larger corpus for better results
text = "hello world " * 200
chars = sorted(set(text))
stoi = {c: i for i, c in enumerate(chars)}
itos = {i: c for i, c in enumerate(chars)}
vocab_size = len(chars)


class CharDataset(Dataset):
    """Sliding windows: predict next character at each position."""

    def __init__(self, text, block_size=8):
        self.data = [stoi[c] for c in text]
        self.block_size = block_size

    def __len__(self):
        return len(self.data) - self.block_size

    def __getitem__(self, i):
        chunk = self.data[i : i + self.block_size + 1]
        x = torch.tensor(chunk[:-1], dtype=torch.long)
        y = torch.tensor(chunk[1:], dtype=torch.long)
        return x, y


class TinyLM(nn.Module):
    """Embedding -> GRU -> linear head over vocabulary."""

    def __init__(self, vocab_size, n_embd=32, n_hidden=64):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, n_embd)
        self.rnn = nn.GRU(n_embd, n_hidden, batch_first=True)
        self.head = nn.Linear(n_hidden, vocab_size)

    def forward(self, x, h=None):
        e = self.emb(x)
        out, h = self.rnn(e, h)
        logits = self.head(out)
        return logits, h


def train():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    block_size = 16
    batch_size = 32
    epochs = 300
    lr = 1e-2

    ds = CharDataset(text, block_size)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=True)

    model = TinyLM(vocab_size).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    model.train()
    for epoch in range(epochs):
        total = 0.0
        for x, y in dl:
            x, y = x.to(device), y.to(device)
            logits, _ = model(x)
            loss = loss_fn(logits.reshape(-1, vocab_size), y.reshape(-1))
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item()
        if (epoch + 1) % 50 == 0:
            print(f"epoch {epoch + 1}  loss {total / len(dl):.4f}")

    return model


@torch.no_grad()
def sample(model, start="h", n=80, temperature=0.9):
    """Autoregressive sampling from the trained model."""
    model.eval()
    device = next(model.parameters()).device
    h = None
    ids = [stoi[c] for c in start if c in stoi]
    if not ids:
        ids = [0]
    out = ids.copy()
    x = torch.tensor([ids], dtype=torch.long, device=device)

    for _ in range(n):
        logits, h = model(x, h)
        # Higher temperature -> flatter distribution -> more random tokens
        logits = logits[:, -1, :] / temperature
        probs = torch.softmax(logits, dim=-1)
        next_id = torch.multinomial(probs, 1).item()
        out.append(next_id)
        x = torch.tensor([[next_id]], dtype=torch.long, device=device)
    return "".join(itos[i] for i in out)


if __name__ == "__main__":
    m = train()
    print(sample(m, start="h", n=100))




