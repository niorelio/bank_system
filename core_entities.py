from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from enum import Enum
from decimal import Decimal

@dataclass
class Client:
    id: UUID | None = None
    login: str = ""
    password_hash: bytes = field(default_factory=lambda: b"")

@dataclass
class Account:
    client_id: UUID
    id: int | None = None
    balance: Decimal = field(default_factory=lambda: Decimal('0.0'))

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"

@dataclass
class Transaction:
    account_id: int
    amount: Decimal
    type: TransactionType
    id: int | None = None
    timestamp: datetime = field(default_factory=datetime.now)
