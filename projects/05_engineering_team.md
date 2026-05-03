# Project 5 — Engineering Team

## What This Project Does

Four specialised agents collaborate to build a complete software module from a natural-language requirements spec. The engineering lead writes a design document; the backend engineer implements the module and can execute code to verify it; the frontend engineer writes a Gradio UI that wraps the module; the test engineer writes unit tests and can execute them to confirm they pass. Each agent's output is written to disk and feeds into the next agent via explicit `context:` links. The inputs — requirements, module name, class name — are hardcoded in `main.py` and can be changed before each run.

## New Concepts Introduced

**Multi-agent specialisation — dividing work across role-specific agents**
Rather than one agent doing everything, each agent is scoped to a single responsibility: design, implementation, UI, or testing. This mirrors how real engineering teams organise work. Each agent has a focused goal and backstory that shapes the style and depth of its output. The crew's sequential process ensures agents only receive output from the agents that precede them.

**Chained `context:` across four tasks**
`code_task` lists `context: [design_task]`, `frontend_task` lists `context: [code_task]`, and `test_task` lists `context: [code_task]`. This means the backend engineer reads the design, and both the frontend and test engineers read the implementation. The engineering lead's design never reaches the test engineer directly — it flows through the backend engineer's code, which is the right dependency. Context chains let you model information flow explicitly rather than passing everything to everyone.

**Mixed execution modes — some agents run code, others just write it**
`backend_engineer` and `test_engineer` have `allow_code_execution=True` and `code_execution_mode="safe"`. This lets them verify their output — the backend engineer can run the module to check it executes without error; the test engineer can run the test suite and see passes/failures. `engineering_lead` and `frontend_engineer` do not have code execution enabled — their output is text (a design doc) and Python source (a Gradio app), respectively, which does not need to be run during generation.

**Gradio UI generation as a task output**
The `frontend_task` produces a runnable `app.py` that imports from the generated `accounts.py`. The frontend agent is not running the UI — it is writing code that a human will run later. The key constraint in the task description is that the output must be raw Python with no markdown fences, so the file can be executed as-is.

**Mixing LLMs across agents**
Different agents can use different models. LLM is a one-line change per agent in `agents.yaml`.

## Key Principles

**Specialisation improves output quality.** A single agent asked to design, implement, test, and build a UI produces shallow work in each area. Separate agents with focused roles and backstories produce a design document that looks like a design document, code that looks like production code, and tests that cover edge cases — because each agent is primed to think like that specialist.

**Context chains model real information flow.** In a real team, the test engineer reads the code, not the design doc. Reflecting that in `context:` dependencies keeps each agent's input tight and reduces noise. Pass only what the agent actually needs.

**The LLM will extrapolate beyond the spec — and that's often good.** The engineering lead received a minimal requirements description and produced a production-grade design: a custom exception hierarchy, a `Transaction` dataclass with timestamps and UUIDs, historical time-travel queries (`at_time`), and serialisation helpers. None of this was in the spec. The more capable the model, the more it will apply engineering judgement rather than just transcribing the requirements. That's the value of a capable engineering lead agent.

**Raw code output requires explicit instruction.** LLMs default to wrapping code in markdown fences. Tasks that write code to `output_file` must explicitly instruct the agent to output raw Python only — otherwise the file will contain ` ```python ` delimiters and will not execute. This applies to every task that writes a `.py` file.

**Downstream agents match the API they actually received, not the one you expected.** Because the test engineer and frontend engineer read the backend code via `context:`, they adapted to the richer API the backend engineer produced — importing `AccountError`, `InsufficientFundsError`, `Transaction`, etc. This is a strength: the pipeline stays internally consistent even when agents diverge from the spec.

**`output_file` saves the final task output, not intermediate context.** The `code_task` output flows to `frontend_task` and `test_task` via context, but if the `output_file` path is misconfigured or the agent narrates rather than outputs raw code, the file won't land on disk. The downstream agents still get the code via context — the pipeline continues — but the file will be missing. Always verify all four output files exist after a run.

## Sample Output

**Requirements:** Account management system for a trading simulation platform — deposit/withdraw funds, buy/sell shares, portfolio value, profit/loss, transaction history, guard rails against overdrafts and invalid trades.

`output/engineering_team/accounts.py_design.md` (excerpt) — the engineering lead went beyond the spec, designing a production-grade module:
```markdown
## Exceptions

- class AccountError(Exception)           # base
- class InsufficientFundsError(AccountError)
- class InsufficientSharesError(AccountError)
- class InvalidTransactionError(AccountError)
- class UnknownSymbolError(AccountError)  # raised by get_share_price for unknown symbols

## Transaction dataclass

@dataclass
class Transaction:
    id: str                    # uuid4 hex
    timestamp: datetime
    type: str                  # "DEPOSIT" | "WITHDRAWAL" | "BUY" | "SELL"
    symbol: Optional[str]
    quantity: Optional[int]
    price: Optional[float]
    amount: float              # cash delta (positive = credit, negative = debit)
    balance_after: float
    notes: Optional[str]

## Class Account

def __init__(self, account_id: str, created_at: Optional[datetime] = None)
def deposit(self, amount: float, ...) -> Transaction
def withdraw(self, amount: float, ...) -> Transaction
def buy(self, symbol: str, quantity: int, ...) -> Transaction
def sell(self, symbol: str, quantity: int, ...) -> Transaction
def get_holdings(self, at_time: Optional[datetime] = None) -> Dict[str, int]
def get_portfolio_value(self, at_time: Optional[datetime] = None) -> float
def get_profit_loss(self, at_time: Optional[datetime] = None) -> float
def list_transactions(self, start=None, end=None, symbol=None, ttype=None,
                      limit=None, reverse=False) -> List[Transaction]
def to_dict(self) -> Dict[str, Any]
@classmethod def from_dict(cls, data) -> "Account"
```

`output/engineering_team/app.py` (excerpt) — the frontend engineer used `gr.State` to hold the account object across interactions, a better pattern than a global variable:
```python
with gr.Blocks(title="Trading Simulation Account Demo") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            # Controls: create, deposit, withdraw, buy, sell
            ...
        with gr.Column(scale=2):
            status_out = gr.Textbox(label="Status", ...)
            summary_out = gr.Textbox(label="Account Summary", lines=10)
            tx_out     = gr.Textbox(label="Transactions (most recent first)", lines=12)
    state = gr.State(value=None)  # holds the Account object between clicks

buy_btn.click(fn=buy_action,
              inputs=[symbol_dropdown, buy_qty, buy_notes, state],
              outputs=[status_out, summary_out, tx_out, state])
```

`output/engineering_team/test_accounts.py` (excerpt) — tests matched the richer API the backend engineer generated, including historical queries and exception types:
```python
class TestAccountHistoricalViews(unittest.TestCase):
    def test_get_holdings_at(self):
        self.assertEqual(self.ac.get_holdings(self.t1), {})       # before buy
        self.assertEqual(self.ac.get_holdings(self.t2), {"AAPL": 2})  # after buy

class TestListTransactionsAndSerialization(unittest.TestCase):
    def test_to_dict_and_from_dict_rebuilds_state(self):
        acc2 = Account.from_dict(self.ac.to_dict())
        self.assertAlmostEqual(acc2.get_cash_balance(), self.ac.get_cash_balance())
        self.assertEqual(acc2.holdings, self.ac.holdings)
```

## What to Try

- After running the crew, check that all four output files exist. If `accounts.py` is missing, the `app.py` and tests cannot be run — this is a sign the `code_task` agent narrated rather than outputting raw code. Tighten the `expected_output` wording or lower the model temperature.
- Run `uv run python output/engineering_team/app.py` (from the repo root, with `accounts.py` present) to launch the Gradio UI in a browser and exercise the full pipeline end-to-end.
- Compare the design doc to the original requirements and note every decision the engineering lead made that wasn't asked for — exception hierarchy, UUIDs, historical queries, serialisation. These are the places where model capability shows most clearly.
- Add a fifth agent — a `code_reviewer` — that reads both `design_task` and `code_task` via context and writes a markdown review noting where the implementation diverges from the design.
- Remove `context: [design_task]` from `code_task` and observe whether the backend engineer still produces a coherent, consistent implementation — does removing the design improve or degrade output quality?
- Set `allow_code_execution=False` on `test_engineer` and compare the test coverage — does writing tests without being able to run them produce more or fewer edge-case tests?
