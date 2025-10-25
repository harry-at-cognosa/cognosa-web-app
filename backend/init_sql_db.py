###
# This script will create necessary tables in database
# and INSERT data rows from file: .api_settings_init_data.json
###

import asyncio
from datetime import datetime, timedelta
import json
import os
from sqlalchemy import text
from common import WORK_DIR
from common.helpers import utcnow
from common.enums.api_settings_names import API_SETTINGS_NAMES_LIST
from common.enums.doc_task_status import TaskStatus
from common.sql_db_async import Base, sql_async_engine, async_get_session
from common.sql_models import ApiSettings, ApiGroups, GroupVDBs, GroupLLMs, GroupContexts, DocTasks, User
from common.sql_tools import fix_autoincrement
from cwa_lib.sql_tables.api_users import ApiUsersTable

# log.init('init_sql_db', log_sqlalchemy='DEBUG')

with open(os.path.join(WORK_DIR, '.init_sql_data', 'api_settings.json'), 'r', encoding='utf8') as f_json:
    api_settings_initial_data = json.loads(f_json.read())

with open(os.path.join(WORK_DIR, '.init_sql_data', 'api_groups.json'), 'r', encoding='utf8') as f_json:
    api_groups_initial_data = json.loads(f_json.read())

with open(os.path.join(WORK_DIR, '.init_sql_data', 'api_users.json'), 'r', encoding='utf8') as f_json:
    api_users_initial_data = json.loads(f_json.read())

with open(os.path.join(WORK_DIR, '.init_sql_data', 'group_vdbs.json'), 'r', encoding='utf8') as f_json:
    group_vdbs_initial_data = json.loads(f_json.read())

with open(os.path.join(WORK_DIR, '.init_sql_data', 'group_llms.json'), 'r', encoding='utf8') as f_json:
    group_llms_initial_data = json.loads(f_json.read())

with open(os.path.join(WORK_DIR, '.init_sql_data', 'group_contexts.json'), 'r', encoding='utf8') as f_json:
    group_contexts_initial_data = json.loads(f_json.read())

with open(os.path.join(WORK_DIR, '.init_sql_data', 'doc_tasks.json'), 'r', encoding='utf8') as f_json:
    doc_tasks_initial_data = json.loads(f_json.read())


class InitDatabase:
    def __init__(self) -> None:
        pass

    async def run(self):
        # 1. Drop the table if it exists
        # 2. Create the table
        await self.drop_and_recreate()
        # 3. Insert initial data
        await self.insert_values()
        # Close the engine
        await sql_async_engine.dispose()

    async def drop_and_recreate(self):
        async with sql_async_engine.begin() as conn:            
            # 1. Drop the table if it exists
            # Get all table names from metadata
            table_names = list(reversed(Base.metadata.tables.keys()))  # reverse to drop children first (optional, CASCADE handles it)
            table_names += ['tasks']  # TODO: remove in the next init_sql_db versions
            for table_name in table_names:
                await conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'))
            await conn.execute(text("DROP TYPE IF EXISTS gllms_type_enum CASCADE;"))
            await conn.execute(text("DROP TYPE IF EXISTS gvdbs_type_enum CASCADE;"))
            # 2. Create the table
            await conn.run_sync(Base.metadata.create_all)
    
    async def insert_values(self):
        # 3. Insert initial data
        async for session in async_get_session():
            try:
                api_settings_names_left = API_SETTINGS_NAMES_LIST[:]
                errors = False
                for item in api_settings_initial_data:
                    if (name := item['name']) in api_settings_names_left:
                        api_settings_names_left.remove(name)
                    else:
                        print(f"Wrong {name=} in .init_sql_data/api_settings.json")
                        errors = True
                for name in api_settings_names_left:
                        print(f"Not found {name=} in .init_sql_data/api_settings.json")
                        errors = True
                if errors:
                    exit(-1)

                api_settings_objects = [
                    ApiSettings(name=item['name'], value=item['value']) 
                    for item in api_settings_initial_data
                ]                
                session.add_all(api_settings_objects)
                await session.commit()
                print(f"Inserted {len(api_settings_objects)} api_settings rows")
                
                api_groups_objects = [
                    ApiGroups(group_id=item['group_id'], group_name=item['group_name'], created_at=utcnow())
                    for item in api_groups_initial_data                
                ]
                session.add_all(api_groups_objects)
                await session.commit()
                await fix_autoincrement(session, ApiGroups)
                print(f"Inserted {len(api_groups_objects)} api_groups rows")

                # api_users
                for item in api_users_initial_data:
                    try:
                        await ApiUsersTable.create_user(
                            user_id=item.get('user_id'),
                            email=item['email'],
                            password=item['password'],
                            user_name=item['user_name'],
                            full_name=item['full_name'],
                            group_id=item['group_id'],
                            is_active=item.get('is_active', True),
                            is_verified=item.get('is_verified', True),
                            is_superuser=item.get('is_superuser', False),
                            is_groupadmin=item.get('is_groupadmin', False),
                            is_contentmanager=item.get('is_contentmanager', False),
                        )
                    except Exception as exc:
                        print(exc)
                        exit(-1)
                await fix_autoincrement(session, User)
                
                group_vdbs_objects = [
                    GroupVDBs(
                        group_id=item['group_id'], 
                        gvdbs_seqn=item['gvdbs_seqn'],
                        gvdbs_type=item['gvdbs_type'],
                        gvdbs_name=item['gvdbs_name'],
                        gvdbs_url=item['gvdbs_url'], 
                        gvdbs_collection=item['gvdbs_collection'], 
                        gvdbs_emb_model=item['gvdbs_emb_model'],
                        gvdbs_created_at=utcnow()
                    )
                    for item in group_vdbs_initial_data                
                ]
                session.add_all(group_vdbs_objects)
                await session.commit()
                print(f"Inserted {len(group_vdbs_objects)} group_vdbs rows")

                group_llms_objects = [
                    GroupLLMs(
                        group_id=item['group_id'], 
                        gllms_seqn=item['gllms_seqn'],
                        gllms_type=item['gllms_type'],
                        gllms_name=item['gllms_name'],
                        gllms_api_base=item['gllms_api_base'], 
                        gllms_model=item['gllms_model'], 
                        gllms_api_key=item['gllms_api_key'],
                        gllms_created_at=utcnow()
                    )
                    for item in group_llms_initial_data                
                ]
                session.add_all(group_llms_objects)
                await session.commit()
                print(f"Inserted {len(group_llms_objects)} group_llms rows")
                
                group_contexts_objects = [
                    GroupContexts(
                        group_id=item['group_id'], 
                        gc_seqn=item['gc_seqn'],
                        gc_name=item['gc_name'],
                        gc_text=item['gc_text'],
                        created_at=utcnow()
                    )
                    for item in group_contexts_initial_data                
                ]
                session.add_all(group_contexts_objects)
                await session.commit()
                print(f"Inserted {len(group_contexts_objects)} group_contexts rows")

                def prepare_dt(item: dict, minutes_plus: int = 0):
                    return datetime.now() \
                        - timedelta(hours=int(item.get('created_at__hours_before', 1))) \
                        + timedelta(minutes=minutes_plus)
                doc_tasks_objects = [
                    DocTasks(
                        group_id=item.get('group_id', 1), 
                        user_id=item.get('user_id', 1),
                        status=TaskStatus.QD_LLM_FETCHED,
                        status_text="Completed",
                        short_name=item.get('short_name', ''),
                        input_text=item.get('input_text', ''),
                        optional_text=item.get('optional_text', ''),
                        gvdbs_id=item.get('gvdbs_id', 1),
                        gvdbs_json="{}",
                        gllms_id=item.get('gllms_id', 1),
                        gllms_json="{}",
                        gc_id=item.get('gc_id', 1),
                        context_json=item.get('context_json', '[]'),
                        output_text=item.get('output_text', ''),
                        created_at=prepare_dt(item, 0),
                        fetched_at=prepare_dt(item, 1),
                        context_at=prepare_dt(item, 2),
                        completed_at=prepare_dt(item, 3),
                        vdb_query_seconds=1,
                        llm_query_seconds=1,
                        llm_tokens_sent=1,
                        llm_tokens_received=1,
                    )
                    for item in doc_tasks_initial_data                
                ]
                session.add_all(doc_tasks_objects)
                await session.commit()
                print(f"Inserted {len(doc_tasks_objects)} doc_tasks rows")
            except Exception as e:
                print(f"Error inserting data!")
                raise
            except SystemExit:
                print(f"Error inserting data!")
            else:
                print("Database initialized successfully!")
            finally:
                await session.close()


if __name__ == "__main__":
    asyncio.run(InitDatabase().run())
