"""add gvdbs_retr_params to api_groups

Revision ID: cba154c972d6
Revises: adf87cf4e03f
Create Date: 2026-01-24 05:22:59.315648

"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'cba154c972d6'
down_revision: Union[str, Sequence[str], None] = 'adf87cf4e03f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def convert_old(gvdbs_cfg: str) -> str:
        def_dict = {
            'search_type': 'similarity', 
            'search_kwargs__similarity': {'k': 10},
            'search_kwargs__mmr': {'k': 10, 'fetch_k': 20, 'lambda_mult': 0.5},
            'search_kwargs__similarity_score_threshold': {'k': 10, 'score_threshold': 0.5}
        }
        def get_pos_int(value: str | float | int) -> int:
            value = int(value)
            if value <= 0:
                raise Exception
            return value            
        def get_float(value: str | float | int) -> float:
            return float(value)            
        try:
            d: dict = json.loads(gvdbs_cfg) if isinstance(gvdbs_cfg, str) else gvdbs_cfg
            search_type = str(d['search_type'])
            if not(search_type in ['similarity', 'mmr', 'similarity_score_threshold']):
                raise Exception
            sk: dict[str, int | float] = dict(d['search_kwargs'])
            # make new search_kwargs__* dictionaries
            drp = def_dict['search_kwargs__similarity']
            k = get_pos_int(sk.get('k', int(drp['k'])))
            sk_sim = {'k': k}
            #
            drp = def_dict['search_kwargs__mmr']
            k = get_pos_int(sk.get('k', int(drp['k'])))
            fetch_k = get_pos_int(sk.get('fetch_k', int(drp['fetch_k'])))
            lambda_mult = get_float(sk.get('lambda_mult', float(drp['lambda_mult'])))
            sk_mmr = {'k': k, 'fetch_k': fetch_k, 'lambda_mult': lambda_mult}
            #
            drp = def_dict['search_kwargs__similarity_score_threshold']
            k = get_pos_int(sk.get('k', int(drp['k'])))
            score_threshold = get_float(sk.get('score_threshold', float(drp['score_threshold'])))
            sk_sst = {'k': k, 'score_threshold': score_threshold}
            return json.dumps({
                'search_type': search_type,
                'search_kwargs__similarity': sk_sim,
                'search_kwargs__mmr': sk_mmr,
                'search_kwargs__similarity_score_threshold': sk_sst
            }, default=str)            
        except Exception:
            raise ValueError(f'Wrong api_settings -> gvdbs_cfg_json value:\n{gvdbs_cfg}') from None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Add the column as nullable first
    op.add_column(
        'api_groups',
        sa.Column('gvdbs_retr_params', sa.VARCHAR(), nullable=True)
    )
    
    # Step 2: Populate the column with value from api_settings
    connection = op.get_bind()
    
    # Get the value from api_settings
    result = connection.execute(
        text("SELECT value FROM api_settings WHERE name = 'gvdbs_def_retr_params'")
    ).fetchone()
    
    if result is None:
        result = connection.execute(
            text("SELECT value FROM api_settings WHERE name = 'gvdbs_cfg_json'")
        ).fetchone()
        if result is None:
            raise ValueError(
                "Cannot find 'gvdbs_cfg_json' in api_settings table. "
                "Please ensure this setting exists before running the migration."
            )
        gvdbs_cfg_json_str = result[0]
        default_value = convert_old(gvdbs_cfg_json_str)
        connection.execute(
            text("INSERT INTO api_settings (name, value) VALUES(:name, :value)"), 
            {"name": 'gvdbs_def_retr_params', "value": default_value}
        )        
    else:
        default_value = result[0]
    
    # Update all existing rows with the value
    connection.execute(
        text("UPDATE api_groups SET gvdbs_retr_params = :value"),
        {"value": default_value}
    )
    
    # Step 3: Make the column non-nullable
    op.alter_column(
        'api_groups',
        'gvdbs_retr_params',
        nullable=False
    )
    connection.execute(
        text("DELETE FROM api_settings WHERE name=:name"), 
        {"name": 'gvdbs_cfg_json'}
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the column
    op.drop_column('api_groups', 'gvdbs_retr_params')
    connection = op.get_bind()
    value = r'{"search_type": "similarity", "search_kwargs": {"k": 20}}'
    connection.execute(
        text("INSERT INTO api_settings (name, value) VALUES(:name, :value)"), 
        {"name": 'gvdbs_cfg_json', "value": value}
    )
    connection.execute(
        text("DELETE FROM api_settings WHERE name=:name"), 
        {"name": 'gvdbs_def_retr_params'}
    )

