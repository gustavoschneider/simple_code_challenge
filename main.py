from datetime import datetime, timedelta
from typing import Optional, Mapping, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from pydantic import BaseModel

class Account(BaseModel):
    account_id: int
    account_balance: float
    account_saving: float

class Movement(BaseModel):
    movement_id: Optional[int]
    amount: float
    description: str
    date: datetime

class MovementCreate(BaseModel):
    amount: float



ACCOUNTS = [
    Account(account_id=1, account_balance=1000.00, account_saving=1.00)
]

MOVEMENTS: Mapping[int, List[Movement]] = {}

app = FastAPI()

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError): # pylint: disable=unused-argument
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.get('/')
async def root() -> dict:
    return {
        'message': 'Hello'
    }

@app.get('/{account_id}', response_model=Account)
async def get_account(account_id: int) -> Account:
    accounts = [account for account in ACCOUNTS if account.account_id == account_id]
    if len(accounts) <= 0:
        raise HTTPException(status_code=404, detail='Account not found!')
    return accounts[0]


@app.post('/{account_id}/savings', response_model=Movement)
async def post_savings(account_id: int, movement: MovementCreate) -> Movement:
    if account_id not in MOVEMENTS:
        MOVEMENTS[account_id] = []

    account = await get_account(account_id=account_id)
    if account.account_balance <= movement.amount:
        raise ValueError('Account does not have funds.')

    next_movement_id = max(
        [ movement.movement_id for movement in MOVEMENTS[account_id]],
        default=0) + 1
    new_movement = Movement(
        movement_id = next_movement_id,
        amount=movement.amount,
        description='Moving from balance to savings',
        date=datetime.now()
        )
    account.account_balance -= movement.amount
    account.account_saving += movement.amount
    MOVEMENTS[account_id].append(new_movement)
    return new_movement


@app.post('/{account_id}/withdraw', response_model=Movement)
async def post_withdraw(account_id: int, movement: MovementCreate) -> Movement:
    if account_id not in MOVEMENTS:
        MOVEMENTS[account_id] = []

    account = await get_account(account_id=account_id)
    if account.account_saving <= movement.amount:
        raise ValueError('Account savings does not have funds.')

    next_movement_id = max(
        [ movement.movement_id for movement in MOVEMENTS[account_id]],
        default=0) + 1
    new_movement = Movement(
        movement_id = next_movement_id,
        amount=movement.amount,
        description='Moving from savings to balance',
        date=datetime.now()
        )
    account.account_saving -= movement.amount
    account.account_balance += movement.amount
    MOVEMENTS[account_id].append(new_movement)
    return new_movement

@app.get('/{account_id}/movements')
async def get_movements(account_id: int, month: int | None = None) -> dict:
    account = await get_account(account_id=account_id)

    if month is None:
        month = datetime.today().month

    first_date = datetime(year=datetime.today().year, month=month, day=1)
    last_date = last_day_of(month=month)
    movements = [movement for movement in MOVEMENTS.get(account.account_id, []) \
                 if movement.date >= first_date and movement.date <= last_date]
    return {
        'account': account,
        'movements': movements
    }

def last_day_of(month: int) -> datetime:
    year = datetime.today().year
    if month == 12:
        year += 1
        month = 1
    else:
        month +=1
    return datetime(year=year, month=month, day=1) - timedelta(days=1)
